# Class to retrieve data via beacon files or APIs
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries

# Import script modules


# Retrieve data via beacon files or APIs
class HydraRetrieve:

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

# types: api, resources

# # Set up Hydra API routine if required
# if 'lists' in command.request or 'beacon' in command.request or 'list_triples' in command.request or 'list_cgif' in command.request:
#     hydra = Hydra(command.target_folder_name, command.source_url, command.content_type)

#     # Populate the object, and download each API list if requested
#     if 'lists' in command.request:
#         save_lists = True
#     else:
#         save_lists = False
#     hydra.populate(save_lists, command.resource_url_filter, command.resource_url_replace, command.resource_url_replace_with, command.resource_url_add)

#     # Compile a beacon list if requested
#     if 'beacon' in command.request:
#         hydra.save_beacon()

#     # Compile list triples if requested
#     if 'list_triples' in command.request:
#         hydra.save_triples()

#     # Compile list CGIF triples if requested
#     if 'list_cgif' in command.request:
#         hydra.save_triples('cgif', 'lists_cgif')

#     # Add status message
#     status.extend(hydra.status)

# # Mini Hydra routine if Beacon logic is requested but no beacon file is given
# elif command.source_file == '':
#     hydra = Hydra(command.target_folder_name, command.source_url, command.content_type)
#     hydra.populate(False, command.resource_url_filter, command.resource_url_replace, command.resource_url_replace_with, command.resource_url_add)

# # Mark absence of hydra object if beacon file is present
# else:
#     hydra = False

# # Set up beacon file routine if required
# if 'resources' in command.request or 'resource_triples' in command.request or 'resource_cgif' in command.request or 'resource_table' in command.request:

#     # Use previous resource list if present
#     if hydra == False:
#         beacon = Beacon(command.target_folder_name, command.content_type)
#     else:
#         beacon = Beacon(command.target_folder_name, command.content_type, hydra.resources)

#     # Populate the object, and download each resource if requested
#     if 'resources' in command.request:
#         save_resources = True
#     else:
#         save_resources = False
#     beacon.populate(save_resources, command.clean_resource_names, command.source_file, command.source_folder, command.supplement_data_feed, command.supplement_data_catalog, command.supplement_data_catalog_publisher)

#     # Compile resource triples if requested
#     if 'resource_triples' in command.request:
#         beacon.save_triples()

#     # Compile resource CGIF triples if requested
#     if 'resource_cgif' in command.request:
#         beacon.save_triples('cgif', 'resources_cgif')

#     # Compile resource table if requested
#     if 'resource_table' in command.request:
#         beacon.save_table(command.table_data)

#     # Add status message
#     status.extend(beacon.status)



# # Import libraries
# from urllib import request

# # Import script modules
# from helpers.clean import clean_lines


# def download_file(url:str, content_type:str = '') -> dict:
#     '''
#     Retrieves a file from a URL and returns the content

#         Parameters:
#             url (str): URL to download the file from
#             content_type (str, optional): content type to request, defaults to none

#         Returns:
#             dict: Provides 'file_type', 'file_extension' and 'content' of the retrieved file
#     '''

#     # Retrieve URL content
#     try:
#         if content_type != '':
#             request_header = { 'Accept': content_type }
#             request_object = request.Request(url, headers = request_header)
#             response = request.urlopen(request_object)
#         else:
#             response = request.urlopen(url)

#         # Check if response is invalid
#         if response.status != 200:
#             simple_response = None

#         # If response is valid, get clean file content
#         else:
#             headers = dict(response.headers.items())
#             file_type = determine_file_type(headers, False)
#             file_extension = determine_file_type(headers, True)
#             content = response.read().decode('utf-8')

#             # If present, isolate embedded JSON-LD as it is not supported by RDFLib yet
#             if determine_file_type(headers, False) == 'rdfa':
#                 embedded_jsonld = content.find('application/ld+json')
#                 if embedded_jsonld != -1:
#                     embedded_jsonld_start = content.find('>', embedded_jsonld) + 1
#                     embedded_jsonld_end = content.find('</script>', embedded_jsonld)
#                     if embedded_jsonld_start > 0 and embedded_jsonld_end > embedded_jsonld_start:

#                         # Correct previous assumptions
#                         file_type = 'json-ld'
#                         file_extension = 'jsonld'
#                         content = content[embedded_jsonld_start:embedded_jsonld_end]

