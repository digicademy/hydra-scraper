# Data conversion routines
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from lxml import etree
from rdflib import Graph, Namespace
from rdflib.term import BNode, Literal, URIRef

# Import script modules
from helpers.clean import clean_string_for_csv

# Define namespaces
from rdflib.namespace import RDF
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
    try:
        lido_root = etree.fromstring(bytes(lido, encoding='utf8'))
        resource = URIRef(lido_root.findtext('.//{http://www.lido-schema.org}recordInfoLink'))

        # TODO TODO Type festlegen, Reste an Tripeln

        # SCHEMA.contentLocation
        schema_content_location = lido_root.findtext('.//{http://www.lido-schema.org}repositoryLocation/{http://www.lido-schema.org}placeID[@{http://www.lido-schema.org}type="http://terminology.lido-schema.org/lido00099"]')
        if schema_content_location != None:
            cgif_triples.add((resource, SCHEMA.contentLocation, URIRef(schema_content_location)))

        # SCHEMA.creator
        # TODO NFDI-URI falls möglich

        # SCHEMA.isPartOf
        # TODO URL des Datensatzes

        # SCHEMA.name
        # TODO Titel des Bildes, falls möglich deutsch und englisch ggf. mehrfach

        # SCHEMA.keywords
        # TODO Geonames-URL, Getty-URL zum Genre (Glasmalerei), Iconclass-URLs
        # TODO Geonames außerdem als Type "schema:DefinedTerm" und "schema:LandmarksOrHistoricalBuildings" und mit eigenem Tripel "schema:inDefinedTermSet" und "https://geonames.org/", welches wiederum den Type "schema:DefinedTermSet" benötigt
        # TODO Getty-URL zum Genre (Glasmalerei) außerdem als Type "schema.DefinedTerm" und mit eigenem Tripel "schema:inDefinedTermSet" und "http://vocab.getty.edu/page/aat/", welches wiederum den Type "schema:DefinedTermSet" benötigt
        # TODO Iconclass außerdem als Type "schema.DefinedTerm" und mit eigenem Tripel "schema:inDefinedTermSet" und "https://iconclass.org/", welches wiederum den Type "schema:DefinedTermSet" benötigt

        # SCHEMA.temporalCoverage
        # TODO Anfangs- und Enddatum durch / getrennt, mit "T00:00:00" am Anfang und "T23:59:59" am Ende, mit Type "schema:Date"

        # SCHEMA.dateModified
        # TODO Normdatum der letzten Aktualisierung, als Type "schema.Date"

        # SCHEMA.license
        # TODO URLs der Lizenzen für Bilddatei und Metadaten (Record)), ggf. mehrfach, als Type "schema.URL"

        # SCHEMA.height
        # TODO Höhe des Bildes in Pixeln, "??? px", als Type "schema.Distance"

        # SCHEMA.width
        # TODO Breite des Bildes in Pixeln, "??? px", als Type "schema.Distance"

        # SCHEMA.contentUrl
        # TODO größte Bild-URL als Type "schema.URL"

        # SCHEMA.creditText
        # TODO Bildunterschrift, falls möglich

        # SCHEMA.copyrightNotice
        # TODO Text zur Beschreibung des Copyrights, deutsch und englisch ggf. mehrfach, falls möglich

        # --- Fehlende Angaben zu DataFeed und DataCatalog ---

        # TODO Eine URL als Type "schema.DataCatalog" mit Tripeln für "schema.name" plus String(s) sowie "schema.publisher" plus N4C-URL

        # TODO Eine URL als Types "schema.DataFeed", "schema.Dataset" und "schema.URL" mit Tripeln für "schema.creator" plus N4C-URL, "schema.name" plus String(s), "schema.includedInDataCatalog" mit URL des DataCatalog, nochmal "schema.url" und evtl. allen Lizenzen des Dokuments als "schema.license"-Angaben falls vorhanden

        # TODO Pro N4C-URL den Type "schema.Organization" (falls zutreffend), dazu womöglich "schema.name" plus String(s) und "schema.url" mit Web-URL der Organisationen

    # Empty variable if content does not parse
    except:
        cgif_triples = None

    # Return Graph object containing CGIF triples
    return cgif_triples


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
