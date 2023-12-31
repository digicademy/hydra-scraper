# Configuration for a scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
#from datetime import datetime
#from validators import url

# Import script modules
#from helpers.status import *


# Configuration dictionary to use in the script
config = {
    'download_delay': 0.02,
    'download_base': 'downloads',
    'max_paginated_lists': 500,
    'non_rdf_formats': [
        'lido'
    ],
    'known_defined_term_sets': [
        'http://sws.geonames.org/',
        'https://iconclass.org/',
        'http://vocab.getty.edu/page/aat/',
        'http://d-nb.info/gnd/',
        'http://www.wikidata.org/wiki/',
        'https://viaf.org/viaf/'
    ]
}
