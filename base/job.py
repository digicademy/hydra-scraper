# Execute a scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from datetime import datetime
from os.path import getsize
from pyoxigraph import DefaultGraph, RdfFormat, Store
from rdflib import Graph, Namespace

# Import script modules
import extract.beacon as beacon
import extract.cmif as cmif
import extract.folder as folder
import extract.lido as lido
import extract.schema as schema
from base.data import Uri, UriList
from base.file import File, files_in_folder, remove_folder
from base.lookup import Lookup
from base.organise import Organise, delay_request

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
        self.lookup:Lookup = Lookup(self.organise.folder + '/lookup')
        self.last_request:datetime|None = None

        # Set up reporting
        if not self.organise.quiet:
            print('')
        status = Progress('Setting up tasks', self.organise.quiet)
        status_feed = 'Entire feed processed.'
        status_elements = 'All feed elements processed.'

        # Enter feed pagination loop
        feed_uri = self.organise.location
        feed_index = 0
        while feed_index < self.organise.max_pagination:
            feed_index += 1

            # Delay if necessary
            if self.last_request:
                delay_request(self.last_request, self.organise.delay)

            # Get feed
            status.done()
            status = Progress('Retrieving feed no. ' + str(feed_index) + ' and extracting data', self.organise.quiet)
            feed_file = File(feed_uri)
            self.last_request = feed_file.request_time

            # Extract feed data
            if self.organise.feed == 'beacon':
                feed_data = beacon.Feed(feed_file)
            elif self.organise.feed == 'cmif':
                feed_data = cmif.Feed(feed_file)
            elif self.organise.feed == 'folder':
                feed_data = folder.Feed(feed_file)
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
                    feed_data.element_uris = [element_uri for element_uri in feed_data.element_uris if self.organise.include in element_uri]
                for index, element_uri in enumerate(feed_data.element_uris):
                    if self.organise.replace and self.organise.replace_with:
                        feed_data.element_uris[index] = element_uri.replace(self.organise.replace, self.organise.replace_with, 1)
                    if self.organise.append:
                        feed_data.element_uris[index] = element_uri + self.organise.append

                # Generate feed file name
                feed_name = str(feed_index).zfill(len(str(self.organise.max_pagination)))

                # Save list with elements
                if self.organise.feed == 'schema':

                    # Save original data
                    if 'files' in self.organise.output:
                        status.done()
                        status = Progress('Saving original feed file', self.organise.quiet)
                        feed_file.save(self.organise.folder_files + '/' + feed_name)
                    if 'triples' in self.organise.output:
                        status.done()
                        status = Progress('Saving temporary triples', self.organise.quiet)
                        feed_file.turtle(self.organise.folder_triples + '/' + feed_name)

                    # Reconcile data
                    if 'csv' in self.organise.output or 'cto' in self.organise.output:
                        status.done()
                        status = Progress('Reconciling authority URIs', self.organise.quiet)
                        for element_index_minus, element_data in enumerate(feed_data.feed_elements):
                            element_index = element_index_minus + 1
                            status.update(element_index, len(feed_data.feed_elements))

                            # Check each vocab_further URI
                            vocab_further = []
                            for uri_label in element_data.vocab_further.uri_labels:
                                if uri_label.uri.uri:
                                    check = self.lookup.check(uri_label.uri.uri)
                                else:
                                    check = None

                                # Add it to the right list
                                if check == 'person':
                                    element_data.vocab_related_person.uri_labels.append(uri_label)
                                elif check == 'organization':
                                    element_data.vocab_related_organization.uri_labels.append(uri_label)
                                elif check == 'location':
                                    element_data.vocab_related_location.uri_labels.append(uri_label)
                                elif check == 'event':
                                    element_data.vocab_related_event.uri_labels.append(uri_label)
                                elif check == 'subject_concept':
                                    element_data.vocab_subject_concept.uri_labels.append(uri_label)
                                elif check == 'element_type':
                                    element_data.vocab_element_type.uri_labels.append(uri_label)

                                # Recompile vocab_further with everything else
                                else:
                                    vocab_further.append(uri_label)
                            element_data.vocab_further.uri_labels = vocab_further

                    # Transform data
                    if 'beacon' in self.organise.output:
                        status.done()
                        status = Progress('Saving temporary Beacon-like list', self.organise.quiet)
                        feed_data.map_and_save('beacon', self.organise.folder_beacon + '/' + feed_name, prepare = self.organise.prepare)
                    if 'csv' in self.organise.output:
                        status.done()
                        status = Progress('Saving temporary CSV table', self.organise.quiet)
                        feed_data.map_and_save('csv', self.organise.folder_csv + '/' + feed_name, prepare = self.organise.prepare)
                    if 'cto' in self.organise.output:
                        status.done()
                        status = Progress('Saving temporary nfdicore/cto triples', self.organise.quiet)
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
                    status.done()
                    status = Progress('Retrieving feed elements and extracting data', self.organise.quiet)
                    for element_index_minus, element_uri in enumerate(feed_data.element_uris):
                        element_index = element_index_minus + 1

                        # Delay if necessary
                        if self.last_request:
                            delay_request(self.last_request, self.organise.delay)

                        # Get feed element
                        status.update(element_index, len(feed_data.element_uris))
                        element_file = File(element_uri, self.organise.dialect)
                        self.last_request = element_file.request_time

                        # Generate element file name
                        if self.organise.clean:
                            element_name = element_uri
                            for clean in self.organise.clean:
                                element_name = element_name.replace(clean, '', 1)
                            element_name = element_name.replace('/', '')
                            element_name = element_name.replace(':', '')
                        else:
                            element_name = feed_name + '-' + str(element_index).zfill(len(str(len(feed_data.element_uris))))

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
                                logger.error('Could not extract data from feed element ' + element_uri)
                                status_elements = 'At least one feed element could not be processed.'
                                self.success = False
                            else:

                                # Add data if missing
                                if not element_data.feed_uri:
                                    element_data.feed_uri = Uri(self.organise.location)
                                if not element_data.element_uri:
                                    element_data.element_uri = Uri(element_uri)

                                # Alter data if requested
                                if self.organise.add_feed:
                                    element_data.feed_uri = Uri(self.organise.add_feed)
                                if self.organise.add_publisher:
                                    element_data.publisher = UriList(self.organise.add_publisher)

                                # Reconcile data
                                if 'csv' in self.organise.output or 'cto' in self.organise.output:

                                    # Check each vocab_further URI
                                    vocab_further = []
                                    for uri_label in element_data.vocab_further.uri_labels:
                                        if uri_label.uri.uri:
                                            check = self.lookup.check(uri_label.uri.uri)
                                        else:
                                            check = None

                                        # Add it to the right list
                                        if check == 'person':
                                            element_data.vocab_related_person.uri_labels.append(uri_label)
                                        elif check == 'organization':
                                            element_data.vocab_related_organization.uri_labels.append(uri_label)
                                        elif check == 'location':
                                            element_data.vocab_related_location.uri_labels.append(uri_label)
                                        elif check == 'event':
                                            element_data.vocab_related_event.uri_labels.append(uri_label)
                                        elif check == 'subject_concept':
                                            element_data.vocab_subject_concept.uri_labels.append(uri_label)
                                        elif check == 'element_type':
                                            element_data.vocab_element_type.uri_labels.append(uri_label)

                                        # Recompile vocab_further with everything else
                                        else:
                                            vocab_further.append(uri_label)
                                    element_data.vocab_further.uri_labels = vocab_further

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
                    if feed_index >= self.organise.max_pagination:
                        logger.error('Maximum number of paginated feeds reached, i.e., ' + str(self.organise.max_pagination))
                else:
                    break

        # Remove content of unpack folder
        remove_folder(feed_file.unpack, True)

        # Compile outputs, task delayed to prevent memory issues during long harvests
        if self.organise.elements and 'beacon' in self.organise.output:
            status.done()
            status = Progress('Saving compiled Beacon-like list', self.organise.quiet)
            combine_text(self.organise.folder_beacon, self.organise.folder + '/beacon', 'txt', '#')
            remove_folder(self.organise.folder_beacon)
        if self.organise.elements and 'csv' in self.organise.output:
            status.done()
            status = Progress('Saving compiled CSV table', self.organise.quiet)
            combine_text(self.organise.folder_csv, self.organise.folder + '/table', 'csv', '"feed_uri","element_uri","element_uri_same"')
            remove_folder(self.organise.folder_csv)
        if self.organise.elements and 'cto' in self.organise.output:
            status.done()
            status = Progress('Saving compiled nfdicore/cto triples', self.organise.quiet)
            combine_triples(self.organise.folder_cto, self.organise.folder + '/cto')
            remove_folder(self.organise.folder_cto)
        if 'triples' in self.organise.output:
            status.done()
            status = Progress('Saving compiled triples', self.organise.quiet)
            combine_triples(self.organise.folder_triples, self.organise.folder + '/triples')
            remove_folder(self.organise.folder_triples)
        logger.info('Cleaned up working folder')

        # Save look-up file
        status.done()
        status = Progress('Saving look-up file', self.organise.quiet)
        self.lookup.save()
        status.done()

        # Show log report
        self.status.append(status_feed)
        self.status.append(status_elements)
        self.status_report()


    def status_report(self):
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


