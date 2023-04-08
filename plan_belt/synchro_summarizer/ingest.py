import pandas as pd
from pathlib import Path
import subprocess
import openpyxl
import re


class SynchroTxt:
    """
    Class to summarize and handle Synchro text files

    Todo: build handler for multiple page / intersection files

    """

    def __init__(self, filepath: Path) -> None:
        self.filepath = Path(filepath)
        self.dir = self.filepath.parent
        self.metadf = pd.read_csv(
            self.filepath, nrows=2, header=None, usecols=[0], delimiter="\t"
        )
        self.hcm_version = self.metadf.iloc[0, 0]
        self.intersection_name = self.metadf.iloc[1, 0]
        self.streets = self.intersection_name.split("&")
        self.street_a = self.streets[0].split(":")[1]
        self.street_b = self.streets[1]
        self.df = pd.read_csv(self.filepath, skiprows=4, delimiter="\t")
        self.column_names = [x.strip(" ") for x in self.df.columns.values.tolist()]
        self.df.columns = self.column_names
        self.scenario = self.df.iloc[43]["Movement"]
        self.volume = self.df.loc[[1]]
        self.vc_ratio = self.df.loc[[20]]
        self.queue = self.df.loc[[27]]
        self.ln_grp_delay = self.df.loc[[29]]
        self.ln_grp_los = self.df.loc[[30]]
        self.approach_delay = self.df.loc[[32]]
        self.approach_los = self.df.loc[[33]]
        self.intersection_control_delay = self.df.loc[[41]]
        self.intersection_los = self.df.loc[[42]]
        self.summary = pd.concat(
            [
                self.volume,
                self.vc_ratio,
                self.queue,
                self.ln_grp_delay,
                self.ln_grp_los,
                self.approach_delay,
                self.approach_los,
                self.intersection_control_delay,
                self.intersection_los,
            ],
            ignore_index=True,
        )
        self.summary = self.summary.drop("Unnamed: 1", axis=1)
        self.summary = self.summary.transpose()
        self.summary.columns = self.summary.iloc[0]
        self.summary = self.summary[1:]
        self.column_names = [x.strip(" ") for x in self.summary.columns.values.tolist()]
        self.summary.columns = self.column_names
        self.summary = self.summary.rename(
            columns={"%ile BackOfQ(95%),veh/ln": "%ile BackOfQ(95%),feet"}
        )
        self.summary["%ile BackOfQ(95%),feet"] = self.summary[
            "%ile BackOfQ(95%),feet"
        ].apply(pd.to_numeric)
        self.summary["%ile BackOfQ(95%),feet"] = (
            self.summary["%ile BackOfQ(95%),feet"] * 25
        )  # 25' per car instead of just car lengths
        self.summary.index = pd.MultiIndex.from_arrays(
            [self.summary.index.str[:2], self.summary.index.str[2:]]
        )
        self.summary = self.summary.rename_axis(("Direction", "Movement"))
        self.to_csv()

    def to_csv(self):
        with pd.ExcelWriter(self.dir / "synchro_summary.xlsx") as writer:
            self.summary.to_excel(writer, sheet_name="summary", index=True)
        return f"saved file to {dir}"


class SynchroSim:
    """
    Class to handle simtraffic pdfs.

    Leverages Linux tool pdftotext to setup initial text file.

    """

    def __init__(self, filepath: Path) -> None:
        self.filepath = Path(filepath)
        self.dir = self.filepath.parent
        self.__create_txt()
        self.full_df = pd.read_csv(
            self.filepath.with_suffix(".txt"),
            sep="\s{5,100}",  # if dfs aren't coming in right, tune the number on the left, which represents the minimum spaces used as separator
            engine="python",
            names=range(15),
        )
        self.create_csv()

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
        los_totals = self.full_df[self.full_df[0].str.contains("Total", na=False)]
        los_totals = los_totals.drop([0], axis=1)
        headers = headers.dropna(axis="columns")
        headers = headers[headers[0] != "Arterial Level of Service"]
        los_totals = los_totals.dropna(axis="columns")
        arterial_los = pd.concat(
            [headers.reset_index(drop=True), los_totals.reset_index(drop=True)], axis=1
        )
        arterial_los.columns = cols
        arterial_los = arterial_los.drop(["dist (mi)", "arterial speed"], axis=1)
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

        if is_duplicate == True:
            intersection_index = intersection_index + 12
        else:
            pass

        intersection_df = self.full_df.iloc[
            intersection_index : (intersection_index + 6)
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
            intersection_df = intersection_df[col_list].agg(" ".join, axis=1).to_frame()
            intersection_df.columns = intersection_df.iloc[0]
            col_list = intersection_df.columns.tolist()
            intersection_df = intersection_df[col_list[0]].str.split(expand=True)

        else:
            intersection_df = intersection_df[col_list[0]].str.split(expand=True)

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
        df = self.find_arterial_los()
        dfs = self.qb_report()
        shape = df.shape[0]
        start_count = shape + 4

        with pd.ExcelWriter(self.dir / "sim_summary.xlsx") as writer:
            df.to_excel(writer, sheet_name="summary", index=False)
            df.to_excel(writer, sheet_name="arterial_los", index=False)
            for key in dfs:
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