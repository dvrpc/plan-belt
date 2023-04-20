"""
plan_belt.cli.py
---------------------
This module wraps various tools in planbelt into one convenient CLI.
-------------------------
"""

import click
from .conflation import conflator
from .synchro_summarizer import SynchroTxt, SynchroSim


@click.group()
def main():
    """
    planbelt CLI tools.
    """
    pass


@main.command()
@click.option(
    "--distance_threshold", default=5, help="distance threshold of conflation"
)
@click.option(
    "--coverage_threshold",
    default=75,
    help="acceptable percent coverage for conflation",
)
@click.option("--db", required=True, help="database name in postgres")
@click.option(
    "--db_config_name", required=True, help="bracketed name in pg-data-etl config file"
)
@click.option(
    "--input_table", required=True, help="input table name, what you want to conflate"
)
@click.option(
    "--output_table",
    required=True,
    help="desired output table name. sql conventions apply",
)
@click.option(
    "--unique_id_a", required=True, help="unique identifier field for input table"
)
@click.option(
    "--unique_id_b", required=True, help="unique identifier field for base table"
)
@click.option(
    "--base_layer", required=True, help="base layer, the layer you want to conflate to"
)
@click.option("--column", required=True, help="columns to include")
def conflation(
    distance_threshold,
    coverage_threshold,
    db,
    db_config_name,
    input_table,
    output_table,
    unique_id_a,
    unique_id_b,
    base_layer,
    column,
):
    """
    Conflates an input table to a base layer.
    """

    conflator(
        db,
        db_config_name,
        input_table,
        output_table,
        unique_id_a,
        unique_id_b,
        base_layer,
        column,
        distance_threshold,
        coverage_threshold,
    )


@click.group()
def main():
    """
    synchro and simtraffic summarizers.
    ingest outputs from synchro/simtraffic and bundle nicely.
    """
    pass


@main.command()
@click.argument("text_file_path")
def synchro(text_file_path):
    """
    Uses the SynchroTxt class to summarize text files from Synchro's output
    """

    SynchroTxt(text_file_path)


@main.command()
@click.argument("pdf_file_path")
def sim(pdf_file_path):
    """
    Uses the SynchroSim class to summarize pdf files from Simtraffic's output
    """

    SynchroSim(pdf_file_path)
