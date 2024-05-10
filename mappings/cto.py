# Classes to provide nfdicore/cto triples
# Currently targeting nfdicore 2.0.0 and cto 2.2.0
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date, datetime
from rdflib import Graph, Namespace
from rdflib.term import BNode, Literal, URIRef
from validators import url

# Define namespaces
from rdflib.namespace import OWL, RDF, RDFS, SDO, SKOS, XSD
NFDICORE = Namespace('https://nfdi.fiz-karlsruhe.de/ontology/')
CTO = Namespace('https://nfdi4culture.de/ontology#')
MO = Namespace('http://purl.org/ontology/mo/')
N4C = Namespace('https://nfdi4culture.de/id/')
GN = Namespace('http://sws.geonames.org/')
IC = Namespace('https://iconclass.org/')
AAT = Namespace('http://vocab.getty.edu/page/aat/')
GND = Namespace('https://d-nb.info/gnd/')
WD = Namespace('http://www.wikidata.org/entity/')
VIAF = Namespace('https://viaf.org/viaf/')
RISM = Namespace('https://rism.online/')
FG = Namespace('https://database.factgrid.de/wiki/Item:')
ISIL = Namespace('https://ld.zdb-services.de/resource/organisations/')


# FEED OBJECT #################################################################


class Feed:


    def __new__(self, feed_uri:str|Literal|URIRef, feed_uri_same:str|list|Literal|URIRef = None, connect:bool = False, catalog_uri:str|Literal|URIRef = None, catalog_uri_same:str|list|Literal|URIRef = None):
        '''
        Produce all triples for an nfdicore/cto feed

            Parameters:
                feed_uri (str|Literal|URIRef): URI of the feed, preferably an NFDI4Culture IRI
                feed_uri_same (str|list|Literal|URIRef): Additional URIs identifying the same feed
                connect (bool): Prepare triples for the connection of research data to research information
                catalog_uri (str|Literal|URIRef): URI of the catalog the feed belongs to, preferably an NFDI4Culture IRI
                catalog_uri_same (str|list|Literal|URIRef): Additional URIs identifying the same catalog
        '''

        # Set up graph
        output = spacify_graph()

        # FEED

        # Feed URI
        feed_uri = urify(feed_uri)
        if feed_uri == None:
            raise ValueError('A feed URI was not valid.')
        else:
            output.add((feed_uri, RDF.type, NFDICORE.Dataset))

            # Optional date modified
            if connect:
                today = date.today()
                output.add((feed_uri, SDO.dateModified, Literal(today, datatype=XSD.date)))

            # Same as feed URI
            feed_uri_same = urify_list(feed_uri_same)
            for i in feed_uri_same:
                output.add((feed_uri, OWL.sameAs, i))

            # Catalog URI
            catalog_uri = urify(catalog_uri)
            if catalog_uri != None:
                output.add((catalog_uri, RDF.type, NFDICORE.DataPortal))
                output.add((catalog_uri, NFDICORE.dataset, feed_uri))

                # Same as catalog URI
                catalog_uri_same = urify_list(catalog_uri_same)
                for i in catalog_uri_same:
                    output.add((catalog_uri, OWL.sameAs, i))

        # Return graph
        return output
    

# FEED ELEMENT OBJECT #########################################################


