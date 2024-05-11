# Class to provide a structured input command
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from argparse import ArgumentParser
from datetime import datetime
from os import makedirs
from os.path import exists
from validators import url


class HyOrganise:

    # Config
    delay = 0.02
    folder = 'downloads'
    max_number_paginated_lists = 500

    # Vars
    start = None
    location = None
    markup = None
    output = None
    name = None
    dialect = None
    filter = None
    replace = None
    replace_with = None
    add = None
    add_feed = None
    add_catalog = None
    add_publisher = None
    clean = None
    table = None
    quiet = False
    folder_files = None
    status = []


    def __init__(self, args:list = []):
        '''
        Provide a structured input command

            Parameters:
                args (list): List of command-line arguments including script call
        '''

        # Set up list of allowed arguments
        hy_args = ArgumentParser(
            prog = 'go.py',
            description = 'Comprehensive scraper for Hydra-paginated APIs, Beacon files, and RDF file dumps'
        )
        hy_args.add_argument(
            '-s', '--start',
            choices = [
                'rdf-feed',
                'beacon-feed',
                'dump-folder',
                'xml-feed',
                'dump-file'
            ],
            required = True,
            type = str,
            help = 'Type of starting point for the scraping run'
        )
        hy_args.add_argument(
            '-l', '--location',
            required = True,
            type = str,
            help = 'Source URL, folder, or file path (depending on the start parameter)'
        )
        hy_args.add_argument(
            '-m', '--markup',
            choices = [
                'rdf-feed',
                'rdf-members',
                'lido',
                'tei',
                'mei',
                'csv'
            ],
            required = True,
            type = str,
            help = 'Markup to query during the scraping run'
        )
        hy_args.add_argument(
            '-o', '--output',
            choices = [
                'beacon',
                'files',
                'triples',
                'triples-nfdi',
                'csv'
            ],
            nargs='+',
            required = True,
            type = str,
            help = 'Outputs to produce in the scraping run'
        )
        hy_args.add_argument(
            '-n', '--name',
            default = self.__generate_timestamp(),
            type = str,
            help = 'Name of the subfolder to download data to'
        )
        hy_args.add_argument(
            '-d', '--dialect',
            default = None,
            type = str,
            help = 'Content type to use for requests'
        )
        hy_args.add_argument(
            '-f', '--filter',
            default = None,
            type = str,
            help = 'String to use as a filter for member/file URLs'
        )
        hy_args.add_argument(
            '-r', '--replace',
            default = None,
            type = str,
            help = 'String to replace in member/file URLs'
        )
        hy_args.add_argument(
            '-rw', '--replace_with',
            default = None,
            type = str,
            help = 'string to replace the previous one with'
        )
        hy_args.add_argument(
            '-a', '--add',
            default = None,
            type = str,
            help = 'addition to the end of each member/file URL'
        )
        hy_args.add_argument(
            '-af', '--add_feed',
            default = None,
            type = str,
            help = 'URI of a data feed to bind members to'
        )
        hy_args.add_argument(
            '-ac', '--add_catalog',
            default = None,
            type = str,
            help = 'URI of a data catalog the data feed belongs to'
        )
        hy_args.add_argument(
            '-ap', '--add_publisher',
            default = None,
            type = str,
            help = 'URI of the data publisher'
        )
        hy_args.add_argument(
            '-c', '--clean',
            default = None,
            type = str,
            nargs='+',
            help = 'Strings to remove from member/file URLs to build their file names'
        )
        hy_args.add_argument(
            '-t', '--table',
            default = None,
            type = str,
            nargs='+',
            help = 'Property URIs to compile in a table'
        )
        hy_args.add_argument(
            '-p', '--prepare',
            default = False,
            action = 'store_true',
            help = 'Prepare NFDI-style triples for ingest into a knowledge graph'
        )
        hy_args.add_argument(
            '-q', '--quiet',
            default = False,
            action = 'store_true',
            help = 'Avoid intermediate progress reporting'
        )

        # Parse user input
        args = hy_args.parse_args(args)

        # Assign arguments to object
        self.start = args.start
        self.location = args.location
        self.markup = args.markup
        self.output = args.output
        self.name = args.name
        self.dialect = args.dialect
        self.filter = args.filter
        self.replace = args.replace
        self.replace_with = args.replace_with
        self.add = args.add
        self.add_feed = args.add_feed
        self.add_catalog = args.add_catalog
        self.add_publisher = args.add_publisher
        self.clean = args.clean
        self.table = args.table
        self.prepare = args.prepare
        self.quiet = args.quiet

        # Check location based on start paramter
        if self.start == 'rdf-feed':
            if not url(self.location):
                raise ValueError('Hydra Scraper called with a malformed RDF feed location.')
        elif self.start == 'beacon-feed' or self.start == 'xml-feed' or self.start == 'dump-file':
            if not url(self.location) and not exists(self.location):
                raise ValueError('Hydra Scraper called with a malformed location.')
        elif self.start == 'dump-folder':
            if not exists(self.location):
                raise ValueError('Hydra Scraper called with a malformed dump folder location.')

        # Check further URIs
        uri_checks = [
            self.add_feed,
            self.add_catalog,
            self.add_publisher
        ]
        if self.table != None:
            uri_checks += self.table
        for uri_check in uri_checks:
            if uri_check != None and not url(uri_check):
                raise ValueError('Hydra Scraper called with a malformed URI.')

        # Create target folders
        self.folder += '/' + self.name
        self.folder_files = self.folder + '/files'
        self.__create_folder(self.folder_files)


    def __generate_timestamp(self) -> str:
        '''
        Produce a current timestamp

            Returns:
                str: current date and time as a string
        '''

        # Format timestamp
        timestamp = datetime.now()
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M')

        # Return as string
        return str(timestamp)


    def __create_folder(folder_name:str):
        '''
        Creates a folder with a given name

            Parameters:
                folder_name (str): Name of the folder to create
        '''

        # Create folders, may be error-prone
        try:
            makedirs(folder_name, exist_ok=True)
        except OSError:
            pass


    def report(self):
        '''
        Produce a final report of what happened during a scraping run
        '''

        # Basic info
        report = 'Looking good!'
        for entry in self.status:
            if entry['success'] == False:
                report = 'Something went wrong!'

        # Add reason
        for entry in self.status:
            report += ' ' + entry['reason']

        # Add missing data
        for entry in self.status:
            if 'missing' in entry:
                report = report + '\n\nMissing data:\n- ' + '\n- '.join(entry['missing'])

        # Add incompatible data
        for entry in self.status:
            if 'incompatible' in entry:
                report = report + '\n\nIncompatible data:\n- ' + '\n- '.join(entry['incompatible'])

        # Display result
        print(report)
