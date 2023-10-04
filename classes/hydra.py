# Class to manage scraping a Hydra API
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Graph
from rdflib import Namespace
from math import ceil
from time import sleep

# Import script modules
from helpers.config import *
from helpers.download import download_file
from helpers.fileio import create_folder
from helpers.fileio import save_file
from helpers.fileio import save_list
from helpers.status import echo_progress

# Define namespaces
from rdflib.namespace import RDF
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
SCHEMA = Namespace('http://schema.org/')


# Base class for a Hydra API to process
class Hydra:


    # Variables
    status = []
    populated = None
    triples = Graph()
    resources = []
    target_folder = ''
    entry_point_url = ''
    entry_point_url_type = ''
    current_list_url = ''
    next_list_url = ''
    final_list_url = ''
    number_of_resources = 0
    resources_per_list = 0
    number_of_lists = 0


    def __init__(self, target_folder:str, entry_point_url:str, entry_point_url_type:str = ''):
        '''
        Sets up a Hydra entry point to process

            Parameters:
                target_folder (str): Name of the downloads subfolder to store files in
                entry_point_url (str): URL to use as an entry point for a scraping run
                entry_point_url_type (str, optional): Content type to request when retrieving resources, defaults to none
        '''

        # Assign variables
        self.target_folder = config['download_base'] + '/' + target_folder
        self.entry_point_url = entry_point_url
        self.entry_point_url_type = entry_point_url_type
        self.current_list_url = entry_point_url
        self.next_list_url = entry_point_url


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if self.populated == None:
            return 'Hydra entry point to be scraped at ' + self.entry_point_url
        elif self.populated == False:
            return 'Hydra entry point at ' + self.entry_point_url + ' being processed'
        elif self.populated == True:
            return 'Processed Hydra entry point at ' + self.entry_point_url


    def __modify_resource_urls(self, resource_url_filter:str = '', resource_url_replace:str = '', resource_url_replace_with:str = '', resource_url_add:str = ''):
        '''
        Mofifies the list of individual resource URLs on demand

            Parameters:
                resources (list): List of resource URLs to modify
                resource_url_filter (str, optional): String applied to filter resource URLs, defaults to an empty string
                resource_url_replace (str, optional): String to replace in listed URLs before retrieving a resource, defaults to an empty string
                resource_url_replace_with (str, optional): String to use as a replacement before retrieving a resource, defaults to an empty string
                resource_url_add (str, optional): String to add to each URL before retrieving a resource, defaults to an empty string
        '''

        # Empty list for revised URLs
        modified_resources = []

        # Check each URL in the list
        for url in self.resources:
            if resource_url_filter != '':
                if resource_url_filter not in url:
                    url = ''
            if url != '':
                if resource_url_replace != '':
                    url = url.replace(resource_url_replace, resource_url_replace_with)
                if resource_url_add != '':
                    url = url + resource_url_add
                modified_resources.append(url)
            
        # Use the revised URLs instead of the original
        self.resources = modified_resources


    def __get_triple(self, graph:object, predicate:str, list_items:bool = False) -> str | int:
        '''
        Helper function to return a single object or a list of objects from triples

            Parameters:
                graph (object): Graph to perform the get request on
                predicate (str): Predicate to find in all triples
                list_items (bool, optional): Switch to determine whether to return a list or a single item, defaults to False

            Returns:
                str | int: Last object string identified by the predicate
        '''

        # Find triples
        triples = graph.objects(None, predicate, unique=True)

        # Find a single item
        if list_items == False:
            result = ''
            for triple in triples:
                result = triple.toPython()

        # Find a list of items
        else:
            result = []
            for triple in triples:
                result.append(triple.toPython())

        # Return the result
        return result


    def populate(self, save_original_files:bool = True, resource_url_filter:str = '', resource_url_replace:str = '', resource_url_replace_with:str = '', resource_url_add:str = ''):
        '''
        Pages through the Hydra API, populates the object, and optionally stores the original files in the process

            Parameters:
                save_original_files (bool, optional): Switch to also save original files on download, defaults to True
                resource_url_filter (str, optional): String applied to filter resource URLs, defaults to an empty string
                resource_url_replace (str, optional): String to replace in resource URLs, defaults to an empty string
                resource_url_replace_with (str, optional): String to use as a replacement in resource URLs, defaults to an empty string
                resource_url_add (str, optional): String to add to each resource URL, defaults to an empty string
        '''

        # Notify object that it is being populated
        self.populated = False

        # Provide initial status
        status_report = {
            'success': True,
            'reason': 'All lists retrieved successfully.'
        }

        # Main loop to retrieve list files
        number = 0
        while self.current_list_url != self.final_list_url:
            number += 1

            # Retrieve file
            hydra = download_file(self.next_list_url, self.entry_point_url_type)
            if hydra != None:

                # Optionally save file
                if save_original_files:
                    file_folder = self.target_folder + '/lists'
                    create_folder(file_folder)
                    file_path = file_folder + '/' + str(number) + '.' + hydra['file_extension']
                    save_file(hydra['content'], file_path)
                    status_report['reason'] = 'All lists saved to download folder.'

            # Throw error if list file is missing
            else:
                status_report['success'] = False
                status_report['reason'] = 'One of the paginated lists is not available.'
                break

            # Add triples to object storage
            try:
                hydra_triples = Graph()
                hydra_triples.parse(data=hydra['content'], format=hydra['file_type'])
            except:
                status_report['success'] = False
                status_report['reason'] = 'The Hydra API could not be parsed as RDF-style data.'
                break

            # Add each individual resource URL to main resource list
            self.resources.extend(self.__get_triple(hydra_triples, HYDRA.member, True))
            self.resources.extend(self.__get_triple(hydra_triples, SCHEMA.item, True))

            # Get total number of items per list (only makes sense on first page)
            if number == 1:
                if len(self.resources) != 0:
                    self.resources_per_list = len(self.resources)
                else:
                    status_report['success'] = False
                    status_report['reason'] = 'The Hydra API does not contain any resources.'
                    break

            # Retrieve URL of current, next, and final list
            self.current_list_url = self.__get_triple(hydra_triples, HYDRA.view)
            self.next_list_url = self.__get_triple(hydra_triples, HYDRA.next)
            self.final_list_url = self.__get_triple(hydra_triples, HYDRA.last)

            # Throw error if the API is paginated but there is no final list
            if self.next_list_url != '' and self.final_list_url == '':
                status_report['success'] = False
                status_report['reason'] = 'The Hydra API is paginated but does not specify a final list.'
                break

            # Get total number of resources and calculate number of lists
            self.number_of_resources = int(self.__get_triple(hydra_triples, HYDRA.totalItems))
            self.number_of_lists = int(ceil(self.number_of_resources / self.resources_per_list))

            # Remove pagination info from triples, but leave HYDRA.collection and HYDRA.member intact
            hydra_triples.remove((None, HYDRA.totalItems, None))
            hydra_triples.remove((None, HYDRA.view, None))
            hydra_triples.remove((None, HYDRA.first, None))
            hydra_triples.remove((None, HYDRA.last, None))
            hydra_triples.remove((None, HYDRA.next, None))
            hydra_triples.remove((None, HYDRA.previous, None))
            hydra_triples.remove((None, RDF.type, HYDRA.PartialCollectionView))

            # Add list triples to object triples
            self.triples = self.triples + hydra_triples

            # Delay next retrieval to avoid a server block
            echo_progress('Retrieving API lists', number, self.number_of_lists)
            sleep(config['download_delay'])

            # Get out of loop if there is no next page
            if self.next_list_url == '':
                break

            # Throw error if maximum number of lists is reached as a safety net
            if number > config['max_paginated_lists']:
                status_report['success'] = False
                status_report['reason'] = 'Maximum number of allowed lists was reached.'
                break

        # Filter, replace or augment strings in resource URLs if requested
        if resource_url_filter != '' or resource_url_replace != '' or resource_url_add != '':
            self.__modify_resource_urls(resource_url_filter, resource_url_replace, resource_url_replace_with, resource_url_add)

        # Notify object that it is populated
        self.populated = True

        # Provide final status
        self.status.append(status_report)


    def save_beacon(self, file_name:str = 'beacon'):
        '''
        Lists all individual resources in a beacon file

            Parameters:
                file_name (str, optional): Name of the beacon file without a file extension, defaults to 'beacon'
        '''

        # Provide initial status
        status_report = {
            'success': False,
            'reason': ''
        }

        # Prevent routine if object is not populated yet
        if self.populated != True:
            status_report['reason'] = 'A beacon file can only be written when the API was read.'
        else:

            # Initial progress
            echo_progress('Saving beacon file', 0, 100)

            # Save file if there are resources
            if self.resources != []:
                file_path = self.target_folder + '/' + file_name + '.txt'
                save_list(file_path, self.resources)

                # Compile success status
                status_report['success'] = True
                status_report['reason'] = 'All resources listed in a beacon file.'

            # Report if there are no resources
            else:
                status_report['reason'] = 'No resources to list in a beacon file.'

            # Final progress
            echo_progress('Saving beacon file', 100, 100)

        # Provide final status
        self.status.append(status_report)


    def save_triples(self, file_name:str = 'lists'):
        '''
        Saves all downloaded triples into a single Turtle file

            Parameters:
                file_name (str, optional): Name of the triple file without a file extension, defaults to 'lists'
        '''

        # Provide initial status
        status_report = {
            'success': False,
            'reason': ''
        }

        # Prevent routine if object is not populated yet
        if self.populated != True:
            status_report['reason'] = 'A list of triples can only be written when the API was read.'
        else:

            # Initial progress
            echo_progress('Saving list of API triples', 0, 100)

            # Compile file if there are triples
            if len(self.triples):
                file_path = self.target_folder + '/' + file_name + '.ttl'
                self.triples.serialize(destination=file_path, format='turtle')

                # Compile success status
                status_report['success'] = True
                status_report['reason'] = 'All API triples listed in a Turtle file.'

            # Report if there are no resources
            else:
                status_report['reason'] = 'No API triples to list in a Turtle file.'

            # Final progress
            echo_progress('Saving list of API triples', 100, 100)

        # Provide final status
        self.status.append(status_report)
