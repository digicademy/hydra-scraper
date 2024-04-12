# Entry-point script
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from sys import argv

# Import script modules
from classes.hydracommand import *
from classes.hydraoutput import *
from classes.hydrareport import *
from classes.hydramunch import *
from classes.hydrafetch import *


# Collect configuration info
command = HydraCommand(argv[1:])

# Set up helper objects
output = HydraOutput(command)
report = HydraReport(command)
munch = HydraMunch(command)

# Run main fetch job
fetch = HydraFetch(command, output, report, munch)


### OLD VERSION

# # Get request data and create download folder for this job
# request = clean_request(argv[1:])
# job_folder = config['download_base'] + '/' + request['target_folder']
# create_folder(job_folder)

# # Set up status messages
# status = []

# # Set up Hydra API routine if required
# if 'lists' in request['download'] or 'beacon' in request['download'] or 'list_triples' in request['download'] or 'list_cgif' in request['download']:
#     hydra = Hydra(request['target_folder'], request['source_url'], request['content_type'])

#     # Populate the object, and download each API list if requested
#     if 'lists' in request['download']:
#         save_lists = True
#     else:
#         save_lists = False
#     hydra.populate(save_lists, request['resource_url_filter'], request['resource_url_replace'], request['resource_url_replace_with'], request['resource_url_add'])

#     # Compile a beacon list if requested
#     if 'beacon' in request['download']:
#         hydra.save_beacon()

#     # Compile list triples if requested
#     if 'list_triples' in request['download']:
#         hydra.save_triples()

#     # Compile list CGIF triples if requested
#     if 'list_cgif' in request['download']:
#         hydra.save_triples('cgif', 'lists_cgif')

#     # Add status message
#     status.extend(hydra.status)

# # Mini Hydra routine if Beacon logic is requested but no beacon file is given
# elif request['source_file'] == '':
#     hydra = Hydra(request['target_folder'], request['source_url'], request['content_type'])
#     hydra.populate(False, request['resource_url_filter'], request['resource_url_replace'], request['resource_url_replace_with'], request['resource_url_add'])

# # Mark absence of hydra object if beacon file is present
# else:
#     hydra = False

# # Set up beacon file routine if required
# if 'resources' in request['download'] or 'resource_triples' in request['download'] or 'resource_cgif' in request['download'] or 'resource_table' in request['download']:

#     # Use previous resource list if present
#     if hydra == False:
#         beacon = Beacon(request['target_folder'], request['content_type'])
#     else:
#         beacon = Beacon(request['target_folder'], request['content_type'], hydra.resources)

#     # Populate the object, and download each resource if requested
#     if 'resources' in request['download']:
#         save_resources = True
#     else:
#         save_resources = False
#     beacon.populate(save_resources, request['clean_resource_names'], request['source_file'], request['source_folder'], request['supplement_data_feed'], request['supplement_data_catalog'], request['supplement_data_catalog_publisher'])

#     # Compile resource triples if requested
#     if 'resource_triples' in request['download']:
#         beacon.save_triples()

#     # Compile resource CGIF triples if requested
#     if 'resource_cgif' in request['download']:
#         beacon.save_triples('cgif', 'resources_cgif')

#     # Compile resource table if requested
#     if 'resource_table' in request['download']:
#         beacon.save_table(request['table_data'])

#     # Add status message
#     status.extend(beacon.status)

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