#                         # Remove empty lines
#                         content = clean_lines(content)

#             # Structure the data
#             simple_response = {
#                 'file_type': file_type,
#                 'file_extension': file_extension,
#                 'content': content
#             }


#     # Notify if URL not available
#     except:
#         simple_response = None

#     # Return simplified response
#     return simple_response

# def retrieve_local_file(file_path:str, content_type:str) -> dict:
#     '''
#     Retrieves a local file and returns the content

#         Parameters:
#             file_path (str): path to open the file at
#             content_type (str): content type to parse

#         Returns:
#             dict: Provides 'file_type', 'file_extension' and 'content' of the retrieved file
#     '''

#     # Retrieve file content
#     try:
#         with open(file_path) as f:
#             content = f.read()

#             # Get file type and file extension
#             headers = {
#                 'Content-Type': content_type
#             }
#             file_type = determine_file_type(headers, False)
#             file_extension = determine_file_type(headers, True)

#             # Structure the data
#             simple_response = {
#                 'file_type': file_type,
#                 'file_extension': file_extension,
#                 'content': content
#             }

#     # Notify if file not available
#     except:
#         simple_response = None

#     # Return simplified response
#     return simple_response


# def determine_file_type(headers:dict, getFileExtension:bool = False) -> str:
#     '''
#     Determines the best file type and extension based on the server response

#         Parameters:
#             headers (dict): Headers of the server response as a dictionary
#             getFileExtension (bool, optional): Determines whether the type or the extension is returned
        
#         Returns:
#             str: Best file extension
#     '''

#     # Retrieve content type
#     content_type = headers['Content-Type']

#     # Get best file type and extension, list originally based on
#     # https://github.com/RDFLib/rdflib/blob/main/rdflib/parser.py#L237
#     # and extended based on further RDFLib documentation
#     if 'text/html' in content_type:
#         file_type = 'rdfa'
#         file_extension = 'html'
#     elif 'application/xhtml+xml' in content_type:
#         file_type = 'rdfa'
#         file_extension = 'xhtml'
#     elif 'application/rdf+xml' in content_type:
#         file_type = 'xml'
#         file_extension = 'xml'
#     elif 'text/n3' in content_type:
#         file_type = 'n3'
#         file_extension = 'n3'
#     elif 'text/turtle' in content_type or 'application/x-turtle' in content_type:
#         file_type = 'turtle'
#         file_extension = 'ttl'
#     elif 'application/trig' in content_type:
#         file_type = 'trig'
#         file_extension = 'trig'
#     elif 'application/trix' in content_type:
#         file_type = 'trix'
#         file_extension = 'trix'
#     elif 'application/n-quads' in content_type:
#         file_type = 'nquads'
#         file_extension = 'nq'
#     elif 'application/ld+json' in content_type:
#         file_type = 'json-ld'
#         file_extension = 'jsonld'
#     elif 'application/json' in content_type:
#         file_type = 'json-ld'
#         file_extension = 'json'
#     elif 'application/hex+x-ndjson' in content_type:
#         file_type = 'hext'
#         file_extension = 'hext'
#     elif 'text/plain' in content_type:
#         file_type = 'nt'
#         file_extension = 'nt'

#     # Non-RDF file types that may be useful
#     # When you add a file type here, make sure you also list it in the config dictionary
#     elif 'application/xml' in content_type:
#         file_type = 'lido'
#         file_extension = 'xml'
#     else:
#         raise Exception('Hydra Scraper does not recognise this file type.')

#     # Return file extension or type
#     if getFileExtension == True:
#         return file_extension
#     else:
#         return file_type


#------------------------------------------------------------------

# # Import libraries
# from rdflib import Graph, Namespace
# from math import ceil
# from time import sleep

# # Import script modules
# from helpers.config import *
# from helpers.download import download_file
# from helpers.fileio import save_file
# from helpers.fileio import save_list
# from helpers.status import echo_progress

# # Define namespaces
# from rdflib.namespace import RDF
# HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
# SCHEMA = Namespace('http://schema.org/')


# # Base class for a Hydra API to process
# class Hydra:


