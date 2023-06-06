# Hydra Scraper

- Description: simple scraper for APIs with Hydra pagination
- Author: Jonatan Jalle Steller ([jonatan.steller@adwmainz.de](mailto:jonatan.steller@adwmainz.de))
- Requirements: `python3`, `python3-validators` (0.20.x), `python3-rdflib` (6.x.x)
- License: MIT
- Version: 0.7.5

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
- `-add '<string>'`: Add this string to the end of each URL to download (defaults to empty string)
- `-clean_names '<string>'`: Comma-separated substrings to remove from the URL to get a resource's file name (empty default string leads to enumerated files instead)

## Examples

The scraper was originally developed as part of the Corpus Vitrearum Germany (CVMA) at the Academy of Sciences and Liteture Mainz. The commands listed below are supposed to illustrate how to harvest all CVMA APIs.

**CVMA: all embedded metadata**

```
python go.py hydra -url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -folder 'cvma-embedded' -list 'beacon.txt'
python go.py beacon -file 'downloads/cvma-embedded/beacon.txt' -folder 'cvma-embedded' -clean_names 'https://corpusvitrearum.de/id/'
```

**CVMA: all JSON-LD files**

```
python go.py hydra -url 'https://corpusvitrearum.de/id/about.json' -folder 'cvma-jsonld' -list 'beacon.txt'
python go.py beacon -file 'downloads/cvma-jsonld/beacon.txt' -folder 'cvma-jsonld' -clean_names 'https://corpusvitrearum.de/id/,/about.json'
```

**CVMA: all RDF/XML files**

```
python go.py hydra -url 'https://corpusvitrearum.de/id/about.rdf' -folder 'cvma-rdfxml' -list 'beacon.txt'
python go.py beacon -file 'downloads/cvma-rdfxml/beacon.txt' -folder 'cvma-rdfxml' -clean_names 'https://corpusvitrearum.de/id/,/about.rdf'
```

**CVMA: all Turtle files**

```
python go.py hydra -url 'https://corpusvitrearum.de/id/about.ttl' -folder 'cvma-turtle' -list 'beacon.txt'
python go.py beacon -file 'downloads/cvma-turtle/beacon.txt' -folder 'cvma-turtle' -clean_names 'https://corpusvitrearum.de/id/,/about.ttl'
```

**CVMA: all CGIF files**

```
python go.py hydra -url 'https://corpusvitrearum.de/id/about.cgif' -folder 'cvma-cgif' -list 'beacon.txt'
python go.py beacon -file 'downloads/cvma-cgif/beacon.txt' -folder 'cvma-cgif' -add '/about.cgif' -clean_names 'https://corpusvitrearum.de/id/,/about.cgif'
```

**CVMA: all LIDO files**

```
python go.py hydra -url 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html' -folder 'cvma-lido' -list 'beacon.txt'
rm -r downloads/cvma-lido/lists
python go.py beacon -file 'downloads/cvma-lido/beacon.txt' -folder 'cvma-lido' -add '/about.lido' -clean_names 'https://corpusvitrearum.de/id/,/about.lido'
```

**NFDI4Culture: all Turtle files**

```
python go.py hydra -url 'https://nfdi4culture.de/resource.ttl' -folder 'n4c-turtle' -list 'beacon.txt'
python go.py beacon -file 'downloads/n4c-turtle/beacon.txt' -folder 'n4c-turtle' -clean_names 'https://nfdi4culture.de/resource/,.ttl'
```

## Development

## Roadmap

- Allow combined hydra/beacon requests
- Allow downloading triples instead of individual files (with CGIF filters?)
- Check features of the Beacon standard that need to be supported
- Add the interactive mode
- Add the help routine
- Remove leftovers file

**Possible improvements**

- Implement request shortcuts?
- Re-add routine that compiles CSV tables to use the script for data testing?
- Consider adding a fourth routine to integrate, for example, an XTriples or XSLT conversion for LIDO data to CGIF?
