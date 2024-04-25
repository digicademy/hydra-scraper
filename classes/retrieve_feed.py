# Class to retrieve data feeds like beacon files or APIs
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from glob import glob
from math import ceil
from re import search
from rdflib import Graph, Namespace
from time import sleep

# Import script modules
from classes.retrieve import *

# Define namespaces
from rdflib.namespace import RDF, SDO
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')

class HydraRetrieveFeed(HydraRetrieve):

    # Variables
    feed = []
    feed_url = None
    feed_file = None
    store = None


    # READ ####################################################################


    def __init__(self, report:object, feed_file:str = None, feed_url:str = None, content_type:str = None, max_number_of_paginated_lists:int = 0, retrieval_delay:float = 0, download:bool = False, file_path:str = None):
        '''
        Retrieve data feeds like beacon files or APIs

            Parameters:
                report (object): The report object to use
                feed_file (str): Path to the file to read
                feed_url (str): URL of the endpoint API to read
                content_type (str): Content type to request
                max_number_of_paginated_lists (int): Allowed number of lists to retrieve
                retrieval_delay (float): Delay between requests
                download (bool): Whether to save individual list files or not
                file_path (str): Path to target folder if list files are to be saved
        '''

        # Inherit from base class
        super().__init__(report)

        # Assign argument to object
        self.feed_url = feed_url
        self.feed_file = feed_file

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Routine: beacon file
        if self.feed_file != None:
            progress_message = 'Reading a Beacon file'
            self.report.echo_progress(progress_message, 0, 100)
            status = self.__read_list(self.feed_file)
            self.report.echo_progress(progress_message, 100, 100)

        # Routine: endpoint URL
        elif self.feed_url != None:
            progress_message = 'Reading an endpoint URL'
            self.report.echo_progress(progress_message, 0, 100)
            status = self.__read_api(self.feed_url, content_type, max_number_of_paginated_lists, retrieval_delay, progress_message, download, file_path)
            self.report.echo_progress(progress_message, 100, 100)

        # Routine: error
        else:
            status['reason'] = 'Neither Beacon file nor endpoint URL given.'

        # Update status
        self.report.status.append(status)


    def __read_list(self, feed_file:str) -> dict:
        '''
        Read a list file and save each line in a list

            Parameters:
                feed_file (str): Path to the file to read

            Returns:
                dict: Status report
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': 'No resources listed in Beacon file.'
        }

        # Open file
        try:
            f = open(feed_file, 'r')
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

            # Go through each line
            entries = []
            for line in lines:

                # Remove additional Beacon features
                line_option1 = line.find(' |')
                line_option2 = line.find('|')
                if line_option1 != -1:
                    line = line[:line_option1]
                elif line_option2 != -1:
                    line = line[:line_option2]
                
                # Add complete line to list
                if pattern != None:
                    line = pattern.replace('{ID}', line)
                entries.append(line)

                # Report success
                status['success'] = True
                status['reason'] = 'Beacon file read successfully.'

            # Update list
            self.feed = entries

        # Do nothing if file not found
        except:
            status['reason'] = 'Beacon file was not found.'


    def __read_api(self, feed_url:str, content_type:str = None, max_number_of_paginated_lists:int = 0, retrieval_delay:float = 0, progress_message:str = '', download:bool = False, file_path:str = None) -> dict:
        '''
        Read an endpoint API and save both triples and individual resource URLs

            Parameters:
                feed_url (str): URL of the endpoint API to read
                content_type (str): Content type to request
                max_number_of_paginated_lists (int): Allowed number of lists to retrieve
                retrieval_delay (float): Delay between requests
                progress_message (str): Message to display while paging through lists
                download (bool): Whether to save individual list files or not
                file_path (str): Path to target folder if list files are to be saved

            Returns:
                dict: Status report
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Set up variables
        current_list = feed_url
        next_list = ''
        final_list = ''
        number_of_resources = 0
        resources_per_list = 0
        number_of_lists = 0
        number = 0

        # Main loop to retrieve lists
        while current_list != final_list:
            number += 1

            # Retrieve file
            list_data = self.__download_file(next_list, content_type)
            if list_data != None:

                # Optionally save file
                if download and file_path != None:
                    file_path += '/lists/' + str(number) + '.' + list_data['file_extension']
                    self.__save_file(list_data['content'], file_path)
                    status['success'] = True
                    status['reason'] = 'All lists downloaded successfully.'

            # Get out of loop if list file is missing
            else:
                status['success'] = False
                status['reason'] = 'One of the paginated lists was not available.'
                break

            # Parse file
            try:
                store_new = Graph()
                store_new.parse(data=list_data['content'], format=list_data['file_type'])
            except:
                status['success'] = False
                status['reason'] = 'The endpoint response could not be parsed as RDF-style data.'
                break

            # Add individual resource URLs to list
            for o in store_new.objects(None, HYDRA.member, True):
                self.feed.extend(o.toPython())
            for o in store_new.objects(None, SDO.item, True):
                self.feed.extend(o.toPython())

            # Get total number of items per list on first list
            if number == 1:
                if len(self.feed) != 0:
                    resources_per_list = len(self.feed)
                else:
                    status['success'] = False
                    status['reason'] = 'The endpoint does not contain any resources.'
                    break

            # Get URL of current, next, and final list
            for o in store_new.objects(None, HYDRA.view, True):
                current_list = o.toPython()
            for o in store_new.objects(None, HYDRA.next, True):
                next_list = o.toPython()
            for o in store_new.objects(None, HYDRA.last, True):
                final_list = o.toPython()

            # Get out of loop if API is paginated without a final list
            if next_list != '' and final_list == '':
                status['success'] = False
                status['reason'] = 'The endpoint response is paginated but does not specify a final list.'
                break

            # Get total number of resources and calculate number of lists
            for o in store_new.objects(None, HYDRA.totalItems, True):
                number_of_resources = int(o.toPython())
            number_of_lists = int(ceil(number_of_resources / resources_per_list))

            # Remove pagination from triples
            store_new.remove((None, HYDRA.totalItems, None))
            store_new.remove((None, HYDRA.view, None))
            store_new.remove((None, HYDRA.first, None))
            store_new.remove((None, HYDRA.last, None))
            store_new.remove((None, HYDRA.next, None))
            store_new.remove((None, HYDRA.previous, None))
            store_new.remove((None, RDF.type, HYDRA.PartialCollectionView))

            # Add list triples to object
            self.store += store_new

            # Delay next retrieval to avoid server block
            self.report.echo_progress(progress_message, number, number_of_lists)
            sleep(retrieval_delay)

            # Get out of loop if there is no next page
            if next_list == '':
                break

            # Get out of loop if maximum number of lists is reached
            if number > max_number_of_paginated_lists:
                status['success'] = False
                status['reason'] = 'Maximum number of allowed lists was reached.'
                break

        # Return status
        return status


    # STRING ##################################################################


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if self.feed_url != None:
            return 'Feed based on web data from ' + self.feed_url + '.'
        elif self.feed_file != None:
            return 'Feed based on file data from ' + self.feed_file + '.'
        else:
            return 'Empty feed without a data source.'


    # MORPH ###################################################################


    def morph(self, routine:str, url_filter:str = None, url_replace:str = None, url_replace_with:str = None, url_add:str = None):
        '''
        Morphs the feed to a different format

            Parameters:
                routine (str): Transformation routine to use
                url_filter (str): String as a filter for resource URLs
                url_replace (str): String to replace in resource URLs
                url_replace_with (str): String to replace the previous one with
                url_add (str): Addition to the end of each resource URL
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Routine: URLs
        if routine == 'urls':
            progress_message = 'Altering list of resource URLs in feed'
            self.report.echo_progress(progress_message, 0, 100)
            status = self.__morph_urls(url_filter, url_replace, url_replace_with, url_add)
            self.report.echo_progress(progress_message, 100, 100)

        # Routine: error
        else:
            status['reason'] = 'Invalid transformation routine called.'

        # Update status
        self.report.status.append(status)


    def __morph_urls(self, filter:str = None, replace:str = None, replace_with:str = None, add:str = None) -> dict:
        '''
        Mofifies the list of individual resource URLs

            Parameters:
                filter (str): String applied to filter resource URLs
                replace (str): String to replace in listed URLs before retrieving a resource
                replace_with (str): String to use as a replacement before retrieving a resource
                add (str): String to add to each URL before retrieving a resource

            Returns:
                dict: Status report
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Check if there is data to transform
        if self.feed == []:
            status['reason'] = 'No resource URLs to alter.'
        else:

            # Simplify input
            if filter == None:
                filter = ''
            if replace == None:
                replace = ''
            if replace_with == None:
                replace_with = ''
            if add == None:
                add = ''

            # Check each URL
            morphed_feed = []
            for url in self.feed:

                # Filter list
                if filter != '':
                    if filter not in url:
                        url = ''
                if url != '':

                    # Replace and add URL parts
                    if replace != '':
                        url = url.replace(replace, replace_with)
                    if add != '':
                        url = url + add
                    morphed_feed.append(url)
                
            # Use the revised URLs instead of the original
            self.feed = morphed_feed
            status['success'] = True
            status['reason'] = 'Resource URLs in feed altered.'

        # Return status
        return status


    # SAVE ####################################################################


    def save(self, target_folder_path:str, file_name:str, routine:str = None):
        '''
        Saves graph data to a file

            Parameters:
                target_folder_path (str): Path of the folder to create files in
                file_name (str): Name of the file to create
                routine (str): Specific data to save
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Construct file name
        file_path = target_folder_path + '/' + file_name

        # Routine: Beacon file
        if routine == 'beacon':
            progress_message = 'Saving Beacon file'
            self.report.echo_progress(progress_message, 0, 100)
            status = self.__save_list(self.feed, file_path)
            self.report.echo_progress(progress_message, 100, 100)

        # Routine: error
        else:
            status['reason'] = 'Invalid saving routine called.'

        # Update status
        self.report.status.append(status)


    def __save_list(self, list_to_save:list, file_path:str) -> dict:
        '''
        Saves a list to a file

            Parameters:
                list_to_save (list): List of entries to be saved to file
                file_path (str): Path of the file to create

            Returns:
                dict: Status report
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }
        
        # Check if there is data to save
        if self.feed == []:
            status['reason'] = 'No resource URLs to list in Beacon file.'
        else:

            # Convert lines to file content
            content = ["{}\n".format(index) for index in list_to_save]
            self.__save_file(self, content, file_path)
            status['success'] = True
            status['reason'] = 'Beacon file saved.'

        # Return status
        return status