#     # Variables
#     status = []
#     populated = None
#     triples = Graph()
#     triples.bind('hydra', HYDRA)
#     triples.bind('schema', SCHEMA)
#     resources = []
#     target_folder = ''
#     entry_point_url = ''
#     content_type = ''
#     current_list_url = ''
#     next_list_url = ''
#     final_list_url = ''
#     number_of_resources = 0
#     resources_per_list = 0
#     number_of_lists = 0


#     def __init__(self, target_folder:str, entry_point_url:str, content_type:str = ''):
#         '''
#         Sets up a Hydra entry point to process

#             Parameters:
#                 target_folder (str): Name of the downloads subfolder to store files in
#                 entry_point_url (str): URL to use as an entry point for a scraping run
#                 content_type (str, optional): Content type to request when retrieving resources, defaults to none
#         '''

#         # Assign variables
#         self.target_folder = is actually command.target_folder
#         self.entry_point_url = entry_point_url
#         self.content_type = content_type
#         self.current_list_url = entry_point_url
#         self.next_list_url = entry_point_url


#     def __str__(self):
#         '''
#         String representation of instances of this object
#         '''

#         # Put together a string
#         if self.populated == None:
#             return 'Hydra entry point to be scraped at ' + self.entry_point_url
#         elif self.populated == False:
#             return 'Hydra entry point at ' + self.entry_point_url + ' being processed'
#         elif self.populated == True:
#             return 'Processed Hydra entry point at ' + self.entry_point_url


#     def __modify_resource_urls(self, resource_url_filter:str = '', resource_url_replace:str = '', resource_url_replace_with:str = '', resource_url_add:str = ''):
#         '''
#         Mofifies the list of individual resource URLs on demand

#             Parameters:
#                 resources (list): List of resource URLs to modify
#                 resource_url_filter (str, optional): String applied to filter resource URLs, defaults to an empty string
#                 resource_url_replace (str, optional): String to replace in listed URLs before retrieving a resource, defaults to an empty string
#                 resource_url_replace_with (str, optional): String to use as a replacement before retrieving a resource, defaults to an empty string
#                 resource_url_add (str, optional): String to add to each URL before retrieving a resource, defaults to an empty string
#         '''

#         # Empty list for revised URLs
#         modified_resources = []

#         # Check each URL in the list
#         for url in self.resources:
#             if resource_url_filter != '':
#                 if resource_url_filter not in url:
#                     url = ''
#             if url != '':
#                 if resource_url_replace != '':
#                     url = url.replace(resource_url_replace, resource_url_replace_with)
#                 if resource_url_add != '':
#                     url = url + resource_url_add
#                 modified_resources.append(url)
            
#         # Use the revised URLs instead of the original
#         self.resources = modified_resources


#     def __get_triple(self, graph:object, predicate:str, list_items:bool = False) -> str | int:
#         '''
#         Helper function to return a single object or a list of objects from triples

#             Parameters:
#                 graph (object): Graph to perform the get request on
#                 predicate (str): Predicate to find in all triples
#                 list_items (bool, optional): Switch to determine whether to return a list or a single item, defaults to False

#             Returns:
#                 str | int: Last object string identified by the predicate
#         '''

#         # Find triples
#         triples = graph.objects(None, predicate, unique=True)

#         # Find a single item
#         if list_items == False:
#             result = ''
#             for triple in triples:
#                 result = triple.toPython()

#         # Find a list of items
#         else:
#             result = []
#             for triple in triples:
#                 result.append(triple.toPython())

#         # Return the result
#         return result


#     def populate(self, save_original_files:bool = True, resource_url_filter:str = '', resource_url_replace:str = '', resource_url_replace_with:str = '', resource_url_add:str = ''):
#         '''
#         Pages through the Hydra API, populates the object, and optionally stores the original files in the process

#             Parameters:
#                 save_original_files (bool, optional): Switch to also save original files on download, defaults to True
#                 resource_url_filter (str, optional): String applied to filter resource URLs, defaults to an empty string
#                 resource_url_replace (str, optional): String to replace in resource URLs, defaults to an empty string
#                 resource_url_replace_with (str, optional): String to use as a replacement in resource URLs, defaults to an empty string
#                 resource_url_add (str, optional): String to add to each resource URL, defaults to an empty string
#         '''

#         # Notify object that it is being populated
#         self.populated = False

#         # Provide initial status
#         status_report = {
#             'success': True,
#             'reason': 'All lists retrieved successfully.'
#         }

