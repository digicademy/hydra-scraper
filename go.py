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
from helpers.config import *
from helpers.fileio import create_folder
from helpers.status import echo_note


# Get request data and create download folder for this job
request = clean_request(argv[1:])
job_folder = config['download_base'] + '/' + request['folder']
create_folder(job_folder)

# Set up status messages
status = []

# Set up Hydra API routine if required
if 'lists' in request['download'] or 'beacon' in request['download'] or 'list_triples' in request['download']:
    hydra = Hydra(request['folder'], request['url'])

    # Populate the object, and download each API list if requested
    if 'lists' in request['download']:
        save_lists = True
    else:
        save_lists = False
    hydra.populate(save_lists, request['resource_url_replace'], request['resource_url_replace_with'], request['resource_url_add'])

    # Compile a beacon list if requested
    if 'beacon' in request['download']:
        hydra.save_beacon()

    # Compile list triples if requested
    if 'list_triples' in request['download']:
        hydra.save_triples()

    # Add status message
    status.extend(hydra.status)

# Mini Hydra routine if Beacon logic is requested but no beacon file is given
elif request['file'] == '':
    hydra = Hydra(request['folder'], request['url'])
    hydra.populate(False, request['resource_url_replace'], request['resource_url_replace_with'], request['resource_url_add'])

# Mark absence of hydra object if beacon file is present
else:
    hydra = False

# Set up beacon file routine if required
if 'resources' in request['download'] or 'resource_triples' in request['download']:

    # Use previous resource list if present
    if hydra == False:
        beacon = Beacon(request['folder'])
    else:
        beacon = Beacon(request['folder'], hydra.resources)

    # Populate the object, and download each resource if requested
    if 'resources' in request['download']:
        save_resources = True
    else:
        save_resources = False
    beacon.populate(save_resources, request['clean_resource_names'], request['file'])

    # Compile resource triples if requested
    if 'resource_triples' in request['download']:
        beacon.save_triples()

    # Add status message
    status.extend(beacon.status)

# Compile a report string
report = 'Done!'
for entry in status:
    if entry['success'] == False:
        report = 'Something went wrong!'
for entry in status:
    report = report + ' ' + entry['reason']

# Provide final report
echo_note('\n' + report + '\n')
