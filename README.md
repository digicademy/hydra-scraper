[![DOI](https://zenodo.org/badge/700253411.svg)](https://zenodo.org/badge/latestdoi/700253411)

# Hydra Scraper

**Comprehensive scraper for Hydra-paginated APIs, Beacon files, and RDF file dumps**

This scraper provides a command-line toolset to pull data from various sources,
such as Hydra paginated APIs, Beacon files, or local file dumps. The tool
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

## Workflows

![Flowchart overview of possible workflows](assets/workflows.png)

## Installation

To use this script, make sure your system has a working `python` as well as
the packages `validators`, `rdflib`, and `lxml`. Then clone this repository (e.g. `git
clone https://github.com/digicademy/hydra-scraper.git` or the SSH equivalent).
Open a terminal in the resulting folder to run the script as described below.

## Usage

This scraper is a command-line tool. Use `python go.py` to run the script in
interactive mode. Alternatively, use the configuration options listed below to
run the script without interaction.

- `-download '<string list>'`: comma-separated list of what you need, possible values:
  - `lists`: all Hydra-paginated lists (requires `-source_url`)
  - `list_triples`: all RDF triples in a Hydra API (requires`-source_url`)
  - `list_cgif`: CGIF triples in a Hydra API (requires`-source_url`)
  - `beacon`: Beacon file of all resources listed in an API (requires `-source_url`)
  - `resources`: all resources of an API or Beacon (requires `-source_url`/`_file`)
  - `resource_triples`: all RDF triples of resources (requires `-source_url`/`_file`/`_folder`)
  - `resource_cgif`: CGIF triples of resources (requires `-source_url`/`_file`/`_folder`)
  - `resource_table`: CSV table of data in resources (requires `-source_url`/`_file`/`_folder`)
- `-source_url '<url>'`: use this entry-point URL to scrape content (default: none)
- `-source_file '<path to file>'`: use the URLs in this Beacon file to scrape content (default: none)
- `-source_folder '<name of folder>'`: use this folder (default: none, requires `-content_type`)
- `-content_type '<string>'`: request/use this content type when scraping content (default: none)
- `-target_folder '<name of folder>'`: download to this subfolder of `downloads` (default: timestamp)
- `-resource_url_filter '<string>'`: use this string as a filter for resource lists (default: none)
- `-resource_url_replace '<string>'`: replace this string in resource lists (default: none)
- `-resource_url_replace_with '<string>'`: replace the previous string with this one (default: none)
- `-resource_url_add '<string>'`: add this to the end of each resource URL (default: none)
- `-clean_resource_names '<string list>'`: build file names from resource URLs (default: enumeration)
- `-table_data '<string list>'`: comma-separated property URIs to compile in a table (default: all)
- `-supplement_data_feed '<url>'`: URI of a data feed to bind LIDO files to (default: none)
- `-supplement_data_catalog '<url>'`: URI of a data catalog the data feed belongs to (default: none)
- `-supplement_data_catalog_publisher '<url>'`: URI of the publisher of the catalog (default: none)

## Examples

The commands listed below illustrate possible command-line arguments. They
refer to specific projects that use this script, but the commands should work
with any Hydra-paginated API in an RDF-comptabile format. Depending on your
operating system, you may need to use `python3` instead of `python`.

### NFDI4Culture

Grab all **portal data** as triples:

```
python go.py -download 'resource_triples' -source_url 'https://nfdi4culture.de/resource.ttl' -target_folder 'n4c-turtle'
```

Get **CGIF data** from an API entry point:

```
python go.py -download 'list_cgif' -source_url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -target_folder 'sample-cgif'
```

Get **CGIF data from a Beacon** file:

```
python go.py -download 'resource_cgif' -source_file 'downloads/sample-cgif/beacon.txt' -target_folder 'sample-cgif'
```

Get **CGIF data from a Beacon** file that lists LIDO files:

```
python go.py -download 'resource_cgif' -source_file 'downloads/sample-cgif/beacon.txt' -target_folder 'sample-cgif' -supplement_data_feed 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -supplement_data_catalog 'https://corpusvitrearum.de' -supplement_data_catalog_publisher 'https://nfdi4culture.de/id/E1834'
```

Get **CGIF data from a file dump**:

```
python go.py -download 'resource_cgif' -source_folder 'downloads/sample-cgif' -content_type 'application/ld+json' -target_folder 'sample-cgif'
```

### Corpus Vitrearum Germany

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
python go.py -download 'lists,list_triples,list_cgif,beacon,resources,resource_triples,resource_cgif' -source_url 'https://corpusvitrearum.de/id/about.cgif' -target_folder 'cvma-cgif' -resource_url_filter 'https://corpusvitrearum.de/id/F' -resource_url_add '/about.cgif' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.cgif'
```

All available **LIDO** data:

```
python go.py -download 'beacon,resources' -source_url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -target_folder 'cvma-lido' -resource_url_add '/about.lido' -clean_resource_names 'https://corpusvitrearum.de/id/,/about.lido'
```

All available **embedded metadata**:

```
python go.py -download 'lists,list_triples,list_cgif,beacon,resources,resource_triples,resource_cgif' -source_url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -target_folder 'cvma-embedded' -clean_resource_names 'https://corpusvitrearum.de/id/'
```

**Table** of specific metadata:

```
python go.py -download 'resource_table' -source_url 'https://corpusvitrearum.de/id/about.json' -target_folder 'cvma-jsonld' -resource_url_filter 'https://corpusvitrearum.de/id/F' -table_data 'http://purl.org/dc/elements/1.1/Title,http://iptc.org/std/Iptc4xmpExt/2008-02-29/ProvinceState,http://iptc.org/std/Iptc4xmpExt/2008-02-29/City,http://iptc.org/std/Iptc4xmpExt/2008-02-29/Sublocation,http://iptc.org/std/Iptc4xmpExt/2008-02-29/LocationId,http://ns.adobe.com/exif/1.0/GPSLatitude,http://ns.adobe.com/exif/1.0/GPSLongitude,https://lod.academy/cvma/ns/xmp/AgeDeterminationStart,https://lod.academy/cvma/ns/xmp/AgeDeterminationEnd,https://lod.academy/cvma/ns/xmp/IconclassNotation'
```

Table of specific metadata **from an existing dump**:

```
python go.py -download 'resource_table' -source_folder 'downloads/cvma-jsonld/resources' -content_type 'application/ld+json' -target_folder 'cvma-jsonld' -table_data 'http://purl.org/dc/elements/1.1/Title,http://iptc.org/std/Iptc4xmpExt/2008-02-29/ProvinceState,http://iptc.org/std/Iptc4xmpExt/2008-02-29/City,http://iptc.org/std/Iptc4xmpExt/2008-02-29/Sublocation,http://iptc.org/std/Iptc4xmpExt/2008-02-29/LocationId,http://ns.adobe.com/exif/1.0/GPSLatitude,http://ns.adobe.com/exif/1.0/GPSLongitude,https://lod.academy/cvma/ns/xmp/AgeDeterminationStart,https://lod.academy/cvma/ns/xmp/AgeDeterminationEnd,https://lod.academy/cvma/ns/xmp/IconclassNotation'
```

## Contributing

This package has three main areas:

1. The file `go.py` provides the main logic of a scraping run.
2. It relies on several `helpers` that provide basic functions such as cleaning up request arguments, saving files, printing status updates, or providing configuration options throughout the package.
3. The two classes `Hydra` and `Beacon` do the heavy lifting of paging through an API entry point or a (Beacon) list of individual resources, respectively. In addition to a standard initialisation, both classes have a `populate()` function that retrieves and saves data. Additional functions may then carry out further tasks such as saving a Beacon list or saving collected triples.

If you change the code, please remember to document each function and walk other users through significant steps. This package is governed by the [Contributor Covenant](https://www.contributor-covenant.org/de/version/1/4/code-of-conduct/) code of conduct. Please keep this in mind in all interactions.

## Releasing

Before you make a new release, make sure the following files are up to date:

- CHANGELOG.md: version number and changes
- CITATION.cff: version number, authors, and release date

Use GitHub to make the release. Use semantic versioning once the scraper has reached 1.0.0.

## Roadmap

- Find way to add remaining LIDO triples
- Enable checking `schema:dateModified` when collating paged results
- Implement a JSON return (including dateModified, number of resources, errors)
- Add conversion routines, i.e. for the RADAR version of DataCite/DataVerse to CGIF
- Add filter for CGIF triples which aligns those produced by lists and by resources and could host further quality assurance
- Allow usage of OAI-PMH APIs to produce Beacon lists
- Re-add the interactive mode
- Properly package the script and use the system's download folder, and possibly enable pushing to a Git repo?
