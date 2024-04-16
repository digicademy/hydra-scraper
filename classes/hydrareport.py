# Class to report status updates and results
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


class HydraReport:

    # Variables
    be_quiet = False
    status = []
    report = ''


    def __init__(self):
        '''
        Report status updates and results
        '''

        # Add blank line for a scraping run
        if self.be_quiet == False:
            self.echo_note('\n')


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a useful string
        if self.be_quiet == False:
            return 'Report set up for live status updates'
        else:
            return 'Report set up to only provide status info at the end'


    def echo_note(self, note:str, even_if_quiet:bool = True):
        '''
        Echoes a note to the user

            Parameters:
                note (str): Note to show the user
                even_if_quiet (bool): Whether or not to print the note in quiet mode
        '''

        # Echo note or add to final report
        if even_if_quiet:
            if self.be_quiet != True:
                print(note)
            else:
                self.report += note + '\n'


    def echo_progress(self, note:str, current:int=None, maximum:int=None):
        '''
        Echoes progress information to the user

            Parameters:
                note (str): Note to show the user
                current (int): Current number of files, defaults to "None"
                maximum (int): Total number of files, defaults to "None"
        '''

        # Start string
        if self.be_quiet != True:
            echo_string = '- ' + note + '… '

            # Just echo string if loop has not started yet
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


    def echo_report(self):
        '''
        Compiles a final report
        '''

        # Compile a report string (success, reason, missing, incompatible)
        self.report += 'Done!'
        for entry in self.status:
            if entry['success'] == False:
                report = 'Something went wrong!'
        for entry in self.status:
            report = report + ' ' + entry['reason']
        for entry in self.status:
            if 'missing' in entry:
                report = report + '\n\nMissing files:\n- ' + '\n- '.join(entry['missing'])
        for entry in self.status:
            if 'incompatible' in entry:
                report = report + '\n\nNot compatible:\n- ' + '\n- '.join(entry['incompatible'])

        #Provide final report
        self.echo_note('\n' + report + '\n')
