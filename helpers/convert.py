# Data conversion routines
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
#from os import makedirs

# Import script modules
#from helpers.clean import clean_lines


def convert_triples_to_table(triples:object, limit_predicates:list = []) -> list:
    '''
    Converts triples into tabular data, aka a uniform two-dimensional list

        Parameters:
            triples (object): Graph object containing the triples to convert
            limit_predicates (list, optional): List of predicates to include, defaults to all

        Returns:
            list: Uniform two-dimensional list
    '''

    # Set up the output list
    output = []

    # Get unique predicates or a filtered list

    # Go through each object with a URI in the triple store

        # Retrieve each desired predicate for this URI

        # Convert object to string and remove quotation marks

    # Return tabular data
    return output