class FeedElement:


    def __new__(self, feed_uri:str|Literal|URIRef, element_type:str|URIRef, element_uri:str|Literal|URIRef, element_uri_same:str|list|Literal|URIRef = None, connect:bool = False, label:str|list|Literal|URIRef = None, label_alt:str|list|Literal|URIRef = None, shelf_mark:str|list|Literal|URIRef = None, image:str|list|Literal|URIRef = None, lyrics:str|list|Literal|URIRef = None, text_incipit:str|list|Literal|URIRef = None, music_incipit:dict|list = None, source_file:str|list|Literal|URIRef = None, iiif_image_api:str|list|Literal|URIRef = None, iiif_presentation_api:str|list|Literal|URIRef = None, ddb_api:str|list|Literal|URIRef = None, oaipmh_api:str|list|Literal|URIRef = None, publisher:str|list|Literal|URIRef = None, license:str|list|Literal|URIRef = None, vocab_element_type:str|list|Literal|URIRef = None, vocab_subject_concept:str|list|Literal|URIRef = None, vocab_related_location:str|list|Literal|URIRef = None, vocab_related_event:str|list|Literal|URIRef = None, vocab_related_organization:str|list|Literal|URIRef = None, vocab_holding_organization:str|list|Literal|URIRef = None, vocab_related_person:str|list|Literal|URIRef = None, vocab_further:str|list|Literal|URIRef = None, related_item:str|list|Literal|URIRef = None, birth_date:str|int|date|datetime|list|Literal = None, death_date:str|int|date|datetime|list|Literal = None, foundation_date:str|int|date|datetime|list|Literal = None, dissolution_date:str|int|date|datetime|list|Literal = None, start_date:str|int|date|datetime|list|Literal = None, end_date:str|int|date|datetime|list|Literal = None, creation_date:str|int|date|datetime|list|Literal = None, creation_period:str|list|Literal = None, destruction_date:str|int|date|datetime|list|Literal = None, approximate_period:str|list|Literal = None, existence_period:str|list|Literal = None):
        '''
        Produce all triples for an nfdicore/cto feed element

            Parameters:
                feed_uri (str|Literal|URIRef): URI of the feed that the element is part of
                element_type (str|URIRef): Schema.org class URI or generic string 'person', 'organization', 'place', 'event', or 'item'
                element_uri (str|Literal|URIRef): URI of the feed element
                element_uri_same (str|list|Literal|URIRef): Additional URIs identifying the same feed element
                connect (bool): Prepare triples for the connection of research data to research information
                label (str|list|Literal|URIRef): Main text label of the feed element
                label_alt (str|list|Literal|URIRef): Alternative text label of the feel element
                shelf_mark (str|list|Literal|URIRef): Shelf mark in a holding repository, such as a library
                image (str|list|Literal|URIRef): URL of an image representation of the element
                lyrics (str|list|Literal|URIRef): Lyrics of a musical composition
                text_incipit (str|list|Literal|URIRef): First few words of text content
                music_incipit (dict|list): Dictionary with the keys 'uri' (optional), 'clef', 'key_sig', 'time_sig', and 'pattern'
                source_file (str|list|Literal|URIRef): URL of the data source used for this element
                iiif_image_api (str|list|Literal|URIRef): URL of the IIIF Image API of this element
                iiif_presentation_api (str|list|Literal|URIRef): URL of the IIIF Presentation API of this element
                ddb_api (str|list|Literal|URIRef): URL of the DDB API of this element
                oaipmh_api (str|list|Literal|URIRef): URL of the OAI-PMH API of this element
                publisher (str|list|Literal|URIRef): URI of the publisher of the element
                license (str|list|Literal|URIRef): URI of the element's license
                vocab_element_type (str|list|Literal|URIRef): Getty AAT URI or another string indicating the element type
                vocab_subject_concept (str|list|Literal|URIRef): URI or string of a subject, including Iconclass
                vocab_related_location (str|list|Literal|URIRef): URI or string of a related place, including GeoNames
                vocab_related_event (str|list|Literal|URIRef): URI or string of a related event
                vocab_related_organization (str|list|Literal|URIRef): URI or string of a related organization, including ISILs
                vocab_related_person (str|list|Literal|URIRef): URI or string of a related person
                vocab_further (str|list|Literal|URIRef): URI of further vocabulary terms which do not fit other categories
                related_item (str|list|Literal|URIRef): URI of a related creative work
                birth_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp of a person's birth 
                death_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp of a person's death
                foundation_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp of an organisation's foundation
                dissolution_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp of an organisation's dissolution
                start_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp when an event started
                end_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp when an event ended
                creation_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp of an item's creation
                creation_period (str|list|Literal): String providing an item's creation period
                destruction_date (str|int|date|datetime|list|Literal): Exact date, datetime, or timestamp of an item's destruction
                approximate_period (str|list|Literal): String providing a period that an item is associated with
                existence_period (str|list|Literal): String providing the period of an item's existence
        '''

        # Set up graph
        output = spacify_graph()

        # ELEMENT

        # Check element and feed URIs
        element_uri = urify(element_uri)
        feed_uri = urify(feed_uri)
        if element_uri == None:
            raise ValueError('A feed element URI was not valid.')
        elif feed_uri == None:
            raise ValueError('A feed URI was not valid.')
        else:

            # Element and feed URI
            output.add((element_uri, RDF.type, CTO.DatafeedElement))
            output.add((element_uri, CTO.elementOf, feed_uri))

            # Element type
            if isinstance(element_type, URIRef):
                element_type = spacify_uri(element_type)
            # Element type: person
            if element_type == 'person' or element_type in sdo_person:
                output.add((element_uri, RDF.type, NFDICORE.Person))
            # Element type: organization
            elif element_type == 'organization' or element_type == 'organisation' or element_type in sdo_organization:
                output.add((element_uri, RDF.type, NFDICORE.Organization))
            # Element type: place
            elif element_type == 'place' or element_type == 'location' or element_type in sdo_place:
                output.add((element_uri, RDF.type, NFDICORE.Place))
            # Element type: event
            elif element_type == 'event' or element_type == 'date' or element_type in sdo_event:
                output.add((element_uri, RDF.type, NFDICORE.Event))
            # Element type: item that is a schema.org creative work
            elif element_type in sdo_item:
                output.add((element_uri, RDF.type, element_type))
            # Element type: generic item
            else:
                output.add((element_uri, RDF.type, CTO.Item))

            # Same as element URI
            element_uri_same = urify_list(element_uri_same)
            for i in element_uri_same:
                output.add((element_uri, OWL.sameAs, i))

            # Optional wrapper
            if connect:
                wrapper = BNode()
                output.add((feed_uri, SDO.dataFeedElement, wrapper))
                output.add((wrapper, RDF.type, SDO.DataFeedItem))
                output.add((wrapper, SDO.item, element_uri))

            # LABEL AND REFERENCE LITERALS

            # Main label
            label = literalify_list(label)
            for i in label:
                output.add((element_uri, RDFS.label, i))

            # Alternative label
            label_alt = literalify_list(label_alt)
            for i in label_alt:
                output.add((element_uri, SKOS.altLabel, i))

            # Shelf mark
            shelf_mark = literalify_list(shelf_mark)
            for i in shelf_mark:
                i = Literal(str(i)) # Removes lang
                output.add((element_uri, CTO.shelfMark, i))

            # MEDIA LITERALS

            # URL
            element_url = literalify(element_uri, SDO.URL)
            if element_url != None:
                output.add((element_uri, SDO.url, element_url))

            # Image
            image = literalify_list(image, SDO.URL)
            for i in image:
                output.add((element_uri, SDO.image, i))

            # Lyrics
            lyrics = literalify_list(lyrics)
            for i in lyrics:
                blank = BNode()
                output.add((element_uri, MO.lyrics, blank))
                output.add((blank, RDF.type, MO.Lyrics))
                output.add((blank, MO.text, i))

            # Text incipit
            text_incipit = literalify_list(text_incipit)
            for i in text_incipit:
                output.add((element_uri, CTO.textIncipit, i))

            # Music incipit
            music_incipit = dictify_list(music_incipit, ['uri', 'clef', 'key_sig', 'time_sig', 'pattern'])
            for i in music_incipit:
                i_uri = urify(i['uri'])
                i_clef = literalify(i['clef'])
                i_key_sig = literalify(i['key_sig'])
                i_time_sig = literalify(i['time_sig'])
                i_pattern = literalify(i['pattern'])
                if i_uri != None:
                    uri_or_blank = i_uri
                else:
                    uri_or_blank = BNode()
                output.add((uri_or_blank, RDF.type, CTO.Incipit))
                output.add((uri_or_blank, CTO.incipitOf, element_uri))
                output.add((uri_or_blank, CTO.clef, i_clef))
                output.add((uri_or_blank, CTO.keySignature, i_key_sig))
                output.add((uri_or_blank, CTO.timeSignature, i_time_sig))
                output.add((uri_or_blank, CTO.pattern, i_pattern))

            # Source file
            source_file = literalify_list(source_file, SDO.URL)
            for i in source_file:
                output.add((element_uri, CTO.sourceFile, i))

            # API LITERALS

            # IIIF Image API
            iiif_image_api = literalify_list(iiif_image_api, SDO.URL)
            for i in iiif_image_api:
                output.add((element_uri, CTO.iiifImageAPI, i))

            # IIIF Presentation API
            iiif_presentation_api = literalify_list(iiif_presentation_api, SDO.URL)
            for i in iiif_presentation_api:
                output.add((element_uri, CTO.iiifPresentationAPI, i))

            # DDB API
            ddb_api = literalify_list(ddb_api, SDO.URL)
            for i in ddb_api:
                output.add((element_uri, CTO.ddbAPI, i))

            # OAI-PMH API
            oaipmh_api = literalify_list(oaipmh_api, SDO.URL)
            for i in oaipmh_api:
                output.add((element_uri, CTO['oai-pmhAPI'], i)) # Alternative notation due to hyphen

            # RIGHTS URIS

            # Publisher
            publisher = urify_list(publisher)
            for i in publisher:
                output.add((element_uri, NFDICORE.publisher, i))

            # License
            license = urify_list(license)
            for i in license:
                output.add((element_uri, NFDICORE.license, i))

            # RELATED URIS AND FALLBACK LITERALS

            # Element type
            vocab_element_type = urify_or_literalify_list(vocab_element_type)
            no_literals = False
            for i in vocab_element_type:
                if isinstance(i, URIRef):
                    no_literals = True
                    output.add((element_uri, CTO.elementType, i))
                    output += vocabify(i, element_uri)
                elif no_literals == False:
                    output.add((element_uri, CTO.elementTypeLiteral, i))

            # Subject concept
            vocab_subject_concept = urify_or_literalify_list(vocab_subject_concept)
            no_literals = False
            for i in vocab_subject_concept:
                if isinstance(i, URIRef):
                    no_literals = True
                    output.add((element_uri, CTO.subjectConcept, i))
                    output += vocabify(i, element_uri)
                elif no_literals == False:
                    output.add((element_uri, CTO.subjectConceptLiteral, i))

            # Related location
            vocab_related_location = urify_or_literalify_list(vocab_related_location)
            no_literals = False
            for i in vocab_related_location:
                if isinstance(i, URIRef):
                    no_literals = True
                    output.add((element_uri, CTO.relatedLocation, i))
                    output.add((i, RDF.type, NFDICORE.Place))
                    output += vocabify(i, element_uri)
                elif no_literals == False:
                    output.add((element_uri, CTO.relatedLocationLiteral, i))

            # Related event
            vocab_related_event = urify_or_literalify_list(vocab_related_event)
            no_literals = False
            for i in vocab_related_event:
                if isinstance(i, URIRef):
                    no_literals = True
                    output.add((element_uri, CTO.relatedEvent, i))
                    output.add((i, RDF.type, NFDICORE.Event))
                    output += vocabify(i, element_uri)
                elif no_literals == False:
                    output.add((element_uri, CTO.relatedEventLiteral, i))

            # Related organization
            vocab_related_organization = urify_or_literalify_list(vocab_related_organization)
            no_literals = False
            for i in vocab_related_organization:
                if isinstance(i, URIRef):
                    no_literals = True
                    output.add((element_uri, CTO.relatedOrganization, i))
                    output.add((i, RDF.type, NFDICORE.Organization))
                    output += vocabify(i, element_uri)
                elif no_literals == False:
                    output.add((element_uri, CTO.relatedOrganizationLiteral, i))

            # Related person
            vocab_related_person = urify_or_literalify_list(vocab_related_person)
            no_literals = False
            for i in vocab_related_person:
                if isinstance(i, URIRef):
                    no_literals = True
                    output.add((element_uri, CTO.relatedPerson, i))
                    output.add((i, RDF.type, NFDICORE.Person))
                    output += vocabify(i, element_uri)
                elif no_literals == False:
                    output.add((element_uri, CTO.relatedPersonLiteral, i))

            # Further vocabularies
            vocab_further = urify_list(vocab_further)
            for i in vocab_further:
                output += vocabify(i, element_uri)

            # Related item
            related_item = urify_list(related_item)
            for i in related_item:
                output.add((element_uri, CTO.relatedItem, i))

            # DATES BY TYPE

            # For persons
            if element_type == 'person' or element_type in sdo_person:

                # Birth date
                birth_date = datify_list(birth_date)
                for i in birth_date:
                    output.add((element_uri, NFDICORE.birthDate, i))

                # Death date
                death_date = datify_list(death_date)
                for i in death_date:
                    output.add((element_uri, NFDICORE.deathDate, i))

            # For organizations
            elif element_type == 'organization' or element_type == 'organisation' or element_type in sdo_organization:

                # Foundation date
                foundation_date = datify_list(foundation_date)
                for i in foundation_date:
                    output.add((element_uri, NFDICORE.foundationDate, i))

                # Dissolution date
                dissolution_date = datify_list(dissolution_date)
                for i in dissolution_date:
                    output.add((element_uri, NFDICORE.dissolutionDate, i))

            # For places
            elif element_type == 'place' or element_type == 'location' or element_type in sdo_place:
                pass

            # For events
            elif element_type == 'event' or element_type == 'date' or element_type in sdo_event:

                # Start date
                start_date = datify_list(start_date)
                for i in start_date:
                    output.add((element_uri, NFDICORE.startDate, i))

                # End date
                end_date = datify_list(end_date)
                for i in end_date:
                    output.add((element_uri, NFDICORE.endDate, i))

            # For items
            else:

                # Creation date
                creation_date = datify_list(creation_date)
                for i in creation_date:
                    output.add((element_uri, CTO.creationDate, i))

                # Creation period
                creation_period = periodify_or_literalify_list(creation_period)
                for i in creation_period:
                    output.add((element_uri, CTO.creationPeriod, i))

                # Destruction date
                destruction_date = datify_list(destruction_date)
                for i in destruction_date:
                    output.add((element_uri, CTO.destructionDate, i))

                # Approximate period
                approximate_period = periodify_or_literalify_list(approximate_period)
                for i in approximate_period:
                    output.add((element_uri, CTO.approximatePeriod, i))

                # Existence period
                existence_period = periodify_or_literalify_list(existence_period)
                for i in existence_period:
                    output.add((element_uri, CTO.existencePeriod, i))

        # Return graph
        return output


