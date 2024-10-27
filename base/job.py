# Execute a scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from datetime import datetime, timedelta
from glob import glob
from pyoxigraph import DefaultGraph, RdfFormat, Store
from rdflib import Graph, Namespace
from shutil import rmtree
from time import sleep

# Import script modules
import extract.beacon as beacon
import extract.cmif as cmif
#import extract.folder as folder
import extract.lido as lido
import extract.schema as schema
#import extract.zipped as zipped
from base.data import Uri, UriList
from base.file import File
from base.organise import Organise

# Define namespaces
SCHEMA = Namespace('http://schema.org/')

# Set up logging
logger = logging.getLogger(__name__)


class Job:


    def __init__(self, organise:Organise):
        '''
        Execute a scraping run

            Parameters:
                organise (Organise): Configuration object for a single job
        '''

        # Vars
        self.success:bool = True
        self.status:list = []
        self.organise:Organise = organise
        self.last_request:datetime|None = None

        # Set up log report
        self.log_start()
        status_feed = 'Entire feed processed.'
        status_elements = 'All feed elements processed.'

        # Enter feed pagination loop
        feed_uri = self.organise.location
        feed_index = 0
        while feed_index < self.organise.max_pagination:
            feed_index += 1

            # Delay if necessary
            if self.last_request:
                self.delay_request(self.last_request, self.organise.delay)

            # Get feed
            self.log_progress('Retrieving feed no. ' + str(feed_index) + ' and extracting data')
            feed_file = File(feed_uri)
            self.last_request = feed_file.request_time

            # Extract feed data
            if self.organise.feed == 'beacon':
                feed_data = beacon.Feed(feed_file)
            elif self.organise.feed == 'cmif':
                feed_data = cmif.Feed(feed_file)
            #elif self.organise.feed == 'folder':
            #    feed_data = folder.Feed(feed_file)
            #elif self.organise.feed == 'zipped':
            #    feed_data = zipped.Feed(feed_file)
            elif self.organise.feed == 'schema':
                feed_data = schema.Feed(feed_file, True)
            elif self.organise.feed == 'schema-list':
                feed_data = schema.Feed(feed_file)
            else:
                raise ValueError('Hydra Scraper called with an invalid feed type.')

            # Continue only when successfully retrieved
            if not feed_data.success:
                logger.error('Data not available for feed ' + feed_uri)
                status_feed = 'One of the feeds could not be processed.'
                self.success = False
                break
            else:

                # Alter data if requested
                if self.organise.add_feed:
                    feed_data.feed_uri = Uri(self.organise.add_feed)
                if self.organise.add_catalog:
                    feed_data.catalog_uri = Uri(self.organise.add_catalog)

                # Alter element URIs
                if self.organise.include:
                    feed_data.element_uris = UriList([element_uri.uri for element_uri in feed_data.element_uris.uris if self.organise.include in element_uri.uri])
                for index, element_uri in enumerate(feed_data.element_uris.uris):
                    if self.organise.replace and self.organise.replace_with:
                        feed_data.element_uris.uris[index].uri = element_uri.uri.replace(self.organise.replace, self.organise.replace_with, 1)
                    if self.organise.append:
                        feed_data.element_uris.uris[index].uri = element_uri.uri + self.organise.append

                # Generate feed file name
                feed_name = str(feed_index).zfill(len(str(self.organise.max_pagination)))

                # Save list with elements
                if self.organise.feed == 'schema':

                    # Save original data
                    if 'files' in self.organise.output:
                        self.log_progress('Saving original feed file')
                        feed_file.save(self.organise.folder_files + '/' + feed_name)
                    if 'triples' in self.organise.output:
                        self.log_progress('Saving temporary triples')
                        feed_file.turtle(self.organise.folder_triples + '/' + feed_name)

                    # Transform data
                    if 'beacon' in self.organise.output:
                        self.log_progress('Saving temporary Beacon-like list')
                        feed_data.map_and_save('beacon', self.organise.folder_beacon + '/' + feed_name, prepare = self.organise.prepare)
                    if 'csv' in self.organise.output:
                        self.log_progress('Saving temporary CSV table')
                        feed_data.map_and_save('csv', self.organise.folder_csv + '/' + feed_name, prepare = self.organise.prepare)
                    if 'cto' in self.organise.output:
                        self.log_progress('Saving temporary nfdicore/cto triples')
                        feed_data.map_and_turtle('cto', self.organise.folder_cto + '/' + feed_name, self.organise.prepare)

                # Save list without elements
                else:

                    # Save header data for collation
                    if feed_index == 1:
                        if 'beacon' in self.organise.output:
                            feed_data.map_and_save('beacon', self.organise.folder_beacon + '/0', prepare = self.organise.prepare)
                        if 'csv' in self.organise.output:
                            feed_data.map_and_save('csv', self.organise.folder_csv + '/0', prepare = self.organise.prepare)
                        if 'cto' in self.organise.output:
                            feed_data.map_and_turtle('cto', self.organise.folder_cto + '/0', self.organise.prepare)

                    # Loop through elements
                    for element_index_minus, element_uri in enumerate(feed_data.element_uris.uris):
                        element_index = element_index_minus + 1

                        # Delay if necessary
                        if self.last_request:
                            self.delay_request(self.last_request, self.organise.delay)

                        # Get feed element
                        if not self.organise.elements:
                            self.log_progress('Retrieving feed elements', element_index, len(feed_data.element_uris.uris))
                        else:
                            self.log_progress('Retrieving feed elements and extracting data', element_index, len(feed_data.element_uris.uris))
                        element_file = File(element_uri.uri, self.organise.dialect)
                        self.last_request = element_file.request_time

                        # Generate element file name
                        if self.organise.clean:
                            element_name = element_uri.uri
                            for clean in self.organise.clean:
                                element_name = element_name.replace(clean, '', 1)
                            element_name = element_name.replace('/', '')
                            element_name = element_name.replace(':', '')
                        else:
                            element_name = feed_name + '-' + str(element_index).zfill(len(str(len(feed_data.element_uris.uris))))

                        # Save original data
                        if 'files' in self.organise.output:
                            element_file.save(self.organise.folder_files + '/' + element_name)
                        if 'triples' in self.organise.output:
                            element_file.turtle(self.organise.folder_triples + '/' + element_name)

                        # Optionally extract data
                        if self.organise.elements:
                            if self.organise.elements == 'lido':
                                element_data = lido.FeedElement(element_file)
                            elif self.organise.elements == 'schema':
                                element_data = schema.FeedElement(element_file)
                            else:
                                raise ValueError('Hydra Scraper called with an invalid element markup.')

                            # Continue only when successfully retrieved
                            if not element_data.success:
                                logger.error('Could not extract data from feed element ' + element_uri.uri)
                                status_elements = 'At least one feed element could not be processed.'
                                self.success = False
                            else:

                                # Add data if missing
                                if not element_data.feed_uri:
                                    element_data.feed_uri = Uri(self.organise.location)
                                if not element_data.element_uri:
                                    element_data.element_uri = element_uri

                                # Alter data if requested
                                if self.organise.add_feed:
                                    element_data.feed_uri = Uri(self.organise.add_feed)
                                if self.organise.add_publisher:
                                    element_data.publisher = UriList(self.organise.add_publisher)

                                # Transform data
                                if 'beacon' in self.organise.output:
                                    element_data.map_and_save('beacon', self.organise.folder_beacon + '/' + element_name, prepare = self.organise.prepare)
                                if 'csv' in self.organise.output:
                                    element_data.map_and_save('csv', self.organise.folder_csv + '/' + element_name, prepare = self.organise.prepare)
                                if 'cto' in self.organise.output:
                                    element_data.map_and_turtle('cto', self.organise.folder_cto + '/' + element_name, self.organise.prepare)

                # Set up next feed page to harvest, if available
                if feed_data.feed_uri_next:
                    feed_uri = feed_data.feed_uri_next.uri
                else:
                    break

        # Compile outputs, task delayed to prevent memory issues during long harvests
        if self.organise.elements and 'beacon' in self.organise.output:
            self.log_progress('Saving compiled Beacon-like list')
            self.combine_text(self.organise.folder_beacon, self.organise.folder + '/beacon', 'txt', '#')
            self.remove_folder(self.organise.folder_beacon)
        if self.organise.elements and 'csv' in self.organise.output:
            self.log_progress('Saving compiled CSV table')
            self.combine_text(self.organise.folder_csv, self.organise.folder + '/table', 'csv', '"feed_uri","element_uri","element_uri_same"')
            self.remove_folder(self.organise.folder_csv)
        if self.organise.elements and 'cto' in self.organise.output:
            self.log_progress('Saving compiled nfdicore/cto triples')
            self.combine_triples(self.organise.folder_cto, self.organise.folder + '/cto')
            self.remove_folder(self.organise.folder_cto)
        if 'triples' in self.organise.output:
            self.log_progress('Saving compiled triples')
            self.combine_triples(self.organise.folder_triples, self.organise.folder + '/triples')
            self.remove_folder(self.organise.folder_triples)
        logger.info('Cleaned up working folder')

        # Show log report
        self.status.append(status_feed)
        self.status.append(status_elements)
        self.log_report()


    def delay_request(self, last_time:datetime, delay:int):
        '''
        Dynamically delay the next quest by a given time

            Parameters:
                note (str): Note to show the user
                current (int): Current number used to calculate a percentage
                max (int): Total number used to calculate a percentage
        '''

        # Sleep if next allowed request time is not now
        now = datetime.now()
        then = last_time + timedelta(milliseconds = delay)
        if now < then:
            wait = then - now
            sleep(wait.total_seconds())

            # Log info
            logger.info('Waited ' + str(wait.total_seconds()) + ' before making the next request')


    def combine_text(self, folder:str, file_path:str, file_extension:str, ignore:str):
        '''
        Collects text files and saves them in a single file

            Parameters:
                folder (str): Path of the folder to parse
                file_path (str): Path of the file to create
                file_extension (str): Extension of the file to create
                ignore (str): Start of lines to ignore
        '''

        # Prepare paths
        file_path += '.' + file_extension
        paths = self.files_in_folder(folder)

        # File by file, and line by line
        with open(file_path, 'w') as collated:
            for p, path in enumerate(paths):

                # Add line break on consecutive files
                if p != 0:
                    collated.write('\n')
                with open(path, 'r') as lines:
                    for line in lines:

                        # Full first file, leave out comments from consecutive ones
                        if p == 0 or not line.startswith(ignore):
                            collated.write(line)

        # Log info
        logger.info('Combined temporary text files into ' + file_path)


    def combine_triples(self, folder:str, file_path:str):
        '''
        Parses all Turtle files in a folder and saves them as a single file

            Parameters:
                folder (str): Path of the folder to parse
                file_path (str): Path of the file to create
        '''

        # Prepare paths
        file_path += '.ttl'
        paths = self.files_in_folder(folder)

        # Parse and save using pyoxigraph (quick and dirty, JSON-LD not supported)
        if len(paths) >= 15000:
            rdf = Store()
            for path in paths:
                rdf.load(path = path, format = RdfFormat.TURTLE, to_graph = DefaultGraph())
            rdf.dump(output = file_path, format = RdfFormat.TURTLE, from_graph = DefaultGraph())

        # Parse and save using rdflib (slow and pretty)
        else:
            rdf = Graph()
            rdf.bind('schema', SCHEMA, replace = True) # "Replace" overrides the RDFLib schema namespace (SDO), which uses "https"
            for path in paths:
                rdf.parse(path, format = 'turtle')
            rdf.serialize(destination = file_path, format = 'turtle')

        # Log info
        logger.info('Combined temporary RDF files into ' + file_path)


    def files_in_folder(self, folder_path:str) -> list:
        '''
        Read a local folder and return a list of resources

            Parameters:
                folder_path (str): Path to the folder to read
        '''

        # Prepare list and path
        entries = []
        folder_path += '/**/*'

        # Add each file path to list
        for entry in glob(folder_path, recursive = True):
            entries.append(entry)

        # Return entries
        return entries


    def remove_folder(self, folder:str):
        '''
        Removes a temporary folder and its contents

            Parameters:
                folder (str): Path of the folder to remove
        '''

        # Remove folder
        rmtree(folder)


    def log_start(self):
        '''
        Produce an intro note to show at the beginning of a scraping run
        '''

        # Show note
        if not self.organise.quiet:
            print('')


    def log_progress(self, note:str, current:int|None = None, max:int|None = None):
        '''
        Log and list progress information during a job

            Parameters:
                note (str): Note to show the user
                current (int): Current number used to calculate a percentage
                max (int): Total number used to calculate a percentage
        '''

        # Start string
        if not self.organise.quiet:
            echo_string = '- ' + note

            # Just echo string if there is no loop
            if current == None and max == None:
                print(echo_string)

            # Calculate percentage if loop is not complete
            elif current < max:
                progress = int((current / max ) * 100)
                echo_string += '… ' + f"{progress:02}" + '%'
                print(echo_string, end = '\r')

            # End line when loop id complete
            else:
                echo_string +=  '… done'
                print(echo_string)


    def log_report(self):
        '''
        Produce a final report of what happened during a scraping run
        '''

        # Basic info
        if not self.organise.quiet:
            report = 'Looking good! '
            if self.success == False:
                report = 'Something went wrong! '

            # Add reasons and general note
            for status in self.status:
                report += status + ' '
            report += 'Check harvesting log for more.'

            # Display result
            print('\n' + report + '\n')
