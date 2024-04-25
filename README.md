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

- `-download <value> <value>`: list of downloads you require, possible values:
  - `lists`: all Hydra-paginated lists (requires `-source_url`)
  - `list_triples`: all RDF triples in a Hydra API (requires`-source_url`)
  - `list_nfdi`: nfdicore/cto triples from a CGIF-compatible Hydra API (requires`-source_url`)
  - `beacon`: Beacon file of all resources listed in an API (requires `-source_url`)
  - `resources`: all resources of an API or Beacon (requires `-source_url`/`_file`)
  - `resource_triples`: all RDF triples of resources (requires `-source_url`/`_file`/`_folder`)
  - `resource_nfdi`: Cnfdicore/cto triples from CGIF-compatible resources (requires `-source_url`/`_file`/`_folder`)
  - `resource_table`: CSV table of data in resources (requires `-source_url`/`_file`/`_folder`)
- `-source_url <url>`: entry-point URL to scrape content from (default: none)
- `-source_file <path to file>`: path to Beacon file containing URLs to scrape (default: none)
- `-source_folder <name of folder>`: path to folder containing files to scrape (default: none, requires `-content_type`)
- `-content_type <string>`: content type to request or use when scraping (default: none)
- `-target_folder <name of folder>`: download to this subfolder of the download folder (default: timestamp)
- `-resource_url_filter <string>`: string as a filter for resource lists (default: none)
- `-resource_url_replace <string>`: string to replace in resource lists (default: none)
- `-resource_url_replace_with <string>`: string to replace the previous one with (default: none)
- `-resource_url_add <string>`: addition to the end of each resource URL (default: none)
- `-clean_resource_names <string> <string>`: list of strings to remove from resource URLs to build their file name (default: enumeration)
- `-table_data <uri> <uri>`: list of property URIs to compile in a table (default: all)
- `-supplement_data_feed <url>`: URI of a data feed to bind LIDO files to (default: none)
- `-supplement_data_catalog <url>`: URI of a data catalog the data feed belongs to (default: none)
- `-supplement_data_catalog_publisher <url>`: URI of the publisher of the catalog (default: none)

## Examples

The commands listed below illustrate possible command-line arguments. They
refer to specific projects that use this script, but the commands should work
with any Hydra-paginated API in an RDF-comptabile format. Depending on your
operating system, you may need to use `python3` instead of `python`.

### NFDI4Culture

Grab all **portal data** as triples:

```
python go.py \
-download resource_triples \
-source_url https://nfdi4culture.de/resource.ttl \
-target_folder n4c-turtle
```

Get **NFDI-style data** from an API entry point:

```
python go.py \
-download list_nfdi \
-source_url https://corpusvitrearum.de/cvma-digital/bildarchiv.html \
-target_folder sample-nfdi
```

Get **NFDI-style data from a Beacon** file:

```
python go.py \
-download resource_nfdi \
-source_file downloads/sample-nfdi/beacon.txt \
-target_folder sample-nfdi
```

Get **NFDI-style data from a Beacon** file that lists LIDO files:

```
python go.py \
-download resource_nfdi \
-source_file downloads/sample-nfdi/beacon.txt \
-target_folder sample-nfdi \
-supplement_data_feed https://corpusvitrearum.de/cvma-digital/bildarchiv.html \
-supplement_data_catalog https://corpusvitrearum.de \
-supplement_data_catalog_publisher https://nfdi4culture.de/id/E1834
```

Get **NFDI-style data from a file dump**:

```
python go.py \
-download resource_nfdi \
-source_folder downloads/sample-nfdi \
-content_type application/ld+json \
-target_folder sample-nfdi
```

### Corpus Vitrearum Germany

All available **JSON-LD** data:

```
python go.py \
-download lists list_triples beacon resources resource_triples \
-source_url https://corpusvitrearum.de/id/about.json \
-target_folder cvma-jsonld \
-resource_url_filter https://corpusvitrearum.de/id/F \
-clean_resource_names https://corpusvitrearum.de/id/ /about.json
```

All available **RDF/XML** data:

```
python go.py \
-download lists list_triples beacon resources resource_triples \
-source_url https://corpusvitrearum.de/id/about.rdf \
-target_folder cvma-rdfxml \
-resource_url_filter https://corpusvitrearum.de/id/F \
-clean_resource_names https://corpusvitrearum.de/id/ /about.rdf
```

All available **Turtle** data:

