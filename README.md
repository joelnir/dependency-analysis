# dependency-analysis
Script for analysing dependencies from Javascript projects to npm packages.

## Requirements
* Python 3
* npm command line tool
* SQLite
* Plotly (for creating plots of the data)

## How to run
* Create a SQLite db called "database.db" in src/db.
* Use wanted function calls from main.py. In the folder src run Python and import main to gain access to these funcations. See main.py for documentation of these functions.
* A log of the script output is written to the file dependency.log.
* Functions for creating plots of the data can be found in plots.py.

## Data
Data from my runs of the script can be found in the data directory. For each run the complete log, the database file and a complete SQL export of the database are stored.
