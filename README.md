# Hydra Scraper

- Description: simple scraper for APIs with Hydra pagination
- Author: Jonatan Jalle Steller ([jonatan.steller@adwmainz.de](mailto:jonatan.steller@adwmainz.de))
- Requirements: `python3`, `python3-validators` (0.20.x), `python3-rdflib` (6.x.x)
- License: MIT
- Version: 0.8.0

This simple scraper for APIs that use Hydra pagination provides a toolset to pull data from resource lists as well as individual resources in RDF-compatible formats such as JSON-LD or Turtle. Command-line calls can be combined and adapted to build fully-fledged scraping mechanisms. The script was originally developed as an API testing tool for of the Corpus Vitrearum Germany (CVMA) at the Academy of Sciences and Literature Mainz.

## Setup

To use this script, simply clone this repository (e.g. via `git clone https://gitlab.rlp.net/adwmainz/digicademy/cvma/hydra-scraper.git` or the SSH equivalent). Open a terminal in the resulting folder to run the script as described below.

## Usage

This scraper is a command-line tool. Use `python go.py` to run the script in interactive mode. Alternatively, use the configuration options listed below to run the script without interaction.

- `-download '<string list>'`: comma-separated list of requests, possible values:
  - `lists`: all Hydra-paginated lists (requires `-url`)
  - `list_triples`: all RDF triples in a Hydra API (requires`-url`)
  - `beacon`: beacon file of all resources listed in a Hydra API (requires `-url`)
  - `resources`: all resources listed in a Hydra API or a beacon file (requires `-url` or `-file`)
  - `resource_triples`: all RDF triples in resources listed in a Hydra API or a beacon file (requires `-url` or `-file`)
- `-url '<url>'`: use this entry-point URL to scrape content
- `-file '<path to file>'`: use the URLs contained in this beacon file to scrape content
- `-folder '<name of folder>'`: download everything into this subfolder of `downloads` (defaults to timestamp)
- `-resource_url_replace '<string>'`: before downloading, replace this string in each resource URL (defaults to none)
- `-resource_url_replace_with '<string>'`: before downloading, replace the previous string in each resource URL with this one (defaults to none)
- `-resource_url_add '<string>'`: before downloading, add this string to the end of each resource URL (defaults to none)
- `-clean_resource_names '<string list>'`: comma-separated strings to remove from a resource URL to produce its file name (defaults to enumerated files)

## Examples

The commands listed below illustrate possible command-line arguments. They refer to specific projects, but should work with any Hydra-paginated API in an RDF-comptabile format.

**CVMA: all embedded metadata lists**

```
python go.py -download 'lists' -url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -folder 'cvma-embedded' -clean_resource_names 'https://corpusvitrearum.de/id/'
```

**CVMA: all JSON-LD lists and resources**

```
python go.py -download 'lists,beacon,resources' -url 'https://corpusvitrearum.de/id/about.json' -folder 'cvma-jsonld' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.json'
```

**CVMA: all RDF/XML lists and resources**

```
python go.py -download 'lists,beacon,resources' -url 'https://corpusvitrearum.de/id/about.rdf' -folder 'cvma-rdfxml' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.rdf'
```

**CVMA: all Turtle lists and resources**

```
python go.py -download 'lists,beacon,resources' -url 'https://corpusvitrearum.de/id/about.ttl' -folder 'cvma-turtle' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.ttl'
```

**CVMA: all CGIF lists and resources**

```
python go.py -download 'lists,beacon,resources' -url 'https://corpusvitrearum.de/id/about.cgif' -folder 'cvma-cgif' -resource_url_add '/about.cgif' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.cgif'
```

**CVMA: all LIDO resources**

```
python go.py -download 'beacon,resources' -url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -folder 'cvma-lido' -resource_url_add '/about.lido' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.lido'
```

**NFDI4Culture: all Turtle lists and resources**

```
python go.py -download 'lists,beacon,resources' -url 'https://nfdi4culture.de/resource.ttl' -folder 'n4c-turtle' -clean_resource_names 'https://nfdi4culture.de/resource/,.ttl'
```

## Development

## Roadmap

- Add URL composition feature of the Beacon standard
- Re-add the interactive mode
- Re-add a `-csv` option and remove leftover file

**Possible improvements**

- Package the script?
- Add option to get only CGIF triples?
- Add option to convert LIDO to CGIF triples (using XTriples, XSLT, or lxml)?
