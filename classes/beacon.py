# Class to manage scraping a list of individual resources
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Graph
from time import sleep

# Import script modules
from helpers.config import *
from helpers.convert import convert_triples_to_table
from helpers.download import download_file
from helpers.fileio import create_folder
from helpers.fileio import read_list
from helpers.fileio import save_file
from helpers.fileio import save_table
from helpers.status import echo_progress


# Base class for a beacon list to process
class Beacon:


    # Variables
    status = []
    populated = None
    triples = Graph()
    resources = []
    resources_type = ''
    target_folder = ''
    number_of_resources = 0
    missing_resources = 0
    missing_resources_list = []
    non_rdf_resources = 0
    non_rdf_resources_list = []


    def __init__(self, target_folder:str, resources_type:str = '', resources:list = []):
        '''
        Sets up a list of resources to process

            Parameters:
                target_folder (str): Name of the downloads subfolder to store files in
                resources_type (str, optional): Content type to request when retrieving resources, defaults to none
                resources (list, optional): List of resources to retrieve, defaults to empty list
        '''

        # Assign variables
        self.target_folder = config['download_base'] + '/' + target_folder
        self.resources_type = resources_type
        self.resources = resources


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if self.populated == None:
            return 'List of individual resources to be retrieved'
        elif self.populated == False:
            return 'List of individual resources currently being processed'
        elif self.populated == True:
            return 'Processed list of individual resources'


    def populate(self, save_original_files:bool = True, clean_resource_urls:list = [], beacon_file:str = ''):
        '''
        Retrieves all individual resources from the list, populates the object, and optionally stores the original files in the process

            Parameters:
                save_original_files (bool, optional): Switch to also save original files on download, defaults to True
                clean_resource_urls (list, optional): List of substrings to remove in the resource URLs to produce a resource's file name, defaults to empty list that enumerates resources
                beacon_file (str, optional): Path to the beacon file to process, defaults to an empty string
        '''

        # Notify object that it is being populated
        self.populated = False

        # Provide initial status
        status_report = {
            'success': True,
            'reason': 'All resources retrieved successfully.'
        }
        echo_progress('Retrieving individual resources', 0, 100)

        # If requested, get list of individual resources from beacon file
        if beacon_file != '':
            self.resources = read_list(beacon_file)

        # Throw error if resource list is empty
        if self.resources == []:
            status_report['success'] = False
            status_report['reason'] = 'There were no resources to retrieve.'

        # Count number of resources
        else:
            self.number_of_resources = len(self.resources)

            # Main loop to retrieve resource files
            for number, resource_url in enumerate(self.resources, start = 1):

                # Retrieve file
                resource = download_file(resource_url, self.resources_type)
                if resource != None:

                    # Optionally save file
                    if save_original_files:
                        file_folder = self.target_folder + '/resources'
                        create_folder(file_folder)

                        # Clean up file name if required
                        if clean_resource_urls == []:
                            file_name = str(number)
                        else:
                            file_name = resource_url
                            for clean_resource_url in clean_resource_urls:
                                file_name = file_name.replace(clean_resource_url, '')

                        # Save file
                        file_path = file_folder + '/' + file_name + '.' + resource['file_extension']
                        save_file(resource['content'], file_path)
                        status_report['reason'] = 'All resources saved to download folder.'

                # Report if download failed
                else:
                    self.missing_resources += 1
                    self.missing_resources_list.append(resource_url)
                    continue

                # Add triples to object storage
                if resource['file_type'] not in config['non_rdf_formats']:
                    try:
                        self.triples.parse(data=resource['content'], format=resource['file_type'])
                    except:
                        self.non_rdf_resources += 1
                        self.non_rdf_resources_list.append(resource_url)
                        continue

                # Report any failed state
                if self.missing_resources >= self.number_of_resources:
                    status_report['success'] = False
                    status_report['reason'] = 'All resources were missing.'
                elif self.missing_resources > 0 and self.non_rdf_resources > 0:
                    status_report['reason'] = 'Resources retrieved, but ' + str(self.missing_resources) + ' were missing and ' + str(self.non_rdf_resources) + ' were not RDF-compatible.'
                    status_report['missing'] = self.missing_resources_list
                    status_report['non_rdf'] = self.non_rdf_resources_list
                elif self.missing_resources > 0:
                    status_report['reason'] = 'Resources retrieved, but ' + str(self.missing_resources) + ' were missing.'
                    status_report['missing'] = self.missing_resources_list
                elif self.non_rdf_resources > 0:
                    status_report['reason'] = 'Resources retrieved, but ' + str(self.non_rdf_resources) + ' were not RDF-compatible.'
                    status_report['non_rdf'] = self.non_rdf_resources_list

                # Delay next retrieval to avoid a server block
                echo_progress('Retrieving individual resources', number, self.number_of_resources)
                sleep(config['download_delay'])

        # Notify object that it is populated
        self.populated = True

        # Provide final status
        self.status.append(status_report)


    def save_triples(self, file_name:str = 'resources'):
        '''
        Saves all downloaded triples into a single Turtle file

            Parameters:
                file_name (str, optional): Name of the triple file without a file extension, defaults to 'resources'
        '''

        # Provide initial status
        status_report = {
            'success': False,
            'reason': ''
        }

        # Prevent routine if object is not populated yet
        if self.populated != True:
            status_report['reason'] = 'A list of triples can only be written when the resources were read.'
        else:

            # Initial progress
            echo_progress('Saving list of resource triples', 0, 100)

            # Compile file if there are triples
            if len(self.triples):
                file_path = self.target_folder + '/' + file_name + '.ttl'
                self.triples.serialize(destination=file_path, format='turtle')

                # Compile success status
                status_report['success'] = True
                status_report['reason'] = 'All resource triples listed in a Turtle file.'

            # Report if there are no resources
            else:
                status_report['reason'] = 'No resource triples to list in a Turtle file.'

            # Final progress
            echo_progress('Saving list of resource triples', 100, 100)

        # Provide final status
        self.status.append(status_report)


    def save_table(self, table_data:list = [], file_name:str = 'resources'):
        '''
        Saves specified data from all downloaded triples into a single CSV file

            Parameters:
                table_data (list, optional): List of properties to save, defaults to all
                file_name (str, optional): Name of the table file without a file extension, defaults to 'resources'
        '''

        # Provide initial status
        status_report = {
            'success': False,
            'reason': ''
        }

        # Prevent routine if object is not populated yet
        if self.populated != True:
            status_report['reason'] = 'A data table can only be written when the resources were read.'
        else:

            # Initial progress
            echo_progress('Saving table from resource data', 0, 100)

            # Compile table if there are triples
            if len(self.triples):
                file_path = self.target_folder + '/' + file_name
                tabular_data = convert_triples_to_table(self.triples)
                save_table(tabular_data, file_path)

                # Compile success status
                status_report['success'] = True
                status_report['reason'] = 'Resource data listed in a table.'

            # Report if there are no resources
            else:
                status_report['reason'] = 'No resource data to list in a table.'

            # Final progress
            echo_progress('Saving table from resource data', 100, 100)

        # Provide final status
        self.status.append(status_report)
