# Classes to morph and save data
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Graph, Namespace
from rdflib.term import BNode, Literal, URIRef

# Import script modules
from classes.base import HyBase
from extraction import lido, schema
from mapping import cto

# Define namespaces
from rdflib.namespace import RDF
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')


class HyMorph(HyBase):

    # Vars
    store = None
    files = None
    folder = None
    folder_files = None
    is_nfdi = False


    def __init__(self, files:list, folder:str, folder_files:str, quiet:bool = False):
        '''
        Base class to morph and save data

            Parameters:
                files (list): List of files to morph
                folder (str): Path of the folder where serialised data should be stored
                folder_files (str): Path of the subfolder where downloaded files are stored
                quiet (bool): Avoid intermediate progress reports
        '''

        # Inherit from base class
        super().__init__(quiet)

        # Assign arguments to object
        self.files = files
        self.folder = folder
        self.folder_files = folder_files


    def save_triples(self, file_name:str = 'triples.ttl', progress_message:str = 'Saving triples'):
        '''
        Save triples to file

            Parameters:
                file_name (list): File name to use
                progress_message (list): Message to show to users
        '''

        # Provide initial status
        self.echo_progress(progress_message, 0, 100)
        status = {
            'success': False,
            'reason': ''
        }

        # Check if there is data to save
        if self.store == None:
            status['reason'] = 'No triples to save.'
        else:

            # Save file
            file_path = self.folder + '/' + file_name
            self.store.serialize(destination = file_path, format = 'turtle')
            status['success'] = True
            status['reason'] = 'Triples saved to file.'

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


    def save_triples_nfdi(self, add_feed:str = None, add_catalog:str = None, add_publisher:str = None, prepare:bool = False, source:str = None, file_name:str = 'triples_nfdi.ttl', progress_message:str = 'Saving NFDI-style triples'):
        '''
        Save NFDI-style triples to file

            Parameters:
                prepare (bool): Add wrappers required for use in a larger knowledge graph
                file_name (list): File name to use
                progress_message (list): Message to show to users
        '''

        # Provide initial status
        self.echo_progress(progress_message, 0, 100)
        status = {
            'success': False,
            'reason': ''
        }

        # Check if there is data to morph
        if self.store == None:
            status['reason'] = 'No triples to transform to NFDI style.'
        else:

            # Use store if triples are NFDI-style already
            nfdi = None
            if self.is_nfdi:
                nfdi = self.store
            else:

                # Set up NFDI-style feed
                data = schema.Feed(self.store)
                if data.success:
                    feed = cto.Feed(prepare = prepare)
                    if add_feed != None:
                        feed.feed_uri = add_feed
                    if add_catalog != None:
                        feed.catalog_uri = add_catalog

                    # Set up NFDI-style elements
                    elements = []
                    for element_uri in data.list_of_elements:
                        element_data = schema.FeedElement(self.store, data.feed_uri, element_uri)
                        if element_data.success == True:
                            if source != None:
                                element_data.source_file = source
                            element = cto.FeedElement(element_data, prepare)
                            if add_publisher != None:
                                element.publisher = add_publisher
                            elements.append(element)
                    feed.elements = elements

                    # Generate NFDI-style triples
                    nfdi = feed.generate()

            # Check if there is NFDI-style data
            if not nfdi:
                status['reason'] = 'No NFDI-style data available.'
            else:

                # Save file
                file_path = self.folder + '/' + file_name
                nfdi.serialize(destination = file_path, format = 'turtle')
                status['success'] = True
                status['reason'] = 'NFDI-style triples saved to file.'

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


    def save_csv(self, table:list = None, file_name:str = 'table.csv', progress_message:str = 'Saving a CSV file'):
        '''
        Save tabular CSV to file

            Parameters:
                table (list): List of predicates to include
                file_name (list): File name to use
                progress_message (list): Message to show to users
        '''

        # Provide initial status
        self.echo_progress(progress_message, 0, 100)
        status = {
            'success': False,
            'reason': ''
        }

        # Check if there is data to morph
        if self.store == None:
            status['reason'] = 'No triples to transform to CSV.'
        else:

            # Produce CSV content
            csv = self.__morph_store_to_csv(table)
            if csv == None:
                status['reason'] = 'No CSV data available.'
            else:

                # Save file
                file_path = self.folder + '/' + file_name
                self.__save_file(csv, file_path)
                status['success'] = True
                status['reason'] = 'CSV data saved to file.'

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


    def __morph_store_to_csv(self, table:list = None) -> str|None:
        '''
        Converts triples to CSV data

            Parameters:
                table (list): List of predicates to include

            Returns:
                str: Content as CSV
        '''

        # Set up output
        csv = ''
        output = []
        predicates = []

        # Collect desired predicates
        all_predicates = list(self.store.predicates(None, None, True))
        if table != None:
            for table_column in table:
                if URIRef(table_column) in all_predicates:
                    predicates.append(URIRef(table_column))
        else:
            predicates = all_predicates
            predicates.sort()

        # List predicates as table header
        header = ['URI']
        for predicate in predicates:
            header.append(str(predicate))
        output.append(header)

        # Get unique entities used as subjects
        entities = list(self.store.subjects(unique = True))
        entities.sort()
        for entity in entities:
            if isinstance(entity, URIRef):
                table_row = [str(entity)]

                # Set up a query routine for each desired predicate
                for predicate in predicates:
                    table_row_columns = []

                    # Find triples with this subject and predicate and add their Literal/URIRef objects to the current table row
                    # Repeated for three levels to also find nested predicates plus an exception for lists, i.e., BNodes

                    # Main property, level 1
                    for o1 in self.store.objects((entity, predicate, None)):
                        if isinstance(o1, (Literal, URIRef)):
                            table_row_columns.append(self.__strip_string(str(o1)))

                        # List, multiple levels
                        elif isinstance(o1, BNode):
                            table_row_columns.extend(self.__morph_store_to_csv_list(o1))

                        # Nested property, level 2
                        else:
                            for o2 in self.store.objects((o1, predicate, None)):
                                if isinstance(o2, (Literal, URIRef)):
                                    table_row_columns.append(self.__strip_string(str(o2)))

                                # Nested property, level 3
                                else:
                                    for o3 in self.store.objects((o2, predicate, None)):
                                        if isinstance(o3, (Literal, URIRef)):
                                            table_row_columns.append(self.__strip_string(str(o3)))

                    # Produce entry for this predicate
                    table_row_column = ', '.join(table_row_columns)
                    table_row.append(table_row_column)

                # Add new line to output
                output.append(table_row)

            # Save tabular data
            for table_row in output:
                csv += '"' + '","'.join(table_row) + '"\n'

        # Return CSV
        if csv != '':
            return csv
        else:
            return None


    def __morph_store_to_csv_list(self, previous:BNode) -> list:
        '''
        Helper to go through lists when converting triples to CSV data

            Parameters:
                previous (BNode): Previous entry in the list

            Returns:
                list: Further entries of the list
        '''

        # Set up empty list
        entries = []

        # Dig one level further down the ordered list
        for entry in self.store.objects((previous, None)):
            if isinstance(entry, (Literal, URIRef)) and entry != URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil'):
                entries.append(self.__strip_string(str(entry)))

            # Keep digging if there is more
            elif isinstance(entry, BNode):
                entries.extend(self.__morph_store_to_csv_list(entry))

        # Return list
        return entries


