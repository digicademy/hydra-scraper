# Clean up data for a scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import datetime
from os import linesep
from validators import url

# Import script modules
from helpers.status import echo_help
from helpers.status import echo_note


def clean_request(arguments:list) -> dict:
    '''
    Produces a clean request dictionary from interactive mode or command line arguments

        Parameters:
            arguments (list): List of command line arguments handed to the script
        
        Returns:
            dict: Clean request dictionary
    '''

    # Set up an empty request dictionary
    request = {
        'download': [], # May contain lists, list_triples, beacon, resources, resource_triples
        'url': '',
        'file': '',
        'folder': current_timestamp(),
        'resource_url_replace': '',
        'resource_url_replace_with': '',
        'resource_url_add': '',
        'clean_resource_names': [] # Collects individual strings to remove from URLs in order to build file names
    }

    # If no arguments were provided, start interactive mode
    if arguments == []:
        echo_note('\nInteractive mode has not been implemented yet.\n')

    # If arguments were provided, enter non-interactive mode
    else:

        # Help request as a special case
        if arguments[0] in [
            'help',
            '-help',
            '--help',
            'h',
            '-h',
            '--h'
        ]:
            echo_help()

        # Check requests and modify the request dictionary accordingly
        elif '-download' in arguments:
            echo_note('')

            # Go through each key/value pair
            request = clean_argument(request, arguments, 'download', 'list')
            request = clean_argument(request, arguments, 'url', 'url')
            request = clean_argument(request, arguments, 'file', 'str')
            request = clean_argument(request, arguments, 'folder', 'str')
            request = clean_argument(request, arguments, 'resource_url_replace', 'str')
            request = clean_argument(request, arguments, 'resource_url_replace_with', 'str')
            request = clean_argument(request, arguments, 'resource_url_add', 'str')
            request = clean_argument(request, arguments, 'clean_resource_names', 'list')

        # Throw error if there are options but '-download' is not one of them
        else:
            raise ValueError('Hydra Scraper called with invalid options.')

        # Check requirements for the Hydra class
        if 'lists' in request['download'] or 'list_triples' in request['download'] or 'beacon' in request['download']:
            if request['url'] == None:
                raise ValueError('Hydra Scraper called without valid URL.')

        # Check requirements for the Beacon class
        elif 'resources' in request['download'] or 'resource_triples' in request['download']:
            if request['url'] == None and request['file'] == None:
                raise ValueError('Hydra Scraper called without valid URL or file name.')

        # No valid download requests
        else:
            raise ValueError('Hydra Scraper called without valid download requests.')

    # Return the request dictionary
    return request


def clean_argument(request:dict, arguments:list, key:str, evaluation:str = None) -> dict:
    '''
    Checks the value of a command-line argument, validates it, and adds it to the request dictionary

        Parameters:
            request (dict): old request dictionary
            arguments (list): command line arguments
            key (str): key to find the right value
            evaluation (str): type of evaluation to run (url, )

        Returns:
            dict: revised request dictionary
    '''

    # Check if argument key is used
    if '-' + key in arguments:

        # Retrieve argument value
        value_index = arguments.index('-' + key) + 1
        if len(arguments) >= value_index:
            value = arguments[value_index]

            # Perform a string evaluation
            if evaluation == 'str':
                if isinstance(value, str):
                    request[key] = value
                else:
                    raise ValueError('The command-line argument -' + key + ' uses a malformed string.')

            # Perform a comma-separated list evaluation
            elif evaluation == 'list':
                if isinstance(value, str):
                    if ', ' in value:
                        request[key] = value.split(', ')
                    elif ',' in value:
                        request[key] = value.split(',')
                    else:
                        request[key] = [ value ]
                else:
                    raise ValueError('The command-line argument -' + key + ' uses a malformed comma-separated list.')

            # Perform a URL evaluation
            elif evaluation == 'url':
                if url(value):
                    request[key] = value
                else:
                    raise ValueError('The command-line argument -' + key + ' uses a malformed URL.')
                
            # Perform no evaluation
            else:
                pass
            
        # Throw error if there is no value for the key 
        else:
            raise ValueError('The command-line argument -' + key + ' is missing a value.')
    
    # Return request dictionary
    return request


def clean_lines(content:str) -> str:
    '''
    Takes a string, removes empty lines, removes comments, and returns the string

        Parameters:
            content (str): input string to clean

        Returns:
            str: cleaned output string
    '''

    # Split up by lines and remove empty ones as well as comments
    content_lines = [
        line for line in content.splitlines()
        if line.strip() and line[0] != '#'
    ]

    # Return re-assembled string
    return linesep.join(content_lines)


def current_timestamp() -> str:
    '''
    Produces a current timestamp to be used as a folder name

        Returns:
            str: current timestamp as a string
    '''

    # Format timestamp
    timestamp = datetime.now()
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M')

    # Return it as a string
    return str(timestamp)