#         # Main loop to retrieve list files
#         number = 0
#         while self.current_list_url != self.final_list_url:
#             number += 1

#             # Retrieve file
#             hydra = download_file(self.next_list_url, self.content_type)
#             if hydra != None:

#                 # Optionally save file
#                 if save_original_files:
#                     file_folder = self.target_folder + '/lists'
#                     common.create_folder(file_folder)
#                     file_path = file_folder + '/' + str(number) + '.' + hydra['file_extension']
#                     save_file(hydra['content'], file_path)
#                     status_report['reason'] = 'All lists saved to download folder.'

#             # Throw error if list file is missing
#             else:
#                 status_report['success'] = False
#                 status_report['reason'] = 'One of the paginated lists is not available.'
#                 break

#             # Add triples to object storage
#             try:
#                 hydra_triples = Graph()
#                 hydra_triples.bind('hydra', HYDRA)
#                 hydra_triples.bind('schema', SCHEMA)
#                 hydra_triples.parse(data=hydra['content'], format=hydra['file_type'])
#             except:
#                 status_report['success'] = False
#                 status_report['reason'] = 'The Hydra API could not be parsed as RDF-style data.'
#                 break

#             # Add each individual resource URL to main resource list
#             self.resources.extend(self.__get_triple(hydra_triples, HYDRA.member, True))
#             self.resources.extend(self.__get_triple(hydra_triples, SCHEMA.item, True))

#             # Get total number of items per list (only makes sense on first page)
#             if number == 1:
#                 if len(self.resources) != 0:
#                     self.resources_per_list = len(self.resources)
#                 else:
#                     status_report['success'] = False
#                     status_report['reason'] = 'The Hydra API does not contain any resources.'
#                     break

#             # Retrieve URL of current, next, and final list
#             self.current_list_url = self.__get_triple(hydra_triples, HYDRA.view)
#             self.next_list_url = self.__get_triple(hydra_triples, HYDRA.next)
#             self.final_list_url = self.__get_triple(hydra_triples, HYDRA.last)

#             # Throw error if the API is paginated but there is no final list
#             if self.next_list_url != '' and self.final_list_url == '':
#                 status_report['success'] = False
#                 status_report['reason'] = 'The Hydra API is paginated but does not specify a final list.'
#                 break

#             # Get total number of resources and calculate number of lists
#             self.number_of_resources = int(self.__get_triple(hydra_triples, HYDRA.totalItems))
#             self.number_of_lists = int(ceil(self.number_of_resources / self.resources_per_list))

#             # Remove pagination info from triples, but leave HYDRA.collection and HYDRA.member intact
#             hydra_triples.remove((None, HYDRA.totalItems, None))
#             hydra_triples.remove((None, HYDRA.view, None))
#             hydra_triples.remove((None, HYDRA.first, None))
#             hydra_triples.remove((None, HYDRA.last, None))
#             hydra_triples.remove((None, HYDRA.next, None))
#             hydra_triples.remove((None, HYDRA.previous, None))
#             hydra_triples.remove((None, RDF.type, HYDRA.PartialCollectionView))

#             # Add list triples to object triples
#             self.triples += hydra_triples

#             # Delay next retrieval to avoid a server block
#             echo_progress('Retrieving API lists', number, self.number_of_lists)
#             sleep(command.retrieval_delay)

#             # Get out of loop if there is no next page
#             if self.next_list_url == '':
#                 break

#             # Throw error if maximum number of lists is reached as a safety net
#             if number > command.max_number_of_paginated_lists:
#                 status_report['success'] = False
#                 status_report['reason'] = 'Maximum number of allowed lists was reached.'
#                 break

#         # Filter, replace or augment strings in resource URLs if requested
#         if resource_url_filter != '' or resource_url_replace != '' or resource_url_add != '':
#             self.__modify_resource_urls(resource_url_filter, resource_url_replace, resource_url_replace_with, resource_url_add)

#         # Notify object that it is populated
#         self.populated = True

#         # Provide final status
#         self.status.append(status_report)


#     def save_beacon(self, file_name:str = 'beacon'):
#         '''
#         Lists all individual resources in a beacon file

#             Parameters:
#                 file_name (str, optional): Name of the beacon file without a file extension, defaults to 'beacon'
#         '''