class HyMorphRdf(HyMorph):


    def __init__(self, files:list, folder:str, folder_files:str, dialect:str = None, prepare:bool = False, quiet:bool = False, progress_message:str = 'Reading RDF data'):
        '''
        Class to morph and save RDF data

            Parameters:
                files (list): List of files to morph
                folder (str): Path of the folder where serialised data should be stored
                folder_files (str): Path of the subfolder where downloaded files are stored
                dialect (str): Content type to read
                prepare (bool): Add ingest-ready wrappers to NFDI-style triples
                quiet (bool): Avoid intermediate progress reports
                progress_message (str): Message to show to users
        '''

        # Inherit from base class
        super().__init__(files, folder, folder_files, quiet)

        # Provide initial status
        self.echo_progress(progress_message, 0, 100)
        status = {
            'success': False,
            'reason': ''
        }

        # Set up variables
        number_of_files = len(self.files)
        incompatible_files = []
        
        # Check if there are files to read
        if number_of_files == 0:
            status['reason'] = 'There were no RDF files to read.'
        else:

            # Loop to read files
            for number, file in enumerate(self.files, start = 1):

                # Retrieve file
                file_data = self.__local_file(file, dialect)
                if file_data != None:
                    status['success'] = True
                    status['reason'] = 'All files read successfully.'

                    # Parse RDF and gather triples
                    try:
                        store = Graph()
                        store.parse(data = file_data['content'], format = file_data['file_type'])
                    except:
                        incompatible_files.append(file)
                        continue

                    # Remove pagination triples
                    store.remove((None, HYDRA.totalItems, None))
                    store.remove((None, HYDRA.view, None))
                    store.remove((None, HYDRA.first, None))
                    store.remove((None, HYDRA.last, None))
                    store.remove((None, HYDRA.next, None))
                    store.remove((None, HYDRA.previous, None))
                    store.remove((None, RDF.type, HYDRA.PartialCollectionView))

                    # Add file triples to object store
                    self.store += store

                # Report progress
                self.echo_progress(progress_message, number, number_of_files)

            # Report any failed state
            if len(incompatible_files) >= number_of_files:
                status['success'] = False
                status['reason'] = 'All files were incompatibile.'
                status['incompatible'] = incompatible_files
            elif len(incompatible_files) > 0:
                status['success'] = False
                status['reason'] = 'Files read, but ' + str(len(incompatible_files)) + ' were not compatible.'
                status['incompatible'] = incompatible_files

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


