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

## Development

## Roadmap

- Filter triples instead? Use oxygraph!!!
- Finish debugging the script
- Try to compile all CVMA file dumps with it
- Find out what I meant when I wrote 'ESCAPE VALUES AND REMOVE APOSTROPHES'
- Add the interactive mode
- Test the script on another API
- Re-add routine that compiles CSV tables to use the script for API testing
- Consider adding a fourth routine to integrate, for example, an XTriples or XSLT conversion for LIDO data
