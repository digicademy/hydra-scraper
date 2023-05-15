# Hydra API Class for Scraping Runs
# Copyright (c) 2023 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# MIT License


# Import script modules
from helpers.download import download_file
from helpers.fileio import save_file
from helpers.fileio import save_list
from helpers.status import echo_progress
from math import ceil
from rdflib import Graph


# Base class for any hydra API
class Hydra:


    # Variables
    url = ''
    folder = ''
    list_file_path = ''
    number_of_resources = 0
    resources_per_list = 0
    number_of_lists = 0
    next_url = ''
    final_url = ''
    resources = []
    done = None


    def __init__( self, url:str, folder:str, list_file_path:str = '' ):
        '''
        Sets up a hydra entry point

            Parameters:
                url (str): URL to use as a starting point for a scraping run
                folder (str): Folder beneath 'downloads' to download (paginated) lists to
                list_file_path (str): Path to a beacon file to create and fill with individual resource URLs
        '''

        # Assign variables
        self.url = url
        self.folder = folder
        self.list_file_path = list_file_path
        self.next_url = url


    def __str__( self ):
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


    def __download_list( self, number:int, url:str ) -> str:
        '''
        Downloads an individual list and processes its content

            Parameters:
                number (int): Number of this list file
                url (str): URL of the list to download

            Returns:
                str: URL of the next file to download
        '''

        # Retrieve and save the file
        hydra = download_file( url )
        if hydra != None:
            file_path = 'downloads/' + self.folder + '/hydra/' + str( number ) + '.' + hydra['file_extension']
            save_file( hydra['content'], file_path )

        # Parse the file's content (a second request is initiated here to benefit
        # from content-type headers not available in the text strings saved above)
        rdf = Graph()
        rdf.parse( url )

        # Optionally retrieve each individual resource URL
        if self.list_file_path != '':
            list_query = '''PREFIX hydra: <http://www.w3.org/ns/hydra/core#> SELECT * WHERE { ?subject hydra:member ?object . }'''
            list_triples = rdf.query( list_query )
            if len( list_triples ) == 0:
                list_query = '''PREFIX schema: <http://schema.org/> SELECT * WHERE { ?subject schema:item ?object . }'''
                list_triples = rdf.query( list_query )
            if len( list_triples ) > 0:
                for list_triple in list_triples:
                    self.resources.append( list_triple.object )

        # Retrieve the URL of the next list to see if the file is paginated
        next_query = '''PREFIX hydra: <http://www.w3.org/ns/hydra/core#> SELECT * WHERE { ?subject hydra:next ?object . } LIMIT 1'''
        next_triples = rdf.query( next_query )
        if len( next_triples ) >= 1:

            # Get total number of resources
            total_query = '''PREFIX hydra: <http://www.w3.org/ns/hydra/core#> SELECT * WHERE { ?subject hydra:totalItems ?object . } LIMIT 1'''
            total_triples = rdf.query( total_query )
            if len( total_triples ) >= 1:
                self.number_of_resources = total_triples[0].object
            
            # Get number of items per list and number of lists using hydra:member or schema:DataFeedItem
            resources_query = '''PREFIX hydra: <http://www.w3.org/ns/hydra/core#> SELECT * WHERE { ?subject hydra:member ?object . }'''
            resources_triples = rdf.query( resources_query )
            self.resources_per_list = len( resources_triples )
            if self.resources_per_list == 0:
                resources_query = '''PREFIX schema: <http://schema.org/> SELECT * WHERE { ?subject schema:DataFeedItem ?object . }'''
                resources_triples = rdf.query( resources_query )
                self.resources_per_list = len( resources_triples )
            if self.number_of_resources > 0 and self.resources_per_list > 0:
                self.number_of_lists = ceil( self.number_of_resources / self.resources_per_list )

            # Return the next list URL
            return next_triples[0].object
        
        # Return blank value if the file is not paginated
        else:
            return None


    def download( self ):
        '''
        Downloads all lists in the hydra API
        '''

        # Progress indicator
        index = 0
        echo_progress( 'Retrieving paginated lists', index, self.number_of_lists )

        # Retrieve each list file
        while self.next_url != self.final_url:
            index += 1
            self.next_url = self.__download_list( index, self.next_url )

        # Retrieve the penultimate and the final lists
        index += 1
        self.__download_list( index, self.next_url )
        index += 1
        self.__download_list( index, self.final_url )

        # Optionally save the resource list to a beacon file
        if self.list_file_path != '' and self.resources != []:
            file_path = 'downloads/' + self.folder + '/' + self.list_file_path
            save_list( file_path, self.resources )