# TRIPLE HELPERS ##############################################################


def vocabify(input:URIRef, element_uri:URIRef) -> URIRef:
    '''
    Clean vocabulary URIs, add their respective vocab triple, and return the clean URIRef

        Parameters:
            input (URIRef): Variable to check and add a triple for
            element_uri (URIRef): URI of the element to add the triple to

        Returns:
            URIRef: Normalised input
    '''

    # Set up graph
    output = spacify_graph()

    # Check which vocab triple is necessary
    if input in GN:
        output.add((element_uri, CTO.geonames, input))
    elif input in IC:
        output.add((element_uri, CTO.iconclass, input))
    elif input in AAT:
        output.add((element_uri, CTO.aat, input))
    elif input in GND:
        output.add((element_uri, CTO.gnd, input))
    elif input in WD:
        output.add((element_uri, CTO.wikidata, input))
    elif input in VIAF:
        output.add((element_uri, CTO.viaf, input))
    elif input in RISM:
        output.add((element_uri, CTO.rism, input))
    elif input in FG:
        output.add((element_uri, CTO.factgrid, input))
    elif input in ISIL:
        output.add((element_uri, CTO.isil, input))
    else:
        output.add((element_uri, CTO.externalVocabulary, input))
            
    # Return altered input
    return output


# INPUT HELPERS ###############################################################


