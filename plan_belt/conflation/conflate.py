from pg_data_etl import Database
from dotenv import load_dotenv

load_dotenv()

db = Database.from_config("mercer", "omad")
gis_db = Database.from_config("gis", "gis")


def conflation_schema():
    query = """
        create schema if not exists tmp;
        create schema if not exists conflated;
        create schema if not exists rejoined;"""
    db.execute(query)


def convert_to_point(input_table: str, output_table: str, unique_id: str):
    # converts line layer to be conflated to point using st_interpolate point
    query = f"""drop table if exists tmp.{output_table}_pt;
                create table tmp.{output_table}_pt as
                select
                    n,
                    {unique_id} as id,
                    ST_LineInterpolatePoint(
                        st_linemerge((st_dump(geom)).geom),
                    least(n *(4 / st_length(geom)), 1.0)
                    )::GEOMETRY(POINT,
                    26918) as geom
                from
                    {input_table}
                cross join Generate_Series(0, ceil(st_length(geom) / 4)::INT) as n
                where
                    st_length(geom) > 0;"""
    db.execute(query)


def point_to_base_layer(baselayer: str, output_table: str, distance_threshold: int):
    # selects points that are within threshold distance from base layer (i.e. layer you're conflating to)
    query = f"""drop table if exists tmp.{output_table}_point_to_base;
                create table tmp.{output_table}_point_to_base as
                select
                    a.id as {output_table}_id,
                    b.globalid,
                    a.geom
                from
                    tmp.{output_table}_pt a,
                    public.{baselayer} b
                where
                    st_dwithin(a.geom,
                    b.geom,
                    {distance_threshold})
                order by
                    a.n,
                    st_distance(a.geom,
                    b.geom);
                """
    db.execute(query)


def point_count(output_table: str, distance_threshold: int):
    # counts the number of records that are within distance threshold of base layer
    query = f"""drop table if exists tmp.{output_table}_point{distance_threshold}_count;
            create table tmp.{output_table}_point{distance_threshold}_count as
            select
                globalid,
                count(*) as pnt_{distance_threshold}_count,
                {output_table}_id
            from
                tmp.{output_table}_point_to_base
            group by
                globalid,
                {output_table}_id;
            """
    db.execute(query)


def total_point_count(output_table: str):
    # counts total points in line layer
    query = f"""drop table if exists tmp.{output_table}_total_point_count;
                create table tmp.{output_table}_total_point_count as
                select
                    globalid,
                    count(*) as {output_table}_total_point_count
                from
                    tmp.{output_table}_point_to_base
                group by
                    globalid;
                            """
    db.execute(query)


def most_occuring_in_threshold(output_table: str, distance_threshold: int):
    # finds percent match of points within distance threshold vs total points
    query = f"""drop table if exists tmp.{output_table}point{distance_threshold}_most_occurring;
                create table tmp.{output_table}point{distance_threshold}_most_occurring as
                select
                    distinct on
                    (a.globalid) a.globalid,
                    a.pnt_{distance_threshold}_count,
                    b.{output_table}_total_point_count,
                    round(
                        (
                            (
                                a.pnt_{distance_threshold}_count::numeric / b.{output_table}_total_point_count::numeric
                            ) * 100
                        ),
                        0
                    ) as pnt_{distance_threshold}_pct_match,
                    a.{output_table}_id
                from
                    tmp.{output_table}_point{distance_threshold}_count a
                left join tmp.{output_table}_total_point_count b on
                    (a.globalid = b.globalid)
                order by
                    a.globalid,
                    a.pnt_{distance_threshold}_count desc;
                            """
    db.execute(query)


def conflate_to_base(output_table: str, distance_threshold: int, baselayer: str):
    # finds percent match of points within distance threshold vs total points
    query = f"""drop table if exists conflated.{output_table}_to_{baselayer};
                create table conflated.{output_table}_to_{baselayer} as
                select
                    distinct on
                    (a.globalid) a.*,
                    b.{output_table}_id,
                    b.pnt_{distance_threshold}_count,
                    b.{output_table}_total_point_count,
                    b.pnt_{distance_threshold}_pct_match,
                    round(
                        (st_length(a.geom) / 4)::numeric,
                        0
                    ) as total_possible_pnts,
                    round(
                        (
                            (
                                b.{output_table}_total_point_count / (st_length(a.geom) / 4)
                            ) * 100
                        )::numeric,
                        0
                    ) as possible_coverage
                from
                    {baselayer} a
                left join tmp.{output_table}point{distance_threshold}_most_occurring b on
                    a.globalid = b.globalid;
                            """
    db.execute(query)


def conflator(
    """
    Conflates an input table to a base layer.

    Generates both a conflated and rejoined schema. Rejoined contains all data, 
    Conflated is raw geoms conflated, rejoined connects to rest of data.

    Parameters
    --------------
    input_table : str
        the table you'd like to conflate to a base network
    output_table: str
        the name of your desired output. sql tablename conventions apply
    unique_id: str 
        a unique identifier in your input table
    base_layer: str
        the network you're conflating to (needs to exist in the db or in a FDW)
    column: str
        the columns you'd like to include with conflation. default is all.
    distance_threshold: int
        how far to venture when searching for nearby layers to conflate. defaults
        are in meters.
    coverage_threshold: int
        the percentage of coverage needed to perform the conflation.
        coverage is based on distance_threshold buffer, not on
        actual line overlap.  

    """
    input_table: str,
    output_table: str,
    unique_id: str,
    base_layer: str,
    column: str = 'b.*',
    distance_threshold: int = 5,
    coverage_threshold: int = 70,
):
    conflation_schema()
    convert_to_point(input_table, output_table, unique_id)
    point_to_base_layer(base_layer, output_table, distance_threshold)
    point_count(output_table, distance_threshold)
    total_point_count(output_table)
    most_occuring_in_threshold(output_table, distance_threshold)
    conflate_to_base(output_table, distance_threshold, base_layer)

    # necessary to rejoin the conflated geometry back to the id of the original geometry. might be a better way to do this
    query = f"""
        drop table if exists rejoined.{output_table};
        create table rejoined.{output_table} as
            select
                a.*,
                {column}
            from conflated.{output_table}_to_{base_layer} a
            inner join public.{input_table} b
            on a.{output_table}_id = b.uid
            where a.possible_coverage > {coverage_threshold}"""
    print(f"conflating {input_table} to {base_layer}")
    db.execute(query)

if __name__ == "__main__":
    # nj_transit routes, possible coverage >=80
    conflator("nj_transit_routes", "njt", "uid", "nj_centerline", "b.line", 8, 80)

