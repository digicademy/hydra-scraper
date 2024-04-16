# Class to provide a structured input command
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from argparse import ArgumentParser
from argparse import FileType
from datetime import datetime
from os import makedirs
from pathlib import Path
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
    download = []
    source_url = None
    source_file = None
    source_folder = None
    content_type = None
    target_folder = None
    target_folder_path = None
    resource_url_filter = None
    resource_url_replace = None
    resource_url_replace_with = None
    resource_url_add = None
    clean_resource_names = []
    table_data = []
    supplement_data_feed = None
    supplement_data_catalog = None
    supplement_data_catalog_publisher = None
    quiet = False


    def __init__(self, command_line_arguments:list = []):
        '''
        Provide a structured input command

            Parameters:
                command_line_arguments (list): List of command-line arguments including script call
        '''

        # Set up list of allowed arguments
        allowed_arguments = ArgumentParser(
            prog = 'go.py',
            description = 'Comprehensive scraper for Hydra-paginated APIs, Beacon files, and RDF file dumps'
        )
        allowed_arguments.add_argument(
            '-download', '--download',
            choices = [
                'lists',
                'list_triples',
                'list_nfdi',
                'beacon',
                'resources',
                'resource_triples',
                'resource_nfdi',
                'resource_table'
            ],
            nargs='+',
            required = True,
            type = str,
            help = 'List of downloads you require'
        )
        allowed_arguments.add_argument(
            '-source_url', '--source_url',
            default = None,
            type = url,
            help = 'Entry-point URL to scrape content from'
        )
        allowed_arguments.add_argument(
            '-source_file', '--source_file',
            default = None,
            type = FileType('r', encoding='UTF-8'),
            help = 'Path to Beacon file containing URLs to scrape'
        )
        allowed_arguments.add_argument(
            '-source_folder', '--source_folder',
            default = None,
            type = Path,
            help = 'Path to folder containing files to scrape'
        )
        allowed_arguments.add_argument(
            '-content_type', '--content_type',
            default = None,
            type = str,
            help = 'Content type to request or use when scraping'
        )
        allowed_arguments.add_argument(
            '-taget_folder', '--taget_folder',
            default = self._generate_timestamp(),
            type = Path,
            help = 'Download to this subfolder of the download folder'
        )
        allowed_arguments.add_argument(
            '-resource_url_filter', '--resource_url_filter',
            default = None,
            type = str,
            help = 'String as a filter for resource lists'
        )
        allowed_arguments.add_argument(
            '-resource_url_replace', '--resource_url_replace',
            default = None,
            type = str,
            help = 'String to replace in resource lists'
        )
        allowed_arguments.add_argument(
            '-resource_url_replace_with', '--resource_url_replace_with',
            default = None,
            type = str,
            help = 'String to replace the previous one with'
        )
        allowed_arguments.add_argument(
            '-resource_url_add', '--resource_url_add',
            default = None,
            type = str,
            help = 'Addition to the end of each resource URL'
        )
        allowed_arguments.add_argument(
            '-clean_resource_names', '--clean_resource_names',
            default = None,
            type = str,
            nargs='+',
            help = 'List of strings to remove from resource URLs to build their file name'
        )
        allowed_arguments.add_argument(
            '-table_data', '--table_data',
            default = None,
            type = str,
            nargs='+',
            help = 'List of property URIs to compile in a table'
        )
        allowed_arguments.add_argument(
            '-supplement_data_feed', '--supplement_data_feed',
            default = None,
            type = url,
            help = 'URI of a data feed to bind LIDO files to'
        )
        allowed_arguments.add_argument(
            '-supplement_data_catalog', '--supplement_data_catalog',
            default = None,
            type = url,
            help = 'URI of a data catalog the data feed belongs to'
        )
        allowed_arguments.add_argument(
            '-supplement_data_catalog_publisher', '--supplement_data_catalog_publisher',
            default = None,
            type = url,
            help = 'URI of the publisher of the catalog'
        )
        allowed_arguments.add_argument(
            '-quiet', '--quiet',
            default = False,
            action = 'store_true',
            help = 'Option to avoid intermediate progress reporting'
        )

        # Parse user input
        arguments = allowed_arguments.parse_args(command_line_arguments)

        # Assign arguments to object
        self.download = arguments.download
        self.source_url = arguments.source_url
        self.source_file = arguments.source_file
        self.source_folder = arguments.source_folder
        self.content_type = arguments.content_type
        self.target_folder = arguments.target_folder
        self.target_folder_path = arguments.target_folder_path
        self.resource_url_filter = arguments.resource_url_filter
        self.resource_url_replace = arguments.resource_url_replace
        self.resource_url_replace_with = arguments.resource_url_replace_with
        self.resource_url_add = arguments.resource_url_add
        self.clean_resource_names = arguments.clean_resource_names
        self.table_data = arguments.table_data
        self.supplement_data_feed = arguments.supplement_data_feed
        self.supplement_data_catalog = arguments.supplement_data_catalog
        self.supplement_data_catalog_publisher = arguments.supplement_data_catalog_publisher
        self.quiet = arguments.quiet

        # More complex argument requirements
        if 'lists' in self.download or 'list_triples' in self.download or 'list_nfdi' in self.download or 'beacon' in self.download:
            if self.source_url == None:
                raise ValueError('Hydra Scraper called without valid source URL.')
        elif 'resources' in self.download:
            if self.source_url == None and self.source_file == None:
                raise ValueError('Hydra Scraper called without valid source URL or file name.')
        elif 'resource_triples' in self.download or 'resource_nfdi' in self.download or 'resource_table' in self.download:
            if self.source_url == None and self.source_file == None and self.source_folder == None:
                raise ValueError('Hydra Scraper called without valid source URL, file, or folder name.')
            elif self.source_folder != None and self.content_type == None:
                raise ValueError('Hydra Scraper called with a folder name but without a content type.')

        # Create target folder
        self.target_folder_path = self.target_folder_base + '/' + self.target_folder
        self._create_folder(self.target_folder_path)


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a useful string
        if self.download != []:
            return 'Scraping command to produce the following items: ' + ', '.join(self.download) + '.'
        else:
            return 'Empty scraping command.'


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


    def _create_folder(folder_name:str):
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
