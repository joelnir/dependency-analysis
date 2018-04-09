# dependency-analysis
Script for analysing dependencies from Javascript projects to npm packages.

## Requirements
* Python 3
* npm command line tool
* SQLite (if you want to inspect the database)

## How to run
All needed function calls can be found in main.py. In the folder src run Python and import main to gain access to these funcations. See main.py for documentation of these functions.

A log of the script output is written to the file dependency.log.

## Data
Data from my runs of the script can be found in the data directory. For each run the complete log, the database file and a complete SQL export of the database are stored.