#         # Provide initial status
#         status_report = {
#             'success': False,
#             'reason': ''
#         }

#         # Prevent routine if object is not populated yet
#         if self.populated != True:
#             status_report['reason'] = 'A beacon file can only be written when the API was read.'
#         else:

#             # Initial progress
#             echo_progress('Saving beacon file', 0, 100)

#             # Save file if there are resources
#             if self.resources != []:
#                 file_path = self.target_folder + '/' + file_name + '.txt'
#                 save_list(file_path, self.resources)

#                 # Compile success status
#                 status_report['success'] = True
#                 status_report['reason'] = 'All resources listed in a beacon file.'

#             # Report if there are no resources
#             else:
#                 status_report['reason'] = 'No resources to list in a beacon file.'

#             # Final progress
#             echo_progress('Saving beacon file', 100, 100)

#         # Provide final status
#         self.status.append(status_report)


#     def save_triples(self, triple_filter:str = 'none', file_name:str = 'lists'):
#         '''
#         Saves all downloaded triples into a single Turtle file

#             Parameters:
#                 triple_filter (str, optional): Name of a filter (e.g. 'cgif') to apply to triples before saving them, default to 'none'
#                 file_name (str, optional): Name of the triple file without a file extension, defaults to 'lists'
#         '''

#         # Provide initial status
#         status_report = {
#             'success': False,
#             'reason': ''
#         }

#         # Prevent routine if object is not populated yet
#         if self.populated != True:
#             status_report['reason'] = 'A list of triples can only be written when the API was read.'
#         else:

#             # Generate filter description to use in status updates
#             filter_description = ''
#             if triple_filter == 'cgif':
#                 filter_description = 'CGIF-filtered '

#             # Optionally filter CGIF triples
#             if triple_filter == 'cgif':
#                 # TODO Add CGIF filters here
#                 filtered_triples = self.triples

#             # Initial progress
#             echo_progress('Saving list of ' + filter_description + 'API triples', 0, 100)

#             # Compile file if there are triples
#             if len(self.triples):
#                 file_path = self.target_folder + '/' + file_name + '.ttl'
#                 if triple_filter == 'cgif':
#                     filtered_triples.serialize(destination=file_path, format='turtle')
#                 else:
#                     self.triples.serialize(destination=file_path, format='turtle')

#                 # Compile success status
#                 status_report['success'] = True
#                 status_report['reason'] = 'All ' + filter_description + 'API triples listed in a Turtle file.'

#             # Report if there are no resources
#             else:
#                 status_report['reason'] = 'No ' + filter_description + 'API triples to list in a Turtle file.'

#             # Final progress
#             echo_progress('Saving list of ' + filter_description + 'API triples', 100, 100)

#         # Provide final status
#         self.status.append(status_report)

# -----------------------------------------------------------------------

# # Import libraries
# from rdflib import Graph, Namespace
# from time import sleep

# # Import script modules
# from helpers.config import *
# from helpers.convert import convert_lido_to_cgif
# from helpers.convert import convert_triples_to_table
# from helpers.download import download_file
# from helpers.download import retrieve_local_file
# from helpers.fileio import read_list
# from helpers.fileio import read_folder
# from helpers.fileio import save_file
# from helpers.fileio import save_table
# from helpers.status import echo_progress

# # Define namespaces
# SCHEMA = Namespace('http://schema.org/')

# # Base class for a beacon list to process
# class Beacon:


#     # Variables
#     status = []
#     populated = None
#     triples = Graph()
#     triples.bind('schema', SCHEMA)
#     resources = []
#     resources_from_folder = False
#     content_type = ''
#     target_folder = ''
#     number_of_resources = 0
#     missing_resources = 0
#     missing_resources_list = []
#     incompatible_resources = 0
#     incompatible_resources_list = []


#     def __init__(self, target_folder:str, content_type:str = '', resources:list = []):
#         '''
#         Sets up a list of resources to process

#             Parameters:
#                 target_folder (str): Name of the downloads subfolder to store files in
#                 content_type (str, optional): Content type to request when retrieving resources, defaults to none
#                 resources (list, optional): List of resources to retrieve, defaults to empty list
#         '''

#         # Assign variables
#         self.target_folder = is actually command.target_folder
#         self.content_type = content_type
#         self.resources = resources


