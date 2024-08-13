# Classes to retrieve and save data
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from glob import glob
from math import ceil
from rdflib import Graph, Namespace
from re import search
from shutil import rmtree
from time import sleep
from urllib import request
from validators import url

# Import script modules
from classes.base import HyBase

# Define namespaces
from rdflib.namespace import SDO
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
SCHEMA = Namespace('http://schema.org/')


class HyRetrieve(HyBase):

    # Vars
    feed = []
    local = []
    folder = None
    folder_files = None
    file_type = None


    def __init__(self, location:str, folder:str, folder_files:str, quiet:bool = False):
        '''
        Base class to retrieve and save data

            Parameters:
                location (str): URL or file path to start a scraping run with
                folder (str): Path of the folder to save downloaded data to
                folder_files (str): Path of the subfolder to save downloaded files to
                quiet (bool): Avoid intermediate progress reports
        '''

        # Inherit from base class
        super().__init__(quiet)

        # Assign arguments to object
        self.location = location
        self.folder = folder
        self.folder_files = folder_files


    def save_beacon(self):
        '''
        Save the feed list as a Beacon file
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': 'No resource URLs to list in Beacon file.'
        }

        # Indicate progress
        progress_message = 'Saving Beacon file'
        self.echo_progress(progress_message, 0, 100)
        
        # Check if there is data to save
        if self.feed != []:
            status['success'] = True
            status['reason'] = 'Beacon file saved.'

            # Convert lines to file content
            content = ["{}\n".format(line) for line in self.feed]
            file_path = self.folder + '/' + 'beacon.txt'
            self.__save_file(content, file_path)

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


    def remove_downloads(self):
        '''
        Delete all downloaded files and the respective folder
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Indicate progress
        progress_message = 'Removing intermediate files'
        self.echo_progress(progress_message, 0, 100)

        # Remove file download folder
        try:
            rmtree(self.folder_files)
            status['success'] = True
            status['reason'] = 'Intermediate files removed.'
        except:
            status['reason'] = 'Intermediate files could not be removed.'

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


    def download_feed(self, delay:float, dialect:str = None, clean:list = None):
        '''
        Retrieves all remote resources and populates the triple store

            Parameters:
                delay (float): Delay between requests
                dialect (str): Content type to request
                clean (list): List of strings to remove from a file URL to build its file name
        '''

        # Continue only when feed is populated but there are no downloaded files
        missing_files = []
        number_of_files = len(self.feed)
        if number_of_files > 0 and len(self.local) == 0:

            # Provide initial status
            status = {
                'success': False,
                'reason': ''
            }

            # Indicate progress
            progress_message = 'Downloading files'
            self.echo_progress(progress_message, 0, 100)

            # Loop to retrieve files
            for number, file_url in enumerate(self.feed, start = 1):

                # Retrieve file
                file_data = self.__download_file(file_url, dialect)
                if file_data != None:

                    # Optionally clean file name
                    if clean != None:
                        file_name = file_url
                        for clean_item in clean:
                            file_name = file_name.replace(clean_item, '')
                    else:
                        file_name = str(number)

                    # Save file
                    file_path = self.folder_files + '/' + file_name + '.' + file_data['file_extension']
                    self.__save_file(file_data['content'], file_path)
                    self.file_type = file_data['file_type']
                    status['success'] = True
                    status['reason'] = 'All files downloaded successfully.'

                # Report if download failed
                else:
                    missing_files.append(file_url)
                    continue

                # Delay next retrieval to avoid server block
                self.echo_progress(progress_message, number, number_of_files)
                sleep(delay)

            # Report any failed state
            if len(missing_files) >= number_of_files:
                status['success'] = False
                status['reason'] = 'All files were missing.'
            elif missing_files > 0:
                status['success'] = False
                status['reason'] = 'Files downloaded, but ' + str(len(missing_files)) + ' were missing.'
                status['missing'] = missing_files
        
        # Read local folder
        self.local = self.__read_folder(self.folder_files)

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


    def __read_folder(self, folder_path:str) -> list:
        '''
        Read a local folder and return a list of resources

            Parameters:
                folder_path (str): Path to the folder to read
        '''

        # Prepare folder path
        folder_path += '/**/*'
        entries = []

        # Add each file to list
        for entry in glob(folder_path, recursive = True):
            entries.append(entry)

        # Return entries
        return entries


