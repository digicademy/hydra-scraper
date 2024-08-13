# Main scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from sys import argv

# Import script modules
from classes.organise import HyOrganise
from classes.retrieve import HyRetrieveApi, HyRetrieveFiles, HyRetrieveSingle
from classes.morph import HyMorphRdf, HyMorphXml, HyMorphTabular


# Organise input
organise = HyOrganise(argv[1:])
retrieve, morph = None

# Retrieve data: APIs
if (organise.start == 'rdf-feed' or organise.start == 'xml-feed') and (organise.markup == 'feed' or organise.markup == 'rdf' or organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei'):
    retrieve = HyRetrieveApi(organise.start, organise.markup, organise.location, organise.folder, organise.folder_files, organise.delay, organise.max_pagination, organise.dialect, organise.quiet)
    retrieve.download_feed(organise.delay, organise.dialect, organise.clean)

# Retrieve data: files
elif (organise.start == 'beacon-feed' or organise.start == 'dump-folder') and (organise.markup == 'rdf' or organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei'):
    retrieve = HyRetrieveFiles(organise.start, organise.location, organise.folder, organise.folder_files, organise.quiet)
    retrieve.download_feed(organise.delay, organise.dialect, organise.clean)

# Retrieve data: single file
elif organise.start == 'dump-file' and organise.markup == 'csv':
    retrieve = HyRetrieveSingle(organise.location, organise.folder, organise.folder_files, organise.quiet)
else:
    raise ValueError('Hydra Scraper called with invalid combination of start and markup parameters.')

# Morph data: from RDF data
if (organise.markup == 'feed' or organise.markup == 'rdf') and set(organise.output).issubset(['beacon', 'files', 'triples', 'triples-nfdi', 'csv']):
    pass
    if 'triples' in organise.output or 'triples-nfdi' in organise.output or 'csv' in organise.output:
        morph = HyMorphRdf(retrieve.local, organise.folder, organise.folder_files, organise.dialect, organise.prepare, organise.quiet)
        if 'triples' in organise.output:
            morph.save_triples()
        if 'triples-nfdi' in organise.output:
            morph.save_triples_nfdi(organise.add_feed, organise.add_catalog, organise.add_publisher, organise.prepare)
        if 'csv' in organise.output:
            morph.save_csv(organise.table)

# Morph data: from XML data
elif (organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei') and set(organise.output).issubset(['beacon', 'files', 'triples', 'triples-nfdi', 'csv']):
    if 'triples' in organise.output or 'triples-nfdi' in organise.output or 'csv' in organise.output:
        morph = HyMorphXml(retrieve.local, organise.markup, organise.folder, organise.folder_files, organise.dialect, organise.add_feed, organise.add_catalog, organise.add_publisher, organise.prepare, organise.quiet)
        if 'triples' in organise.output:
            morph.save_triples()
        if 'triples-nfdi' in organise.output:
            morph.save_triples_nfdi(organise.add_feed, organise.add_catalog, organise.add_publisher, organise.prepare, organise.location)
        if 'csv' in organise.output:
            morph.save_csv(organise.table)

# Morph data: from tabular data
elif organise.markup == 'csv' and organise.output == ['triples-nfdi']:
    morph = HyMorphTabular(retrieve.local, organise.folder, organise.folder_files, organise.quiet)
    morph.save_triples_nfdi(organise.add_feed, organise.add_catalog, organise.add_publisher, organise.prepare)
else:
    raise ValueError('Hydra Scraper called with invalid combination of markup and output parameters.')

# Special treatment for 'beacon' and 'files' output
if retrieve and 'beacon' in organise.output:
    retrieve.save_beacon()
if retrieve and organise.start != 'dump-folder' and organise.start != 'dump-file' and 'files' not in organise.output:
    retrieve.remove_downloads()

# Report results
if retrieve:
    organise.status += retrieve.status
if morph:
    organise.status += morph.status
organise.report()
