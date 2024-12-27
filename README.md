# plan-belt
A (WIP) collection of tools for planners. More to come.
modules included at the moment:
* census: wrapper for census ACS api.
* conflation: conflate a line layer to a base layer
* synchrosum: scrapes synchro/simtraffic pdfs/txt files and produces summary.
* (in-progress) isochrones: generate travel time isochrones from a point or segment
* (in-progress) automap: a way to automate map creation with qgis.

## CLIs
### conflate: a command line interface (cli) for conflation.
#### requirements:
* pg-data-etl and config file (included in environment yaml, but config file needs to be generated, see [documentation](https://github.com/aaronfraint/pg-data-etl))
* postgresql with postgis installed
* a postgresql db, postgis enabled, and an input and base table (what you want to conflate, and the network to conflate to)
* an activated conda / venv environment. all needed reqs will be installed if you just use ```pip install git+https://github.com/dvrpc/plan-belt``` or add the same to your reqs.txt or environment.yml.

#### usage
for help and explanation of params:
```conflate --help```
example query
```conflate --distance_threshold=5 --coverage_threshold=75 --db=test --db_config_name=localhost --input_table=circuittrails --output_table=circuit  --unique_id_a=objectid --unique_id_b=objectid  --base_layer=rail --column=b.circuit```

db configuration is all done through pg-data-etl, where you save database connection params.

if both datasets have duplicate column names, you might have trouble (other than the unique id fields, which can be the same in both as they're explicitly aliased under the hood).
consider only pulling necessary columns instead of all if you're having trouble, or rename duplicates in one of the tables.

### synchrosum / synchrosim: cli for tools to process synchro outputs.
#### usage
synchro outputs should be saved as textfiles. they can be processed with:
```synchrosum '{filepath}.txt'```
there will be an output called 'synchro_summary.xlsx' that summarizes the file


simtraffic outputs don't have a text file, so a different method is used to scrape the pdf.
this is all abstracted into a similar command:
```synchrosim '{filepath}.pdf'```

this command produces a similar summary, called 'sim_summary.xlsx' in the same directory.

if you'd like to run both at once, and combine their results, simply call synchrosum, but add an additional argument for the simtraffic report.
```synchrosum '{filepath}.txt' '{filepath}.pdf'```

this calls both, but pipes the synchrosim output into a function which matches it and folds it into the synchrosum report.

todo:
* pull sim report into synchro output, probably need to fuzzymatch
* deal with secondary headings in unsignalized reports, check others
