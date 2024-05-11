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
# from classes.retrieve import HyRetrieveApi, HyRetrieveFiles, HyRetrieveSingle
# from classes.morph import HyMorphRdf, HyMorphXml, HyMorphTabular


# Organise
organise = HyOrganise(argv)

# Retrieve
if organise.start == 'rdf-feed' and (organise.markup == 'rdf-feed' or organise.markup == 'rdf-members' or organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei' or organise.markup == 'csv'):
    pass # HyRetrieveApi
elif (organise.start == 'beacon-feed' or organise.start == 'dump-folder' or organise.start == 'xml-feed') and (organise.markup == 'rdf-members' or organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei'):
    pass # HyRetrieveFiles
elif organise.start == 'dump-file' and organise.markup == 'csv':
    pass # HyRetrieveSingle
else:
    raise ValueError('Hydra Scraper called with invalid combination of start and markup parameters.')

# Morph
if (organise.markup == 'rdf-feed' or organise.markup == 'rdf-members') and set(organise.output).issubset(['beacon', 'files', 'triples', 'triples-nfdi', 'csv']):
    pass # HyMorphRdf
elif (organise.markup == 'lido' or organise.markup == 'tei' or organise.markup == 'mei') and set(organise.output).issubset(['files', 'triples-nfdi', 'csv']):
    pass # HyMorphXml
elif organise.markup == 'csv' and set(organise.output).issubset(['triples-nfdi']):
    pass # HyMorphTabular
else:
    raise ValueError('Hydra Scraper called with invalid combination of markup and output parameters.')

# Report
organise.report()





# # Beacons or endpoints
# if command.source_file != None or command.source_url != None or 'lists' in command.download or 'list_triples' in command.download or 'list_nfdi' in command.download or 'beacon' in command.download:

#     # Setting to download list files
#     feed_download = False
#     if 'lists' in command.download:
#         feed_download = True

#     # Retrieve lists and alter resource URLs
#     feed = HydraRetrieveFeed(report, command.source_file, command.source_url, command.content_type, command.max_number_paginated_lists, command.delay, feed_download, command.target_folder_path)
#     feed.morph('urls', command.resource_url_filter, command.resource_url_replace, command.resource_url_replace_with, command.resource_url_add)

#     # Save Beacon file
#     if 'beacon' in command.download:
#         feed.save(command.target_folder_path, 'beacon.txt', 'beacon')

#     # Update status from feed
#     report.status += feed.report.status

#     # Set up feed graph
#     if 'list_triples' in command.download or 'list_nfdi' in command.download:
#         feed_graph = HydraRetrieveGraph(report, feed.store)

#         # Compile triples
#         if 'list_triples' in command.download:
#             feed_graph.save(command.target_folder_path, 'list_triples.ttl', 'ttl')

#         # Compile NFDI-style triples
#         if 'list_nfdi' in command.download:
#             feed_graph.morph('cgif-to-nfdi')
#             feed_graph.save(command.target_folder_path, 'list_nfdi.ttl', 'nfdi')

#         # Update status from feed graph
#         report.status += feed_graph.report.status

# # Individual resource files
# if command.source_folder != None or 'resources' in command.download or 'resource_triples' in command.download or 'resource_nfdi' in command.download or 'resource_table' in command.download:

#     # Setting to download resource files and store triples
#     resource_download = False
#     if 'resources' in command.download:
#         resource_download = True
#     resource_store_triples = False
#     if 'resource_triples' in command.download or 'resource_nfdi' in command.download or 'resource_table' in command.download:
#         resource_store_triples = True
#         # TODO FIND OUT IF MORPH FROM LIDO TO NFDI IS REQUIRED

#     # Retrieve resources
#     if command.source_folder != None:
#         resource = HydraRetrieveResource(report, 'local', None, command.source_folder, command.content_type, command.clean_resource_names, command.delay, resource_store_triples, resource_download)
#     else:
#         resource = HydraRetrieveResource(report, 'remote', feed.feed, command.source_folder, command.content_type, command.clean_resource_names, command.delay, resource_store_triples, resource_download)

#     # Update status from resource
#     report.status += resource.report.status

#     # Set up feed graph
#     if 'resource_triples' in command.download or 'resource_nfdi' in command.download or 'resource_table' in command.download:
#         resource_graph = HydraRetrieveGraph(report, resource.store)

#         # Compile triples
#         if 'resource_triples' in command.download:
#             resource_graph.save(command.target_folder_path, 'resource_triples.ttl', 'triples')

#         # Compile NFDI-style triples (and first parse LIDO if requested)
#         if 'resource_nfdi' in command.download:
#             if command.content_type_xml == 'lido':
#                 resource.morph('lido-to-nfdi', command.supplement_data_feed, command.supplement_data_catalog, command.supplement_data_catalog_publisher)
#                 resource_graph.nfdi = resource.nfdi
#             else:
#                 resource_graph.morph('cgif-to-nfdi')
#             resource_graph.save(command.target_folder_path, 'resource_nfdi.ttl', 'nfdi')

#         # Compile CSV table
#         if 'resource_table' in command.download:
#             resource_graph.morph('to-csv', command.table_data)
#             resource_graph.save(command.target_folder_path, 'resource_table.csv', 'csv')

#         # Update status from resource graph
#         report.status += resource_graph.report.status
