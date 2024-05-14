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
# from classes.morph import HyMorphRdf, HyMorphXml, HyMorphTabular


# Organise input
organise = HyOrganise(argv[1:])
retrieve, morph = None

# Retrieve data
if (organise.start == 'rdf-feed' or organise.start == 'xml-feed') and (organise.markup == 'feed' or organise.markup == 'rdf' or organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei'):
    retrieve = HyRetrieveApi(organise.start, organise.markup, organise.location, organise.folder, organise.folder_files, organise.delay, organise.max_pagination, organise.dialect, organise.quiet)
    retrieve.download_feed(organise.delay, organise.dialect, organise.clean)
elif (organise.start == 'beacon-feed' or organise.start == 'dump-folder') and (organise.markup == 'rdf' or organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei'):
    retrieve = HyRetrieveFiles(organise.start, organise.location, organise.folder, organise.folder_files, organise.quiet)
    retrieve.download_feed(organise.delay, organise.dialect, organise.clean)
elif organise.start == 'dump-file' and organise.markup == 'csv':
    retrieve = HyRetrieveSingle(organise.location, organise.folder, organise.folder_files, organise.quiet)
else:
    raise ValueError('Hydra Scraper called with invalid combination of start and markup parameters.')

# Morph data
if (organise.markup == 'feed' or organise.markup == 'rdf') and set(organise.output).issubset(['beacon', 'files', 'triples', 'triples-nfdi', 'csv']):
    pass
    #if 'triples' in organise.output or 'triples-nfdi' in organise.output or 'csv' in organise.output:
        #morph = HyMorphRdf()
        #if 'triples' in organise.output:
            #morph.save_triples()
        #if 'triples-nfdi' in organise.output:
            #morph.save_triples_nfdi()
        #if 'csv' in organise.output:
            #morph.save_csv()
elif (organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei') and set(organise.output).issubset(['beacon', 'files', 'triples', 'triples-nfdi', 'csv']):
    pass
    #if 'triples' in organise.output or 'triples-nfdi' in organise.output or 'csv' in organise.output:
        #morph = HyMorphXml()
        #if 'triples' in organise.output:
            #morph.save_triples()
        #if 'triples-nfdi' in organise.output:
            #morph.save_triples_nfdi()
        #if 'csv' in organise.output:
            #morph.save_csv()
elif organise.markup == 'csv' and organise.output == ['triples-nfdi']:
    raise NotImplementedError('CSV functionality is not available in Hydra Scraper yet.')
    #morph = HyMorphTabular()
    #morph.save_triples_nfdi()
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






#     feed.morph('urls', command.resource_url_filter, command.resource_url_replace, command.resource_url_replace_with, command.resource_url_add)
#         feed.save(command.target_folder_path, 'beacon.txt', 'beacon')
#         feed_graph = HydraRetrieveGraph(report, feed.store)
#             feed_graph.save(command.target_folder_path, 'list_triples.ttl', 'ttl')
#             feed_graph.morph('cgif-to-nfdi')
#             feed_graph.save(command.target_folder_path, 'list_nfdi.ttl', 'nfdi')
#         resource = HydraRetrieveResource(report, 'local', None, command.source_folder, command.content_type, command.clean_resource_names, command.delay, resource_store_triples, resource_download)
#         resource = HydraRetrieveResource(report, 'remote', feed.feed, command.source_folder, command.content_type, command.clean_resource_names, command.delay, resource_store_triples, resource_download)
#         resource_graph = HydraRetrieveGraph(report, resource.store)
#             resource_graph.save(command.target_folder_path, 'resource_triples.ttl', 'triples')
#                 resource.morph('lido-to-nfdi', command.supplement_data_feed, command.supplement_data_catalog, command.supplement_data_catalog_publisher)
#             resource_graph.save(command.target_folder_path, 'resource_nfdi.ttl', 'nfdi')
#             resource_graph.morph('to-csv', command.table_data)
#             resource_graph.save(command.target_folder_path, 'resource_table.csv', 'csv')
