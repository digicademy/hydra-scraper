# Beacon file class for scraping runs
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import script modules
from classes.resource import *
from helpers.fileio import read_list
from helpers.status import echo_note
from helpers.status import echo_progress


# Base class for any beacon file
class Beacon:


    # Variables
    file_path = ''
    folder = ''
    replace = ''
    replace_with = ''
    clean_names = []
    done = None


    def __init__( self, file_path:str, folder:str, replace:str, replace_with:str, clean_names:list = [] ):
        '''
        Sets up a beacon file

            Parameters:
                file_path (str): Path to the beacon file
                folder (str): Folder beneath 'downloads' to download individual resources to
                replace (str): String to replace in listed URLs before downloading the resource
                replace_with (str): String to use as a replacement for the previous argument
                clean_names (list, optional): List of substrings to remove in the final URLs to result in a resource's file name
        '''

        # Assign variables
        self.file_path = file_path
        self.folder = folder
        self.replace = replace
        self.replace_with = replace_with
        self.clean_names = clean_names


    def __str__( self ):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if self.done == None:
            return 'Beacon file to be read at ' + self.file_path
        elif self.done == False:
            return 'Beacon file at ' + self.file_path + ' being processed'
        elif self.done == True:
            return 'Processed beacon file from ' + self.file_path


    def __list_resources( self ):
        '''
        Generates a list of individual resources from a beacon file
        '''

        # Get file content and check each entry
        resources = read_list( self.file_path )
        if resources != []:
            for resource in resources:

                # Replace string if requested
                if self.replace != '':
                    resource = resource.replace( self.replace, self.replace_with )

        # Return the list
        return resources


    def download( self ):
        '''
        Downloads each resource listed in the beacon file
        '''

        # Get list of resource
        resources = self.__list_resources()
        if resources != None:
            self.done = False

            # Download each resource and show progress
            if resources != []:
                for index, resource in enumerate(resources, start = 1):
                    echo_progress( 'Downloading files listed in the beacon', index, len( resources ) )
                    resource_object = Resource( index, resource, self.folder, self.clean_names )
                    resource_object.download()

            else:
                echo_note( 'No files listed in the beacon' )

            # Report new status
            self.done = True

        # Raise an error if the file
        else:
            raise FileNotFoundError( 'The requested beacon file is not available' )
