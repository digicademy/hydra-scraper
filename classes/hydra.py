# Hydra API Class for Scraping Runs
# Copyright (c) 2023 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# MIT License


# Import script modules
from helpers.fileio import save_list


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


    def __download_list( self, url:str ) -> str:
        '''
        Downloads an individual list and processes its content

            Parameters:
                url (str): URL of the list to download

            Returns:
                str: URL of the next file to download
        '''

        # TODO Retrieve and save the file

        # TODO Parse the file's content

        # TODO Crunch the numbers (resources, per list, lists)

        # TODO Optionally retrieve each individual resource URL
        #if self.list_file_path != '':
            #resource = 'Testing'
            #self.resources.append( resource )

        # TODO Retrieve the URL of the next list and return it (but only change values if they are available)


    def download( self ):
        '''
        Downloads all lists in the hydra API
        '''

        # TODO Add progress indicator

        # Retrieve each list file
        while self.next_url != self.final_url:
            self.next_url = self.__download_list( self.next_url )

        # Retrieve the penultimate and the final lists
        self.__download_list( self.next_url )
        self.__download_list( self.final_url )

        # Optionally save the resource list to a beacon file
        if self.list_file_path != '' and self.resources != []:
            save_list( self.list_file_path, self.resources )
