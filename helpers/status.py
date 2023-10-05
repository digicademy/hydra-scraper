# Status reporting for a scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


def echo_note(note:str):
    '''
    Echoes a note to the user

        Parameters:
            note (str): Note to show the user
    '''

    # Echo note
    print(note)


def echo_progress(note:str, current:int=None, maximum:int=None):
    '''
    Echoes progress information to the user

        Parameters:
            note (str): Note to show the user
            current (int): Current number of files, defaults to "None"
            maximum (int): Total number of files, defaults to "None"
    '''

    # Start echo string
    echo_string = '- ' + note + '… '

    # Just echo string if the loop has not started yet
    if current == None and maximum == None:
        print(echo_string, end='\r')

    # Calculate percentage if task is not complete
    elif current < maximum:
        progress = int((current / maximum ) * 100)
        echo_string += f"{progress:02}" + '%'
        print(echo_string, end='\r')

    # End line properly when task is done
    else:
        echo_string += 'done!'
        print(echo_string)


def echo_help():
    '''
    Echoes a help text to the user instead of checking other command-line options.
    The data should be kept in sync with the readme file.
    '''

    print(
'''

This scraper is a command-line tool. Use "python go.py" to run the script in interactive mode. Alternatively, use the configuration options listed below to run the script without interaction.

-download '<value>': comma-separated list of requests, possible values:

    lists: all Hydra-paginated lists (requires -url)

    list_triples: all RDF triples in a Hydra API (requires-url)

    beacon: beacon file of all resources listed in a Hydra API (requires -url)

    resources: all resources listed in a Hydra API or a beacon file (requires -url or -file)

    resource_triples: all RDF triples in resources listed in a Hydra API or a beacon file (requires -url or -file)

-source_url '<url>': use this entry-point URL to scrape content

-source_file '<path to file>': use the URLs contained in this beacon file to scrape content

-content_type '<string>': request this content type when scraping content (defaults to none)

-taget_folder '<name of folder>': download everything into this subfolder of `downloads` (defaults to timestamp)

-resource_url_filter '<regular expression>': when listing resources, apply this string as a filter (defaults to none)

-resource_url_replace '<string>': before downloading, replace this string in each resource URL (defaults to none)

-resource_url_replace_with '<string>': before downloading, replace the previous string in each resource URL with this one (defaults to none)

-resource_url_add '<string>': before downloading, add this string to the end of each resource URL (defaults to none)

-clean_resource_names '<string>': comma-separated strings to remove from a resource URL to produce its file name (defaults to enumerated files)

'''
    )
