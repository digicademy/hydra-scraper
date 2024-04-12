# Changelog

## 0.8.2

- Add code of conduct
- Use speaking command-line arguments
- Add option to filter resource downloads by string
- Add optional content negotiation
- Test everything against the CVMA API

## 0.8.3

- Rename `-source_url_type` to `-content_type`
- Add option to harvest from file dump
- Bring back option to compile CSV table from scraped data
- Implement URL composition feature for Beacon files

## 0.8.4

- Provide infrastructure for CGIF filters
- Add ability to read triples from LIDO files

## 0.9.0

- Refactor code to use a single main script and five classes
  - HydraCommand
  - HydraOutput
  - HydraReport
  - HydraMunch
  - HydraFetch
- Switch custom argument processing and progress reporting to Python libraries
- Add routine to process CGIF to nfdicore and cto ontologies
