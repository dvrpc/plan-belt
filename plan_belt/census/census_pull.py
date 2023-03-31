from dotenv import load_dotenv
import pandas as pd
import requests
import os

load_dotenv()

apikey = os.getenv("api_key")


class acsTable:
    """A simple class to grab census data from whatever vintage you're interested in from the ACS.

    Requires an API, here stored in a .env file on your machine.

    https://api.census.gov/data/2021/acs/acs5/variables.html holds 2021 ACS 5 year variables for tablenames, find others by replacing the year.

    """

    def __init__(
        self, year, census, subcensus, table, state, county, apikey, tract="*", table_type="detailed"
    ):
        """
        Parameters
        ----------
        year : str
            Census year you're interested in
        census : str
            acs, typically
        subcensus: str
            1 year? 3 year? 5 year? example: acs5 = Five year ACS
        table : str
            The table you're interested in from the variables page on Census.gov
        state : str
            FIPS code for the state you're interested in.
        county : str
            County code for the county you're interested in.
            TODO: test for multiple states/counties in query
        apikey : str
        Register for one on census.gov, store it in a .env file in your project directory.
        tract : str
            the tract you're interested in. * = all
        table_type : str
            subject table or detailed table

        TODO:
        implement blockgroups to url
        """
        self.year: str = year + "/"
        self.subcensus: str = subcensus  
        self.census: str = census + "/"
        self.table: str = table 
        self.state: str = state 
        self.county: str = county 
        self.apikey: str = apikey 
        self.tract: str = tract 
        self.table_type: str = table_type + "/"
        self.api_base = "https://api.census.gov/data/"
        self._validate_table_type()
        self.api_url = (
            self.api_base
            + self.year
            + self.census
            + self.subcensus
            + self.table_type
            + "?get=NAME,"
            + self.table
            + "&for=tract:"
            + self.tract
            + "&in=state:"
            + self.state
            + "&in=county:"
            + self.county
            + "&key="
            + self.apikey
        )
        self.r = requests.get(self.api_url)
        self.make_dataframe()

    def _validate_table_type(self):
        if self.table_type.lower() == "detailed/":
            self.table_type = ""
        elif self.table_type.lower() == "subject/":
            self.table_type = "/subject"
        else:
            raise ValueError("ERROR: table_type must be subject or detailed")

    def make_dataframe(self):
        self.df = pd.DataFrame.from_dict(self.r.json())
        self.df.columns = self.df.iloc[0]
        self.df = self.df[1:]
        return self.df


if __name__ == '__main__':

    testClass = acsTable(
        "2021", "acs", "acs5", "B04005_049E", "34", "021", apikey, "*", "detailed"
    )
    subJect = acsTable("2021", "acs", "acs5", "S0101_C01_001E", "34", "021", apikey, table_type="subject")
    print(testClass.api_url)
    print(subJect.api_url)
