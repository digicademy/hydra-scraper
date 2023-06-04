# Clean up data for a scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import datetime
from validators import url

# Import script modules
from helpers.status import *


def clean_request(arguments:list) -> dict:
    '''
    Produces a clean request dictionary from interactive mode or command line arguments

        Parameters:
            arguments (list): List of command line arguments handed to the script
        
        Returns:
            dict: Clean request dictionary
    '''

    # Compile expected routine arguments
    request = {}
    arguments_hydra = [
        'hydra',
        '-hydra',
        '--hydra'
    ]
    arguments_beacon = [
        'beacon',
        '-beacon',
        '--beacon'
    ]
    arguments_help = [
        'help',
        '-help',
        '--help',
        'h',
        '-h',
        '--h'
    ]

    # If no arguments were provided, start interactive mode
    if arguments == []:
        echo_note('\nInteractive mode has not been implemented yet.\n')

    # If arguments were provided, enter non-interactive mode
    else:

        # 'hydra' is requested and required fields are provided
        if arguments[0] in arguments_hydra:
            if '-url' in arguments:
                request['routine'] = 'hydra'

                # Check '-url' key/value pair
                value_index = arguments.index('-url') + 1
                if len(arguments) >= value_index:
                    value = arguments[value_index]
                    if url(value):
                        request['url'] = value
                    else:
                        raise ValueError('Hydra call uses a faulty URL.')
                else:
                    raise ValueError('Hydra call is missing a URL.')

                # Check '-folder' key/value pair
                if '-folder' in arguments:
                    value_index = arguments.index('-folder') + 1
                    if len(arguments) >= value_index:
                        value = arguments[value_index]
                        if isinstance(value, str):
                            request['folder'] = value
                        else:
                            raise ValueError('Hydra call uses a faulty folder path.')
                    else:
                        raise ValueError('Hydra call is missing a folder path.')
                else:
                    timestamp = datetime.now()
                    timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
                    timestamp = str(timestamp)
                    request['folder'] = str(timestamp)

                # Check '-list' key/value pair
                if '-list' in arguments:
                    value_index = arguments.index('-list') + 1
                    if len(arguments) >= value_index:
                        value = arguments[value_index]
                        if isinstance(value, str):
                            request['list'] = value
                        else:
                            raise ValueError('Hydra call uses a faulty list-file path.')
                    else:
                        raise ValueError('Hydra call is missing a list-file path.')
                else:
                    request['list'] = 'beacon.txt'

            # Throw error if required attribute is missing
            else:
                raise IndexError('Hydra call is missing a required attribute.')

        # 'beacon' is requested and required fields are provided
        elif arguments[0] in arguments_beacon:
            if '-file' in arguments:
                request['routine'] = 'beacon'

                # Check '-file' key/value pair
                value_index = arguments.index('-file') + 1
                if len(arguments) >= value_index:
                    value = arguments[value_index]
                    if isinstance(value, str):
                        request['file'] = value
                    else:
                        raise ValueError('Beacon call uses a faulty file path.')
                else:
                    raise ValueError('Beacon call is missing a file path.')

                # Check '-folder' key/value pair
                if '-folder' in arguments:
                    value_index = arguments.index('-folder') + 1
                    if len(arguments) >= value_index:
                        value = arguments[value_index]
                        if isinstance(value, str):
                            request['folder'] = value
                        else:
                            raise ValueError('Beacon call uses a faulty folder path.')
                    else:
                        raise ValueError('Beacon call is missing a folder path.')
                else:
                    timestamp = datetime.now()
                    timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
                    timestamp = str(timestamp)
                    request['folder'] = str(timestamp)

                # Check '-replace' key/value pair
                if '-replace' in arguments:
                    value_index = arguments.index('-replace') + 1
                    if len(arguments) >= value_index:
                        value = arguments[value_index]
                        if isinstance(value, str):
                            request['replace'] = value
                        else:
                            raise ValueError('Beacon call uses a faulty replacement string.')
                    else:
                        raise ValueError('Beacon call is missing a replacement string.')
                else:
                    request['replace'] = ''

                # Check '-with' key/value pair
                if '-with' in arguments:
                    value_index = arguments.index('-with') + 1
                    if len(arguments) >= value_index:
                        value = arguments[value_index]
                        if isinstance(value, str):
                            request['with'] = value
                        else:
                            raise ValueError('Beacon call uses a faulty replacement string')
                    else:
                        raise ValueError('Beacon call is missing a replacement string.')
                else:
                    request['with'] = ''

                # Check '-add' key/value pair
                if '-add' in arguments:
                    value_index = arguments.index('-add') + 1
                    if len(arguments) >= value_index:
                        value = arguments[value_index]
                        if isinstance(value, str):
                            request['add'] = value
                        else:
                            raise ValueError('Beacon call uses a faulty string to add.')
                    else:
                        raise ValueError('Beacon call is missing a string to add.')
                else:
                    request['with'] = ''

                # Check '-clean_names' key/value pair
                if '-clean_names' in arguments:
                    value_index = arguments.index('-clean_names') + 1
                    if len(arguments) >= value_index:
                        value = arguments[value_index]
                        if isinstance(value, str):
                            if ', ' in value:
                                request['clean_names'] = value.split(', ')
                            elif ',' in value:
                                request['clean_names'] = value.split(',')
                            else:
                                request['clean_names'] = [ value ]
                        else:
                            raise ValueError('Beacon call uses a faulty name-cleaning string.')
                    else:
                        raise ValueError('Beacon call is missing a name-cleaning string.')
                else:
                    request['clean_names'] = []

            # Throw an error if required attribute is missing
            else:
                raise IndexError('Beacon call is missing a required attribute.')

        # '-help' is requested
        elif arguments[0] in arguments_help:
            request['routine'] = 'help'

        # Throw an error if invalid request was made
        else:
            raise IndexError('Hydra Scraper called with faulty attributes.')

    # Return the request dictionary
    return request
