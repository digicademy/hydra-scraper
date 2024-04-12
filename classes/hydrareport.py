# Class to provide a structured input command
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries

# Import script modules


# Provide a structured input command
class HydraReport:

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