def urify(input:str|URIRef|Literal) -> URIRef|None:
    '''
    Make sure a variable is a URI

        Parameters:
            input (str|URIRef|Literal): Variable to check and transform

        Returns:
            URIRef: URI value
    '''

    # Turn str to URIRef
    if isinstance(input, str):
        if url(input):
            input = URIRef(input)
        else:
            input = None

    # Turn Literal to URIRef
    elif isinstance(input, Literal):
        if url(str(input)):
            input = URIRef(str(input))
        else:
            input = None

    # Check URIRef
    elif isinstance(input, URIRef):
        if not url(str(input)):
            input = None
    else:
        input = None

    # Normalise URI
    if input != None:
        input = spacify_uri(input)

    # Return URI
    return input


def urify_list(input:str|list|Literal|URIRef|None) -> list:
    '''
    Make sure a variable contains a list of URIs

        Parameters:
            input (str|list|Literal|URIRef|None): Variable to check and transform

        Returns:
            list: List of URI values
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn str, URIRef, and Literal to list
    elif isinstance(input, (str, URIRef, Literal)):
        input = [input]

    # Switch each str and Literal to URIRef
    output = []
    for i in input:
        i = urify(i)
        if i != None:
            output.append(i)

    # Return list
    return output


def literalify(input:str|URIRef|Literal, data_type:URIRef = None) -> Literal|None:
    '''
    Make sure a variable is a Literal

        Parameters:
            input (str|URIRef|Literal): Variable to check and transform
            data_type (URIRef): Data type of the literal

        Returns:
            Literal: Literal value
    '''

    # Turn str to Literal
    if isinstance(input, str):
        if input != '':
            input = Literal(input, datatype=data_type)
        else:
            input = None

    # Turn URIRef to Literal
    elif isinstance(input, URIRef):
        if str(input) != '':
            input = Literal(str(input), datatype=data_type)
        else:
            input = None

    # Check Literal
    elif isinstance(input, Literal):
        if str(input) == '':
            input = None
        else:
            input.datatype = data_type
    else:
        input = None

    # Return URI
    return input


def literalify_list(input:str|list|Literal|URIRef|None, data_type:URIRef = None) -> list:
    '''
    Make sure a variable contains a list of Literals

        Parameters:
            input (str|list|Literal|URIRef|None): Variable to check and transform
            data_type (URIRef): Data type of the literal

        Returns:
            list: List of URI values
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn str, URIRef, and Literal to list
    elif isinstance(input, (str, URIRef, Literal)):
        input = [input]

    # Switch each str and URIRef to Literal
    output = []
    for i in input:
        i = literalify(i, data_type)
        if i != None:
            output.append(i)

    # Return list
    return output


