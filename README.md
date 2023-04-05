# plan-belt
A (WIP) collection of tools for planners. More to come.
modules included at the moment:
census: wrapper for census ACS api. 
conflation: conflate a line layer to a base layer
(in-progress) isochrones: generate travel time isochrones from a point or segment

## CLIs
### conflate: a command line interface (cli) for conflation. 
#### requirements:
* pg-data-etl and config file (included in environment yaml, but config file needs to be generated, see [documentation](https://github.com/aaronfraint/pg-data-etl))
* postgresql with postgis installed
* a postgresql db, postgis enabled, and an input and base table (what you want to conflate, and the network to conflate to)
* a conda / venv using the reqs in this repos environment.yml file. must be activated.

#### usage
for help and explanation of params:
```conflate --help``` 
example query
```conflate --distance_threshold=5 --coverage_threshold=75 --db=test --db_config_name=localhost --input_table=circuittrails --output_table=circuit  --unique_id_a=objectid --unique_id_b=objectid  --base_layer=rail --column=b.circuit```

db configuration is all done through pg-data-etl, where you save database connection params. 

if both datasets have duplicate column names, you might have trouble (other than the unique id fields, which can be the same in both as they're explicitly aliased under the hood).
consider only pulling necessary columns instead of all if you're having trouble, or rename duplicates in one of the tables. 