#     def __str__(self):
#         '''
#         String representation of instances of this object
#         '''

#         # Put together a string
#         if self.populated == None:
#             return 'List of individual resources to be retrieved'
#         elif self.populated == False:
#             return 'List of individual resources currently being processed'
#         elif self.populated == True:
#             return 'Processed list of individual resources'


#     def populate(self, save_original_files:bool = True, clean_resource_urls:list = [], beacon_file:str = '', local_folder:str = '', supplement_data_feed:str = '', supplement_data_catalog:str = '', supplement_data_catalog_publisher:str = ''):
#         '''
#         Retrieves all individual resources from the list, populates the object, and optionally stores the original files in the process

#             Parameters:
#                 save_original_files (bool, optional): Switch to also save original files on download, defaults to True
#                 clean_resource_urls (list, optional): List of substrings to remove in the resource URLs to produce a resource's file name, defaults to empty list that enumerates resources
#                 beacon_file (str, optional): Path to the beacon file to process, defaults to an empty string
#                 local_folder (str, optional): Path to a local folder with an existing file dump to process, defaults to an empty string
#                 supplement_data_feed (str, optional): URI of a data feed to bind LIDO files to (defaults to none)
#                 supplement_data_catalog (str, optional): URI of a data catalog that the data feed belongs to (defaults to none)
#                 supplement_data_catalog_publisher (str, optional): URI of the publisher of the data catalog (defaults to none)
#         '''

#         # Notify object that it is being populated
#         self.populated = False

#         # Provide initial status
#         status_report = {
#             'success': True,
#             'reason': 'All resources retrieved successfully.'
#         }
#         echo_progress('Retrieving individual resources', 0, 100)

#         # If requested, get list of individual resources from beacon file
#         if beacon_file != '':
#             self.resources = read_list(beacon_file)

#         # If requested, get list of individual resources from local folder
#         elif local_folder != '':
#             self.resources = read_folder(local_folder)
#             self.resources_from_folder = True

#         # Throw error if resource list is empty
#         if self.resources == []:
#             status_report['success'] = False
#             status_report['reason'] = 'There were no resources to retrieve.'

#         # Count number of resources
#         else:
#             self.number_of_resources = len(self.resources)

#             # Main loop to retrieve resource files
#             for number, resource_url in enumerate(self.resources, start = 1):

#                 # Retrieve file
#                 if self.resources_from_folder == True:
#                     resource = retrieve_local_file(resource_url, self.content_type)
#                 else:
#                     resource = download_file(resource_url, self.content_type)
#                 if resource != None:

#                     # Optionally save file
#                     if save_original_files:
#                         file_folder = self.target_folder + '/resources'
#                         common.create_folder(file_folder)

#                         # Clean up file name if required
#                         if clean_resource_urls == []:
#                             file_name = str(number)
#                         else:
#                             file_name = resource_url
#                             for clean_resource_url in clean_resource_urls:
#                                 file_name = file_name.replace(clean_resource_url, '')

#                         # Save file
#                         file_path = file_folder + '/' + file_name + '.' + resource['file_extension']
#                         save_file(resource['content'], file_path)
#                         status_report['reason'] = 'All resources saved to download folder.'

#                 # Report if download failed
#                 else:
#                     self.missing_resources += 1
#                     self.missing_resources_list.append(resource_url)
#                     continue

#                 # Add triples to object storage from RDF sources
#                 if resource['file_type'] not in command.allowed_non_rdf_formats:
#                     try:
#                         self.triples.parse(data=resource['content'], format=resource['file_type'])
#                     except:
#                         self.incompatible_resources += 1
#                         self.incompatible_resources_list.append(resource_url)
#                         continue

#                 # Add triples to object storage from LIDO sources
#                 elif resource['file_type'] == 'lido':
#                     lido_cgif = convert_lido_to_cgif(resource['content'], supplement_data_feed, supplement_data_catalog, supplement_data_catalog_publisher)
#                     if lido_cgif != None:
#                         self.triples += lido_cgif
#                     else:
#                         self.incompatible_resources += 1
#                         self.incompatible_resources_list.append(resource_url)

#                 # Delay next retrieval to avoid a server block
#                 echo_progress('Retrieving individual resources', number, self.number_of_resources)
#                 if self.resources_from_folder == False:
#                     sleep(command.retrieval_delay)