def urify_or_literalify_list(input:str|list|Literal|URIRef|None) -> list:
    '''
    Make sure a variable contains a list of URIRefs and Literals

        Parameters:
            input (str|list|Literal|URIRef|None): Variable to check and transform

        Returns:
            list: List of URI values and Literals
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn str, URIRef, and Literal to list
    elif isinstance(input, (str, URIRef, Literal)):
        input = [input]

    # Turn each list item to URIRef or Literal
    output = []
    for i in input:
        i_check = urify(i)
        if i_check != None:
            i = i_check
        else:
            i = literalify(i)
        if i != None:
            output.append(i)

    # Return list
    return output


def periodify_or_literalify_list(input:str|list|URIRef|Literal|None) -> list:
    '''
    Make sure a variable contains a list of schema:DateTime periods and Literals

        Parameters:
            input (str|list|URIRef|Literal|None): Variable to check and transform

        Returns:
            list: List of schema:DateTimes and Literals
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn str, URIRef, and Literal to list
    elif isinstance(input, (str, URIRef, Literal)):
        input = [input]

    # Turn each list item to schema:DateTime or regular Literal
    output = []
    for i in input:
        i_check = periodify(i)
        if i_check != None:
            i = i_check
        else:
            i = literalify(i)
        if i != None:
            output.append(i)

    # Return list
    return output


def periodify(input:str|URIRef|Literal|None) -> Literal:
    '''
    Make sure a variable is a schema:DateTime period

        Parameters:
            input (str|URIRef|Literal|None): Variable to check and transform

        Returns:
            Literal: Literal with the data type schema:DateTime
    '''

    # Turn URIRef and Literal to str
    if isinstance(input, (URIRef, Literal)):
        if str(input) != '':
            input = str(input)
        else:
            input = None

    # Check string
    elif isinstance(input, str):
        if input == '':
            input = None
    else:
        input = None

    # Split in two if str contains a slash
    if '/' in input:
        parts_in = input.split('/', 1)
        parts_out = []
        for part in parts_in:
            part = datify(part)
            parts_out.append(part)

        # Construct schema:DateTime Literal if both parts are dates
        if parts_out[0] != None and parts_out[1] != None:
            input = str(parts_out[0]) + '/' + str(parts_out[1])
            input = Literal(input, datatype = SDO.DateTime)
        else:
            input = None
    else:
        input = None

    # Return period
    return input


def datify(input:str|int|date|datetime|Literal) -> Literal:
    '''
    Make sure a variable is a date

        Parameters:
            input (str|int|date|datetime|Literal): Variable to check and transform

        Returns:
            Literal: Literal with the right data type
    '''

    # Leave date and datetime as is
    if isinstance(input, (date, datetime)):
        pass

    # Turn int (timestamp) to datetime
    if isinstance(input, int):
        input = datetime.fromtimestamp(input)

    # Turn Literal to str
    elif isinstance(input, Literal):
        if str(input) != '':
            input = str(input)
        else:
            input = None

    # Check string
    elif isinstance(input, str):
        if input == '':
            input = None
    else:
        input = None

    # Convert str to date or datetime
    if isinstance(input, str):
        try:
            input = date.fromisoformat(input)
        except:
            try:
                input = datetime.fromisoformat(input)
            except:
                input = None

    # Serialise datetime and date
    if input != None:
        if isinstance(input, datetime): # Each datetime is also a date
            input = Literal(input.isoformat(), datatype = XSD.dateTime)
        elif isinstance(input, date):
            input = Literal(input.isoformat(), datatype = XSD.date)
        else:
            input = None

    # Return date
    return input


def datify_list(input:str|int|date|datetime|list|Literal|None) -> list:
    '''
    Make sure a variable contains a list of dates

        Parameters:
            input (str|int|date|datetime|list|Literal|None): Variable to check and transform

        Returns:
            list: List of date literals
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn str, int, date, datetime and Literal to list
    elif isinstance(input, (str, int, date, datetime, Literal)):
        input = [input]

    # Switch inputs to right data type
    output = []
    for i in input:
        i = datify(i)
        if i != None:
            output.append(i)

    # Return list
    return output


def dictify(input:dict, keys:list = None) -> dict|None:
    '''
    Make sure a variable is a dictionary

        Parameters:
            input (dict): Variable to check and transform
            keys (list): List of keys to limit dictionaries to

        Returns:
            dict: Orderly dictionary
    '''

    # Check dictionary
    output = {}
    if isinstance(input, dict):
        if keys != None:
            for key, value in input.items():
                if key in keys:
                    output[key] = value
    else:
        input = None

    # Return dictionary
    return output


def dictify_list(input:dict|list|None, keys:list = None) -> list:
    '''
    Make sure a variable contains a list of dictionaries

        Parameters:
            input (dict|list|None): Variable to check and transform
            keys (list): List of keys to limit dictionaries to

        Returns:
            list: List of dictionaries
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn dict to list
    elif isinstance(input, dict):
        input = [input]

    # Check each dict
    output = []
    for i in input:
        i = dictify(i, keys)
        if i != None:
            output.append(i)

    # Return list
    return output


# NAMESPACE HELPERS ###########################################################


def spacify_graph() -> Graph:
    '''
    Produce an empty graph object with all required namespaces

        Returns:
            Graph: Basic graph object
    '''

    # Initialise graph
    output = Graph()

    # Ontologies
    output.bind('cto', CTO)
    output.bind('mo', MO)
    output.bind('nfdicore', NFDICORE)
    output.bind('owl', OWL)
    output.bind('rdf', RDF)
    output.bind('rdfs', RDFS)
    output.bind('schema', SDO)
    output.bind('xsd', XSD)

    # Vocabularies
    output.bind('n4c', N4C)
    output.bind('gn', GN)
    output.bind('ic', IC)
    output.bind('aat', AAT)
    output.bind('gnd', GND)
    output.bind('wd', WD)
    output.bind('viaf', VIAF)
    output.bind('rism', RISM)
    output.bind('fg', FG)
    output.bind('isil', ISIL)

    # Return graph
    return output


