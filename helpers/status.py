# Status reporting for a scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


def echo_note( note:str ):
    '''
    Echoes a note to the user

        Parameters:
            note (str): Note to show the user
    '''

    # Echo note
    print( note )


def echo_progress( note:str, current:int=None, maximum:int=None ):
    '''
    Echoes progress information to the user

        Parameters:
            note (str): Note to show the user
            current (int): Current number of files, defaults to "None"
            maximum (int): Total number of files, defaults to "None"
    '''

    # Start the echo string
    echo_string = '- ' + note + '… '

    # Just echo the string of the loop has not started yet
    if current == None and maximum == None:
        print( echo_string, end='\r' )

    # Calculate the percentage if the task is not complete
    elif current < maximum:
        progress = int( ( current / maximum ) * 100 )
        echo_string += f"{progress:02}" + '%'
        print( echo_string, end='\r' )

    # End the line properly when the task is done
    else:
        echo_string += 'done!'
        print( echo_string )
