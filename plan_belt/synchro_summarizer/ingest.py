import pandas as pd
import numpy as np
from pathlib import Path
import subprocess
import openpyxl
import re


class SynchroTxt:
    """
    Class to summarize and handle Synchro text files

    """

    def __init__(self, filepath: Path, simtraffic: Path = None) -> None:
        self.filepath = Path(filepath)
        self.dir = self.filepath.parent
        self.whole_csv = pd.read_csv(
            self.filepath, header=None, names=range(30), delimiter="\t", engine="python"
        )
        self.whole_csv = self.whole_csv.dropna(axis=1, how="all")
        self.project_name = str(self.whole_csv.at[0, 0])
        self.startrows = self.whole_csv[
            self.whole_csv[0] == self.project_name
        ].index.tolist()
        self.count = 0
        self.dfs = {}
        self.anomolies = {}
        self.__assemble_dfs()  # populates self.dfs
        if simtraffic is not None:
            self.sim_dfs = SynchroSim(
                Path(simtraffic), "false").return_queues_for_intersection()
            for key in self.sim_dfs:
                keynum = key.split(":")[1].strip()
                for dfkey in self.dfs:
                    dfkey_num = dfkey.split(":")[0]
                    if dfkey_num == keynum:  # if intersection number is the same
                        self.dfs[dfkey] = self.combine_synchro_sim(
                            self.sim_dfs[key], self.dfs[dfkey])

        else:
            pass
        self.create_csv()

    def __create_df(self, index):
        """Create a dataframe from specified startrows index

        dfs are split by self.startrows attribute;
        synchro report break point between tables is the project name
        """
        possible_report_types = [
            "HCM Unsignalized Intersection Capacity Analysis",
            "HCM 6th TWSC",
            "HCM Signalized Intersection Capacity Analysis",
            "HCM 6th Signalized Intersection Summary",
        ]
        try:
            df = self.whole_csv[index: self.startrows[self.count + 1]]
        except IndexError:
            df = self.whole_csv[index:]
        df = df.reset_index(drop=True)
        intersection_name = df.iloc[1, 0]
        if df.loc[(df.shape[0] - 2), 0] in possible_report_types:
            report_type = df.loc[(df.shape[0] - 2), 0]
        elif df.loc[0, 0] in possible_report_types:
            report_type = df.loc[0, 0]
        else:
            print("Report type not in expected locations...")
        unique_name = intersection_name + " " + "| " + report_type
        if df.iloc[2, 0].strip() == "Movement":
            df = df.iloc[2:]
            df = df.reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df[1:]
            df.columns = df.columns.str.rstrip()
        elif df.iloc[2, 0].strip() == "Intersection":
            df = df.iloc[4:]
            df = df.reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df[1:]
            df.columns = df.columns.str.rstrip()
        elif "not" in df.iloc[2, 0].strip():
            self.anomolies[unique_name] = df
        elif "expects" in df.iloc[2, 0].strip():
            self.anomolies[unique_name] = df
        else:
            print("what else could go wrong?")
        self.count += 1
        return df, unique_name

    def __assemble_dfs(self):
        """Assembles and cleans up dfs from report"""

        for index in self.startrows:
            df, unique_name = self.__create_df(index)
            df = df.replace("-", np.NaN)
            if unique_name in self.anomolies:
                pass
            else:
                # add all values from any report type that you want reported
                field_names = [
                    "Movement",
                    "Lane Configurations",
                    "Lanes",
                    "Traffic Volume (veh/h)",
                    "Traffic Vol, veh/h",
                    "V/C Ratio(X)",
                    "v/c Ratio",
                    "HCM Lane V/C Ratio",
                    "Volume to Capacity",
                    "%ile BackOfQ(50%),veh/ln",
                    "%ile BackOfQ(95%),veh/ln",
                    "Queue Length 95th (ft)",
                    "HCM 95th %tile Q(veh)",
                    "LnGrp Delay(d),s/veh",
                    "Delay (s)",
                    "Control Delay (s)",
                    "HCM Control Delay (s)",
                    "Lane LOS" "LnGrp LOS",
                    "Level of Service",
                    "HCM Lane LOS",
                    "Approach Delay, s/veh",
                    "Approach LOS",
                    "HCM 6th Ctrl Delay",
                    "HCM 6th LOS",
                    "HCM 2000 Control Delay"
                    "HCM 2000 Level of Service"  # note: this one might need to be
                    # cleaned up, its not in first col
                ]
                df.query(
                    f"Movement.str.strip() in {field_names}", inplace=True)
                df = df.reset_index(drop=True)
                df = df.dropna(axis=1, how="all")
                df["Movement"] = df["Movement"].str.strip()
                df = df.transpose()
                df.columns = df.iloc[0]
                df = df[1:]
                if "HCM 6th Signalized Intersection Summary" in unique_name:
                    try:
                        df = self.__convert_queue(
                            df, "%ile BackOfQ(50%),veh/ln")
                    except KeyError:
                        df = self.__convert_queue(
                            df, "%ile BackOfQ(95%),veh/ln")

                elif "HCM 6th TWSC" in unique_name:
                    df = self.__convert_queue(df, "HCM 95th %tile Q(veh)")
                elif "HCM Unsignalized Intersection Capacity Analysis" in unique_name:
                    df = self.__convert_queue(df, "Queue Length 95th (ft)")
                else:
                    pass
                df = df.apply(pd.to_numeric, errors="ignore")
                df.index = pd.MultiIndex.from_arrays(
                    [df.index.str[:2], df.index.str[2:]]
                )
                df = df.rename_axis(("Direction", "Movement"))
                df = df.rename(
                    columns={
                        "Lanes": "Lane Configurations",
                        "LnGrp Delay(d),s/veh": "Delay (s)",
                        "Control Delay (s)": "Delay (s)",
                        "HCM Control Delay (s)": "Delay (s)",
                    }
                )
                self.__delay_queue_cleanup(df)
                self.dfs[unique_name] = df

    def __convert_queue(self, df, column_name: str):
        """Converts queue from vehicle lengths to feet"""

        percentile = re.findall(r"\d+", column_name)[0]
        df = df.rename(
            columns={f"{column_name}": f"{percentile} %ile BackOfQ,feet"})
        df[f"{percentile} %ile BackOfQ,feet"] = df[
            f"{percentile} %ile BackOfQ,feet"
        ].apply(pd.to_numeric)
        df[f"{percentile} %ile BackOfQ,feet"] = (
            df[f"{percentile} %ile BackOfQ,feet"] * 25
        ).round()  # 25' per car instead of just car lengths
        return df

    def __delay_queue_cleanup(self, df):
        """
        Reads the lane configuration and applies delay and queue lengths to adjacent
        cells, as appropriate.

        Used as a way to ensure that delay and queue length is applied to all relevant
        cells in the final excel output
        """
        df_movement = df.index.levels[0]
        cols = df.columns.to_list()
        queue_match = re.compile("....ile BackOfQ,feet")
        match = [string for string in cols if re.match(queue_match, string)]

        for value in df_movement:
            max_delay = []
            max_queue = []
            xs = df.xs(value).index.tolist()
            for x in xs:
                if df.at[(value, x), "Lane Configurations"] == "1":
                    pass  # max delay not needed if its its own lane w/o a shared mvmt
                else:
                    max_delay.append(df.at[(value, x), "Delay (s)"])
                    if len(match) == 1:
                        max_queue.append(df.at[(value, x), match[0]])
                    else:
                        pass
            for x in xs:
                if df.at[(value, x), "Lane Configurations"] == "0":
                    pass
                elif pd.isnull(df.at[(value, x), "Lane Configurations"]):
                    pass
                elif df.at[(value, x), "Lane Configurations"] == "1":
                    pass
                elif re.findall("<.>", str(df.at[(value, x), "Lane Configurations"])):
                    for x in xs:
                        df.at[(value, x), "Delay (s)"] = max(max_delay)
                        try:
                            df.at[(value, x), match[0]] = max(max_queue)
                        except:
                            pass
                elif re.findall("<.", str(df.at[(value, x), "Lane Configurations"])):
                    for x in xs:
                        if x == "R":
                            pass
                        else:
                            df.at[(value, x), "Delay (s)"] = max(max_delay)
                            try:
                                df.at[(value, x), match[0]] = max(max_queue)
                            except:
                                pass
                elif re.findall(".>", str(df.at[(value, x), "Lane Configurations"])):
                    for x in xs:
                        if x == "L":
                            pass
                        else:
                            df.at[(value, x), "Delay (s)"] = max(max_delay)
                            try:
                                df.at[(value, x), match[0]] = max(max_queue)
                            except:
                                pass

    def create_csv(self):
        """Creates a csv in the directory the files came from."""

        counter = 1
        df_shape_counter = 1
        with pd.ExcelWriter(self.dir / "synchro_sum.xlsx") as writer:
            for key in self.dfs:
                counter_string = str(counter)
                self.dfs[key].to_excel(
                    writer, sheet_name="summary", startrow=df_shape_counter
                )
                self.dfs[key].to_excel(
                    writer, sheet_name=counter_string, startrow=1)
                keyseries = pd.Series([key])
                iterators = [counter_string, "summary"]
                for val in iterators:
                    if val == counter_string:
                        startrow = 0
                    elif val == "summary":
                        startrow = df_shape_counter - 1
                    keyseries.to_excel(
                        writer,
                        sheet_name=(val),
                        index=False,
                        header=False,
                        startrow=startrow,
                    )
                counter += 1
                df_shape_counter += self.dfs[key].shape[0] + 4

    def combine_synchro_sim(self, sim_df, synchro_df):
        """Does the actual heavy lifting of combining the dataframes"""

        sim_df = sim_df.transpose()
        synchro_df['simtraffic_queue'] = None
        for value in sim_df.index:
            if len(value[1]) == 1:
                synchro_df.at[(value), 'simtraffic_queue'] = sim_df.at[(
                    value)]['95th Queue (ft)'][0]
            elif len(value[1]) == 2:
                for char in value[1]:
                    synchro_df.at[(value[0], char), 'simtraffic_queue'] = sim_df.at[(
                        value)]['95th Queue (ft)'][0]
        return synchro_df


