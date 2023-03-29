# File Input and Output
# Copyright (c) 2023 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# MIT License


# Import libraries
from os import mkdir


def save_file( content:str, file_path:str ):
    '''
    Saves content to a file with a specified name and extension

        Parameters:
            content (str): Content to be saved to file
            file_path (str): Path of the file to create
    '''

    # Write content to file
    f = open( file_path, 'w' )
    f.write( content )
    f.flush


def save_list( file_path:str, list_to_save:list ):
    '''
    Saves a list to a file

        Parameters:
            file_path (str): Path of the file to create
            list_to_save (list): List of entries to save to file
    '''

    # If requested, prepare the beacon file and save each line
    lines = ["{}\n".format( index ) for index in list_to_save]
    with open( file_path, 'w' ) as f:
        f.writelines( lines )


def read_list( file_path:str ) -> list:
    '''
    Reads a list file and returns each line as a list

        Parameters:
            file_path (str): Path to the file to read

        Returns:
            list: List of individual lines
    '''

    # Open the file
    try:
        f = open( file_path, 'r' )

        # Add each line to a list
        entries = []
        for entry in f:
            entry_text = entry.strip()
            if entry_text != '':
                entries.append( entry_text )

        # Return the list
        return entries
    
    # Mark if the file cannot be found
    except:
        return None


def create_folder( folder_name:str ):
    '''
    Creates a folder with a given name in the main script's directory

        Parameters:
            folder_name (str): Name of the folder to create
    '''

    try:
        mkdir( folder_name )
    except OSError as error:
        pass
