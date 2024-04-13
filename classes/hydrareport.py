# Class to report status updates and results
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries

# Import script modules


# Report status updates and results
class HydraReport:

    something = None
    # status = []


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

# type: status, result

# # Compile a report string (success, reason, missing, incompatible)
# report = 'Done!'
# for entry in status:
#     if entry['success'] == False:
#         report = 'Something went wrong!'
# for entry in status:
#     report = report + ' ' + entry['reason']
# for entry in status:
#     if 'missing' in entry:
#         report = report + '\n\nMissing files:\n- ' + '\n- '.join(entry['missing'])
#for entry in status:
#    if 'incompatible' in entry:
#        report = report + '\n\nNot compatible:\n- ' + '\n- '.join(entry['incompatible'])

# Provide final report
#echo_note('\n' + report + '\n')



# def echo_note(note:str):
#     '''
#     Echoes a note to the user

#         Parameters:
#             note (str): Note to show the user
#     '''

#     # Echo note
#     print(note)


# def echo_progress(note:str, current:int=None, maximum:int=None):
#     '''
#     Echoes progress information to the user

#         Parameters:
#             note (str): Note to show the user
#             current (int): Current number of files, defaults to "None"
#             maximum (int): Total number of files, defaults to "None"
#     '''

#     # Start echo string
#     echo_string = '- ' + note + '… '

#     # Just echo string if the loop has not started yet
#     if current == None and maximum == None:
#         print(echo_string, end='\r')

#     # Calculate percentage if task is not complete
#     elif current < maximum:
#         progress = int((current / maximum ) * 100)
#         echo_string += f"{progress:02}" + '%'
#         print(echo_string, end='\r')

#     # End line properly when task is done
#     else:
#         echo_string += 'done!'
#         print(echo_string)


