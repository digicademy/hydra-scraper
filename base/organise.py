# Provide a structured input command
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from argparse import ArgumentParser
from datetime import datetime
from os import makedirs
from os.path import isdir, isfile
from urllib.robotparser import RobotFileParser
from validators import url

# Set up logging
logger = logging.getLogger(__name__)

# Set up user agent
harvest_identifier = 'Hydra Scraper/0.9.0-beta'
harvest_robots = 'HydraScraper'


class Organise:


    def __init__(self, args:list = []):
        '''
        Provide a structured input command

            Parameters:
                args (list): List of command-line arguments including script call
        '''

        # Const
        self.delay:int = 500 # millisenconds, i.e., two requests per second
        self.folder:str = 'downloads'
        self.max_pagination:int = 1000

        # Vars
        self.log:str|None = None
        self.folder_beacon:str|None = None
        self.folder_csv:str|None = None
        self.folder_cto:str|None = None
        self.folder_files:str|None = None
        self.folder_triples:str|None = None

        # Content vars
        self.location:str|None = None
        self.feed:str|None = None
        self.elements:str|None = None
        self.output:str|None = None
        self.name:str|None = None
        self.dialect:str|None = None
        self.include:str|None = None
        self.replace:str|None = None
        self.replace_with:str|None = None
        self.append:str|None = None
        self.add_feed:str|None = None
        self.add_catalog:str|None = None
        self.add_publisher:str|None = None
        self.clean:str|None = None
        self.prepare:str|None = None
        self.quiet:bool = False

        # Set up list of allowed arguments
        available_args = ArgumentParser(
            description = 'Comprehensive scraper for paginated APIs, RDF, XML file dumps, and Beacon files'
        )
        available_args.add_argument(
            '-l', '--location',
            required = True,
            type = str,
            help = 'Source URI, folder, or file path'
        )
        available_args.add_argument(
            '-f', '--feed',
            choices = [
                'beacon',
                'cmif',
                #'csv',
                #'folder',
                #'oaipmh',
                'schema',
                'schema-list',
                #'zipped'
            ],
            required = True,
            type = str,
            help = 'Type of feed or starting point for the scraping run'
        )
        available_args.add_argument(
            '-e', '--elements',
            choices = [
                #'csv',
                'lido',
                #'mei',
                'schema',
                #'tei'
            ],
            default = None,
            type = str,
            help = 'Element markup to extract data from during the scraping run'
        )
        available_args.add_argument(
            '-o', '--output',
            choices = [
                'beacon',
                'csv',
                'cto',
                'files',
                'triples'
            ],
            nargs='+',
            required = True,
            type = str,
            help = 'Outputs to produce in the scraping run'
        )
        available_args.add_argument(
            '-n', '--name',
            default = self.generate_timestamp(),
            type = str,
            help = 'Name of the subfolder to download data to'
        )
        available_args.add_argument(
            '-d', '--dialect',
            default = None,
            type = str,
            help = 'Content type to use for requests'
        )
        available_args.add_argument(
            '-i', '--include',
            default = None,
            type = str,
            help = 'Filter for feed element URIs to include'
        )
        available_args.add_argument(
            '-r', '--replace',
            default = None,
            type = str,
            help = 'String to replace in feed element URIs'
        )
        available_args.add_argument(
            '-rw', '--replace_with',
            default = None,
            type = str,
            help = 'string to replace the previous one with'
        )
        available_args.add_argument(
            '-a', '--append',
            default = None,
            type = str,
            help = 'addition to the end of each feed element URI'
        )
        available_args.add_argument(
            '-af', '--add_feed',
            default = None,
            type = str,
            help = 'URI of a data feed to bind members to'
        )
        available_args.add_argument(
            '-ac', '--add_catalog',
            default = None,
            type = str,
            help = 'URI of a data catalog the data feed belongs to'
        )
        available_args.add_argument(
            '-ap', '--add_publisher',
            default = None,
            type = str,
            help = 'URI of the data publisher'
        )
        available_args.add_argument(
            '-c', '--clean',
            default = None,
            type = str,
            nargs='+',
            help = 'Strings to remove from feed element URIs to build their file names'
        )
        available_args.add_argument(
            '-p', '--prepare',
            default = None,
            type = str,
            help = 'Prepare cto output for this NFDI4Culture feed ID'
        )
        available_args.add_argument(
            '-q', '--quiet',
            default = False,
            action = 'store_true',
            help = 'Do not display status messages'
        )

        # Parse user input
        args = available_args.parse_args(args)

        # Assign arguments to object
        self.location = args.location
        self.feed = args.feed
        self.elements = args.elements
        self.output = args.output
        self.name = args.name
        self.dialect = args.dialect
        self.include = args.include
        self.replace = args.replace
        self.replace_with = args.replace_with
        self.append = args.append
        self.add_feed = args.add_feed
        self.add_catalog = args.add_catalog
        self.add_publisher = args.add_publisher
        self.clean = args.clean
        self.prepare = args.prepare
        self.quiet = args.quiet

        # Check location based on feed parameter
        if self.feed == 'folder':
            if not isdir(self.location):
                raise ValueError('Hydra Scraper called with a malformed folder location.')
        elif self.feed in ['beacon', 'cmif', 'csv', 'zipped']:
            if not url(self.location) and not isfile(self.location):
                raise ValueError('Hydra Scraper called with a malformed ZIP file location.')
        elif self.feed in ['oaipmh', 'schema', 'schema-list']:
            if not url(self.location):
                raise ValueError('Hydra Scraper called with a malformed API location.')

        # Catch output commands that require data extraction
        if not self.elements:
            if 'beacon' in self.organise.output or 'csv' in self.organise.output or 'cto' in self.organise.output:
                raise ValueError('Hydra Scraper called with extraction routine but no element markup.')

        # Check further URIs
        for uri in [self.add_feed, self.add_catalog, self.add_publisher]:
            if uri != None and not url(uri):
                raise ValueError('Hydra Scraper called with a malformed URI to add.')

        # Get delay based on robots.txt
        # Currently only checks the feed, not the feed element URI
        robots_delay = self.robots_delay(self.location)
        if robots_delay:
            self.delay = robots_delay

        # Create base folder
        self.folder += '/' + self.name
        self.create_folder(self.folder)

        # Create target folders
        if 'beacon' in self.output:
            self.folder_beacon = self.folder + '/beacon'
            self.create_folder(self.folder_beacon)
        if 'csv' in self.output:
            self.folder_csv = self.folder + '/csv'
            self.create_folder(self.folder_csv)
        if 'cto' in self.output:
            self.folder_cto = self.folder + '/cto'
            self.create_folder(self.folder_cto)
        if 'files' in self.output:
            self.folder_files = self.folder + '/files'
            self.create_folder(self.folder_files)
        if 'triples' in self.output:
            self.folder_triples = self.folder + '/triples'
            self.create_folder(self.folder_triples)

        # Set up log file
        self.log = self.folder + '/harvesting.log'
        open(self.log, 'w').close()
        logging.basicConfig(filename = self.log, level = logging.INFO)
        logger.info('Created working folder')


    def generate_timestamp(self) -> str:
        '''
        Produce a current timestamp

            Returns:
                str: current date and time as a string
        '''

        # Format timestamp
        timestamp = datetime.now()
        timestamp = str(timestamp.isoformat())

        # Return result
        return timestamp


    def create_folder(self, folder_name:str):
        '''
        Create a folder with a given name

            Parameters:
                folder_name (str): Name of the folder to create
        '''

        # Create folders, may be error-prone
        try:
            makedirs(folder_name, exist_ok = True)
        except OSError:
            pass


    def robots_delay(self, location:str) -> int|None:
        '''
        Find whether there is a delay recommendation for a URI

            Parameters:
                location (str): URI to identify the delay for
        '''

        # Set up output
        output = None

        # URL
        if url(location):
            index = location.find('/')
            if index:
                index = location.find('/', index + 2)
            if index:
                domain = location[:index]
            else:
                domain = location

            # Robots
            robots = RobotFileParser()
            robots.set_url(domain + '/robots.txt')
            robots.read()

            # Delay
            delay = robots.crawl_delay(harvest_robots)
            if not delay:
                delay = robots.crawl_delay('*')
            if delay:
                output = int(delay * 1000)

            # Rate
            rate = robots.request_rate(harvest_robots)
            if not rate:
                rate = robots.request_rate('*')
            if rate:
                output = int((rate.seconds / rate.requests) * 1000)

        # Return
        return output