#             # Report any failed state
#             if self.missing_resources >= self.number_of_resources:
#                 status_report['success'] = False
#                 status_report['reason'] = 'All resources were missing.'
#             elif self.missing_resources > 0 and self.incompatible_resources > 0:
#                 status_report['reason'] = 'Resources retrieved, but ' + str(self.missing_resources) + ' were missing and ' + str(self.incompatible_resources) + ' were not compatible.'
#                 status_report['missing'] = self.missing_resources_list
#                 status_report['incompatible'] = self.incompatible_resources_list
#             elif self.missing_resources > 0:
#                 status_report['reason'] = 'Resources retrieved, but ' + str(self.missing_resources) + ' were missing.'
#                 status_report['missing'] = self.missing_resources_list
#             elif self.incompatible_resources > 0:
#                 status_report['reason'] = 'Resources retrieved, but ' + str(self.incompatible_resources) + ' were not compatible.'
#                 status_report['incompatible'] = self.incompatible_resources_list

#         # Notify object that it is populated
#         self.populated = True

#         # Provide final status
#         self.status.append(status_report)


#     def save_triples(self, triple_filter:str = 'none', file_name:str = 'resources'):
#         '''
#         Saves all downloaded triples into a single Turtle file

#             Parameters:
#                 triple_filter (str, optional): Name of a filter (e.g. 'cgif') to apply to triples before saving them, default to 'none'
#                 file_name (str, optional): Name of the triple file without a file extension, defaults to 'resources'
#         '''

#         # Provide initial status
#         status_report = {
#             'success': False,
#             'reason': ''
#         }

#         # Prevent routine if object is not populated yet
#         if self.populated != True:
#             status_report['reason'] = 'A list of triples can only be written when the resources were read.'
#         else:

#             # Generate filter description to use in status updates
#             filter_description = ''
#             if triple_filter == 'cgif':
#                 filter_description = 'CGIF-filtered '

#             # Optionally filter CGIF triples
#             if triple_filter == 'cgif':
#                 # TODO Add CGIF filters here
#                 filtered_triples = self.triples

#             # Initial progress
#             echo_progress('Saving list of ' + filter_description + 'resource triples', 0, 100)

#             # Compile file if there are triples
#             if len(self.triples):
#                 file_path = self.target_folder + '/' + file_name + '.ttl'
#                 if triple_filter == 'cgif':
#                     filtered_triples.serialize(destination=file_path, format='turtle')
#                 else:
#                     self.triples.serialize(destination=file_path, format='turtle')

#                 # Compile success status
#                 status_report['success'] = True
#                 status_report['reason'] = 'All ' + filter_description + 'resource triples listed in a Turtle file.'

#             # Report if there are no resources
#             else:
#                 status_report['reason'] = 'No ' + filter_description + 'resource triples to list in a Turtle file.'

#             # Final progress
#             echo_progress('Saving list of ' + filter_description + 'resource triples', 100, 100)

#         # Provide final status
#         self.status.append(status_report)


#     def save_table(self, table_data:list = [], file_name:str = 'resources'):
#         '''
#         Saves specified data from all downloaded triples into a single CSV file

#             Parameters:
#                 table_data (list, optional): List of properties to save, defaults to all
#                 file_name (str, optional): Name of the table file without a file extension, defaults to 'resources'
#         '''

#         # Provide initial status
#         status_report = {
#             'success': False,
#             'reason': ''
#         }

#         # Prevent routine if object is not populated yet
#         if self.populated != True:
#             status_report['reason'] = 'A data table can only be written when the resources were read.'
#         else:

#             # Initial progress
#             echo_progress('Saving table from resource data', 0, 100)

#             # Compile table if there are triples
#             if len(self.triples):
#                 file_path = self.target_folder + '/' + file_name
#                 tabular_data = convert_triples_to_table(self.triples, table_data)
#                 save_table(tabular_data, file_path)

#                 # Compile success status
#                 status_report['success'] = True
#                 status_report['reason'] = 'Resource data listed in a table.'

#             # Report if there are no resources
#             else:
#                 status_report['reason'] = 'No resource data to list in a table.'

#             # Final progress
#             echo_progress('Saving table from resource data', 100, 100)

#         # Provide final status
#         self.status.append(status_report)