```
python go.py \
-download lists list_triples beacon resources resource_triples \
-source_url https://corpusvitrearum.de/id/about.ttl \
-target_folder cvma-turtle \
-resource_url_filter https://corpusvitrearum.de/id/F \
-clean_resource_names https://corpusvitrearum.de/id/ /about.ttl
```

All available **CGIF (JSON-LD)** data:

```
python go.py \
-download lists list_triples list_nfdi beacon resources resource_triples resource_nfdi \
-source_url https://corpusvitrearum.de/id/about.cgif \
-target_folder cvma-nfdi \
-resource_url_filter https://corpusvitrearum.de/id/F \
-resource_url_add /about.cgif \
-clean_resource_names https://corpusvitrearum.de/id/ /about.cgif
```

All available **LIDO** data:

```
python go.py \
-download beacon resources \
-source_url https://corpusvitrearum.de/cvma-digital/bildarchiv.html \
-target_folder cvma-lido \
-resource_url_add /about.lido \
-clean_resource_names https://corpusvitrearum.de/id/ /about.lido
```

All available **embedded metadata**:

```
python go.py \
-download lists list_triples list_nfdi beacon resources resource_triples resource_nfdi \
-source_url https://corpusvitrearum.de/cvma-digital/bildarchiv.html \
-target_folder cvma-embedded \
-clean_resource_names https://corpusvitrearum.de/id/
```

**Table** of specific metadata:

```
python go.py \
-download resource_table \
-source_url https://corpusvitrearum.de/id/about.json \
-target_folder cvma-jsonld \
-resource_url_filter https://corpusvitrearum.de/id/F \
-table_data http://purl.org/dc/elements/1.1/Title http://iptc.org/std/Iptc4xmpExt/2008-02-29/ProvinceState http://iptc.org/std/Iptc4xmpExt/2008-02-29/City http://iptc.org/std/Iptc4xmpExt/2008-02-29/Sublocation http://iptc.org/std/Iptc4xmpExt/2008-02-29/LocationId http://ns.adobe.com/exif/1.0/GPSLatitude http://ns.adobe.com/exif/1.0/GPSLongitude https://lod.academy/cvma/ns/xmp/AgeDeterminationStart https://lod.academy/cvma/ns/xmp/AgeDeterminationEnd https://lod.academy/cvma/ns/xmp/IconclassNotation
```

Table of specific metadata **from an existing dump**:

```
python go.py \
-download resource_table \
-source_folder downloads/cvma-jsonld/resources \
-content_type application/ld+json \
-target_folder cvma-jsonld \
-table_data http://purl.org/dc/elements/1.1/Title http://iptc.org/std/Iptc4xmpExt/2008-02-29/ProvinceState http://iptc.org/std/Iptc4xmpExt/2008-02-29/City http://iptc.org/std/Iptc4xmpExt/2008-02-29/Sublocation http://iptc.org/std/Iptc4xmpExt/2008-02-29/LocationId http://ns.adobe.com/exif/1.0/GPSLatitude http://ns.adobe.com/exif/1.0/GPSLongitude https://lod.academy/cvma/ns/xmp/AgeDeterminationStart https://lod.academy/cvma/ns/xmp/AgeDeterminationEnd https://lod.academy/cvma/ns/xmp/IconclassNotation
```

## Contributing

The file `go.py` provides the basic logic of a scraping run. It instantiates three types of objects:

1. `HydraCommand` collects and cleans structured configuration info.
2. This info is passed to three helper objects: `HydraReport` provides status updates throughout or at the end of a run, `HydraOutput` handles all serialisations, and `HydraMorph` transforms ingested data to other ontologies.
3. When all four of these are set up, `HydraRetrieve` does the heavy lifting of fetching information from an API entry point or working through URLs provided in a Beacon list of individual resources, respectively.

If you change the code, please remember to document each function and walk other users through significant steps. This package is governed by the [Contributor Covenant](https://www.contributor-covenant.org/de/version/1/4/code-of-conduct/) code of conduct. Please keep this in mind in all interactions.

## Releasing

Before you make a new release, make sure the following files are up to date:

- `CHANGELOG.md`: version number and changes
- `CITATION.cff`: version number, authors, and release date
- `setup.py`: version number and authors

Use GitHub to make the release. Use semantic versioning.

## Roadmap

- Possibly switch LIDO support to `epoz/lidolator` and nfdicore/cto support to `epoz/nfdi4culture_python_package` after contributing features
- Possibly use the system's download folder to actually distribute the package
- CGIF-to-NFDI routine:
  - Investigate automatic retrieval of remote info to add triples
  - Investigate ways to dynamically generate schema.org class lists
