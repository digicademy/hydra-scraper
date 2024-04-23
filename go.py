# Main script
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from sys import argv

# Import script modules
from classes.command import *
from classes.report import *
from classes.retrieve_feed import *
from classes.retrieve_resource import *
from classes.retrieve_graph import *


# Set up config and reporting
command = HydraCommand(argv)
report = HydraReport(command.quiet)

#feed = HydraRetrieveFeed()
#resource = HydraRetrieveResource()

#

graph = HydraRetrieveGraph(report)

# Compile triples
if 'resource_triples' in command.download:
    graph.save(command.target_folder_path, 'resource_triples.ttl', 'ttl')

# Compile NFDI-style triples
if 'resource_nfdi' in command.download:
    graph.morph('cgif-to-nfdi')
    graph.save(command.target_folder_path, 'resource_nfdi.ttl', 'nfdi')

# Compile CSV table
if 'resource_table' in command.download:
    graph.morph('to-csv', command.table_data)
    graph.save(command.target_folder_path, 'resource_table.csv', 'csv')

# Update status from graph object
report.status += graph.report.status

#

# Produce final report
report.finish()


# types: api, resources

# # Set up Hydra API routine if required
# if 'lists' in command.download or 'beacon' in command.download or 'list_triples' in command.download or 'list_cgif' in command.download:
#     hydra = Hydra(command.target_folder_path, command.source_url, command.content_type)

#     # Populate the object, and download each API list if requested
#     if 'lists' in command.download:
#         save_lists = True
#     else:
#         save_lists = False
#     hydra.populate(save_lists, command.resource_url_filter, command.resource_url_replace, command.resource_url_replace_with, command.resource_url_add)

#     # Compile a beacon list if requested
#     if 'beacon' in command.download:
#         hydra.save_beacon()

#     # Compile list triples if requested
#     if 'list_triples' in command.download:
#         hydra.save_triples()

#     # Compile list CGIF triples if requested
#     if 'list_cgif' in command.download:
#         hydra.save_triples('cgif', 'lists_cgif')

#     # Add status message
#     status.extend(hydra.status)

# # Mini Hydra routine if Beacon logic is requested but no beacon file is given
# elif command.source_file == '':
#     hydra = Hydra(command.target_folder_path, command.source_url, command.content_type)
#     hydra.populate(False, command.resource_url_filter, command.resource_url_replace, command.resource_url_replace_with, command.resource_url_add)

# # Mark absence of hydra object if beacon file is present
# else:
#     hydra = False

# # Set up beacon file routine if required
# if 'resources' in command.download or 'resource_triples' in command.download or 'resource_cgif' in command.download or 'resource_table' in command.download:

#     # Use previous resource list if present
#     if hydra == False:
#         beacon = Beacon(command.target_folder_path, command.content_type)
#     else:
#         beacon = Beacon(command.target_folder_path, command.content_type, hydra.resources)

#     # Populate the object, and download each resource if requested
#     if 'resources' in command.download:
#         save_resources = True
#     else:
#         save_resources = False
#     beacon.populate(save_resources, command.clean_resource_names, command.source_file, command.source_folder, command.supplement_data_feed, command.supplement_data_catalog, command.supplement_data_catalog_publisher)

#     # Add status message
#     status.extend(beacon.status)