# Scra.py: A Simple Scraper for API Data

This script can grab API data, create beacon files and file dumps, and compile data tables to check data and API functionality from outside the source system. Scra.py was originally developed as part of the Corpus Vitrearum Medii Aevi Germany at the Academy of Sciences and Literature Mainz.

To run the script, clone this repo, open a terminal in the resulting folder, rename the `config-template.py` file to `config.py`, and adapt the variables to the API you seek to harvest. When the config file is ready, open a terminal in the script's folder and run `python scra.py`.

## Configuration

The script needs a least three variables as input: `formats`, `requests`, and `rest`. The first one should contain all API formats to call, along with all the starting URLs. For pagination, Scra.py assumes Hydra links (i.e. `hydra:first`, `hydra:last`, `hydra:previous`, and `hydra:next`). The script currently supports JSON-LD, RDF XML, and Turtle-based formats.

```python
formats = [
    [ 'json', 'https://corpusvitrearum.de/id/about.json' ],
    [ 'rdf', 'https://corpusvitrearum.de/id/about.rdf' ],
    [ 'ttl', 'https://corpusvitrearum.de/id/about.ttl' ],
    [ 'cgif', 'https://corpusvitrearum.de/id/about.cgif' ]
]
```

The `requests` list may contain up to three tasks that the script will perform for each format: `beacon and lists` puts together a beacon file for all resources and saves a dump of all listing files. `items` additionally downloads individual item pages as listed in the beacon file. And `table` additionally puts together a table of comma-separated values taken from the items pages.

```python
requests = [
    'beacon and lists',
    'items',
    'table'
]
```

The `rest` variable simply contains the number of seconds that the script waits before making another API call to not put too much of a burden on the server (and to avoid being blocked).

```python
rest = 0.1
```

If your request includes downloading a dump of item files, you can specify three further variables. `fileNameField` sets the name of the field that individual item files should use as a file name and `fileNameRemove` is a list of strings that should be removed from that field to build the file name. In addition, `excludeItems` is a list that may list resource URLs the script should avoid because, for example, they result in errors.

If you also request the script to compile a data table, you need to specify a list of the table's `header` content and another list of the `fields` that should be compiled. In `cleanUps` you can specify search-and-replace patterns to be applied to the fields that are saved into the table.

## Roadmap

- Finish generic version of the script
- Complete CVMA file dumps
- Test the script on another API
