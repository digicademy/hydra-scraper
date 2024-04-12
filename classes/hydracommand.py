# Class to provide a structured input command
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries

# Import script modules


# Provide a structured input command
class HydraCommand:

    something = None


    def __init__(self, something:str = ''):
        '''
        Add required data to instances of this object

            Parameters:
                something (str): ???
        '''

        # Assign variables
        self.something = something


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        return self.something

# # Get request data and create download folder for this job
# request = clean_request(argv[1:])
# job_folder = config['download_base'] + '/' + request['target_folder']
# create_folder(job_folder)

# # Set up status messages
# status = []



# Configuration dictionary to use in the script
# config = {
#     'download_delay': 0.02,
#     'download_base': 'downloads',
#     'max_paginated_lists': 500,
#     'non_rdf_formats': [
#         'lido'
#     ],
#     'known_defined_term_sets': [
#         'http://sws.geonames.org/',
#         'https://iconclass.org/',
#         'http://vocab.getty.edu/page/aat/',
#         'http://d-nb.info/gnd/',
#         'http://www.wikidata.org/wiki/',
#         'https://viaf.org/viaf/'
#     ]
# }



# # Import libraries
# from datetime import datetime
# from os import linesep
# from validators import url

# # Import script modules
# from helpers.status import echo_help
# from helpers.status import echo_note


# def clean_request(arguments:list) -> dict:
#     '''
#     Produces a clean request dictionary from interactive mode or command line arguments

#         Parameters:
#             arguments (list): List of command line arguments handed to the script
        
#         Returns:
#             dict: Clean request dictionary
#     '''

#     # Set up an empty request dictionary
#     request = {
#         'download': [], # May contain lists, list_triples, list_cgif, beacon, resources, resource_triples, resource_cgif, resource_table
#         'source_url': '',
#         'source_file': '',
#         'source_folder': '',
#         'content_type': '',
#         'taget_folder': current_timestamp(),
#         'resource_url_filter': '',
#         'resource_url_replace': '',
#         'resource_url_replace_with': '',
#         'resource_url_add': '',
#         'clean_resource_names': [],
#         'table_data': [],
#         'supplement_data_feed': '',
#         'supplement_data_catalog': '',
#         'supplement_data_catalog_publisher': '',
#     }

#     # If no arguments were provided, start interactive mode
#     if arguments == []:
#         echo_note('\nInteractive mode has not been implemented yet.\n')

#     # If arguments were provided, enter non-interactive mode
#     else:

#         # Help request as a special case
#         if arguments[0] in [
#             'help',
#             '-help',
#             '--help',
#             'h',
#             '-h',
#             '--h'
#         ]:
#             echo_help()

#         # Check requests and modify the request dictionary accordingly
#         elif '-download' in arguments:
#             echo_note('')

#             # Go through each key/value pair
#             request = clean_argument(request, arguments, 'download', 'list')
#             request = clean_argument(request, arguments, 'source_url', 'url')
#             request = clean_argument(request, arguments, 'source_file', 'str')
#             request = clean_argument(request, arguments, 'source_folder', 'str')
#             request = clean_argument(request, arguments, 'content_type', 'str')
#             request = clean_argument(request, arguments, 'target_folder', 'str')
#             request = clean_argument(request, arguments, 'resource_url_filter', 'str')
#             request = clean_argument(request, arguments, 'resource_url_replace', 'str')
#             request = clean_argument(request, arguments, 'resource_url_replace_with', 'str')
#             request = clean_argument(request, arguments, 'resource_url_add', 'str')
#             request = clean_argument(request, arguments, 'clean_resource_names', 'list')
#             request = clean_argument(request, arguments, 'table_data', 'list')
#             request = clean_argument(request, arguments, 'supplement_data_feed', 'url')
#             request = clean_argument(request, arguments, 'supplement_data_catalog', 'url')
#             request = clean_argument(request, arguments, 'supplement_data_catalog_publisher', 'url')

#         # Throw error if there are options but '-download' is not one of them
#         else:
#             raise ValueError('Hydra Scraper called with invalid options.')

