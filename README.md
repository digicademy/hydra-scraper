# Scraper for CVMA Web Data

This script can grab API data from the CVMA website. To run the script, clone this repo, open a terminal in the resulting folder, check the `sourcesIteratorEnd` variable at the beginning of the script and run `python scra.py`.

## Configuration

To specify which type of output you want, edit the `requests` list before running the script. You have the following options:

- `table-csv`: table of all metadata as comma-separated values (results stored in `cvma-metadata.csv`)
- `listdump-json`: dump of all JSON-LD lists (results stored in `cvma-listdump-json`)
- `listdump-rdf`: dump of all RDF lists (results stored in `cvma-listdump-rdf`)
- `listdump-ttl`: dump of all TTL (Turtle) lists (results stored in `cvma-listdump-ttl`)
- `listdump-cgif`: dump of all CGIF lists (results stored in `cvma-listdump-cgif`)
- `dump-json`: dump of all JSON-LD files (results stored in `cvma-dump-json`)
- `dump-rdf`: dump of all RDF files (results stored in `cvma-dump-rdf`)
- `dump-ttl`: dump of all TTL (Turtle) files (results stored in `cvma-dump-ttl`)
- `dump-cgif`: dump of all CGIF files (results stored in `cvma-dump-cgif`)
- `beacon-json`: beacon file with all JSON-LD URLs (results stored in `cvma-beacon-json.txt`)
- `beacon-rdf`: beacon file with all RDF URLs (results stored in `cvma-beacon-rdf.txt`)
- `beacon-ttl`: beacon file with all TTL (Turtle) URLs (results stored in `cvma-beacon-ttl.txt`)
- `beacon-cgif`: beacon file with all CGIF URLs (results stored in `cvma-beacon-cgif.txt`)

If you need to remove entries that cause issues, add them to the `knownIssues` list, such as:

```python
knownIssues = [ 'https://corpusvitrearum.de/id/F5877' ]
```