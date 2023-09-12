# conflation

## how to use
the conflation module has a CLI, which is useful for a quick conflation, but can also be imported and used normally.

### steps
1. create a new virtual environment or conda environment and activate it. if you're using conda, make sure you explicilty install pip into your environment
2. install the library via pip. ```pip install git+https://github.com/dvrpc/plan-belt```, or add it to your environment.txt like  ```git+https://github.com/dvrpc/plan-belt```
3. you should now have access to the conflate tool. check on the commmand line by typing ```conflate --help```
4. you can use the cli tool, or you can import it. see demo script below.

### terminal use
#### requirements:
* pg-data-etl and config file (included in environment yaml, but config file needs to be generated, see [documentation](https://github.com/aaronfraint/pg-data-etl))
* postgresql with postgis installed
* a postgresql db, postgis enabled, and an input and base table (what you want to conflate, and the network to conflate to)
* a conda / venv using the reqs in this repos environment.yml file. must be activated.

#### usage
for help and explanation of params:
```conflate --help```
example command
```conflate --distance_threshold=5 --coverage_threshold=75 --db=test --db_config_name=localhost --input_table=circuittrails --output_table=circuit  --unique_id_a=objectid --unique_id_b=objectid  --base_layer=rail --column=b.circuit```

db configuration is all done through pg-data-etl, where you save database connection params.

if both datasets have duplicate column names, you might have trouble (other than the unique id fields, which can be the same in both as they're explicitly aliased under the hood).
consider only pulling necessary columns instead of all if you're having trouble, or rename duplicates in one of the tables.

### module import
you can also just import the module if needed and use it, though it doesn't return anything useable, just does the work to conflate everything in the db.


```
from plan_belt.conflation import conflator

conflator(
    "mercer",  # name of your database
    "omad",  # name of your config file in pg_etl config file
    "nj_transit_routes",  # name of input table (what you want to conflate)
    "nj_transit",  # what you want the output table to be named
    "index",  # uid of conflate layer
    "index",  # uid of base layer
    "nj_centerline",  # base layer that you want to conflate to
    "b.line",  # columns from conflate layer you want to include. if multiple, just use b. for each. like 'b.line, b.geom'
    5,  # distance threshold in meters. 5 is a good starting point but might need to tune
    70,  # overlap percentage. leave at 70, go smaller if many false negatives, bigger if many false postives
)

print("conflated!")
```
