# Changelog

## 0.9.0

- Refactor and rewrite the scraper using classes and class inheritance to avoid intransparent helper libraries
- Central library to produce triples for the nfdicore/cto ontology
- Switch CGIF and LIDO routines to produce nfdicore/cto
- Reshuffle command-line interface and argument parsing to improve extensibility
- Add a `-quiet` option to stop reporting intermiedate progress
- Set up further ingest formats

## 0.8.4

- Provide infrastructure for CGIF filters
- Add ability to read triples from LIDO files

## 0.8.3

- Rename `-source_url_type` to `-content_type`
- Add option to harvest from file dump
- Bring back option to compile CSV table from scraped data
- Implement URL composition feature for Beacon files

## 0.8.2

- Add code of conduct
- Use speaking command-line arguments
- Add option to filter resource downloads by string
- Add optional content negotiation
- Test everything against the CVMA API
