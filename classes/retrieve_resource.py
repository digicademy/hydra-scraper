# Class to retrieve individual resource files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date
from lxml import etree
from rdflib import Graph
from time import sleep

# Import script modules
from classes.retrieve import *

# # Define namespaces
from rdflib.namespace import SDO


class HydraRetrieveResource(HydraRetrieve):

    # Variables
    resources = []
    store = None


    # READ ####################################################################


    def __init__(self, report:object):
        '''
        Retrieve individual resource files

            Parameters:
                report (object): The report object to use
        '''

        # Inherit from base class
        super().__init__(report)


#     content_type = ''
#     target_folder = ''
#     number_of_resources = 0
#     missing_resources = 0
#     missing_resources_list = []
#     incompatible_resources = 0
#     incompatible_resources_list = []


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


    def __list_files_in_folder(self, folder_path:str) -> list:
        '''
        Reads a local folder and returns each file name as a list

            Parameters:
                folder_path (str): Path to the folder to read

            Returns:
                list: List of individual file names
        '''

        # Prepare folder path and empty list
        folder_path = folder_path + '/**/*'
        entries = []

        # Add each file to list
        for file_path in glob(folder_path, recursive = True):
            entries.append(file_path)

        # Return list
        return entries


    # STRING ##################################################################


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if len(self.resources) > 0:
            return 'Resource retriever for ' + str(len(self.resources)) + ' files.'
        else:
            return 'Empty resource retriever.'


    # MORPH ###################################################################


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
                    language = self.__convert_lido_to_cgif_with_language(schema_name)
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
                schema_keywords.update(self.__convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectClassificationWrap/{http://www.lido-schema.org}objectWorkTypeWrap/{http://www.lido-schema.org}objectWorkType'))
                schema_keywords.update(self.__convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectRelationWrap/{http://www.lido-schema.org}subjectWrap/{http://www.lido-schema.org}subjectSet/{http://www.lido-schema.org}subject/{http://www.lido-schema.org}subjectConcept'))
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
                schema_licences.update(self.__convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsWorkSet/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self.__convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}recordRights/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self.__convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}rightsType'))

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
                        language = self.__convert_lido_to_cgif_with_language(schema_creator_name)
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


    def __convert_lido_to_cgif_with_language(self, language_element:any) -> str:
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


    def __convert_lido_to_cgif_with_concepts(self, lido_root:any, element_path:str) -> list:
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


    # SAVE ####################################################################

    # No routine required yet as all tasks are executed using graph data
