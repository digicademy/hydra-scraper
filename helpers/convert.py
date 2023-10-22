# Data conversion routines
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date
from lxml import etree
from rdflib import Graph, Namespace
from rdflib.term import BNode, Literal, URIRef

# Import script modules
from helpers.clean import clean_string_for_csv
from helpers.config import *

# Define namespaces
from rdflib.namespace import RDF, XSD
SCHEMA = Namespace('http://schema.org/')


def convert_lido_to_cgif(lido:str) -> Graph:
    '''
    Converts a LIDO file to CGIF triples and returns them as a Graph object

        Parameters:
            lido (str): The content of the LIDO file to convert

        Returns:
            Graph: object containing the CGIF triples
    '''

    # Set up an object to store CGIF triples
    cgif_triples = Graph()
    cgif_triples.bind('schema', SCHEMA)

    # Parse LIDO files as XML and retrieve resource URI
    #try:
    lido_root = etree.fromstring(bytes(lido, encoding='utf8'))
    resource = URIRef(lido_root.findtext('.//{http://www.lido-schema.org}recordInfoLink'))

    # RDF.type
    cgif_triples.add((resource, RDF.type, SCHEMA.VisualArtwork))

    # Go into the "descriptiveMetadata" section
    for lido_descriptive in lido_root.iterfind('.//{http://www.lido-schema.org}descriptiveMetadata'):

        # SCHEMA.name
        schema_names = lido_descriptive.iterfind('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}titleWrap/{http://www.lido-schema.org}titleSet/{http://www.lido-schema.org}appellationValue')
        for schema_name in schema_names:
            language = None
            language_element = schema_name
            while language == None and language_element != None:
                if '{http://www.w3.org/XML/1998/namespace}lang' in language_element.attrib:
                    language = language_element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                else:
                    language_element = language_element.getparent()
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
        schema_keywords.update(convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectClassificationWrap/{http://www.lido-schema.org}objectWorkTypeWrap/{http://www.lido-schema.org}objectWorkType'))
        schema_keywords.update(convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectRelationWrap/{http://www.lido-schema.org}subjectWrap/{http://www.lido-schema.org}subjectSet/{http://www.lido-schema.org}subject/{http://www.lido-schema.org}subjectConcept'))
        schema_keywords.add(schema_content_location)

        # SCHEMA.keywords: write property
        for schema_keyword in schema_keywords:
            if schema_keyword != None:
                cgif_triples.add((resource, SCHEMA.keywords, URIRef(schema_keyword)))
                for known_defined_term_set in config['known_defined_term_sets']:
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
        schema_licences.update(convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsWorkSet/{http://www.lido-schema.org}rightsType'))
        schema_licences.update(convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}recordRights/{http://www.lido-schema.org}rightsType'))
        schema_licences.update(convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}rightsType'))

        # SCHEMA.license: write property
        for schema_licence in schema_licences:
            if schema_licence != None:
                cgif_triples.add((resource, SCHEMA.license, URIRef(schema_licence)))

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

    # --- Fehlende Angaben zu DataFeed und DataCatalog ---
    # TODO Resource: SCHEMA.creator mit NFDI-URI falls möglich
    # TODO Resource: SCHEMA.isPartOf mit URL des Datensatzes
    # TODO Eine URL als Type "schema.DataCatalog" mit Tripeln für "schema.name" plus String(s) sowie "schema.publisher" plus N4C-URL
    # TODO Eine URL als Types "schema.DataFeed", "schema.Dataset" und "schema.URL" mit Tripeln für "schema.creator" plus N4C-URL, "schema.name" plus String(s), "schema.includedInDataCatalog" mit URL des DataCatalog, nochmal "schema.url" und evtl. allen Lizenzen des Dokuments als "schema.license"-Angaben falls vorhanden
    # TODO Pro N4C-URL den Type "schema.Organization" (falls zutreffend), dazu womöglich "schema.name" plus String(s) und "schema.url" mit Web-URL der Organisationen

    # Empty variable if content does not parse
    #except:
    #    cgif_triples = None

    # Return Graph object containing CGIF triples
    return cgif_triples


def convert_lido_to_cgif_with_concepts(lido_root:any, element_path:str) -> list:
    '''
    Finds a LIDO concept IDs in an element tree according to LIDO 1.0 or 1.1

        Parameters:
            lido_root (any): The parsed LIDO document
            element_path (str): The initial segment of the element path to look for concept IDs

        Returns:
            list: A list of concept IDs
    '''

    # Set up an empty set
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
    all_predicates = []
    predicates = []

    # Collect limited predicates or get all unique ones
    all_predicates = list(triples.predicates(unique = True))
    if limit_predicates != []:
        for limit_predicate in limit_predicates:
            predicates.append(URIRef(limit_predicate))
    else:
        predicates = all_predicates
        predicates.sort()

    # List all predicates as a table header
    first_line = ['URI']
    for predicate in predicates:
        first_line.append(str(predicate))
    output.append(first_line)

    # Get unique entities used as subjects that start with 'http' and go through them
    entities = list(triples.subjects(unique = True))
    entities.sort()
    for entity in entities:
        if isinstance(entity, URIRef):
            new_line = [str(entity)]

            # Set up a query routine for each desired predicate
            for predicate in predicates:
                new_line_entries = []

                # Go through all predicates with this entity as a subject, find literals as objects of desired predicates, and repeat for several levels
                # Level 1
                for all_predicate1 in all_predicates:
                    for s1, p1, o1 in triples.triples((entity, all_predicate1, None)):
                        if all_predicate1 == predicate and isinstance(o1, (Literal, URIRef)):
                            new_line_entries.append(clean_string_for_csv(str(o1)))

                        # Ordered list, multiple levels
                        elif all_predicate1 == predicate and isinstance(o1, BNode):
                            new_line_entries.extend(convert_triples_to_table_with_ordered_lists(triples, o1))

                        # Nested properties, level 2
                        else:
                            for all_predicate2 in all_predicates:
                                for s2, p2, o2 in triples.triples((o1, all_predicate2, None)):
                                    if all_predicate2 == predicate and isinstance(o2, (Literal, URIRef)):
                                        new_line_entries.append(clean_string_for_csv(str(o2)))

                                    # Nested properties, level 3
                                    else:
                                        for all_predicate3 in all_predicates:
                                            for s3, p3, o3 in triples.triples((o2, all_predicate3, None)):
                                                if all_predicate3 == predicate and isinstance(o3, (Literal, URIRef)):
                                                    new_line_entries.append(clean_string_for_csv(str(o3)))

                # Produce entry for this predicate
                new_line_entry = ', '.join(new_line_entries)
                new_line.append(new_line_entry)

            # Add new line to output
            output.append(new_line)

    # Return tabular data
    return output


def convert_triples_to_table_with_ordered_lists(triples:object, previous:BNode) -> list:
    '''
    Helper function to page through ordered lists when querying properties to print them as a table

        Parameters:
            triples (object): Graph object containing the triples to flick through
            previous (BNode): Previous entry in the unordered list

        Returns:
            list: Further entries of the unordered list
    '''

    # Set up empty list of results to add to
    new_line_entries = []

    # Dig one level further down the ordered list
    for s, p, o in triples.triples((previous, None, None)):
        if isinstance(o, (Literal, URIRef)) and o != URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil'):
            new_line_entries.append(clean_string_for_csv(str(o)))
        elif isinstance(o, BNode):
            new_line_entries.extend(convert_triples_to_table_with_ordered_lists(triples, o))

    # Return the list
    return new_line_entries
