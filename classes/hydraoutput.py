# Class to provide data in various output formats
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from glob import glob
from os import linesep
from re import search

# Import script modules
from classes.hydracommand import *


class HydraOutput:

    # Variables
    command = None


    def __init__(self, command:HydraCommand):
        '''
        Report status updates and results

            Parameters:
                command (HydraCommand): configuration object for the current scraping run
        '''

        # Register user input
        self.command = command

        # Create target folder
        command.create_folder(command.target_folder_path)


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a useful string
        return 'Output object for a scraping run'


    def _strip_lines(self, content:str) -> str:
        '''
        Takes a string, removes empty lines, removes comments, and returns the string

            Parameters:
                content (str): Input string to clean

            Returns:
                str: Cleaned output string
        '''

        # Split up by lines and remove empty ones or comments
        content_lines = [
            line for line in content.splitlines()
            if line.strip() and line[0] != '#'
        ]

        # Return re-assembled string
        return linesep.join(content_lines)


    def read_folder(self, folder_path:str) -> list:
        '''
        Reads a local folder and returns each file name as a list

            Parameters:
                folder_path (str): Path to the folder to read

            Returns:
                list: List of individual file names
        '''

        # Prepare folder path and empty list
        folder_path = folder_path + '/**/*'
        entries = []

        # Add each file to list
        for file_path in glob(folder_path, recursive = True):
            entries.append(file_path)

        # Return list
        return entries


    def read_list(self, file_path:str) -> list:
        '''
        Reads a list file and returns each line as a list

            Parameters:
                file_path (str): Path to the file to read

            Returns:
                list: List of individual lines
        '''

        # Open file
        try:
            f = open(file_path, 'r')
            content = f.read()

            # Optionally identify an ID pattern
            pattern = search(r"(?<=#TARGET: ).*(?<!\n)", content)
            if pattern != None:
                pattern = pattern.group()
                if pattern.find('{ID}') == -1:
                    pattern = None

            # Clean empty lines and comments
            content = self._strip_lines(content)
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

            # Return list
            return entries

        # Report if file is not found
        except:
            return []


    def save_file(self, content:str, file_path:str):
        '''
        Saves content to a file with a specified name and extension

            Parameters:
                content (str): Content to be saved to file
                file_path (str): Path of the file to create
        '''

        # Write content to file
        f = open(file_path, 'w')
        f.write(content)
        f.flush


    def save_list(self, file_path:str, list_to_save:list):
        '''
        Saves a list to a file

            Parameters:
                file_path (str): Path of the file to create
                list_to_save (list): List of entries to save to file
        '''

        # Prepare beacon file and save each line
        lines = ["{}\n".format(index) for index in list_to_save]
        with open(file_path, 'w') as f:
            f.writelines(lines)


    def save_csv(self, tabular_data:list, file_path:str):
        '''
        Saves a uniform two-dimensional list as a comma-separated value file

            Parameters:
                tabular_data (list): Uniform two-dimensional list
                file_path (str): Path of the file to save without the extension
        '''

        # Open file
        f = open(file_path + '.csv', 'w')

        # Write table line by line
        for tabular_data_line in tabular_data:
            tabular_data_string = '"' + '","'.join(tabular_data_line) + '"\n'
            f.write(tabular_data_string)
            f.flush