class Progress:


    def __init__(self, note:str, quiet:bool = False):
        '''
        Show progress information during a job

            Parameters:
                note (str): Note to show the user
        '''

        # Vars
        self.success:bool = False
        self.quiet:bool = quiet
        self.note:str = note + '… '

        # Show note
        if not self.quiet:
            print('▹ ' + self.note, end = '\r')


    def update(self, current:int, max:int):
        '''
        Update progress line with percentage

            Parameters:
                current (int): Current number used to calculate a percentage
                max (int): Total number used to calculate a percentage
        '''

        # Calculate percentage
        if current < max:
            progress = int((current / max ) * 100)

            # Show note
            if not self.quiet:
                print('▹ ' + self.note + f"{progress:02}" + '%', end = '\r')

        else:
            self.done()


    def done(self):
        '''
        End progress line when complete
        '''

        # Show note
        if not self.success:
            self.success = True
            if not self.quiet:
                print('▸ ' + self.note + 'done')


def combine_text(folder:str, file_path:str, file_extension:str, ignore:str):
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
    paths = files_in_folder(folder)

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


def combine_triples(folder:str, file_path:str):
    '''
    Parses all Turtle files in a folder and saves them as a single file

        Parameters:
            folder (str): Path of the folder to parse
            file_path (str): Path of the file to create
    '''

    # Prepare paths
    file_path += '.ttl'
    paths = files_in_folder(folder)

    # Calculate size of folder
    folder_size = 0
    for path in paths:
        folder_size += getsize(path)

    # Parse and save using pyoxigraph (quick and dirty, JSON-LD not supported)
    if folder_size >= 50000000: # 50 MB
        rdf = Store()
        for path in paths:
            rdf.load(path = path, format = RdfFormat.TURTLE, to_graph = DefaultGraph())
        rdf.dump(output = file_path, format = RdfFormat.TURTLE, from_graph = DefaultGraph())

    # Parse and save using rdflib (slow and pretty, hogs more memory)
    else:
        rdf = Graph()
        rdf.bind('schema', SCHEMA, replace = True) # "Replace" overrides the RDFLib schema namespace (SDO), which uses "https"
        for path in paths:
            rdf.parse(path, format = 'turtle')
        rdf.serialize(destination = file_path, format = 'turtle')

    # Log info
    logger.info('Combined temporary RDF files into ' + file_path)