class HyMorphXml(HyMorph):


    def __init__(self, files:list, markup:str, folder:str, folder_files:str, dialect:str = None, prepare:bool = False, add_feed:str = None, add_catalog:str = None, add_publisher:str = None, quiet:bool = False, progress_message:str = 'Reading XML data'):
        '''
        Class to morph and save XML data

            Parameters:
                files (list): List of files to morph
                markup (str): Type of file markup to process
                folder (str): Path of the folder where serialised data should be stored
                folder_files (str): Path of the subfolder where downloaded files are stored
                dialect (str): Content type to read
                prepare (bool): Add ingest-ready wrappers to NFDI-style triples
                quiet (bool): Avoid intermediate progress reports
                progress_message (str): Message to show to users
        '''

        # Inherit from base class
        super().__init__(files, folder, folder_files, quiet)

        # Provide initial status
        self.echo_progress(progress_message, 0, 100)
        status = {
            'success': False,
            'reason': ''
        }

        # Set up variables
        number_of_files = len(self.files)
        incompatible_files = []
        
        # Check if there are files to read
        if number_of_files == 0:
            status['reason'] = 'There were no XML files to read.'
        else:

            # Loop to read files
            elements = []
            for number, file in enumerate(self.files, start = 1):

                # Retrieve file
                file_data = self.__local_file(file, dialect)
                if file_data != None:
                    status['success'] = True
                    status['reason'] = 'All files read successfully.'

                    # Parse XML
                    if markup == 'lido':
                        data = lido.FeedElement(file_data['content'])
                    # TODO Implement TEI functionality
                    elif markup == 'tei':
                        raise NotImplementedError('TEI morph functionality is not available in Hydra Scraper yet.')
                    # TODO Implement MEI functionality
                    elif markup == 'mei':
                        raise NotImplementedError('MEI morph functionality is not available in Hydra Scraper yet.')

                    # Report if unknown markup was requested
                    else:
                        incompatible_files.append(file)
                        continue

                    # Add data to list of feed elements
                    if data.success == True:
                        start_of_file_name = file.rindex('/') + 1
                        data.source_file = file[start_of_file_name:]
                        element = cto.FeedElement(data, prepare)
                        if add_publisher != None:
                            element.publisher = add_publisher
                        elements.append(element)
                    
                    # Report files that could not be parsed
                    else:
                        incompatible_files.append(file)
                        continue

                # Report progress
                self.echo_progress(progress_message, number, number_of_files)

            # Create NFDI-style triples in object store
            feed = cto.Feed(prepare = prepare)
            feed.elements = elements
            if add_feed != None:
                feed.feed_uri = add_feed
            if add_catalog != None:
                feed.catalog_uri = add_catalog

            # Serialise
            self.store = feed.generate()
            self.is_nfdi = True

            # Report any failed state
            if len(incompatible_files) >= number_of_files:
                status['success'] = False
                status['reason'] = 'All files were incompatibile.'
                status['incompatible'] = incompatible_files
            elif len(incompatible_files) > 0:
                status['success'] = False
                status['reason'] = 'Files read, but ' + str(len(incompatible_files)) + ' were not compatible.'
                status['incompatible'] = incompatible_files

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


class HyMorphTabular(HyMorph):


    def __init__(self, files:list, folder:str, folder_files:str, quiet:bool = False, progress_message:str = 'Reading tabular data'):
        '''
        Class to morph and save tabular data

            Parameters:
                files (list): List of files to morph
                folder (str): Path of the folder where serialised data should be stored
                folder_files (str): Path of the subfolder where downloaded files are stored
                quiet (bool): Avoid intermediate progress reports
                progress_message (str): Message to show to users
        '''

        # Inherit from base class
        super().__init__(files, folder, folder_files, quiet)

        # TODO Implement CSV functionality
        raise NotImplementedError('CSV morph functionality is not available in Hydra Scraper yet.')
