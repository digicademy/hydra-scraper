# Changelog

## 0.9.3

- Further LIDO fixes and enhancements
- Better error handling to make sure `KeyboardInterrupt` always works

## 0.9.2

- Retry fetching remote files in case of 5xx responses
- Use file size to calculate RDFLib/pyoxigraph switch
- Enhance LIDO conversion when image sizes are not indicated
- Fix issue in CTO conversion where list are used instead of literal

## 0.9.1

- Updated nfdicore/cto structure with altered `prepare` parameter

## 0.9.0

- Full rewrite with a modular architecture
- Any combination of Feed and FeedElement
- Support for RDF (schema.org), XML (CMIF, LIDO), Beacon, ZIP ingest
- Log but accept missing feed elements
- Less memory hoarding with large datasets
- Look-up routine for authority files
- Single template to generate `nfdicore/cto` triples
- Template adapted to current `nfdicore/cto` version
- Automatically create ARK IDs for `nfdicore/cto`
- Prep work for further serialisations such as DCAT
- New command-line interface and argument parsing
- A `-quiet` option prevents reporting intermiedate progress
- Provide optional OCI (Podman/Docker) container set-up
- Observe rules layed out in `robots.txt` files
- Recognise `http` and `https` namespaces in schema.org sources
- Provide log files for scraping runs
- Switch to `httpx`

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
