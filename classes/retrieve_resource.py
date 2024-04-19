# Class to retrieve individual resource files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries

# Import script modules
from classes.retrieve import *


class HydraRetrieveResource(HydraRetrieve):

    # Variables
    something = None


    def __init__(self, command, output, report, morph):
        '''
        Retrieve individual resource files

            Parameters:
                command (str): ???
                output (str): ???
                report (str): ???
                morph (str): ???
        '''

        # Assign variables
        self.something = something


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        return self.something


    def _determine_file_type(self, headers:dict, getFileExtension:bool = False) -> str:
        '''
        Determines the best file type and extension based on the server response

            Parameters:
                headers (dict): Headers of the server response as a dictionary
                getFileExtension (bool): Determines whether the type or the extension is returned
            
            Returns:
                str: Best file extension
        '''

        # Retrieve content type
        content_type = headers['Content-Type']

        # Get best file type and extension, list originally based on
        # https://github.com/RDFLib/rdflib/blob/main/rdflib/parser.py#L237
        # and extended based on further RDFLib documentation
        if 'text/html' in content_type:
            file_type = 'rdfa'
            file_extension = 'html'
        elif 'application/xhtml+xml' in content_type:
            file_type = 'rdfa'
            file_extension = 'xhtml'
        elif 'application/rdf+xml' in content_type:
            file_type = 'xml'
            file_extension = 'xml'
        elif 'text/n3' in content_type:
            file_type = 'n3'
            file_extension = 'n3'
        elif 'text/turtle' in content_type or 'application/x-turtle' in content_type:
            file_type = 'turtle'
            file_extension = 'ttl'
        elif 'application/trig' in content_type:
            file_type = 'trig'
            file_extension = 'trig'
        elif 'application/trix' in content_type:
            file_type = 'trix'
            file_extension = 'trix'
        elif 'application/n-quads' in content_type:
            file_type = 'nquads'
            file_extension = 'nq'
        elif 'application/ld+json' in content_type:
            file_type = 'json-ld'
            file_extension = 'jsonld'
        elif 'application/json' in content_type:
            file_type = 'json-ld'
            file_extension = 'json'
        elif 'application/hex+x-ndjson' in content_type:
            file_type = 'hext'
            file_extension = 'hext'
        elif 'text/plain' in content_type:
            file_type = 'nt'
            file_extension = 'nt'

        # Non-RDF file types that may be useful
        # When you add a file type here, make sure you also list it in the config dictionary
        elif 'application/xml' in content_type:
            file_type = 'lido'
            file_extension = 'xml'
        else:
            raise Exception('Hydra Scraper does not recognise this file type.')

        # Return file extension or type
        if getFileExtension == True:
            return file_extension
        else:
            return file_type


    def convert_lido_to_cgif(self, lido:str, supplement_data_feed:str = '', supplement_data_catalog:str = '', supplement_data_catalog_publisher:str = '') -> Graph:
        '''
        Converts a LIDO file to CGIF triples and returns them as a Graph object

            Parameters:
                lido (str): The content of the LIDO file to convert
                supplement_data_feed (str, optional): URI of a data feed to bind LIDO files to (defaults to none)
                supplement_data_catalog (str, optional): URI of a data catalog that the data feed belongs to (defaults to none)
                supplement_data_catalog_publisher (str, optional): URI of the publisher of the data catalog (defaults to none)

            Returns:
                Graph: object containing the CGIF triples
        '''

        # Set up an object to store CGIF triples
        cgif_triples = Graph()
        cgif_triples.bind('schema', SCHEMA)

        # Parse LIDO files as XML and retrieve resource URI
        try:
            lido_root = etree.fromstring(bytes(lido, encoding='utf8'))
            resource = URIRef(lido_root.findtext('.//{http://www.lido-schema.org}recordInfoLink'))

            # RDF.type
            cgif_triples.add((resource, RDF.type, SCHEMA.VisualArtwork))

            # SCHEMA.isPartOf
            if supplement_data_feed != '':
                cgif_triples.add((resource, SCHEMA.isPartOf, URIRef(supplement_data_feed)))
                cgif_triples.add((URIRef(supplement_data_feed), RDF.type, SCHEMA.DataFeed))
                cgif_triples.add((URIRef(supplement_data_feed), RDF.type, SCHEMA.Dataset))
                cgif_triples.add((URIRef(supplement_data_feed), RDF.type, SCHEMA.URL))
                cgif_triples.add((URIRef(supplement_data_feed), SCHEMA.url, URIRef(supplement_data_feed)))

                # Add information on data catalog
                if supplement_data_catalog != '':
                    cgif_triples.add((URIRef(supplement_data_feed), SCHEMA.includedInDataCatalog, URIRef(supplement_data_catalog)))
                    cgif_triples.add((URIRef(supplement_data_catalog), RDF.type, SCHEMA.DataCatalog))

                    # Add information on publisher of data catalog
                    if supplement_data_catalog_publisher != '':
                        cgif_triples.add((URIRef(supplement_data_catalog), SCHEMA.publisher, URIRef(supplement_data_catalog_publisher)))

            # Go into the "descriptiveMetadata" section
            for lido_descriptive in lido_root.iterfind('.//{http://www.lido-schema.org}descriptiveMetadata'):

                # SCHEMA.name
                schema_names = lido_descriptive.iterfind('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}titleWrap/{http://www.lido-schema.org}titleSet/{http://www.lido-schema.org}appellationValue')
                for schema_name in schema_names:
                    language = self._convert_lido_to_cgif_with_language(schema_name)
                    if language != None:
                        cgif_triples.add((resource, SCHEMA.name, Literal(schema_name.text, lang = language)))
                    else:
                        cgif_triples.add((resource, SCHEMA.name, Literal(schema_name.text)))

                # SCHEMA.contentLocation
                schema_content_location = lido_descriptive.findtext('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}repositoryWrap/{http://www.lido-schema.org}repositorySet/{http://www.lido-schema.org}repositoryLocation/{http://www.lido-schema.org}placeID[@{http://www.lido-schema.org}type="http://terminology.lido-schema.org/lido00099"]')
                if schema_content_location != None:
                    cgif_triples.add((resource, SCHEMA.contentLocation, URIRef(schema_content_location)))
                    cgif_triples.add((URIRef(schema_content_location), RDF.type, SCHEMA.LandmarksOrHistoricalBuildings))

                # SCHEMA.keywords: get work type, subjects, and location
                schema_keywords = set()
                schema_keywords.update(self._convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectClassificationWrap/{http://www.lido-schema.org}objectWorkTypeWrap/{http://www.lido-schema.org}objectWorkType'))
                schema_keywords.update(self._convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectRelationWrap/{http://www.lido-schema.org}subjectWrap/{http://www.lido-schema.org}subjectSet/{http://www.lido-schema.org}subject/{http://www.lido-schema.org}subjectConcept'))
                schema_keywords.add(schema_content_location)

                # SCHEMA.keywords: write property
                for schema_keyword in schema_keywords:
                    if schema_keyword != None:
                        cgif_triples.add((resource, SCHEMA.keywords, URIRef(schema_keyword)))
                        for known_defined_term_set in self.command.known_defined_term_sets:
                            if known_defined_term_set in schema_keyword:
                                cgif_triples.add((URIRef(schema_keyword), SCHEMA.inDefinedTermSet, URIRef(known_defined_term_set)))
                                cgif_triples.add((URIRef(known_defined_term_set), RDF.type, SCHEMA.DefinedTermSet))

                # SCHEMA.temporalCoverage: get start and end of earliest event
                schema_temporal_coverage_start = None
                schema_temporal_coverage_end = None
                schema_temporal_coverage_elements = lido_descriptive.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}earliestDate')
                for schema_temporal_coverage_element in schema_temporal_coverage_elements:
                    if schema_temporal_coverage_start == None:
                        schema_temporal_coverage_start = date.fromisoformat(schema_temporal_coverage_element.text)
                        schema_temporal_coverage_end = date.fromisoformat(schema_temporal_coverage_element.getparent().findtext('.//{http://www.lido-schema.org}latestDate'))
                    elif schema_temporal_coverage_start > date.fromisoformat(schema_temporal_coverage_element.text):
                        schema_temporal_coverage_start = date.fromisoformat(schema_temporal_coverage_element.text)
                        schema_temporal_coverage_end = date.fromisoformat(schema_temporal_coverage_element.getparent().findtext('.//{http://www.lido-schema.org}latestDate'))

                # SCHEMA.temporalCoverage: write property
                if schema_temporal_coverage_start != None and schema_temporal_coverage_end != None:
                    schema_temporal_coverage = schema_temporal_coverage_start.isoformat() + 'T00:00:00/' + schema_temporal_coverage_end.isoformat() + 'T23:59:59'
                    cgif_triples.add((resource, SCHEMA.temporalCoverage, Literal(schema_temporal_coverage, datatype = SCHEMA.DateTime)))

            # Go into the "descriptiveMetadata" section
            for lido_administrative in lido_root.iterfind('.//{http://www.lido-schema.org}administrativeMetadata'):

                # SCHEMA.dateModified
                schema_date_modified = lido_administrative.findtext('.//{http://www.lido-schema.org}recordWrap/{http://www.lido-schema.org}recordInfoSet/{http://www.lido-schema.org}recordMetadataDate')
                if schema_date_modified != None:
                    cgif_triples.add((resource, SCHEMA.dateModified, Literal(schema_date_modified, datatype = SCHEMA.Date)))

                # SCHEMA.license: get all relevant licences
                schema_licences = set()
                schema_licences.update(self._convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsWorkSet/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self._convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}recordRights/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self._convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}rightsType'))

                # SCHEMA.license: write property
                for schema_licence in schema_licences:
                    if schema_licence != None:
                        cgif_triples.add((resource, SCHEMA.license, URIRef(schema_licence)))
                        cgif_triples.add((URIRef(schema_licence), RDF.type, SCHEMA.URL))

                # SCHEMA.width/SCHEMA.contentUrl: identify largest representation
                schema_width = 0
                schema_width_unit = ''
                schema_content_url = None
                schema_width_elements = lido_administrative.iterfind('.//{http://www.lido-schema.org}resourceWrap/{http://www.lido-schema.org}resourceSet/{http://www.lido-schema.org}resourceRepresentation/{http://www.lido-schema.org}resourceMeasurementsSet/{http://www.lido-schema.org}measurementValue')
                for schema_width_element in schema_width_elements:
                    if int(schema_width_element.text) > schema_width:

                        # Retrieve width, its unit, and content URL
                        schema_width = int(schema_width_element.text)
                        schema_width_unit = schema_width_element.getparent().find('.//{http://www.lido-schema.org}measurementUnit').xpath('string()')
                        schema_content_url = schema_width_element.getparent().getparent().findtext('.//{http://www.lido-schema.org}linkResource')

                # SCHEMA.width/SCHEMA.contentUrl: write SCHEMA.width
                if schema_width != 0:
                    if 'px' in schema_width_unit or 'pixel' in schema_width_unit or 'Pixel' in schema_width_unit:
                        schema_width_unit = ' px'
                    else:
                        schema_width_unit = ''
                    schema_width = str(schema_width) + schema_width_unit
                    cgif_triples.add((resource, SCHEMA.width, Literal(schema_width, datatype = SCHEMA.Distance)))

                # SCHEMA.width/SCHEMA.contentUrl: write SCHEMA.contentUrl
                if schema_content_url != None:
                    cgif_triples.add((resource, SCHEMA.contentUrl, URIRef(schema_content_url)))

                # SCHEMA.creditText
                schema_credit_texts = lido_administrative.iterfind('.//{http://www.lido-schema.org}resourceWrap/{http://www.lido-schema.org}resourceSet/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}creditLine')
                for schema_credit_text in schema_credit_texts:
                    cgif_triples.add((resource, SCHEMA.creditText, Literal(schema_credit_text.text)))

                # SCHEMA.creator
                schema_creators = lido_administrative.iterfind('.//{http://www.lido-schema.org}recordWrap/{http://www.lido-schema.org}recordSource/{http://www.lido-schema.org}legalBodyID')
                for schema_creator in schema_creators:
                    cgif_triples.add((resource, SCHEMA.creator, URIRef(schema_creator.text)))
                    cgif_triples.add((URIRef(schema_creator.text), RDF.type, SCHEMA.Organization))
                    schema_creator_name = schema_creator.getparent().find('.//{http://www.lido-schema.org}legalBodyName/{http://www.lido-schema.org}appellationValue')
                    if schema_creator_name != None:
                        language = self._convert_lido_to_cgif_with_language(schema_creator_name)
                        if language != None:
                            cgif_triples.add((URIRef(schema_creator.text), SCHEMA.name, Literal(schema_creator_name.text, lang = language)))
                        else:
                            cgif_triples.add((URIRef(schema_creator.text), SCHEMA.name, Literal(schema_creator_name.text)))
                    schema_creator_website = schema_creator.getparent().findtext('.//{http://www.lido-schema.org}legalBodyWeblink')
                    if schema_creator_website != None:
                        cgif_triples.add((URIRef(schema_creator.text), SCHEMA.url, URIRef(schema_creator_website)))

        # Empty variable if content does not parse
        except:
            cgif_triples = None

        # Return Graph object containing CGIF triples
        return cgif_triples


    def _convert_lido_to_cgif_with_language(self, language_element:any) -> str:
        '''
        Retrieves the language of a given LIDO element

            Parameters:
                language_element (any): Element of a parsed LIDO document

            Returns:
                str: The language code of the element
        '''

        # Set up empty language variable
        language = None

        # Check for language tags and escalate inquiry to parent elements if necessary
        while language == None and language_element != None:
            if '{http://www.w3.org/XML/1998/namespace}lang' in language_element.attrib:
                language = language_element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            else:
                language_element = language_element.getparent()

        # Return language variable
        return language


    def _convert_lido_to_cgif_with_concepts(self, lido_root:any, element_path:str) -> list:
        '''
        Finds a LIDO concept IDs in an element tree according to LIDO 1.0 or 1.1

            Parameters:
                lido_root (any): The parsed LIDO document
                element_path (str): The initial segment of the element path to look for concept IDs

            Returns:
                list: A list of concept IDs
        '''

        # Set up empty set
        concept_ids = set()

        # Find concept IDs according to LIDO 1.0
        concept_list = lido_root.iterfind(element_path + '/{http://www.lido-schema.org}conceptID')
        for concept_entry in concept_list:
            concept_ids.add(concept_entry.text)

        # Find concept IDs according to LIDO 1.1
        concept_list = lido_root.iterfind(element_path + '/{http://www.w3.org/2004/02/skos/core#}Concept[@{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about]')
        for concept_entry in concept_list:
            concept_ids.add(concept_entry.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'])

        # Return the set of IDs
        return concept_ids




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
#                 save_csv(tabular_data, file_path)

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
