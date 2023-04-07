"""
tmc_summarizer.cli.py
---------------------
This module wraps SynchroSim and SynchroTxt classes
into a command-line-interface (CLI).
Usage: Summarize synchro and simtraffic outputs
-------------------------
    $ synchrosummarize my/data/
-------------------------
"""

import click
from .ingest import SynchroTxt, SynchroSim


@click.group()
def main():
    """
    synchro and simtraffic summarizers.
    ingest outputs from synchro/simtraffic and bundle nicely.
    """
    pass


@main.command()
@click.argument("text_file_path")
def synchrosum(text_file_path):
    """
    Uses the SynchroTxt class to summarize text files from Synchro's output
    """

    SynchroTxt(text_file_path)


@main.command()
@click.argument("pdf_file_path")
def synchrosim(pdf_file_path):
    """
    Uses the SynchroTxt class to summarize text files from Synchro's output
    """

    SynchroSim(pdf_file_path)
