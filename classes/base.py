# Base class to provide reporting capabilities
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


class HyBase:

    # Vars
    quiet = False


    def __init__(self, quiet):
        '''
        Provide a structured input command

            Parameters:
                quiet (bool): Avoid intermediate progress reports
        '''

        # Assign arguments to object
        self.quiet = quiet


    def echo_note(self, note:str):
        '''
        Echoes a note to the user

            Parameters:
                note (str): Note to show the user
        '''

        # Echo note or add to final report
        if self.quiet != True:
            print(note)


    def echo_progress(self, note:str, current:int = None, max:int = None):
        '''
        Echoes progress information to the user

            Parameters:
                note (str): Note to show the user
                current (int): Current number of requests, defaults to "None"
                max (int): Total number of requests, defaults to "None"
        '''

        # Start string
        if self.quiet != True:
            echo_string = '- ' + note + '… '

            # Echo string if loop has not started yet
            if current == None and max == None:
                print(echo_string, end='\r')
                
            # Calculate percentage if task is not complete
            elif current < max:
                progress = int((current / max ) * 100)
                echo_string += f"{progress:02}" + '%'
                print(echo_string, end='\r')

            # End line when task is done
            else:
                echo_string += 'done!'
                print(echo_string)