def spacify_uri(input:URIRef) -> URIRef:
    '''
    Normalise common 'http' and 'https' mistakes in namespaces of incoming URIRefs

        Parameters:
            input (URIRef): Variable to check and transform

        Returns:
            URIRef: Clean URIRef
    '''

    # Remove trailing slashes
    if str(input).endswith('/'):
        input = URIRef(str(input)[:-1])

    # Avoid known GeoNames issues
    if str(input).startswith('http://www.geonames.org/'):
        input = URIRef(str(input).replace('http://www.geonames.org/', 'http://sws.geonames.org/', 1))
    elif str(input).startswith('https://www.geonames.org/'):
        input = URIRef(str(input).replace('https://www.geonames.org/', 'http://sws.geonames.org/', 1))

    # List namespaces to check
    checks = [
        CTO,
        MO,
        NFDICORE,
        OWL,
        RDF,
        RDFS,
        SDO,
        XSD,
        N4C,
        GN,
        IC,
        AAT,
        GND,
        WD,
        VIAF,
        RISM,
        FG,
        ISIL
    ]

    # Prepare http/https check if not a regular namespace
    for check in checks:
        if input not in check:

            # Switch http and https and test again
            if str(input).startswith('http://'):
                input_copy = URIRef(str(input).replace('http://', 'https://', 1))
                if input_copy in check:
                    input = input_copy
            elif str(input).startswith('https://'):
                input_copy = URIRef(str(input).replace('https://', 'http://', 1))
                if input_copy in check:
                    input = input_copy

    # Return URIRef
    return input


# HELPER VARS #################################################################


