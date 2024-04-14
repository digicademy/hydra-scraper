# Class to provide a structured input command
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import datetime
from os import makedirs
from validators import url


class HydraCommand:

    # Fixed config
    retrieval_delay = 0.02
    target_folder_base = 'downloads'
    max_number_of_paginated_lists = 500
    allowed_non_rdf_formats = [
        'lido'
    ]
    known_defined_term_sets = [
        'http://sws.geonames.org/',
        'https://iconclass.org/',
        'http://vocab.getty.edu/page/aat/',
        'https://d-nb.info/gnd/',
        'http://www.wikidata.org/entity/',
        'https://viaf.org/viaf/',
        'https://rism.online/',
        'https://database.factgrid.de/wiki/Item:'
    ]

    # Variables
    request = []
    source_url = ''
    source_file = ''
    source_folder = ''
    content_type = ''
    target_folder_name = ''
    target_folder = ''
    resource_url_filter = ''
    resource_url_replace = ''
    resource_url_replace_with = ''
    resource_url_add = ''
    clean_resource_names = []
    table_data = []
    supplement_data_feed = ''
    supplement_data_catalog = ''
    supplement_data_catalog_publisher = ''


    def __init__(self, command_line_arguments:list = []):
        '''
        Provide a structured input command

            Parameters:
                command_line_arguments (list): List of all command-line arguments
        '''

        # Generate generic target folder
        self.target_folder_name = self._generate_timestamp()

        # Ask for input or use command-line arguments
        if len(command_line_arguments) == 1:
            self._interactive_commands()
        else:
            self._command_line(command_line_arguments)

        # Generate job folder
        self.target_folder = self.target_folder_base + '/' + self.target_folder_name


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a useful string
        if self.request != []:
            return 'Command including the following requests: ' + ', '.join(self.request)
        else:
            return 'Empty command'


    def _interactive_commands(self):
        '''
        Ask for commands interactively to populate object instance
        '''

        # Show placeholder
        print('Interactive mode has not been implemented yet.')
        exit


    def _command_line(self, command_line_arguments:list):
        '''
        Use command-line arguments to populate object instance

            Parameters:
                command_line_arguments (list): List of all command-line arguments
        '''

        # Remove script call
        command_line_arguments = command_line_arguments[1:]

        # Catch help requests
        if command_line_arguments[0] in ['help', '-help', '--help', 'h', '-h', '--h']:
            self.help_message()

        # Check requests and modify the request dictionary accordingly
        elif '-download' in command_line_arguments:

            # Go through each key/value pair
            self.request = self._clean_argument_value(command_line_arguments, 'download', 'list')
            self.source_url = self._clean_argument_value(command_line_arguments, 'source_url', 'url')
            self.source_file = self._clean_argument_value(command_line_arguments, 'source_file', 'str')
            self.source_folder = self._clean_argument_value(command_line_arguments, 'source_folder', 'str')
            self.content_type = self._clean_argument_value(command_line_arguments, 'content_type', 'str')
            self.target_folder_name = self._clean_argument_value(command_line_arguments, 'target_folder', 'str')
            self.resource_url_filter = self._clean_argument_value(command_line_arguments, 'resource_url_filter', 'str')
            self.resource_url_replace = self._clean_argument_value(command_line_arguments, 'resource_url_replace', 'str')
            self.resource_url_replace_with = self._clean_argument_value(command_line_arguments, 'resource_url_replace_with', 'str')
            self.resource_url_add = self._clean_argument_value(command_line_arguments, 'resource_url_add', 'str')
            self.clean_resource_names = self._clean_argument_value(command_line_arguments, 'clean_resource_names', 'list')
            self.table_data = self._clean_argument_value(command_line_arguments, 'table_data', 'list')
            self.supplement_data_feed = self._clean_argument_value(command_line_arguments, 'supplement_data_feed', 'url')
            self.supplement_data_catalog = self._clean_argument_value(command_line_arguments, 'supplement_data_catalog', 'url')
            self.supplement_data_catalog_publisher = self._clean_argument_value(command_line_arguments, 'supplement_data_catalog_publisher', 'url')

        # Throw error if there is no '-download' argument
        else:
            raise ValueError('Hydra Scraper called with invalid arguments.')

        # Check requirements for APIs
        if 'lists' in self.request or 'list_triples' in self.request or 'list_cgif' in self.request or 'beacon' in self.request:
            if self.source_url == None:
                raise ValueError('Hydra Scraper called without valid source URL.')

        # Check requirements for a Beacon list, part 1
        elif 'resources' in self.request:
            if self.source_url == None and self.source_file == None:
                raise ValueError('Hydra Scraper called without valid source URL or file name.')

        # Check requirements for a Beacon list, part 2
        elif 'resource_triples' in self.request or 'resource_cgif' in self.request or 'resource_table' in self.request:
            if self.source_url == None and self.source_file == None and self.source_folder == None:
                raise ValueError('Hydra Scraper called without valid source URL, file, or folder name.')
            elif self.source_folder != None and self.content_type == None:
                raise ValueError('Hydra Scraper called with a folder name but without a content type.')

        # No valid requests
        else:
            raise ValueError('Hydra Scraper called without valid download requests.')


    def _clean_argument_value(command_line_arguments:list, key:str, evaluation:str = None) -> str|list:
        '''
        Checks, validates, and returns the value of a command-line argument

            Parameters:
                command_line_arguments (list): command line arguments
                key (str): key to find the right value
                evaluation (str, optional): type of evaluation to run ('url', 'str', 'list')

            Returns:
                str|list: clean value
        '''

        # Check if argument key is used
        if '-' + key in command_line_arguments:

            # Retrieve argument value
            value_index = command_line_arguments.index('-' + key) + 1
            if len(command_line_arguments) >= value_index:
                value = command_line_arguments[value_index]

                # Perform a string evaluation
                if evaluation == 'str':
                    if not isinstance(value, str):
                        raise ValueError('The command-line argument -' + key + ' uses a malformed string.')

                # Perform a comma-separated list evaluation
                elif evaluation == 'list':
                    if isinstance(value, str):
                        if ', ' in value:
                            value = value.split(', ')
                        elif ',' in value:
                            value = value.split(',')
                        else:
                            value = [ value ]
                    else:
                        raise ValueError('The command-line argument -' + key + ' uses a malformed comma-separated list.')

                # Perform a URL evaluation
                elif evaluation == 'url':
                    if not url(value):
                        raise ValueError('The command-line argument -' + key + ' uses a malformed URL.')
                    
                # Perform no evaluation
                else:
                    pass
                
            # Throw error if there is no value for the key 
            else:
                raise ValueError('The command-line argument -' + key + ' is missing a value.')
        
        # Return value
        return value


    def _generate_timestamp(self) -> str:
        '''
        Produce a current timestamp

            Returns:
                str: current timestamp as a string
        '''

        # Format timestamp
        timestamp = datetime.now()
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M')

        # Return as string
        return str(timestamp)


    def _help_message():
        '''
        Echoes a help message to the user
        '''

        print(
'''

This scraper is a command-line tool. Use "python go.py" to run the script in interactive mode. Alternatively, use the configuration options listed below to run the script without interaction.

-download '<value>': comma-separated list of what you need, possible values:

    lists: all Hydra-paginated lists (requires -source_url)

    list_triples: all RDF triples in a Hydra API (requires -source_url)

    list_cgif: CGIF triples in a Hydra API (requires -source_url)

    beacon: Beacon file of all resources listed in an API (requires -source_url)

    resources: all resources of an API or Beacon (requires -source_url/_file)

    resource_triples: all RDF triples of resources (requires -source_url/_file/_folder)

    resource_cgif: CGIF triples of resources (requires -source_url/_file/_folder)

    resource_table: CSV table of data in resources (requires -source_url/_file/_folder)

-source_url '<url>': use this entry-point URL to scrape content (default: none)

-source_file '<path to file>': use the URLs in this Beacon file to scrape content (default: none)

-source_folder '<name of folder>': use this folder (default: none, requires -content_type)

-content_type '<string>': request/use this content type when scraping content (default: none)

-taget_folder '<name of folder>': download to this subfolder of `downloads` (default: timestamp)

-resource_url_filter '<string>': use this string as a filter for resource lists (default: none)

-resource_url_replace '<string>': replace this string in resource lists (default: none)

-resource_url_replace_with '<string>': replace the previous string with this one (default: none)

-resource_url_add '<string>': add this to the end of each resource URL (default: none)

-clean_resource_names '<string>': build file names from resource URLs (default: enumeration)

-table_data '<string list>': comma-separated property URIs to compile in a table (default: all)

-supplement_data_feed '<url>': URI of a data feed to bind LIDO files to (default: none)

-supplement_data_catalog '<url>': URI of a data catalog the data feed belongs to (default: none)

-supplement_data_catalog_publisher '<url>': URI of the publisher of the catalog (default: none)

'''
        )


    def create_folder(folder_name:str):
        '''
        Creates a folder with a given name

            Parameters:
                folder_name (str): Name of the folder to create
        '''

        # Create folders, may be error-prone
        try:
            makedirs(folder_name, exist_ok=True)
        except OSError as error:
            pass
