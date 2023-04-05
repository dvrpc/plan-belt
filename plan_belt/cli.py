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
@click.option('--distance_threshold', default=5, help='distance threshold of conflation')
@click.option('--coverage_threshold', default=75, help='acceptable percent coverage for conflation')
@click.option('--db', help='db name in postgres')
@click.option('--db_config_name', help='bracketed name in pg-data-etl config file')
@click.option('--input_table', help='input table name')
@click.option('--output_table', help='desired output table name. sql conventions apply')
@click.option('--unique_id_a', help='unique identifier field for input table')
@click.option('--unique_id_b', help='unique identifier field for base table')
@click.option('--base_layer', help='base layer to conflate to')
@click.option('--column', help='columns to include')
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
