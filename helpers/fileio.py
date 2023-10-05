# File input and output
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from os import makedirs

# Import script modules
from helpers.clean import clean_lines


def save_file(content:str, file_path:str):
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


def save_list(file_path:str, list_to_save:list):
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


def save_table(tabular_data:list, file_path:str ):
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


def read_list(file_path:str) -> list:
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

        # Clean empty lines and comments
        content = clean_lines(content)
        lines = iter(content.splitlines())

        # Add each line to list
        entries = []
        for line in lines:
            entries.append(line)

        # Return list
        return entries
    
    # Report if file is not found
    except:
        return []


def create_folder(folder_name:str):
    '''
    Creates a folder with a given name in the main script's directory

        Parameters:
            folder_name (str): Name of the folder to create
    '''

    # Try to create folders
    try:
        makedirs(folder_name, exist_ok=True)
    except OSError as error:
        pass
