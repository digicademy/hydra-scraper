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

-download '<value>': comma-separated list of what you need, possible values:

    lists: all Hydra-paginated lists (requires -source_url)

    list_triples: all RDF triples in a Hydra API (requires -source_url)

    beacon: Beacon file of all resources listed in an API (requires -source_url)

    resources: all resources of an API or Beacon (requires -source_url/_file)

    resource_triples: all RDF triples of resources (requires -source_url/_file/_folder)

    resource_table: CSV table of data in resources (requires -source_url/_file/_folder)

-source_url '<url>': use this entry-point URL to scrape content (default: none)

-source_file '<path to file>': use the URLs in this Beacon file to scrape content (default: none)

-source_folder '<name of folder>': use this folder (default: none, requires -content_type)

-content_type '<string>': request/use this content type when scraping content (default: none)

-taget_folder '<name of folder>': download to this subfolder of `downloads` (default: timestamp)

-resource_url_filter '<string>': use this string as a filter for resource lists (default: none)

-resource_url_replace '<string>': replace this string in resource lists (default: none)

-resource_url_replace_with '<string>': replace the previous string with this one (default: none)

-resource_url_add '<string>': add this to the end of each resource URL (default: none)

-clean_resource_names '<string>': build file names from resource URLs (default: enumeration)

-table_data '<string list>': comma-separated property URIs to compile in a table (default: all)

'''
    )