# Lists of schema.org classes, collated on 17/4/2024, periodical update TODO
# Some SDO items commented out as they are not in RDFLib's internal library
sdo_feed = [
    SDO.DataFeed,
    SDO.Dataset
]
sdo_person = [
    SDO.Person,
    SDO.Patient
]
sdo_organization = [
    SDO.Organization,
    SDO.Airline,
    SDO.Consortium,
    SDO.Corporation,
    SDO.EducationalOrganization,
    SDO.CollegeOrUniversity,
    SDO.ElementarySchool,
    SDO.HighSchool,
    SDO.MiddleSchool,
    SDO.Preschool,
    SDO.School,
    SDO.FundingScheme,
    SDO.GovernmentOrganization,
    SDO.LibrarySystem,
    SDO.LocalBusiness,
    SDO.AnimalShelter,
    SDO.ArchiveOrganization,
    SDO.AutomotiveBusiness,
    SDO.AutoBodyShop,
    SDO.AutoDealer,
    SDO.AutoPartsStore,
    SDO.AutoRental,
    SDO.AutoRepair,
    SDO.AutoWash,
    SDO.GasStation,
    SDO.MotorcycleDealer,
    SDO.MotorcycleRepair,
    SDO.ChildCare,
    SDO.Dentist,
    SDO.DryCleaningOrLaundry,
    SDO.EmergencyService,
    SDO.FireStation,
    SDO.Hospital,
    SDO.PoliceStation,
    SDO.EmploymentAgency,
    SDO.EntertainmentBusiness,
    SDO.AdultEntertainment,
    SDO.AmusementPark,
    SDO.ArtGallery,
    SDO.Casino,
    SDO.ComedyClub,
    SDO.MovieTheater,
    SDO.NightClub,
    SDO.FinancialService,
    SDO.AccountingService,
    SDO.AutomatedTeller,
    SDO.BankOrCreditUnion,
    SDO.InsuranceAgency,
    SDO.FoodEstablishment,
    SDO.Bakery,
    SDO.BarOrPub,
    SDO.Brewery,
    SDO.CafeOrCoffeeShop,
    SDO.Distillery,
    SDO.FastFoodRestaurant,
    SDO.IceCreamShop,
    SDO.Restaurant,
    SDO.Winery,
    SDO.GovernmentOffice,
    SDO.PostOffice,
    SDO.HealthAndBeautyBusiness,
    SDO.BeautySalon,
    SDO.DaySpa,
    SDO.HairSalon,
    SDO.HealthClub,
    SDO.NailSalon,
    SDO.TattooParlor,
    SDO.HomeAndConstructionBusiness,
    SDO.Electrician,
    SDO.GeneralContractor,
    SDO.HVACBusiness,
    SDO.HousePainter,
    SDO.Locksmith,
    SDO.MovingCompany,
    SDO.Plumber,
    SDO.RoofingContractor,
    SDO.InternetCafe,
    SDO.LegalService,
    SDO.Attorney,
    SDO.Notary,
    SDO.Library,
    SDO.LodgingBusiness,
    SDO.BedAndBreakfast,
    SDO.Campground,
    SDO.Hostel,
    SDO.Hotel,
    SDO.Motel,
    SDO.Resort,
    SDO.SkiResort,
    #SDO.VacationRental,
    SDO.MedicalBusiness,
    SDO.Dentist,
    SDO.MedicalClinic,
    SDO.CovidTestingFacility,
    SDO.Optician,
    SDO.Pharmacy,
    SDO.Physician,
    #SDO.IndividualPhysician,
    #SDO.PhysiciansOffice,
    SDO.ProfessionalService,
    SDO.RadioStation,
    SDO.RealEstateAgent,
    SDO.RecyclingCenter,
    SDO.SelfStorage,
    SDO.ShoppingCenter,
    SDO.SportsActivityLocation,
    SDO.BowlingAlley,
    SDO.ExerciseGym,
    SDO.GolfCourse,
    SDO.HealthClub,
    SDO.PublicSwimmingPool,
    SDO.SkiResort,
    SDO.SportsClub,
    SDO.StadiumOrArena,
    SDO.TennisComplex,
    SDO.Store,
    SDO.AutoPartsStore,
    SDO.BikeStore,
    SDO.BookStore,
    SDO.ClothingStore,
    SDO.ComputerStore,
    SDO.ConvenienceStore,
    SDO.DepartmentStore,
    SDO.ElectronicsStore,
    SDO.Florist,
    SDO.FurnitureStore,
    SDO.GardenStore,
    SDO.GroceryStore,
    SDO.HardwareStore,
    SDO.HobbyShop,
    SDO.HomeGoodsStore,
    SDO.JewelryStore,
    SDO.LiquorStore,
    SDO.MensClothingStore,
    SDO.MobilePhoneStore,
    SDO.MovieRentalStore,
    SDO.MusicStore,
    SDO.OfficeEquipmentStore,
    SDO.OutletStore,
    SDO.PawnShop,
    SDO.PetStore,
    SDO.ShoeStore,
    SDO.SportingGoodsStore,
    SDO.TireShop,
    SDO.ToyStore,
    SDO.WholesaleStore,
    SDO.TelevisionStation,
    SDO.TouristInformationCenter,
    SDO.TravelAgency,
    SDO.MedicalOrganization,
    SDO.Dentist,
    SDO.DiagnosticLab,
    SDO.Hospital,
    SDO.MedicalClinic,
    SDO.Pharmacy,
    SDO.Physician,
    SDO.VeterinaryCare,
    SDO.NGO,
    SDO.NewsMediaOrganization,
    #SDO.OnlineBusiness,
    #SDO.OnlineStore,
    SDO.PerformingGroup,
    SDO.DanceGroup,
    SDO.MusicGroup,
    SDO.TheaterGroup,
    #SDO.PoliticalParty,
    SDO.Project,
    SDO.FundingAgency,
    SDO.ResearchProject,
    SDO.ResearchOrganization,
    #SDO.SearchRescueOrganization,
    SDO.SportsOrganization,
    SDO.SportsTeam,
    SDO.WorkersUnion
]
sdo_place = [
    SDO.Place,
    SDO.Accommodation,
    SDO.Apartment,
    SDO.CampingPitch,
    SDO.House,
    SDO.SingleFamilyResidence,
    SDO.Room,
    SDO.HotelRoom,
    SDO.MeetingRoom,
    SDO.Suite,
    SDO.AdministrativeArea,
    SDO.City,
    SDO.Country,
    SDO.SchoolDistrict,
    SDO.State,
    SDO.CivicStructure,
    SDO.Airport,
    SDO.Aquarium,
    SDO.Beach,
    SDO.BoatTerminal,
    SDO.Bridge,
    SDO.BusStation,
    SDO.BusStop,
    SDO.Campground,
    SDO.Cemetery,
    SDO.Crematorium,
    SDO.EducationalOrganization,
    SDO.EventVenue,
    SDO.FireStation,
    SDO.GovernmentBuilding,
    SDO.CityHall,
    SDO.Courthouse,
    SDO.DefenceEstablishment,
    SDO.Embassy,
    SDO.LegislativeBuilding,
    SDO.Hospital,
    SDO.MovieTheater,
    SDO.Museum,
    SDO.MusicVenue,
    SDO.Park,
    SDO.ParkingFacility,
    SDO.PerformingArtsTheater,
    SDO.PlaceOfWorship,
    SDO.BuddhistTemple,
    SDO.Church,
    SDO.CatholicChurch,
    SDO.HinduTemple,
    SDO.Mosque,
    SDO.Synagogue,
    SDO.Playground,
    SDO.PoliceStation,
    SDO.PublicToilet,
    SDO.RVPark,
    SDO.StadiumOrArena,
    SDO.SubwayStation,
    SDO.TaxiStand,
    SDO.TrainStation,
    SDO.Zoo,
    SDO.Landform,
    SDO.BodyOfWater,
    SDO.Canal,
    SDO.LakeBodyOfWater,
    SDO.OceanBodyOfWater,
    SDO.Pond,
    SDO.Reservoir,
    SDO.RiverBodyOfWater,
    SDO.SeaBodyOfWater,
    SDO.Waterfall,
    SDO.Continent,
    SDO.Mountain,
    SDO.Volcano,
    SDO.LandmarksOrHistoricalBuildings,
    SDO.LocalBusiness,
    SDO.Residence,
    SDO.ApartmentComplex,
    SDO.GatedResidenceCommunity,
    SDO.TouristAttraction,
    SDO.TouristDestination
]
sdo_event = [
    SDO.Event,
    SDO.BusinessEvent,
    SDO.ChildrensEvent,
    SDO.ComedyEvent,
    SDO.CourseInstance,
    SDO.DanceEvent,
    SDO.DeliveryEvent,
    SDO.EducationEvent,
    SDO.EventSeries,
    SDO.ExhibitionEvent,
    SDO.Festival,
    SDO.FoodEvent,
    SDO.Hackathon,
    SDO.LiteraryEvent,
    SDO.MusicEvent,
    SDO.PublicationEvent,
    SDO.BroadcastEvent,
    SDO.OnDemandEvent,
    SDO.SaleEvent,
    SDO.ScreeningEvent,
    SDO.SocialEvent,
    SDO.SportsEvent,
    SDO.TheaterEvent,
    SDO.UserInteraction,
    SDO.UserBlocks,
    SDO.UserCheckins,
    SDO.UserComments,
    SDO.UserDownloads,
    SDO.UserLikes,
    SDO.UserPageVisits,
    SDO.UserPlays,
    SDO.UserPlusOnes,
    SDO.UserTweets,
    SDO.VisualArtsEvent
]
sdo_item = [
    SDO.CreativeWork,
    SDO.AmpStory,
    SDO.ArchiveComponent,
    SDO.Article,
    SDO.AdvertiserContentArticle,
    SDO.NewsArticle,
    SDO.AnalysisNewsArticle,
    SDO.AskPublicNewsArticle,
    SDO.BackgroundNewsArticle,
    SDO.OpinionNewsArticle,
    SDO.ReportageNewsArticle,
    SDO.ReviewNewsArticle,
    SDO.Report,
    SDO.SatiricalArticle,
    SDO.ScholarlyArticle,
    SDO.MedicalScholarlyArticle,
    SDO.SocialMediaPosting,
    SDO.BlogPosting,
    SDO.LiveBlogPosting,
    SDO.DiscussionForumPosting,
    SDO.TechArticle,
    SDO.APIReference,
    SDO.Atlas,
    SDO.Blog,
    SDO.Book,
    SDO.Audiobook,
    #SDO.Certification,
    SDO.Chapter,
    SDO.Claim,
    SDO.Clip,
    SDO.MovieClip,
    SDO.RadioClip,
    SDO.TVClip,
    SDO.VideoGameClip,
    SDO.Code,
    SDO.Collection,
    SDO.ProductCollection,
    SDO.ComicStory,
    SDO.ComicCoverArt,
    SDO.Comment,
    SDO.Answer,
    SDO.CorrectionComment,
    SDO.Question,
    SDO.Conversation,
    SDO.Course,
    SDO.CreativeWorkSeason,
    SDO.PodcastSeason,
    SDO.RadioSeason,
    SDO.TVSeason,
    SDO.CreativeWorkSeries,
    SDO.BookSeries,
    SDO.MovieSeries,
    SDO.Periodical,
    SDO.ComicSeries,
    SDO.Newspaper,
    SDO.PodcastSeries,
    SDO.RadioSeries,
    SDO.TVSeries,
    SDO.VideoGameSeries,
    SDO.DataCatalog,
    SDO.Dataset,
    SDO.DataFeed,
    SDO.CompleteDataFeed,
    SDO.DefinedTermSet,
    SDO.CategoryCodeSet,
    SDO.Diet,
    SDO.DigitalDocument,
    SDO.NoteDigitalDocument,
    SDO.PresentationDigitalDocument,
    SDO.SpreadsheetDigitalDocument,
    SDO.TextDigitalDocument,
    SDO.Drawing,
    SDO.EducationalOccupationalCredential,
    SDO.Episode,
    SDO.PodcastEpisode,
    SDO.RadioEpisode,
    SDO.TVEpisode,
    SDO.ExercisePlan,
    SDO.Game,
    SDO.VideoGame,
    SDO.Guide,
    SDO.HowTo,
    SDO.Recipe,
    SDO.HowToDirection,
    SDO.HowToSection,
    SDO.HowToStep,
    SDO.HowToTip,
    SDO.HyperToc,
    SDO.HyperTocEntry,
    SDO.LearningResource,
    SDO.Course,
    SDO.Quiz,
    #SDO.Syllabus,
    SDO.Legislation,
    SDO.LegislationObject,
    SDO.Manuscript,
    SDO.Map,
    SDO.MathSolver,
    SDO.MediaObject,
    #SDO['3DModel'], # Alternative notation due to number
    SDO.AmpStory,
    SDO.AudioObject,
    SDO.AudioObjectSnapshot,
    SDO.Audiobook,
    SDO.DataDownload,
    SDO.ImageObject,
    SDO.Barcode,
    SDO.ImageObjectSnapshot,
    SDO.LegislationObject,
    SDO.MusicVideoObject,
    #SDO.TextObject,
    SDO.VideoObject,
    SDO.VideoObjectSnapshot,
    SDO.MediaReviewItem,
    SDO.Menu,
    SDO.MenuSection,
    SDO.Message,
    SDO.EmailMessage,
    SDO.Movie,
    SDO.MusicComposition,
    SDO.MusicPlaylist,
    SDO.MusicAlbum,
    SDO.MusicRelease,
    SDO.MusicRecording,
    SDO.Painting,
    SDO.Photograph,
    SDO.Play,
    SDO.Poster,
    SDO.PublicationIssue,
    SDO.ComicIssue,
    SDO.PublicationVolume,
    SDO.Quotation,
    SDO.Review,
    SDO.ClaimReview,
    SDO.CriticReview,
    SDO.ReviewNewsArticle,
    SDO.EmployerReview,
    SDO.MediaReview,
    SDO.Recommendation,
    SDO.UserReview,
    SDO.Sculpture,
    SDO.Season,
    SDO.SheetMusic,
    SDO.ShortStory,
    SDO.SoftwareApplication,
    SDO.MobileApplication,
    SDO.VideoGame,
    SDO.WebApplication,
    SDO.SoftwareSourceCode,
    SDO.SpecialAnnouncement,
    SDO.Statement,
    SDO.TVSeason,
    SDO.TVSeries,
    SDO.Thesis,
    SDO.VisualArtwork,
    SDO.CoverArt,
    SDO.ComicCoverArt,
    SDO.WebContent,
    SDO.HealthTopicContent,
    SDO.WebPage,
    SDO.AboutPage,
    SDO.CheckoutPage,
    SDO.CollectionPage,
    SDO.MediaGallery,
    SDO.ImageGallery,
    SDO.VideoGallery,
    SDO.ContactPage,
    SDO.FAQPage,
    SDO.ItemPage,
    SDO.MedicalWebPage,
    SDO.ProfilePage,
    SDO.QAPage,
    SDO.RealEstateListing,
    SDO.SearchResultsPage,
    SDO.WebPageElement,
    SDO.SiteNavigationElement,
    SDO.Table,
    SDO.WPAdBlock,
    SDO.WPFooter,
    SDO.WPHeader,
    SDO.WPSideBar,
    SDO.WebSite
]
