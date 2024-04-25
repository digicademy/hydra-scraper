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

# Beacons or endpoints
if command.source_file != None or command.source_url != None or 'lists' in command.download or 'list_triples' in command.download or 'list_nfdi' in command.download or 'beacon' in command.download:

    # Setting to download list files
    feed_download = False
    if 'lists' in command.download:
        feed_download = True

    # Retrieve lists and alter resource URLs
    feed = HydraRetrieveFeed(report, command.source_file, command.source_url, command.content_type, command.max_number_of_paginated_lists, command.retrieval_delay, feed_download, command.target_folder_path)
    feed.morph('urls', command.resource_url_filter, command.resource_url_replace, command.resource_url_replace_with, command.resource_url_add)

    # Save Beacon file
    if 'beacon' in command.download:
        feed.save(command.target_folder_path, 'beacon.txt', 'beacon')

    # Update status from feed
    report.status += feed.report.status

    # Set up feed graph
    if 'list_triples' in command.download or 'list_nfdi' in command.download:
        feed_graph = HydraRetrieveGraph(report, feed.store)

        # Compile triples
        if 'list_triples' in command.download:
            feed_graph.save(command.target_folder_path, 'list_triples.ttl', 'ttl')

        # Compile NFDI-style triples
        if 'list_nfdi' in command.download:
            feed_graph.morph('cgif-to-nfdi')
            feed_graph.save(command.target_folder_path, 'list_nfdi.ttl', 'nfdi')

        # Update status from feed graph
        report.status += feed_graph.report.status

# Individual resource files
if command.source_folder != None or 'resources' in command.download or 'resource_triples' in command.download or 'resource_nfdi' in command.download or 'resource_table' in command.download:

    # Setting to download resource files and store triples
    resource_download = False
    if 'resources' in command.download:
        resource_download = True
    resource_store_triples = False
    if 'resource_triples' in command.download or 'resource_nfdi' in command.download or 'resource_table' in command.download:
        resource_store_triples = True
        # TODO FIND OUT IF MORPH FROM LIDO TO NFDI IS REQUIRED

    # Retrieve resources
    if command.source_folder != None:
        resource = HydraRetrieveResource(report, 'local', None, command.source_folder, command.content_type, command.clean_resource_names, command.retrieval_delay, resource_store_triples, resource_download)
    else:
        resource = HydraRetrieveResource(report, 'remote', feed.feed, command.source_folder, command.content_type, command.clean_resource_names, command.retrieval_delay, resource_store_triples, resource_download)

    # Update status from resource
    report.status += resource.report.status

    # Set up feed graph
    if 'resource_triples' in command.download or 'resource_nfdi' in command.download or 'resource_table' in command.download:
        resource_graph = HydraRetrieveGraph(report, resource.store)

        # Compile triples
        if 'resource_triples' in command.download:
            resource_graph.save(command.target_folder_path, 'resource_triples.ttl', 'triples')

        # Compile NFDI-style triples
        if 'resource_nfdi' in command.download:
            resource_graph.morph('cgif-to-nfdi')
            resource_graph.save(command.target_folder_path, 'resource_nfdi.ttl', 'nfdi')

        # Compile CSV table
        if 'resource_table' in command.download:
            resource_graph.morph('to-csv', command.table_data)
            resource_graph.save(command.target_folder_path, 'resource_table.csv', 'csv')

        # Update status from resource graph
        report.status += resource_graph.report.status

# Produce final report
report.finish()
