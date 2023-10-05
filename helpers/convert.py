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

    # Set up output and predicate lists
    output = []
    predicates = []

    # Get unique predicates and optionally filter them
    all_predicates = triples.predicates(unique = True)
    if limit_predicates != []:
        for all_predicate in all_predicates:
            if str(all_predicate) in limit_predicates:
                predicates.append(all_predicate)
    else:
        predicates = all_predicates

    # List all predicates as a table header
    first_line = ['URI']
    for predicate in predicates:
        first_line.append(predicate)
    output.append(first_line)

    # Get unique subjects that start with 'http' and go through them
    all_subjects = triples.subjects(unique = True)
    for all_subject in all_subjects:
        if str(all_subject)[0:4] == 'http':
            new_line = [str(all_subject)]

            # TODO Check each required predicate, retrieve its object(s), and remove quotation marks
            for predicate in predicates:
                all_objects = triples.objects(subject = all_subject, predicate = predicate, unique = True)
                if all_objects == None:
                    new_line.append('')
                else:
                    new_line.append(', '.join(str(all_objects).replace('"', '')))

            # Add new line to output
            output.append(new_line)

    # Return tabular data
    return output
