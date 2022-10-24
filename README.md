# Scraper for CVMA Web Data

This script can grab API data from the CVMA website. To run the script, clone this repo, open a terminal in the resulting folder and run `python scra.py`.

To specify which type of output you want, edit the `request` before running the script. You have the following options:

- `csv`: all metadata as comma-separated values (results stored in `cvma-metadata.csv`)
- `dump-jsonld`: dump of all JSON-LD files (results stored in `cvma-dump-jsonld`)
- `dump-rdf`: dump of all RDF files (results stored in `cvma-dump-rdf`)
- `dump-ttl`: dump of all TTL (Turtle) files (results stored in `cvma-dump-ttl`)
- `dump-cgif`: dump of all CGIF (Culture Graph Interchange Format) files (results stored in `cvma-dump-cgif`)
- `beacon-jsonld`: beacon file with all JSON-LD URLs (results stored in `cvma-beacon-jsonld.txt`)
- `beacon-rdf`: beacon file with all RDF URLs (results stored in `cvma-beacon-rdf.txt`)
- `beacon-ttl`: beacon file with all TTL (Turtle) URLs (results stored in `cvma-beacon-ttl.txt`)
- `beacon-cgif`: beacon file with all CGIF (Culture Graph Interchange Format) URLs (results stored in `cvma-beacon-cgif.txt`)