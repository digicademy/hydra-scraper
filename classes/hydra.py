# Class to manage scraping a Hydra API
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import script modules
from helpers.config import *
from helpers.download import download_file
from helpers.fileio import save_file
from helpers.fileio import save_list
from helpers.status import echo_note
from helpers.status import echo_progress
from rdflib import Graph
from rdflib import Namespace
from math import ceil
from time import sleep

# Define namespaces
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
SCHEMA = Namespace('http://schema.org/')


# Base class for a Hydra API to process
class Hydra:


    # Variables
    url = ''
    folder = ''
    list_file_path = ''
    number_of_resources = 0
    resources_per_list = 0
    number_of_lists = 0
    current_list = ''
    final_list = ''
    resources = []
    done = None


    def __init__(self, url:str, folder:str, list_file_path:str = ''):
        '''
        Sets up a Hydra entry point to process

            Parameters:
                url (str): URL to use as an entry point for a scraping run
                folder (str): Name of the downloads subfolder to store (paginated) lists at
                list_file_path (str): Path to a beacon list of individual resource URLs to create
        '''

        # Assign variables
        self.url = url
        self.folder = folder
        self.list_file_path = list_file_path
        self.current_list = url


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if self.done == None:
            return 'Hydra entry point to be scraped at ' + self.url
        elif self.done == False:
            return 'Hydra entry point at ' + self.url + ' being processed'
        elif self.done == True:
            return 'Processed hydra entry point at ' + self.url


    def __download_list(self, number:int, url:str) -> str:
        '''
        Downloads an individual Hydra list and processes its content

            Parameters:
                number (int): Number of this list file
        '''

        # Retrieve and save file
        hydra = download_file(url)
        if hydra != None:
            file_path = config['download_base'] + '/' + self.folder + '/lists/' + str(number) + '.' + hydra['file_extension']
            save_file(hydra['content'], file_path)

        # Throw error if list file is missing
        else:
            raise FileNotFoundError('One of the paginated lists is not available.')

        # Parse file content; parsing the URL directly produced weird cache errors in RDFLib and this
        # version is easier on servers because it accomplishes download and parsing in one request
        rdf = Graph()
        rdf.parse(data=hydra['content'], format=hydra['file_type'])

        # Add each individual resource URL (Hydra member or Schema item) to resource list
        resource_urls = rdf.objects(None, HYDRA.member, unique=True)
        for resource_url in resource_urls:
            self.resources.append(resource_url.toPython())
        resource_urls = rdf.objects(None, SCHEMA.item, unique=True)
        for resource_url in resource_urls:
            self.resources.append(resource_url.toPython())
            
        # Get total number of items per list, only makes sense on first page
        if number == 1:
            if len(self.resources) != 0:
                self.resources_per_list = len(self.resources)
            else:
                raise Exception('The Hydra API does not contain any resources.')

        # Retrieve URL of current list
        current_lists = rdf.objects(None, HYDRA.view, unique=True)
        for current_list in current_lists:
            self.current_list = current_list.toPython()

        # Retrieve URL of next list to see if file is paginated
        next_list_url = ''
        next_lists = rdf.objects(None, HYDRA.next, unique=True)
        for next_list in next_lists:
            next_list_url = next_list.toPython()

            # Retrieve URL of final list
            final_lists = rdf.objects(None, HYDRA.last, unique=True)
            for final_list in final_lists:
                self.final_list = final_list.toPython()
            
            # Throw error if there is no final list
            if self.final_list == '':
                raise Exception('The Hydra API does not specify a final list.')

            # Get total number of resources
            total_ints = rdf.objects(None, HYDRA.totalItems, unique=True)
            for total_int in total_ints:
                self.number_of_resources = int(total_int.toPython())

            # Get number of lists
            self.number_of_lists = int(ceil(self.number_of_resources / self.resources_per_list))

        # Display progress indicator and add delay to avoid getting blocked be server
        echo_progress('Retrieving paginated API lists', number, self.number_of_lists)
        sleep(config['download_delay'])

        # Return next URL to scrape
        return next_list_url


    def process(self):
        '''
        Downloads all lists in the hydra API
        '''

        # Provide initial status
        self.done = False
        echo_progress('Retrieving paginated API lists', 0, 100)

        # Retrieve each Hydra list file
        index = 0
        next_list_url = self.url
        while self.current_list != self.final_list:
            index += 1
            next_list_url = self.__download_list(index, next_list_url)

            # Get out of loop if there is no next page for some reason
            if next_list_url == '':
                break

            # Throw error if maximum number of lists is reached as a safety
            # net if there are API errors that do not stop the script
            if index > config['max_paginated_lists']:
                raise Exception('The maximum number of paginated lists was reached.')

        # Optionally save beacon list as a file
        if self.list_file_path != '' and self.resources != []:
            file_path = config['download_base'] + '/' + self.folder + '/' + self.list_file_path
            save_list(file_path, self.resources)

        # Report new status as successful
        self.done = True
        echo_note('\nDone! All paginated lists saved to the download folder.\n')
