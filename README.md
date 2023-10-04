# Hydra Scraper

**Comprehensive scraper for APIs with Hydra pagination as well as file dumps.**

This scraper provides a command-line toolset to pull data from various sources,
such as Hydra paginated APIs, beacon files, or local file dumps. The tool
differentiates between resource lists and individual resource files in
RDF-compatible formats such as JSON-LD or Turtle, but it can also handle, for
example, LIDO files. Command-line calls can be combined and adapted to build
fully-fledged scraping mechanisms, including the ability output a set of
triples. The script was originally developed as an API testing tool for of the
Corpus Vitrearum Germany (CVMA) at the Academy of Sciences and Literature
Mainz. It was later expanded to add functionality around the
[Culture Graph Interchange Format](https://docs.nfdi4culture.de/ta5-cgif-specification)
(CGIF).

## Licence

Written and maintained by [Jonatan Jalle Steller](mailto:jonatan.steller@adwmainz.de).

This code is covered by the [MIT](https://opensource.org/license/MIT/) licence.

## Installation

To use this script, make sure your system has a working `python` (3.x.x) as well as the
packages `validators` (0.20.x) and `rdflib` (6.x.x) installed. Then clone this
repository (e.g. via `git clone https://github.com/digicademy/hydra-scraper.git`
or the SSH equivalent). Open a terminal in the resulting folder to run the
script as described below.

## Usage

This scraper is a command-line tool. Use `python go.py` to run the script in
interactive mode. Alternatively, use the configuration options listed below to
run the script without interaction.

- `-download '<string list>'`: comma-separated list of requests, possible values:
  - `lists`: all Hydra-paginated lists (requires `-source_url`)
  - `list_triples`: all RDF triples in a Hydra API (requires`-source_url`)
  - `beacon`: beacon file of all resources listed in a Hydra API (requires `-source_url`)
  - `resources`: all resources listed in a Hydra API or a beacon file (requires `-source_url` or `-source_file`)
  - `resource_triples`: all RDF triples in resources listed in a Hydra API or a beacon file (requires `-source_url` or `-source_file`)
- `-source_url '<url>'`: use this entry-point URL to scrape content
- `-source_url_type '<string>'`: request this content type when scraping content (defaults to none)
- `-source_file '<path to file>'`: use the URLs contained in this beacon file to scrape content
- `-target_folder '<name of folder>'`: download everything into this subfolder of `downloads` (defaults to timestamp)
- `-resource_url_filter '<regular expression>'`: when listing resources, apply this string as a filter (defaults to none)
- `-resource_url_replace '<string>'`: when listing resources, replace this string in each URL (defaults to none)
- `-resource_url_replace_with '<string>'`: when listing resources, replace the previous string in each URL with this one (defaults to none)
- `-resource_url_add '<string>'`: when listing resources, add this string to the end of each URL (defaults to none)
- `-clean_resource_names '<string list>'`: comma-separated strings to remove from a resource URL to produce its file name (defaults to enumerated files)

## Examples

The commands listed below illustrate possible command-line arguments. They
refer to specific projects that use this script, but the commands should work
with any Hydra-paginated API in an RDF-comptabile format. Depending on your
operating system, you may need to use `python3` instead of `python`.

### NFDI4Culture

Grab all **portal data** as triples:

```
python go.py -download 'list_triples' -source_url 'https://nfdi4culture.de/resource.ttl' -target_folder 'n4c-turtle'
```

Get **CGIF data** from an API entry point:

```
python go.py -download 'list_triples' -source_url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -target_folder 'sample-cgif'
```

Get **CGIF data from a beacon** file:

```
python go.py -download 'resource_triples' -source_file 'downloads/sample-cgif/beacon.txt' -target_folder 'sample-cgif'
```

### Corpus Vitrearum Germany

All available **embedded metadata**:

```
python go.py -download 'lists,list_triples,beacon,resources,resource_triples' -source_url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -target_folder 'cvma-embedded' -clean_resource_names 'https://corpusvitrearum.de/id/'
```

All available **JSON-LD** data:

```
python go.py -download 'lists,list_triples,beacon,resources,resource_triples' -source_url 'https://corpusvitrearum.de/id/about.json' -target_folder 'cvma-jsonld' -resource_url_filter 'https://corpusvitrearum.de/id/F' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.json'
```

All available **RDF/XML** data:

```
python go.py -download 'lists,list_triples,beacon,resources,resource_triples' -source_url 'https://corpusvitrearum.de/id/about.rdf' -target_folder 'cvma-rdfxml' -resource_url_filter 'https://corpusvitrearum.de/id/F' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.rdf'
```

All available **Turtle** data:

```
python go.py -download 'lists,list_triples,beacon,resources,resource_triples' -source_url 'https://corpusvitrearum.de/id/about.ttl' -target_folder 'cvma-turtle' -resource_url_filter 'https://corpusvitrearum.de/id/F' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.ttl'
```

All available **CGIF (JSON-LD)** data:

```
python go.py -download 'lists,list_triples,beacon,resources,resource_triples' -source_url 'https://corpusvitrearum.de/id/about.cgif' -target_folder 'cvma-cgif' -resource_url_filter 'https://corpusvitrearum.de/id/F' -resource_url_add '/about.cgif' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.cgif'
```

All available **LIDO** data:

```
python go.py -download 'beacon,resources' -source_url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -target_folder 'cvma-lido' -resource_url_add '/about.lido' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.lido'
```

## Contributing

This package has three main areas:

1. The file `go.py` provides the main logic of a scraping run.
2. It relies on several `helpers` that provide basic functions such as cleaning up request arguments, saving files, printing status updates, or providing configuration options throughout the package.
3. The two classes `Hydra` and `Beacon` do the heavy lifting of paging through an API entry point or a (beacon) list of individual resources, respectively. In addition to a standard initialisation, both classes have a `populate()` function that retrieves and saves data. Additional functions may then carry out further tasks such as saving a beacon list or saving collected triples.

If you change the code, please remember to document each function and walk other users through significant steps. This package is governed by the [Contributor Covenant](https://www.contributor-covenant.org/de/version/1/4/code-of-conduct/) code of conduct. Please keep this in mind in all interactions.

## Roadmap

- Enable checking `schema:dateModified` when collating paged results
- Implement a JSON return (including dateModified, number of resources, errors)
- Add conversion routines, i.e. for LIDO to CGIF or for the RADAR version of DataCite/DataVerse to CGIF
- Allow harvesting from local files
- Allow filtering triples for CGIF, add any quality assurance that is needed
- Allow usage of OAI-PMH APIs to produce beacon lists
- Re-add the interactive mode
- Re-add a `-csv` option and remove leftover file
- Add URL composition feature of the Beacon standard
- Properly package the script and use the system's download folder