#         # Check requirements for the Hydra class
#         if 'lists' in request['download'] or 'list_triples' in request['download'] or 'list_cgif' in request['download'] or 'beacon' in request['download']:
#             if request['source_url'] == None:
#                 raise ValueError('Hydra Scraper called without valid source URL.')

#         # Check requirements for the Beacon class I
#         elif 'resources' in request['download']:
#             if request['source_url'] == None and request['source_file'] == None:
#                 raise ValueError('Hydra Scraper called without valid source URL or file name.')

#         # Check requirements for the Beacon class II
#         elif 'resource_triples' in request['download'] or 'resource_cgif' in request['download'] or 'resource_table' in request['download']:
#             if request['source_url'] == None and request['source_file'] == None and request['source_folder'] == None:
#                 raise ValueError('Hydra Scraper called without valid source URL, file, or folder name.')
#             elif request['source_folder'] != None and request['content_type'] == None:
#                 raise ValueError('Hydra Scraper called with a folder name but without a content type.')

#         # No valid download requests
#         else:
#             raise ValueError('Hydra Scraper called without valid download requests.')

#     # Return the request dictionary
#     return request


# def clean_argument(request:dict, arguments:list, key:str, evaluation:str = None) -> dict:
#     '''
#     Checks the value of a command-line argument, validates it, and adds it to the request dictionary

#         Parameters:
#             request (dict): old request dictionary
#             arguments (list): command line arguments
#             key (str): key to find the right value
#             evaluation (str): type of evaluation to run ('url', 'str', 'list')

#         Returns:
#             dict: revised request dictionary
#     '''

#     # Check if argument key is used
#     if '-' + key in arguments:

#         # Retrieve argument value
#         value_index = arguments.index('-' + key) + 1
#         if len(arguments) >= value_index:
#             value = arguments[value_index]

#             # Perform a string evaluation
#             if evaluation == 'str':
#                 if isinstance(value, str):
#                     request[key] = value
#                 else:
#                     raise ValueError('The command-line argument -' + key + ' uses a malformed string.')

#             # Perform a comma-separated list evaluation
#             elif evaluation == 'list':
#                 if isinstance(value, str):
#                     if ', ' in value:
#                         request[key] = value.split(', ')
#                     elif ',' in value:
#                         request[key] = value.split(',')
#                     else:
#                         request[key] = [ value ]
#                 else:
#                     raise ValueError('The command-line argument -' + key + ' uses a malformed comma-separated list.')

#             # Perform a URL evaluation
#             elif evaluation == 'url':
#                 if url(value):
#                     request[key] = value
#                 else:
#                     raise ValueError('The command-line argument -' + key + ' uses a malformed URL.')
                
#             # Perform no evaluation
#             else:
#                 pass
            
#         # Throw error if there is no value for the key 
#         else:
#             raise ValueError('The command-line argument -' + key + ' is missing a value.')
    
#     # Return request dictionary
#     return request


# def clean_lines(content:str) -> str:
#     '''
#     Takes a string, removes empty lines, removes comments, and returns the string

#         Parameters:
#             content (str): input string to clean

#         Returns:
#             str: cleaned output string
#     '''

#     # Split up by lines and remove empty ones as well as comments
#     content_lines = [
#         line for line in content.splitlines()
#         if line.strip() and line[0] != '#'
#     ]

#     # Return re-assembled string
#     return linesep.join(content_lines)


# def clean_string_for_csv(content:str) -> str:
#     '''
#     Takes a string, removes quotation marks, removes newlines, and returns the string

#         Parameters:
#             content (str): input string to clean

#         Returns:
#             str: cleaned output string
#     '''

#     # Remove offending characters
#     content = content.replace('"', '\'')
#     content = content.replace('\n', '')
#     content = content.replace('\r', '')

#     # Return clean string
#     return content


# def current_timestamp() -> str:
#     '''
#     Produces a current timestamp to be used as a folder name

#         Returns:
#             str: current timestamp as a string
#     '''

#     # Format timestamp
#     timestamp = datetime.now()
#     timestamp = timestamp.strftime('%Y-%m-%d %H:%M')

#     # Return it as a string
#     return str(timestamp)
