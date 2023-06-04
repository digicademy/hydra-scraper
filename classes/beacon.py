# Class to manage scraping a beacon list of resources
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import script modules
from helpers.config import *
from helpers.download import download_file
from helpers.fileio import read_list
from helpers.fileio import save_file
from helpers.status import echo_note
from helpers.status import echo_progress
from time import sleep


# Base class for a beacon list to process
class Beacon:


    # Variables
    file_path = ''
    folder = ''
    replace = ''
    replace_with = ''
    add = ''
    clean_names = []
    resources = []
    number_of_resources = 0
    missing_resources = 0
    done = None


    def __init__(self, file_path:str, folder:str, replace:str = '', replace_with:str = '', add:str = '', clean_names:list = []):
        '''
        Sets up a beacon list to process

            Parameters:
                file_path (str): Path to the beacon file
                folder (str): Name of the downloads subfolder to store individual resources at
                replace (str, optional): String to replace in listed URLs before downloading a resource
                replace_with (str, optional): String to use as a replacement before downloading a resource
                add (str, optional): String to add to each URL before downloading a resource
                clean_names (list, optional): List of substrings to remove in the final URLs to result in a resource's file name
        '''

        # Assign variables
        self.file_path = file_path
        self.folder = folder
        self.replace = replace
        self.replace_with = replace_with
        self.add = add
        self.clean_names = clean_names


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if self.done == None:
            return 'Beacon list to be read at ' + self.file_path
        elif self.done == False:
            return 'Beacon list at ' + self.file_path + ' being processed'
        elif self.done == True:
            return 'Processed beacon list from ' + self.file_path


    def __list_resources(self):
        '''
        Generates a Python list of individual resources from a beacon file
        '''

        # Get file content and check each entry
        resources = read_list(self.file_path)
        revised_resources = []
        if resources != None:
            for resource in resources:

                # Replace string if requested
                if self.replace != '':
                    resource = resource.replace(self.replace, self.replace_with)

                # Add string if requested
                if self.add != '':
                    resource = resource + self.add

                revised_resources.append(resource)

            # Save number of resources
            self.number_of_resources = len(revised_resources)

        # Save list
        self.resources = revised_resources
    

    def __download_resource(self, number:int, url:str):
        '''
        Downloads an individual resource

            Parameters:
                number (int): Index number of the resource to download
                url (str): URL of the resource to download
        '''

        # Construct file name as number or as cleaned-up URL if requested
        if self.clean_names == []:
            file_name = str(number)
        else:
            file_name = url
            for clean_name in self.clean_names:
                file_name = file_name.replace(clean_name, '')

        # Download resource
        download = download_file(url)
        if download != None:

            # Set file path accordingly
            file_extension = download['file_extension']
            file_path = config['download_base'] + '/' + self.folder + '/resources/' + file_name + '.' + file_extension

            # Save file
            save_file(download['content'], file_path)

        # Report if download failed
        else:
            self.missing_resources += 1

        # Display progress indicator and add delay to avoid getting blocked be server
        echo_progress('Downloading resources from the list', number, self.number_of_resources)
        sleep(config['download_delay'])


    def process(self):
        '''
        Downloads each resource from the beacon list
        '''

        # Get list of resources
        self.__list_resources()
        if self.resources != None and self.resources != []:
            self.done = False

            # Provide initial status
            echo_progress('Downloading resources from the list', 0, 100)

            # Download each resource
            for index, resource in enumerate(self.resources, start = 1):
                self.__download_resource(index, resource)

            # Report new status as...
            if self.missing_resources > 0:

                # ...failed
                if self.missing_resources >= self.number_of_resources:
                    raise FileNotFoundError('All resources listed in the beacon were missing.')
                
                # ...successful with exceptions
                else:
                    self.done = True
                    echo_note('\nDone! Resources saved to the download folder, but ' + str(self.missing_resources) + ' were missing.\n')

            # ...successful
            else:
                self.done = True
                echo_note('\nDone! All resources saved to the download folder.\n')

        # Throw error if beacon file is empty
        elif self.resources == []:
            raise ValueError('The beacon list is empty.')

        # Throw error if beacon file could not be read
        else:
            raise FileNotFoundError('The beacon list is not available.')