class SynchroSim:
    """
    Class to handle simtraffic pdfs.

    Leverages Linux tool pdftotext to setup initial text file.

    """

    def __init__(self, filepath: Path, csv: str) -> None:
        self.filepath = Path(filepath)
        self.dir = self.filepath.parent
        self.__create_txt()
        self.full_df = pd.read_csv(
            self.filepath.with_suffix(".txt"),
            # if dfs aren't coming in right, tune the number on the left, which represents the minimum spaces used as separator
            sep="\s{5,100}",
            engine="python",
            names=range(15),
        )
        if csv.lower() == "true":
            self.create_csv()
        elif csv.lower() == "false":
            self.return_queues_for_intersection()
        else:
            print("Must use true or false in the csv flag.")

    def __create_txt(self):
        """
        Uses subprocess module and pdftotext tool to turn simtraffic pdf to text file.
        """
        subprocess.run(
            f"pdftotext -layout -colspacing 2 -nopgbrk '{self.filepath}'",
            shell=True,
            check=True,
        )

    def find_arterial_los(self) -> pd.DataFrame:
        """
        Grabs any Arterial LOS headers in Simtraffic report compiles necessary columns into a df.
        """

        cols = [
            "direction",
            "delay (s/veh)",
            "travel time (s)",
            "dist (mi)",
            "arterial speed",
        ]
        headers = self.full_df[
            self.full_df[0].str.contains("Arterial Level of Service", na=False)
        ]
        los_totals = self.full_df[self.full_df[0].str.contains(
            "Total", na=False)]
        los_totals = los_totals.drop([0], axis=1)
        headers = headers.dropna(axis="columns")
        headers = headers[headers[0] != "Arterial Level of Service"]
        los_totals = los_totals.dropna(axis="columns")
        arterial_los = pd.concat(
            [headers.reset_index(drop=True), los_totals.reset_index(drop=True)], axis=1
        )
        arterial_los.columns = cols
        arterial_los = arterial_los.drop(
            ["dist (mi)", "arterial speed"], axis=1)
        return arterial_los

    def qb_intersection(self, intersection_name: str, is_duplicate: bool):
        """
        Generates a dataframe of queuing and blocking report for one intersection

                Parameters:
                    intersection_name (str): The SimTraffic intersection you're analyzing
                    is_duplicate (bool): Marked duplicate in qb_report function if the intersection appears twice.

        limitations: is_duplicate has only been built for cases with one duplicate intersection, for now
        """
        intersection_index = self.full_df[
            self.full_df[0].str.contains(f"{intersection_name}", na=False)
        ].index[0]

        if is_duplicate is True:
            intersection_index = intersection_index + 12
        else:
            pass

        intersection_df = self.full_df.iloc[
            intersection_index: (intersection_index + 6)
        ]
        intersection_df = intersection_df.reset_index(drop=True)
        intersection_df = intersection_df.set_index(0)
        intersection_df = intersection_df.drop(intersection_name)
        intersection_df = intersection_df.drop("Maximum Queue (ft)", axis=0)
        intersection_df = intersection_df.drop("Average Queue (ft)", axis=0)
        intersection_df = intersection_df.dropna(axis=1, how="all")
        intersection_df.columns = intersection_df.iloc[0]
        col_list = intersection_df.columns.tolist()
        if len(col_list) > 1:
            intersection_df = intersection_df[col_list].agg(
                " ".join, axis=1).to_frame()
            intersection_df.columns = intersection_df.iloc[0]
            col_list = intersection_df.columns.tolist()
            intersection_df = intersection_df[col_list[0]].str.split(
                expand=True)

        else:
            intersection_df = intersection_df[col_list[0]].str.split(
                expand=True)

        newcols = col_list[0].split()
        intersection_df.columns = newcols
        intersection_df = intersection_df[1:]
        movement = intersection_df.iloc[0]
        headers = [newcols, movement.tolist()]
        intersection_df.columns = headers
        intersection_df = intersection_df.drop("Directions Served", axis=0)
        intersection_df = intersection_df.astype(int)
        return intersection_df

    def qb_report(self):
        """
        Generates a dataframe of a queuing and blocking, for all intersections in the report.
        """
        dfs = {}
        duplicate_list = []
        headers = self.full_df[self.full_df[0].str.contains("Intersection", na=False)][
            0
        ].tolist()

        for intersection in headers:
            if intersection in duplicate_list:
                intersection_df = self.qb_intersection(
                    intersection_name=intersection, is_duplicate=True
                )
                intersection = intersection + " B"

            else:
                intersection_df = self.qb_intersection(
                    intersection_name=intersection, is_duplicate=False
                )

            duplicate_list.append(intersection)
            dfs[intersection] = intersection_df

        return dfs

    def create_csv(self):
        """Used when this an independent CSV summary is needed"""
        df = self.find_arterial_los()
        dfs = self.qb_report()
        shape = df.shape[0]
        start_count = shape + 4

        with pd.ExcelWriter(self.dir / "sim_summary.xlsx") as writer:
            df.to_excel(writer, sheet_name="summary", index=False)
            df.to_excel(writer, sheet_name="arterial_los", index=False)
            for key in dfs:
                dfs[key] = dfs[key].transpose()
                dfs[key].to_excel(
                    writer,
                    sheet_name=re.sub("[&: ]", "", key[16:]),
                    index=True,
                )
                sheet = re.sub("[&: ]", "", key[16:])
                writer.sheets[sheet].set_row(2, None, None, {"hidden": True})
                dfs[key].to_excel(
                    writer, sheet_name="summary", index=True, startrow=start_count
                )
                keyseries = pd.Series([key])
                keyseries.to_excel(
                    writer,
                    sheet_name="summary",
                    index=False,
                    header=False,
                    startrow=start_count - 1,
                )
                shape2 = dfs[key].shape[0]
                start_count += shape2 + 6

    def return_queues_for_intersection(self):
        dfs = self.qb_report()
        return dfs
