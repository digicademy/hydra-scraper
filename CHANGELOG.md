# Changelog

## 0.9.0

- Refactor code to use a single main script and several classes instead of a helper library
- Add routine to process CGIF to the nfdicore/cto ontology
- Switch LIDO conversion from targeting CGIF to nfdicore/cto
- Simplify command-line interface and argument parsing
- Add `-quiet` option to not report intermiedate progress

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
