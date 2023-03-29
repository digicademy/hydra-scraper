# Hydra Scraper

- Description: simple scraper for APIs with Hydra pagination
- Author: Jonatan Jalle Steller ([jonatan.steller@adwmainz.de](mailto:jonatan.steller@adwmainz.de))
- Requirements: `python3`, `python3-validators`, `python3-rdflib`
- License: MIT
- Version: 0.7

This simple scraper for APIs that use Hydra pagination was originally developed as part of the Corpus Vitrearum Germany (CVMA) at the Academy of Sciences and Literature Mainz. The idea was to provide a basic toolset that can pull data from resource lists as well as individual resource pages in RDF-compatible formats such as JSON-LD or Turtle. Command-line calls can be combined and adapted to build fully-fledged scraping mechanisms.

## Setup

To use this script, simply clone this repository (e.g. via `git clone https://gitlab.rlp.net/adwmainz/digicademy/cvma/hydra-scraper.git` or the SSH equivalent). Open a terminal in the resulting folder to run the script as described below.

## Usage

This scraper is a command-line tool. Use `python go.py` to run the script in interactive mode. Alternatively, add one of the main routines listed below along with any options you require to run the script without interaction.

**`hydra`: Download all resource lists containing Hydra pagination**

- `-url '<url>'`: Use this URL as a starting point (required)
- `-folder '<path to folder>'`: Download everything into this subfolder  of `downloads` (defaults to current timestamp)
- `-list '<path to file>'`: Also use this file name to compile a list of all individual resource URLs (defaults to `beacon.txt`)

**`beacon`: Download all individual resources based on a list**

- `-file '<path to file>'`: Use the list contained in this beacon file (required)
- `-folder '<path to folder>'`: Download all resources into this subfolder  of `downloads` (defaults to current timestamp)
- `-replace '<string>'`: Before downloading, replace this string in each entry in the beacon file (defaults to empty string)
- `-with '<string>'`: Replace the previous string with this one (defaults to empty string)
- `-clean_names '<string>'`: Comma-separated substrings to remove from the URL to get a resource's file name (empty default string leads to enumerated files instead)

## Example

The scraper was originally developed as part of the Corpus Vitrearum Germany (CVMA) at the Academy of Sciences and Liteture Mainz. To harvest all CVMA APIs at once, use the following set of commands:

```
python go.py hydra -url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -folder 'cvma' -list 'beacon.txt'
python go.py beacon -file 'cvma/beacon.txt' -folder 'cvma' -names '@id' -replace 'old' -with 'new'
```

ESCAPE VALUES AND REMOVE APOSTROPHES

## Development

## Roadmap

- Finish generic version of the script
- Compile all CVMA file dumps
- Add the interactive mode
- Test the script on another API
- Re-add option to compile CSV tables to use the script for API testing

## OLD CONFIG INSTRUCTIONS

The script needs a least three variables as input: `formats`, `requests`, and `rest`. The first one should contain all API formats to call, including the parser to use, a folder name for storage, and the entry-point URL. For pagination, Scra.py currently assumes that Hydra links (i.e. `hydra:first`, `hydra:last`, `hydra:previous`, and `hydra:next`) are present. The script supports JSON-LD, RDF XML, and Turtle-based files.

```python
formats = [
    [ 'json-ld', 'json', 'https://corpusvitrearum.de/id/about.json' ],
    [ 'rdf-xml', 'rdf', 'https://corpusvitrearum.de/id/about.rdf' ],
    [ 'turtle', 'ttl', 'https://corpusvitrearum.de/id/about.ttl' ],
    [ 'json-ld', 'cgif', 'https://corpusvitrearum.de/id/about.cgif' ]
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
