# Class to retrieve individual resource files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date
from glob import glob
from lxml import etree
from rdflib import Graph
from time import sleep

# Import script modules
from classes.retrieve import *

# # Define namespaces
from rdflib.namespace import SDO


class HydraRetrieveResource(HydraRetrieve):

    # Variables
    remote_resources = []
    local_resources = []
    store = None


    # READ ####################################################################


    def __init__(self, report:object, routine:str, remote_resources:list = None, source_or_target_path:str = None, content_type:str = None, clean_resource_names:list = None, retrieval_delay:float = 0, store_triples:bool = True, download:bool = False):
        '''
        Retrieve individual resource files

            Parameters:
                report (object): The report object to use
                routine (str): Reading routine to use
                remote_resources (list): List of remote resources to load into the object
                source_or_target_path (str): Local folder to save files to or containing files to read
                content_type (str): Content type to request
                clean_resource_names (list): List of strings to remove from a resource URL to build its file name
                retrieval_delay (float): Delay between requests
                store_triples (bool): Whether to try to store triples from resource files or not
                download (bool): Whether to save individual list files or not
        '''

        # Inherit from base class
        super().__init__(report)

        # Assign argument to object
        if remote_resources != None:
            self.remote_resources = remote_resources

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Routine: remote files
        if routine == 'remote':
            progress_message = 'Reading remote resource files'
            self.report.echo_progress(progress_message, 0, 100)
            status = self.__read_remote(content_type, clean_resource_names, retrieval_delay, progress_message, store_triples, download, source_or_target_path)
            self.report.echo_progress(progress_message, 100, 100)

        # Routine: local files
        elif routine == 'local':
            progress_message = 'Reading local resource files'
            self.report.echo_progress(progress_message, 0, 100)
            status = self.__read_local(content_type, source_or_target_path, progress_message)
            self.report.echo_progress(progress_message, 100, 100)

        # Routine: error
        else:
            status['reason'] = 'Invalid reading routine called.'

        # Update status
        self.report.status.append(status)


    def __read_remote(self, content_type:str = None, clean_resource_names:list = None, retrieval_delay:float = 0, progress_message:str = '', store_triples:bool = True, download:bool = False, target_path:str = None) -> dict:
        '''
        Retrieves all remote resources and populates the triple store

            Parameters:
                content_type (str): Content type to request
                clean_resource_names (list): List of strings to remove from a resource URL to build its file name
                retrieval_delay (float): Delay between requests
                progress_message (str): Message to display while paging through lists
                store_triples (bool): Whether to try to store triples from resource files or not
                download (bool): Whether to save individual list files or not
                target_path (str): Path to target folder if list files are to be saved

            Returns:
                dict: Status report
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Set up variables
        number_of_resources = len(self.remote_resources)
        missing_resources = []
        incompatible_resources = []
        
        # Check if there is data to read
        if number_of_resources == 0:
            status['reason'] = 'There were no remote resources to retrieve.'
        else:

            # Main loop to retrieve resource files
            for number, resource_url in enumerate(self.remote_resources, start = 1):

                # Retrieve file
                resource_data = self.__download_file(resource_url, content_type)
                if resource_data != None:

                    # Optionally clean file name
                    if download and target_path != None:
                        if clean_resource_names != None:
                            file_name = resource_url
                            for clean_resource_name in clean_resource_names:
                                file_name = file_name.replace(clean_resource_name, '')
                        else:
                            file_name = str(number)

                        # Optionally save file
                        target_path += '/resources/' + file_name + '.' + resource_data['file_extension']
                        self.__save_file(resource_data['content'], target_path)
                        status['success'] = True
                        status['reason'] = 'All resources downloaded successfully.'

                    # Provide generic info
                    else:
                        status['success'] = True
                        status['reason'] = 'All resources retrieved successfully.'

                    # Gather resource triples
                    if store_triples:
                        try:
                            store_new = Graph()
                            store_new.parse(data=resource_data['content'], format=resource_data['file_type'])
                        except:
                            incompatible_resources.append(resource_url)
                            continue

                    # Add resource triples to object
                    self.store += store_new

                # Report if download failed
                else:
                    missing_resources.append(resource_url)
                    continue

                # Delay next retrieval to avoid server block
                self.report.echo_progress(progress_message, number, number_of_resources)
                sleep(retrieval_delay)

            # Report any failed state
            if len(missing_resources) >= number_of_resources:
                status['success'] = False
                status['reason'] = 'All resources were missing.'
            elif len(missing_resources) > 0 and len(incompatible_resources) > 0:
                status['reason'] = 'Resources retrieved, but ' + str(len(missing_resources)) + ' were missing and ' + str(len(incompatible_resources)) + ' were not compatible.'
                status['missing'] = missing_resources
                status['incompatible'] = incompatible_resources
            elif self.missing_resources > 0:
                status['reason'] = 'Resources retrieved, but ' + str(len(missing_resources)) + ' were missing.'
                status['missing'] = missing_resources
            elif self.incompatible_resources > 0:
                status['reason'] = 'Resources retrieved, but ' + str(len(incompatible_resources)) + ' were not compatible.'
                status['incompatible'] = incompatible_resources

        # Return status
        return status


    def __read_local(self, source_path:str, content_type:str = None, progress_message:str = '') -> dict:
        '''
        Retrieves all remote resources and populates the triple store

            Parameters:
                source_path (str): Path to the folder to read
                content_type (str): Content type to request
                progress_message (str): Message to display while paging through lists

            Returns:
                dict: Status report
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Set up variables
        self.__read_local_list(source_path)
        number_of_resources = len(self.local_resources)
        incompatible_resources = []
        
        # Check if there is data to read
        if number_of_resources == 0:
            status['reason'] = 'There were no local resources to retrieve.'
        else:

            # Main loop to retrieve resource files
            for number, resource_path in enumerate(self.local_resources, start = 1):

                # Retrieve file
                resource_data = self.__local_file(resource_path, content_type)
                if resource_data != None:
                    status['success'] = True
                    status['reason'] = 'All resources retrieved successfully.'

                    # Gather resource triples
                    try:
                        store_new = Graph()
                        store_new.parse(data=resource_data['content'], format=resource_data['file_type'])
                    except:
                        incompatible_resources.append(resource_path)
                        continue

                    # Add resource triples to object
                    self.store += store_new

                # Report progress
                self.report.echo_progress(progress_message, number, number_of_resources)

            # Report any failed state
            if self.incompatible_resources > 0:
                status['reason'] = 'Resources retrieved, but ' + str(len(incompatible_resources)) + ' were not compatible.'
                status['incompatible'] = incompatible_resources

        # Return status
        return status


    def __read_local_list(self, source_path:str):
        '''
        Reads a local folder and saves all file paths in the list of local resource

            Parameters:
                source_path (str): Path to the folder to read
        '''

        # Prepare folder path and empty list
        source_path += '/**/*'
        entries = []

        # Add each file to list
        for source_path in glob(source_path, recursive = True):
            entries.append(source_path)

        # Return list
        self.local_resources = entries


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


    def morph(self, routine:str, csv_predicates:list = None):
        '''
        Morphs individual resources to a different format

            Parameters:
                routine (str): Transformation routine to use
                csv_predicates (list): List of predicates to include in CSV morph
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Routine: LIDO to NFDI
        if routine == 'lido-to-nfdi':
            progress_message = 'Converting LIDO files to NFDI-style triples'
            self.report.echo_progress(progress_message, 0, 100)
            status = self.__morph_lido_to_nfdi() # TODO
            self.report.echo_progress(progress_message, 100, 100)

        # Routine: error
        else:
            status['reason'] = 'Invalid transformation routine called.'

        # Update status
        self.report.status.append(status)


    def __morph_lido_to_nfdi(self, lido:str, supplement_data_feed:str = '', supplement_data_catalog:str = '', supplement_data_catalog_publisher:str = '') -> Graph:
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
                    language = self.__morph_lido_to_cgif_language(schema_name)
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
                schema_keywords.update(self.__morph_lido_to_nfdi_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectClassificationWrap/{http://www.lido-schema.org}objectWorkTypeWrap/{http://www.lido-schema.org}objectWorkType'))
                schema_keywords.update(self.__morph_lido_to_nfdi_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectRelationWrap/{http://www.lido-schema.org}subjectWrap/{http://www.lido-schema.org}subjectSet/{http://www.lido-schema.org}subject/{http://www.lido-schema.org}subjectConcept'))
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
                schema_licences.update(self.__morph_lido_to_nfdi_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsWorkSet/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self.__morph_lido_to_nfdi_concepts(lido_administrative, './/{http://www.lido-schema.org}recordRights/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self.__morph_lido_to_nfdi_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}rightsType'))

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
                        language = self.__morph_lido_to_nfdi_language(schema_creator_name)
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


    def __morph_lido_to_nfdi_language(self, language_element:any) -> str:
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


    def __morph_lido_to_nfdi_concepts(self, lido_root:any, element_path:str) -> list:
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
