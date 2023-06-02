# Simple scraper for APIs with Hydra pagination
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from sys import argv

# Import script modules
from classes.hydra import *
from classes.beacon import *
from helpers.clean import clean_request
from helpers.fileio import create_folder


# Get request data from command line arguments
request = clean_request( argv[1:] )
create_folder( 'downloads/' + request['folder'] )

# Hydra routine
if request['routine'] == 'hydra':
    create_folder( 'downloads/' + request['folder'] + '/hydra' )
    hydra = Hydra( request['url'], request['folder'], request['list'] )
    hydra.download()

# Beacon routine
elif request['routine'] == 'beacon':
    create_folder( 'downloads/' + request['folder'] + '/resources' )
    beacon = Beacon( request['file'], request['folder'], request['replace'], request['with'], request['clean_names'] )
    beacon.download()

# Catch a corner case that should not occur
else:
    raise Exception( 'Hydra Scraper encountered an unknown error while handling the request' )
