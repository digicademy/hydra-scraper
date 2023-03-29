# Simple Scraper for APIs with Hydra Pagination
# Copyright (c) 2023 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# MIT License


# Import libraries
from sys import argv

# Import script modules
from classes.hydra import *
from classes.beacon import *
from helpers.clean import clean_request
from helpers.fileio import create_folder


# TODO Create the download folder
# TODO Make sure everything looks good in a terminal

# Get request data from command line arguments
request = clean_request( argv[1:] )
create_folder( 'downloads' )
create_folder( request['folder'] )

# Hydra routine
if request['type'] == 'hydra':
    hydra = Hydra( request['url'], request['folder'], request['list'] )
    hydra.download()

# Beacon routine
elif request['type'] == 'beacon':
    beacon = Beacon( request['file'], request['folder'], request['replace'], request['with'], request['clean_names'] )
    beacon.download()

# Catch a corner case that should not occur
else:
    raise Exception( 'Hydra Scraper encountered an unknown error while handling the request' )