class HyRetrieveApi(HyRetrieve):


    def __init__(self, start:str, markup:str, location:str, folder:str, folder_files:str, delay:float, max_pagination:int, dialect:str = None, quiet:bool = False):
        '''
        Class to retrieve and save API data

            Parameters:
                start (str): Type of starting point to use
                markup (str): Type of file markup to process
                location (str): URL or file path to start a scraping run with
                folder (str): Path of the folder to save downloaded data to
                folder_files (str): Path of the subfolder to save downloaded files to
                delay (float): Delay between requests
                max_pagination (int): Maximum number of feed lists to retrieve
                dialect (str): Content type to request
                quiet (bool): Avoid intermediate progress reports
        '''

        # Inherit from base class
        super().__init__(location, folder, folder_files, quiet)

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Indicate progress
        progress_message = 'Reading an API endpoint'
        self.echo_progress(progress_message, 0, 100)
        
        # API pagination properties
        current_list = self.location
        next_list = ''
        final_list = ''
        number_of_resources = 0
        resources_per_list = 0
        number_of_lists = 0
        number = 0

        # Loop for paginated feeds
        while current_list != final_list:
            number += 1

            # Retrieve a single feed
            if url(next_list):
                list_data = self.__download_file(next_list, dialect)
            else:
                list_data = self.__local_file(next_list, dialect)
            if list_data != None:

                # Optionally save feed file
                if markup == 'feed':
                    file_path = self.folder_files + '/' + str(number) + '.' + list_data['file_extension']
                    self.__save_file(list_data['content'], file_path)
                    self.file_type = list_data['file_type']
                    status['success'] = True
                    status['reason'] = 'Feed downloaded successfully.'
                
                # Alternatively provide more generic info
                else:
                    status['success'] = True
                    status['reason'] = 'Feed retrieved successfully.'

            # End loop if list file is missing
            else:
                status['success'] = False
                status['reason'] = 'One page of the feed was not available.'
                break

            # Parse RDF feed
            if start == 'rdf-feed':
                try:
                    store = Graph()
                    store.parse(data=list_data['content'], format=list_data['file_type'])

                # End loop if RDF cannot be parsed
                except:
                    status['success'] = False
                    status['reason'] = 'The feed could not be parsed as RDF.'
                    break

                # Add feed elements to list
                for o in store.objects(None, HYDRA.member, True):
                    self.feed.append(str(o))
                for o in store.objects(None, SDO.item, True):
                    self.feed.append(str(o))
                for o in store.objects(None, SCHEMA.item, True):
                    self.feed.append(str(o))

                # Remove duplicates
                self.feed = list(set(self.feed))

                # Get URLs of current, next, and final lists
                for o in store.objects(None, HYDRA.view, True):
                    current_list = str(o)
                for o in store.objects(None, HYDRA.next, True):
                    next_list = str(o)
                for o in store.objects(None, HYDRA.last, True):
                    final_list = str(o)

                # Get total number of resources
                for o in store.objects(None, HYDRA.totalItems, True):
                    number_of_resources = int(o)

            # TODO Parse XML feed
            elif start == 'xml-feed':
                raise NotImplementedError('XML feed functionality is not available in Hydra Scraper yet.')
                # self.file_type = 
                # self.feed.append()
                # current_list = 
                # next_list = 
                # final_list = 
                # number_of_resources = 

            # On first page, calculate total number of items and lists
            if number == 1:
                if len(self.feed) != 0:
                    resources_per_list = len(self.feed)
                    number_of_lists = int(ceil(number_of_resources / resources_per_list))
                else:
                    status['success'] = False
                    status['reason'] = 'The feed does not contain any resources.'
                    break

            # End loop if API is paginated without a final list
            if next_list != '' and final_list == '':
                status['success'] = False
                status['reason'] = 'The feed is paginated but does not specify a final list.'
                break

            # Delay next retrieval to avoid server block
            self.echo_progress(progress_message, number, number_of_lists)
            sleep(delay)

            # End loop if there is no next page
            if next_list == '':
                break

            # End loop if maximum number of pages is reached
            if number > max_pagination:
                status['success'] = False
                status['reason'] = 'Maximum number of allowed feed pages was reached.'
                break
        
        # Read local folder
        if markup == 'feed':
            self.local = self.__read_folder(self.folder_files)

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


class HyRetrieveFiles(HyRetrieve):


    def __init__(self, start:str, location:str, folder:str, folder_files:str, quiet:bool = False):
        '''
        Class to retrieve and save file-list data

            Parameters:
                start (str): Type of starting point to use
                location (str): URL or file path to start a scraping run with
                folder (str): Path of the folder to save downloaded data to
                folder_files (str): Path of the subfolder to save downloaded files to
                quiet (bool): Avoid intermediate progress reports
        '''

        # Inherit from base class
        super().__init__(location, folder, folder_files, quiet)

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Indicate progress
        progress_message = 'Reading a file list'
        self.echo_progress(progress_message, 0, 100)

        # Open Beacon file
        if start == 'beacon-feed':
            try:
                if url(self.location):
                    f = request.urlopen(url)
                    content = f.read().decode('utf-8')
                else:
                    f = open(location, 'r')
                    content = f.read()

                # Optionally identify an ID pattern
                pattern = search(r"(?<=#TARGET: ).*(?<!\n)", content)
                if pattern != None:
                    pattern = pattern.group()
                    if pattern.find('{ID}') == -1:
                        pattern = None

                # Clean empty lines and comments
                content = self.__strip_lines(content)
                lines = iter(content.splitlines())

                # In each line, remove additional Beacon features
                for line in lines:
                    line_option1 = line.find(' |')
                    line_option2 = line.find('|')
                    if line_option1 != -1:
                        line = line[:line_option1]
                    elif line_option2 != -1:
                        line = line[:line_option2]
                    
                    # Add complete line to list
                    if pattern != None:
                        line = pattern.replace('{ID}', line)
                    self.feed.append(line)

                # Read local folder
                self.local = self.__read_folder(self.folder_files)

                # Report success
                status['success'] = True
                status['reason'] = 'Beacon file read successfully.'

            # Do nothing if file not found
            except:
                status['reason'] = 'Beacon file could not be found.'

        # Read dump folder
        elif start == 'dump-folder':
            self.local = self.__read_folder(self.location)
            status['success'] = True
            status['reason'] = 'Folder content listed successfully.'

        # Update status
        self.echo_progress(progress_message, 100, 100)
        self.status.append(status)


class HyRetrieveSingle(HyRetrieve):


    def __init__(self, location:str, folder:str, folder_files:str, quiet:bool = False):
        '''
        Class to retrieve and save CSV data

            Parameters:
                location (str): URL or file path to start a scraping run with
                folder (str): Path of the folder to save downloaded data to
                folder_files (str): Path of the subfolder to save downloaded files to
                quiet (bool): Avoid intermediate progress reports
        '''

        # Inherit from base class
        super().__init__(location, folder, folder_files, quiet)

        # TODO Implement CSV functionality
        raise NotImplementedError('CSV retrieval functionality is not available in Hydra Scraper yet.')
