# Individual Resource Class for Scraping Runs
# Copyright (c) 2023 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# MIT License


# Import script modules
from helpers.download import download_file
from helpers.fileio import save_file


# Base class for any individual resource
class Resource:


    # Variables
    number = 0
    url = ''
    folder = ''
    clean_names = ''
    file_name = ''
    file_extension = 'txt'
    file_path = ''
    success = None


    def __init__( self, number:int, url:str, folder:str, clean_names:list = [] ):
        '''
        Sets up an individual resource

            Parameters:
                number (int): Number of this resource in a list of resources
                url (str): URL to retrieve this resource from
                folder (str): Folder beneath 'downloads' to download this resource to
                clean_names (list, optional): List of substrings to remove in the final URL to result in the resource's file name
        '''

        # Assign variables
        self.number = number
        self.url = url
        self.folder = folder
        self.clean_names = clean_names

        # Construct file name
        if clean_names == []:
            self.file_name = str( self.number )
        else:
            new_file_name = self.url
            for clean_name in self.clean_names:
                new_file_name = new_file_name.replace( clean_name, '' )
            self.file_name = new_file_name


    def __str__( self ) -> str:
        '''
        String representation of instances of this object
        
            Returns:
                str: String describing the object
        '''

        # Put together a string
        if self.success == None:
            return 'Individual file to download from ' + self.url
        elif self.success == False:
            return 'Individual file unavailable from ' + self.url
        elif self.success == True:
            return 'Individual file downloaded to ' + self.file_path


    def download( self ):
        '''
        Downloads the individual resource
        '''

        # Try to download the resource
        download = download_file( self.url )
        if download != None:

            # Set object variables accordingly
            self.file_extension = download['file_extension']
            self.file_path = 'downloads/' + self.folder + '/resources/' + self.file_name + '.' + self.file_extension
            self.success = True

            # Save file
            save_file( download['content'], self.file_path )

        # Report if the download failed
        else:
            self.success = False