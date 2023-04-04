"""
plan_belt.cli.py
---------------------
This module wraps various tools in planbelt into one convenient CLI.
-------------------------
"""

import click
from .conflation import conflator


@click.group()
def main():
    """
    planbelt CLI tools.
    """
    pass


@main.command()
@click.option("--distance_threshold")
@click.option("--coverage_threshold")
@click.argument("db")
@click.argument("db_config_name")
@click.argument("input_table")
@click.argument("output_table")
@click.argument("unique_id")
@click.argument("base_layer")
def conflation(
    db,
    db_config_name,
    input_table,
    output_table,
    unique_id,
    base_layer,
    column,
    distance_threshold,
    coverage_threshold,
):
    """
    Conflates an input table to a base layer.
    """

    conflator(
        db,
        db_config_name,
        input_table,
        output_table,
        unique_id,
        base_layer,
        column,
        distance_threshold,
        coverage_threshold,
    )
