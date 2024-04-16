# Class to report status updates and results
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


class HydraReport:

    # Variables
    quiet = False
    done = False
    status = []


    def __init__(self, quiet:bool = False):
        '''
        Report status updates and results

            Parameters:
                quiet (bool): Whether to avoid intermediate status updates
        '''

        # Assign argument to object
        self.quiet = quiet


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Basic info
        if self.done == True:
            report = 'Scraping job done'
        else:
            report = 'Scraping job is still running'
            for entry in self.status:
                if entry['success'] == False:
                    report = 'Scraping job is still running, but something went wrong already!'
        
        # Notify about issues
        report_issue = '!'
        for entry in self.status:
            if entry['success'] == False:
                report_issue = ', but something went wrong!'
        report += report_issue

        # Add detail: reason, missing, incompatible
        for entry in self.status:
            report += ' ' + entry['reason']
        for entry in self.status:
            if 'missing' in entry:
                report = report + '\n\nMissing files:\n- ' + '\n- '.join(entry['missing'])
        for entry in self.status:
            if 'incompatible' in entry:
                report = report + '\n\nNot compatible:\n- ' + '\n- '.join(entry['incompatible'])

        # Provide result
        return report


    def echo_note(self, note:str):
        '''
        Echoes a note to the user

            Parameters:
                note (str): Note to show the user
        '''

        # Echo note or add to final report
        if self.quiet != True:
            print(note)


    def echo_progress(self, note:str, current:int = None, maximum:int = None):
        '''
        Echoes progress information to the user

            Parameters:
                note (str): Note to show the user
                current (int): Current number of files, defaults to "None"
                maximum (int): Total number of files, defaults to "None"
        '''

        # Start string
        if self.quiet != True:
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


    def finish(self):
        '''
        Outputs a final report at the end of a scraping run
        '''

        # Mark task as finished and print it
        self.done = True
        print(str(self))
