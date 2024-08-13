# Classes to serialise nfdicore/cto triples
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
from sources.ingest import FeedData, FeedElementData

# Define namespaces
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD
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
SCHEMA = Namespace('http://schema.org/')


# FEED ELEMENT ################################################################


class FeedElement:
    '''
    Object designed to serialise all triples for an nfdicore/cto feed element
    '''

    store = None


    @property
    def feed_uri(self):
        '''
        URI of the feed that the element is part of (provides single URIRef)
        '''
        return self._feed_uri

    @feed_uri.setter
    def feed_uri(self, value:str|Literal|URIRef|None):
        self._feed_uri = urify(value)


    @property
    def element_type(self):
        '''
        Schema.org class URI or generic string 'person', 'organization', 'place', 'event', or 'item' (provides single URIRef or string)
        '''
        return self._element_type

    @element_type.setter
    def element_type(self, value:str|URIRef|None):
        self._element_type = spacify_uri(value)


    @property
    def element_uri(self):
        '''
        URI of the feed element (provides single URIRef)
        '''
        return self._element_uri

    @element_uri.setter
    def element_uri(self, value:str|Literal|URIRef|None):
        self._element_uri = urify(value)


    @property
    def element_uri_same(self):
        '''
        Additional URIs identifying the same feed element (provides list of URIRef)
        '''
        return self._element_uri_same

    @element_uri_same.setter
    def element_uri_same(self, value:str|list|Literal|URIRef|None):
        self._element_uri_same = urify_list(value)


    @property
    def label(self):
        '''
        Main text label of the feed element (provides list of Literal)
        '''
        return self._label

    @label.setter
    def label(self, value:str|list|Literal|URIRef|None):
        self._label = literalify_list(value)


    @property
    def label_alt(self):
        '''
        Alternative text label of the feel element (provides list of Literal)
        '''
        return self._label_alt

    @label_alt.setter
    def label_alt(self, value:str|list|Literal|URIRef|None):
        self._label_alt = literalify_list(value)


    @property
    def shelf_mark(self):
        '''
        Shelf mark in a holding repository, such as a library (provides list of Literal)
        '''
        return self._shelf_mark

    @shelf_mark.setter
    def shelf_mark(self, value:str|list|Literal|URIRef|None):
        self._shelf_mark = literalify_list(value)


    @property
    def image(self):
        '''
        URL of an image representation of the element (provides list of Literal)
        '''
        return self._image

    @image.setter
    def image(self, value:str|list|Literal|URIRef|None):
        self._image = literalify_list(value, SCHEMA.URL)


    @property
    def lyrics(self):
        '''
        Lyrics of a musical composition (provides list of Literal)
        '''
        return self._lyrics

    @lyrics.setter
    def lyrics(self, value:str|list|Literal|URIRef|None):
        self._lyrics = literalify_list(value)


    @property
    def text_incipit(self):
        '''
        First few words of text content (provides list of Literal)
        '''
        return self._text_incipit

    @text_incipit.setter
    def text_incipit(self, value:str|list|Literal|URIRef|None):
        self._text_incipit = literalify_list(value)


    @property
    def music_incipit(self):
        '''
        Dictionary with the keys 'uri' (optional), 'clef', 'key_sig', 'time_sig', and 'pattern' (provides list of dict)
        '''
        return self._music_incipit

    @music_incipit.setter
    def music_incipit(self, value:dict|list|None):
        self._music_incipit = dictify_list(value, ['uri', 'clef', 'key_sig', 'time_sig', 'pattern'])
        checked = []
        for i in self._music_incipit:
            i['uri'] = urify(i['uri'])
            i['clef'] = literalify(i['clef'])
            i['key_sig'] = literalify(i['key_sig'])
            i['time_sig'] = literalify(i['time_sig'])
            i['pattern'] = literalify(i['pattern'])
            checked.append(i)
        self._music_incipit = checked


    @property
    def source_file(self):
        '''
        URL of the data source used for this element (provides list of Literal)
        '''
        return self._source_file

    @source_file.setter
    def source_file(self, value:str|list|Literal|URIRef|None):
        self._source_file = literalify_list(value, SCHEMA.URL)


    @property
    def iiif_image_api(self):
        '''
        URL of the IIIF Image API of this element (provides list of Literal)
        '''
        return self._iiif_image_api

    @iiif_image_api.setter
    def iiif_image_api(self, value:str|list|Literal|URIRef|None):
        self._iiif_image_api = literalify_list(value, SCHEMA.URL)


    @property
    def iiif_presentation_api(self):
        '''
        URL of the IIIF Presentation API of this element (provides list of Literal)
        '''
        return self._iiif_presentation_api

    @iiif_presentation_api.setter
    def iiif_presentation_api(self, value:str|list|Literal|URIRef|None):
        self._iiif_presentation_api = literalify_list(value, SCHEMA.URL)


    @property
    def ddb_api(self):
        '''
        URL of the DDB API of this element (provides list of Literal)
        '''
        return self._ddb_api

    @ddb_api.setter
    def ddb_api(self, value:str|list|Literal|URIRef|None):
        self._ddb_api = literalify_list(value, SCHEMA.URL)


    @property
    def oaipmh_api(self):
        '''
        URL of the OAI-PMH API of this element (provides list of Literal)
        '''
        return self._oaipmh_api

    @oaipmh_api.setter
    def oaipmh_api(self, value:str|list|Literal|URIRef|None):
        self._oaipmh_api = literalify_list(value, SCHEMA.URL)


    @property
    def publisher(self):
        '''
        URI of the publisher of the element (provides list of URIRef)
        '''
        return self._publisher

    @publisher.setter
    def publisher(self, value:str|list|Literal|URIRef|None):
        self._publisher = urify_list(value)


    @property
    def license(self):
        '''
        URI of the element's license (provides list of URIRef)
        '''
        return self._license

    @license.setter
    def license(self, value:str|list|Literal|URIRef|None):
        self._license = urify_list(value)


    @property
    def vocab_element_type(self):
        '''
        Getty AAT URI and/or another string indicating the element type (provides list of URIRef or Literal)
        '''
        return self._vocab_element_type

    @vocab_element_type.setter
    def vocab_element_type(self, value:str|tuple|list|Literal|URIRef|None):
        self._vocab_element_type = tuplify_uri_literal_list(value)


    @property
    def vocab_subject_concept(self):
        '''
        URI and/or string of a subject, including Iconclass (provides list of URIRef or Literal)
        '''
        return self._vocab_subject_concept

    @vocab_subject_concept.setter
    def vocab_subject_concept(self, value:str|tuple|list|Literal|URIRef|None):
        self._vocab_subject_concept = tuplify_uri_literal_list(value)


    @property
    def vocab_related_location(self):
        '''
        URI and/or string of a related place, including GeoNames (provides list of URIRef or Literal)
        '''
        return self._vocab_related_location

    @vocab_related_location.setter
    def vocab_related_location(self, value:str|tuple|list|Literal|URIRef|None):
        self._vocab_related_location = tuplify_uri_literal_list(value)


    @property
    def vocab_related_event(self):
        '''
        URI and/or string of a related event (provides list of URIRef or Literal)
        '''
        return self._vocab_related_event

    @vocab_related_event.setter
    def vocab_related_event(self, value:str|tuple|list|Literal|URIRef|None):
        self._vocab_related_event = tuplify_uri_literal_list(value)


    @property
    def vocab_related_organization(self):
        '''
        URI and/or string of a related organization, including ISILs (provides list of URIRef or Literal)
        '''
        return self._vocab_related_organization

    @vocab_related_organization.setter
    def vocab_related_organization(self, value:str|tuple|list|Literal|URIRef|None):
        self._vocab_related_organization = tuplify_uri_literal_list(value)


    @property
    def vocab_related_person(self):
        '''
        URI and/or string of a related person (provides list of URIRef or Literal)
        '''
        return self._vocab_related_person

    @vocab_related_person.setter
    def vocab_related_person(self, value:str|tuple|list|Literal|URIRef|None):
        self._vocab_related_person = tuplify_uri_literal_list(value)


    @property
    def vocab_further(self):
        '''
        URI of further vocabulary terms which do not fit other categories (provides list of URIRef)
        '''
        return self._vocab_further

    @vocab_further.setter
    def vocab_further(self, value:str|list|Literal|URIRef|None):
        self._vocab_further = urify_list(value)


    @property
    def related_item(self):
        '''
        URI of a related creative work (provides list of URIRef)
        '''
        return self._related_item

    @related_item.setter
    def related_item(self, value:str|list|Literal|URIRef|None):
        self._related_item = urify_list(value)


    @property
    def birth_date(self):
        '''
        Exact date, datetime, or timestamp of a person's birth (provides list of Literal)
        '''
        return self._birth_date

    @birth_date.setter
    def birth_date(self, value:str|int|date|datetime|list|Literal|None):
        self._birth_date = datify_list(value)


    @property
    def death_date(self):
        '''
        Exact date, datetime, or timestamp of a person's death (provides list of Literal)
        '''
        return self._death_date

    @death_date.setter
    def death_date(self, value:str|int|date|datetime|list|Literal|None):
        self._death_date = datify_list(value)


    @property
    def foundation_date(self):
        '''
        Exact date, datetime, or timestamp of an organisation's foundation (provides list of Literal)
        '''
        return self._foundation_date

    @foundation_date.setter
    def foundation_date(self, value:str|int|date|datetime|list|Literal|None):
        self._foundation_date = datify_list(value)


    @property
    def dissolution_date(self):
        '''
        Exact date, datetime, or timestamp of an organisation's dissolution (provides list of Literal)
        '''
        return self._dissolution_date

    @dissolution_date.setter
    def dissolution_date(self, value:str|int|date|datetime|list|Literal|None):
        self._dissolution_date = datify_list(value)


    @property
    def start_date(self):
        '''
        Exact date, datetime, or timestamp when an event started (provides list of Literal)
        '''
        return self._start_date

    @start_date.setter
    def start_date(self, value:str|int|date|datetime|list|Literal|None):
        self._start_date = datify_list(value)


    @property
    def end_date(self):
        '''
        Exact date, datetime, or timestamp when an event ended (provides list of Literal)
        '''
        return self._end_date

    @end_date.setter
    def end_date(self, value:str|int|date|datetime|list|Literal|None):
        self._end_date = datify_list(value)


    @property
    def creation_date(self):
        '''
        Exact date, datetime, or timestamp of an item's creation (provides list of Literal)
        '''
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value:str|int|date|datetime|list|Literal|None):
        self._creation_date = datify_list(value)


    @property
    def creation_period(self):
        '''
        String providing an item's creation period (provides list of Literal)
        '''
        return self._creation_period

    @creation_period.setter
    def creation_period(self, value:str|list|Literal|None):
        self._creation_period = periodify_or_literalify_list(value)


    @property
    def destruction_date(self):
        '''
        Exact date, datetime, or timestamp of an item's destruction (provides list of Literal)
        '''
        return self._destruction_date

    @destruction_date.setter
    def destruction_date(self, value:str|int|date|datetime|list|Literal|None):
        self._destruction_date = datify_list(value)


    @property
    def approximate_period(self):
        '''
        String providing a period that an item is associated with (provides list of Literal)
        '''
        return self._approximate_period

    @approximate_period.setter
    def approximate_period(self, value:str|list|Literal|None):
        self._approximate_period = periodify_or_literalify_list(value)


    @property
    def existence_period(self):
        '''
        String providing the period of an item's existence (provides list of Literal)
        '''
        return self._existence_period

    @existence_period.setter
    def existence_period(self, value:str|list|Literal|None):
        self._existence_period = periodify_or_literalify_list(value)


    def __init__(self, data:FeedElementData|None = None, prepare:bool = True):
        '''
        Object designed to serialise all triples for an nfdicore/cto feed

            Parameters:
                data (FeedElementData|None): Data object to set up the feed
                prepare (bool): Add wrappers to prepare the connection of research data to research information
        '''

        # Assign arguments
        self.prepare = prepare

        # Use data object if available
        if data:
            self.feed_uri = data.feed_uri
            self.element_type = data.element_type
            self.element_uri = data.element_uri
            self.element_uri_same = data.element_uri_same
            self.label = data.label
            self.label_alt = data.label_alt
            self.shelf_mark = data.shelf_mark
            self.image = data.image
            self.lyrics = data.lyrics
            self.text_incipit = data.text_incipit
            self.music_incipit = data.music_incipit
            self.source_file = data.source_file
            self.iiif_image_api = data.iiif_image_api
            self.iiif_presentation_api = data.iiif_presentation_api
            self.ddb_api = data.ddb_api
            self.oaipmh_api = data.oaipmh_api
            self.publisher = data.publisher
            self.license = data.license
            self.vocab_element_type = data.vocab_element_type
            self.vocab_subject_concept = data.vocab_subject_concept
            self.vocab_related_location = data.vocab_related_location
            self.vocab_related_event = data.vocab_related_event
            self.vocab_related_organization = data.vocab_related_organization
            self.vocab_related_person = data.vocab_related_person
            self.vocab_further = data.vocab_further
            self.related_item = data.related_item
            self.birth_date = data.birth_date
            self.death_date = data.death_date
            self.foundation_date = data.foundation_date
            self.dissolution_date = data.dissolution_date
            self.start_date = data.start_date
            self.end_date = data.end_date
            self.creation_date = data.creation_date
            self.creation_period = data.creation_period
            self.destruction_date = data.destruction_date
            self.approximate_period = data.approximate_period
            self.existence_period = data.existence_period


    def generate(self):
        '''
        Generate triples and fill the store attribute
        '''

        # Check requirements
        if self.element_uri == None:
            raise ValueError('The feed element URI is missing.')
        elif self.feed_uri == None:
            raise ValueError('The feed URI is missing.')
        else:
            self.store = spacify_graph()

            # ELEMENT

            # Element and feed URI
            self.store.add((self.element_uri, RDF.type, CTO.DatafeedElement))
            self.store.add((self.element_uri, CTO.elementOf, self.feed_uri))

            # Element type: person
            if self.element_type == 'person' or self.element_type in schema_person:
                self.store.add((self.element_uri, RDF.type, NFDICORE.Person))
             # Element type: organization
            elif self.element_type == 'organization' or self.element_type == 'organisation' or self.element_type in schema_organization:
                self.store.add((self.element_uri, RDF.type, NFDICORE.Organization))
            # Element type: place
            elif self.element_type == 'place' or self.element_type == 'location' or self.element_type in schema_place:
                self.store.add((self.element_uri, RDF.type, NFDICORE.Place))
            # Element type: event
            elif self.element_type == 'event' or self.element_type == 'date' or self.element_type in schema_event:
                self.store.add((self.element_uri, RDF.type, NFDICORE.Event))
            # Element type: item that is a schema.org creative work
            elif self.element_type in schema_item:
                self.store.add((self.element_uri, RDF.type, self.element_type))
            # Element type: generic item
            else:
                self.store.add((self.element_uri, RDF.type, CTO.Item))

            # Same as element URI
            for i in self.element_uri_same:
                self.store.add((self.element_uri, OWL.sameAs, i))

            # Optional wrapper
            if self.prepare:
                wrapper = BNode()
                self.store.add((self.feed_uri, SCHEMA.dataFeedElement, wrapper))
                self.store.add((wrapper, RDF.type, SCHEMA.DataFeedItem))
                self.store.add((wrapper, SCHEMA.item, self.element_uri))

            # LABEL AND REFERENCE LITERALS

            # Main label
            for i in self.label:
                self.store.add((self.element_uri, RDFS.label, i))

            # Alternative label
            for i in self.label_alt:
                self.store.add((self.element_uri, SKOS.altLabel, i))

            # Shelf mark
            for i in self.shelf_mark:
                i = Literal(str(i)) # Removes lang
                self.store.add((self.element_uri, CTO.shelfMark, i))

            # MEDIA LITERALS

            # URL
            self.store.add((self.element_uri, SCHEMA.url, literalify(self.element_uri, SCHEMA.URL)))

            # Image
            for i in self.image:
                self.store.add((self.element_uri, SCHEMA.image, i))

            # Lyrics
            for i in self.lyrics:
                blank = BNode()
                self.store.add((self.element_uri, MO.lyrics, blank))
                self.store.add((blank, RDF.type, MO.Lyrics))
                self.store.add((blank, MO.text, i))

            # Text incipit
            for i in self.text_incipit:
                self.store.add((self.element_uri, CTO.textIncipit, i))

            # Music incipit
            for i in self.music_incipit:
                if i['uri'] != None:
                    uri_or_blank = i['uri']
                else:
                    uri_or_blank = BNode()
                self.store.add((uri_or_blank, RDF.type, CTO.Incipit))
                self.store.add((uri_or_blank, CTO.incipitOf, self.element_uri))
                self.store.add((uri_or_blank, CTO.clef, i['clef']))
                self.store.add((uri_or_blank, CTO.keySignature, i['key_sig']))
                self.store.add((uri_or_blank, CTO.timeSignature, i['time_sig']))
                self.store.add((uri_or_blank, CTO.pattern, i['pattern']))

            # Source file
            for i in self.source_file:
                self.store.add((self.element_uri, CTO.sourceFile, i))

            # API LITERALS

            # IIIF Image API
            for i in self.iiif_image_api:
                self.store.add((self.element_uri, CTO.iiifImageAPI, i))

            # IIIF Presentation API
            for i in self.iiif_presentation_api:
                self.store.add((self.element_uri, CTO.iiifPresentationAPI, i))

            # DDB API
            for i in self.ddb_api:
                self.store.add((self.element_uri, CTO.ddbAPI, i))

            # OAI-PMH API
            for i in self.oaipmh_api:
                self.store.add((self.element_uri, CTO['oai-pmhAPI'], i)) # Alternative notation due to hyphen

            # RIGHTS URIS

            # Publisher
            for i in self.publisher:
                self.store.add((self.element_uri, NFDICORE.publisher, i))

            # License
            for i in self.license:
                self.store.add((self.element_uri, NFDICORE.license, i))

            # RELATED URIS AND FALLBACK LITERALS

            # Element type
            has_uri = None
            for t in self.vocab_element_type:
                for index, i in enumerate(t):
                    if isinstance(i, URIRef):
                        has_uri = index
                if has_uri != None:
                    self.store.add((self.element_uri, CTO.elementType, t[has_uri]))
                    self.store += vocabify(t[has_uri], self.element_uri)
                else:
                    for i in t:
                        self.store.add((self.element_uri, CTO.elementTypeLiteral, i))

            # Subject concept
            has_uri = None
            for t in self.vocab_subject_concept:
                for index, i in enumerate(t):
                    if isinstance(i, URIRef):
                        has_uri = index
                if has_uri != None:
                    self.store.add((self.element_uri, CTO.subjectConcept, t[has_uri]))
                    self.store += vocabify(t[has_uri], self.element_uri)
                else:
                    for i in t:
                        self.store.add((self.element_uri, CTO.subjectConceptLiteral, i))

            # Related location
            has_uri = None
            for t in self.vocab_related_location:
                for index, i in enumerate(t):
                    if isinstance(i, URIRef):
                        has_uri = index
                if has_uri != None:
                    self.store.add((self.element_uri, CTO.relatedLocation, t[has_uri]))
                    self.store.add((t[has_uri], RDF.type, NFDICORE.Place))
                    self.store += vocabify(t[has_uri], self.element_uri)
                    for index, i in enumerate(t):
                        if index != has_uri:
                            self.store.add((t[has_uri], RDFS.label, i))
                else:
                    for i in t:
                        self.store.add((self.element_uri, CTO.relatedLocationLiteral, i))

            # Related event
            has_uri = None
            for t in self.vocab_related_event:
                for index, i in enumerate(t):
                    if isinstance(i, URIRef):
                        has_uri = index
                if has_uri != None:
                    self.store.add((self.element_uri, CTO.relatedEvent, t[has_uri]))
                    self.store.add((t[has_uri], RDF.type, NFDICORE.Event))
                    self.store += vocabify(t[has_uri], self.element_uri)
                    for index, i in enumerate(t):
                        if index != has_uri:
                            self.store.add((t[has_uri], RDFS.label, i))
                else:
                    for i in t:
                        self.store.add((self.element_uri, CTO.relatedEventLiteral, i))

            # Related organization
            has_uri = None
            for t in self.vocab_related_organization:
                for index, i in enumerate(t):
                    if isinstance(i, URIRef):
                        has_uri = index
                if has_uri != None:
                    self.store.add((self.element_uri, CTO.relatedOrganization, t[has_uri]))
                    self.store.add((t[has_uri], RDF.type, NFDICORE.Organization))
                    self.store += vocabify(t[has_uri], self.element_uri)
                    for index, i in enumerate(t):
                        if index != has_uri:
                            self.store.add((t[has_uri], RDFS.label, i))
                else:
                    for i in t:
                        self.store.add((self.element_uri, CTO.relatedOrganizationLiteral, i))

            # Related person
            has_uri = None
            for t in self.vocab_related_person:
                print(str(self.vocab_related_person))
                for index, i in enumerate(t):
                    if isinstance(i, URIRef):
                        has_uri = index
                if has_uri != None:
                    self.store.add((self.element_uri, CTO.relatedPerson, t[has_uri]))
                    self.store.add((t[has_uri], RDF.type, NFDICORE.Person))
                    self.store += vocabify(t[has_uri], self.element_uri)
                    for index, i in enumerate(t):
                        if index != has_uri:
                            self.store.add((t[has_uri], RDFS.label, i))
                else:
                    for i in t:
                        self.store.add((self.element_uri, CTO.relatedPersonLiteral, i))

            # Further vocabularies
            for i in self.vocab_further:
                self.store += vocabify(i, self.element_uri)

            # Related item
            for i in self.related_item:
                self.store.add((self.element_uri, CTO.relatedItem, i))

            # DATES BY TYPE

            # For persons
            if self.element_type == 'person' or self.element_type in schema_person:

                # Birth date
                for i in self.birth_date:
                    self.store.add((self.element_uri, NFDICORE.birthDate, i))

                # Death date
                for i in self.death_date:
                    self.store.add((self.element_uri, NFDICORE.deathDate, i))

            # For organizations
            elif self.element_type == 'organization' or self.element_type == 'organisation' or self.element_type in schema_organization:

                # Foundation date
                for i in self.foundation_date:
                    self.store.add((self.element_uri, NFDICORE.foundationDate, i))

                # Dissolution date
                for i in self.dissolution_date:
                    self.store.add((self.element_uri, NFDICORE.dissolutionDate, i))

            # For places
            elif self.element_type == 'place' or self.element_type == 'location' or self.element_type in schema_place:
                pass

            # For events
            elif self.element_type == 'event' or self.element_type == 'date' or self.element_type in schema_event:

                # Start date
                for i in self.start_date:
                    self.store.add((self.element_uri, NFDICORE.startDate, i))

                # End date
                for i in self.end_date:
                    self.store.add((self.element_uri, NFDICORE.endDate, i))

            # For items
            else:

                # Creation date
                for i in self.creation_date:
                    self.store.add((self.element_uri, CTO.creationDate, i))

                # Creation period
                for i in self.creation_period:
                    self.store.add((self.element_uri, CTO.creationPeriod, i))

                # Destruction date
                for i in self.destruction_date:
                    self.store.add((self.element_uri, CTO.destructionDate, i))

                # Approximate period
                for i in self.approximate_period:
                    self.store.add((self.element_uri, CTO.approximatePeriod, i))

                # Existence period
                for i in self.existence_period:
                    self.store.add((self.element_uri, CTO.existencePeriod, i))


    def turtle(self, file_path:str):
        '''
        Serialise triples as a Turtle file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Store triples and save file
        self.generate()
        self.store.serialize(destination = file_path, format = 'turtle')


    def ntriples(self, file_path:str):
        '''
        Serialise triples as an NTriples file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Store triples and save file
        self.generate()
        self.store.serialize(destination = file_path, format = 'ntriples')


    def rdfxml(self, file_path:str):
        '''
        Serialise triples as an NTriples file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Store triples and save file
        self.generate()
        self.store.serialize(destination = file_path, format = 'xml')


# FEED ########################################################################


class Feed:
    '''
    Object designed to serialise all triples for an nfdicore/cto feed
    '''

    store = None


    @property
    def feed_uri(self):
        '''
        URI of the feed, preferably an NFDI4Culture IRI (provides single URIRef)
        '''
        return self._feed_uri

    @feed_uri.setter
    def feed_uri(self, value:str|Literal|URIRef|None):
        self._feed_uri = urify(value)


    @property
    def feed_uri_same(self):
        '''
        Additional URIs identifying the same feed (provides list of URIRef)
        '''
        return self._feed_uri_same

    @feed_uri_same.setter
    def feed_uri_same(self, value:str|list|Literal|URIRef|None):
        self._feed_uri_same = urify_list(value)


    @property
    def catalog_uri(self):
        '''
        URI of the catalog the feed belongs to, preferably an NFDI4Culture IRI (provides single URIRef)
        '''
        return self._catalog_uri

    @catalog_uri.setter
    def catalog_uri(self, value:str|Literal|URIRef|None):
        self._catalog_uri = urify(value)


    @property
    def catalog_uri_same(self):
        '''
        Additional URIs identifying the same catalog (provides list of URIRef)
        '''
        return self._catalog_uri_same

    @catalog_uri_same.setter
    def catalog_uri_same(self, value:str|Literal|URIRef|None):
        self._catalog_uri_same = urify_list(value)

    @property
    def elements(self):
        '''
        List of elements that are part of this feed (provides list of FeedElement)
        '''
        return self._elements

    @elements.setter
    def elements(self, value:list|FeedElement|None):
        self._elements = elementify_list(value)


    def __init__(self, data:FeedData|None = None, prepare:bool = True):
        '''
        Object designed to serialise all triples for an nfdicore/cto feed

            Parameters:
                data (FeedData|None): Data object to set up the feed
                prepare (bool): Add wrappers to prepare the connection of research data to research information
        '''

        # Assign arguments
        self.prepare = prepare

        # Use data object if available
        if data:
            self.feed_uri = data.feed_uri
            self.feed_uri_same = data.feed_uri_same
            self.catalog_uri = data.catalog_uri
            self.catalog_uri_same = data.catalog_uri_same
            self.elements = data.elements


    def generate(self):
        '''
        Generate triples and fill the store attribute
        '''

        # Check requirements
        if self.feed_uri == None:
            raise ValueError('The feed URI is missing.')
        else:
            self.store = spacify_graph()

            # Feed URI
            self.store.add((self.feed_uri, RDF.type, NFDICORE.Dataset))

            # Optional date modified
            if self.prepare:
                today = date.today()
                self.store.add((self.feed_uri, SCHEMA.dateModified, Literal(today, datatype=XSD.date)))

            # Same as feed URI
            for i in self.feed_uri_same:
                self.store.add((self.feed_uri, OWL.sameAs, i))

            # Catalog URI
            if self.catalog_uri:
                self.store.add((self.catalog_uri, RDF.type, NFDICORE.DataPortal))
                self.store.add((self.catalog_uri, NFDICORE.dataset, self.feed_uri))

                # Same as catalog URI
                for i in self.catalog_uri_same:
                    self.store.add((self.catalog_uri, OWL.sameAs, i))

            # Add element triples and overwrite the feed URI
            for i in self.elements:
                i.feed_uri = self.feed_uri
                i.generate()
                self.store += i.store


    def turtle(self, file_path:str):
        '''
        Serialise triples as a Turtle file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Store triples and save file
        self.generate()
        self.store.serialize(destination = file_path, format = 'turtle')


    def ntriples(self, file_path:str):
        '''
        Serialise triples as an NTriples file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Store triples and save file
        self.generate()
        self.store.serialize(destination = file_path, format = 'ntriples')


    def rdfxml(self, file_path:str):
        '''
        Serialise triples as an NTriples file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Store triples and save file
        self.generate()
        self.store.serialize(destination = file_path, format = 'xml')


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


def tuplify_uri_literal(input:str|tuple|Literal|URIRef) -> tuple:
    '''
    Make sure a variable contains a tuple with a URIRef and/or Literals

        Parameters:
            input (str|tuple|Literal|URIRef): Variable to check and transform

        Returns:
            tuple: Tuple with a URI value and/or Literals
    '''

    # Turn str to tuple
    if isinstance(input, str):
        if input != '':
            input = (Literal(input),)
        else:
            input = None

    # Turn Literal to tuple
    elif isinstance(input, Literal):
        if str(input) != '':
            input = (input,)
        else:
            input = None

    # Turn URIRef to tuple
    elif isinstance(input, URIRef):
        if str(input) != '':
            input = (input,)
        else:
            input = None

    # Check tuples to contain only Literals and URIRefs
    if isinstance(input, tuple):
        output = []
        for i in input:
            if isinstance(i, URIRef):
                output.append(i)
            elif isinstance(i, Literal):
                i_check = urify(str(i))
                if i_check != None:
                    output.append(i_check)
                else:
                    i_check = literalify(i)
                    if i_check != None:
                        output.append(i_check)
        input = tuple(output)
    else:
        input = None

    # Return tuple
    return input


def tuplify_uri_literal_list(input:str|tuple|list|Literal|URIRef|None) -> list:
    '''
    Make sure a variable contains a list of tuples with a URIRef and/or Literals

        Parameters:
            input (str|tuple|list|Literal|URIRef|None): Variable to check and transform

        Returns:
            list: List of tuples with a URI value and/or Literals
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn str, tuple, URIRef, and Literal to list
    elif isinstance(input, (str, tuple, URIRef, Literal)):
        input = [input]

    # Turn each list item to tuple
    output = []
    for i in input:
        i = tuplify_uri_literal(i)
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
            input = Literal(input, datatype = SCHEMA.DateTime)
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


def elementify_list(input:list|FeedElement|None) -> list:
    '''
    Make sure a variable contains a list of FeedElements

        Parameters:
            input (list|FeedElement|None): Variable to check and transform

        Returns:
            list: List of FeedElements
    '''

    # Catch type None
    if input == None:
        input = []

    # Turn FeedElement to list
    elif isinstance(input, FeedElement):
        input = [input]

    # Remove other types
    elif not isinstance(input, list):
        input = []

    # Check list
    output = []
    for i in input:
        if isinstance(i, FeedElement):
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
    output.bind('schema', SCHEMA)
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
        SCHEMA,
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
# Some SCHEMA items commented out as they are not in RDFLib's internal library
schema_feed = [
    SCHEMA.DataFeed,
    SCHEMA.Dataset
]
schema_person = [
    SCHEMA.Person,
    SCHEMA.Patient
]
schema_organization = [
    SCHEMA.Organization,
    SCHEMA.Airline,
    SCHEMA.Consortium,
    SCHEMA.Corporation,
    SCHEMA.EducationalOrganization,
    SCHEMA.CollegeOrUniversity,
    SCHEMA.ElementarySchool,
    SCHEMA.HighSchool,
    SCHEMA.MiddleSchool,
    SCHEMA.Preschool,
    SCHEMA.School,
    SCHEMA.FundingScheme,
    SCHEMA.GovernmentOrganization,
    SCHEMA.LibrarySystem,
    SCHEMA.LocalBusiness,
    SCHEMA.AnimalShelter,
    SCHEMA.ArchiveOrganization,
    SCHEMA.AutomotiveBusiness,
    SCHEMA.AutoBodyShop,
    SCHEMA.AutoDealer,
    SCHEMA.AutoPartsStore,
    SCHEMA.AutoRental,
    SCHEMA.AutoRepair,
    SCHEMA.AutoWash,
    SCHEMA.GasStation,
    SCHEMA.MotorcycleDealer,
    SCHEMA.MotorcycleRepair,
    SCHEMA.ChildCare,
    SCHEMA.Dentist,
    SCHEMA.DryCleaningOrLaundry,
    SCHEMA.EmergencyService,
    SCHEMA.FireStation,
    SCHEMA.Hospital,
    SCHEMA.PoliceStation,
    SCHEMA.EmploymentAgency,
    SCHEMA.EntertainmentBusiness,
    SCHEMA.AdultEntertainment,
    SCHEMA.AmusementPark,
    SCHEMA.ArtGallery,
    SCHEMA.Casino,
    SCHEMA.ComedyClub,
    SCHEMA.MovieTheater,
    SCHEMA.NightClub,
    SCHEMA.FinancialService,
    SCHEMA.AccountingService,
    SCHEMA.AutomatedTeller,
    SCHEMA.BankOrCreditUnion,
    SCHEMA.InsuranceAgency,
    SCHEMA.FoodEstablishment,
    SCHEMA.Bakery,
    SCHEMA.BarOrPub,
    SCHEMA.Brewery,
    SCHEMA.CafeOrCoffeeShop,
    SCHEMA.Distillery,
    SCHEMA.FastFoodRestaurant,
    SCHEMA.IceCreamShop,
    SCHEMA.Restaurant,
    SCHEMA.Winery,
    SCHEMA.GovernmentOffice,
    SCHEMA.PostOffice,
    SCHEMA.HealthAndBeautyBusiness,
    SCHEMA.BeautySalon,
    SCHEMA.DaySpa,
    SCHEMA.HairSalon,
    SCHEMA.HealthClub,
    SCHEMA.NailSalon,
    SCHEMA.TattooParlor,
    SCHEMA.HomeAndConstructionBusiness,
    SCHEMA.Electrician,
    SCHEMA.GeneralContractor,
    SCHEMA.HVACBusiness,
    SCHEMA.HousePainter,
    SCHEMA.Locksmith,
    SCHEMA.MovingCompany,
    SCHEMA.Plumber,
    SCHEMA.RoofingContractor,
    SCHEMA.InternetCafe,
    SCHEMA.LegalService,
    SCHEMA.Attorney,
    SCHEMA.Notary,
    SCHEMA.Library,
    SCHEMA.LodgingBusiness,
    SCHEMA.BedAndBreakfast,
    SCHEMA.Campground,
    SCHEMA.Hostel,
    SCHEMA.Hotel,
    SCHEMA.Motel,
    SCHEMA.Resort,
    SCHEMA.SkiResort,
    SCHEMA.VacationRental,
    SCHEMA.MedicalBusiness,
    SCHEMA.Dentist,
    SCHEMA.MedicalClinic,
    SCHEMA.CovidTestingFacility,
    SCHEMA.Optician,
    SCHEMA.Pharmacy,
    SCHEMA.Physician,
    SCHEMA.IndividualPhysician,
    SCHEMA.PhysiciansOffice,
    SCHEMA.ProfessionalService,
    SCHEMA.RadioStation,
    SCHEMA.RealEstateAgent,
    SCHEMA.RecyclingCenter,
    SCHEMA.SelfStorage,
    SCHEMA.ShoppingCenter,
    SCHEMA.SportsActivityLocation,
    SCHEMA.BowlingAlley,
    SCHEMA.ExerciseGym,
    SCHEMA.GolfCourse,
    SCHEMA.HealthClub,
    SCHEMA.PublicSwimmingPool,
    SCHEMA.SkiResort,
    SCHEMA.SportsClub,
    SCHEMA.StadiumOrArena,
    SCHEMA.TennisComplex,
    SCHEMA.Store,
    SCHEMA.AutoPartsStore,
    SCHEMA.BikeStore,
    SCHEMA.BookStore,
    SCHEMA.ClothingStore,
    SCHEMA.ComputerStore,
    SCHEMA.ConvenienceStore,
    SCHEMA.DepartmentStore,
    SCHEMA.ElectronicsStore,
    SCHEMA.Florist,
    SCHEMA.FurnitureStore,
    SCHEMA.GardenStore,
    SCHEMA.GroceryStore,
    SCHEMA.HardwareStore,
    SCHEMA.HobbyShop,
    SCHEMA.HomeGoodsStore,
    SCHEMA.JewelryStore,
    SCHEMA.LiquorStore,
    SCHEMA.MensClothingStore,
    SCHEMA.MobilePhoneStore,
    SCHEMA.MovieRentalStore,
    SCHEMA.MusicStore,
    SCHEMA.OfficeEquipmentStore,
    SCHEMA.OutletStore,
    SCHEMA.PawnShop,
    SCHEMA.PetStore,
    SCHEMA.ShoeStore,
    SCHEMA.SportingGoodsStore,
    SCHEMA.TireShop,
    SCHEMA.ToyStore,
    SCHEMA.WholesaleStore,
    SCHEMA.TelevisionStation,
    SCHEMA.TouristInformationCenter,
    SCHEMA.TravelAgency,
    SCHEMA.MedicalOrganization,
    SCHEMA.Dentist,
    SCHEMA.DiagnosticLab,
    SCHEMA.Hospital,
    SCHEMA.MedicalClinic,
    SCHEMA.Pharmacy,
    SCHEMA.Physician,
    SCHEMA.VeterinaryCare,
    SCHEMA.NGO,
    SCHEMA.NewsMediaOrganization,
    SCHEMA.OnlineBusiness,
    SCHEMA.OnlineStore,
    SCHEMA.PerformingGroup,
    SCHEMA.DanceGroup,
    SCHEMA.MusicGroup,
    SCHEMA.TheaterGroup,
    SCHEMA.PoliticalParty,
    SCHEMA.Project,
    SCHEMA.FundingAgency,
    SCHEMA.ResearchProject,
    SCHEMA.ResearchOrganization,
    SCHEMA.SearchRescueOrganization,
    SCHEMA.SportsOrganization,
    SCHEMA.SportsTeam,
    SCHEMA.WorkersUnion
]
schema_place = [
    SCHEMA.Place,
    SCHEMA.Accommodation,
    SCHEMA.Apartment,
    SCHEMA.CampingPitch,
    SCHEMA.House,
    SCHEMA.SingleFamilyResidence,
    SCHEMA.Room,
    SCHEMA.HotelRoom,
    SCHEMA.MeetingRoom,
    SCHEMA.Suite,
    SCHEMA.AdministrativeArea,
    SCHEMA.City,
    SCHEMA.Country,
    SCHEMA.SchoolDistrict,
    SCHEMA.State,
    SCHEMA.CivicStructure,
    SCHEMA.Airport,
    SCHEMA.Aquarium,
    SCHEMA.Beach,
    SCHEMA.BoatTerminal,
    SCHEMA.Bridge,
    SCHEMA.BusStation,
    SCHEMA.BusStop,
    SCHEMA.Campground,
    SCHEMA.Cemetery,
    SCHEMA.Crematorium,
    SCHEMA.EducationalOrganization,
    SCHEMA.EventVenue,
    SCHEMA.FireStation,
    SCHEMA.GovernmentBuilding,
    SCHEMA.CityHall,
    SCHEMA.Courthouse,
    SCHEMA.DefenceEstablishment,
    SCHEMA.Embassy,
    SCHEMA.LegislativeBuilding,
    SCHEMA.Hospital,
    SCHEMA.MovieTheater,
    SCHEMA.Museum,
    SCHEMA.MusicVenue,
    SCHEMA.Park,
    SCHEMA.ParkingFacility,
    SCHEMA.PerformingArtsTheater,
    SCHEMA.PlaceOfWorship,
    SCHEMA.BuddhistTemple,
    SCHEMA.Church,
    SCHEMA.CatholicChurch,
    SCHEMA.HinduTemple,
    SCHEMA.Mosque,
    SCHEMA.Synagogue,
    SCHEMA.Playground,
    SCHEMA.PoliceStation,
    SCHEMA.PublicToilet,
    SCHEMA.RVPark,
    SCHEMA.StadiumOrArena,
    SCHEMA.SubwayStation,
    SCHEMA.TaxiStand,
    SCHEMA.TrainStation,
    SCHEMA.Zoo,
    SCHEMA.Landform,
    SCHEMA.BodyOfWater,
    SCHEMA.Canal,
    SCHEMA.LakeBodyOfWater,
    SCHEMA.OceanBodyOfWater,
    SCHEMA.Pond,
    SCHEMA.Reservoir,
    SCHEMA.RiverBodyOfWater,
    SCHEMA.SeaBodyOfWater,
    SCHEMA.Waterfall,
    SCHEMA.Continent,
    SCHEMA.Mountain,
    SCHEMA.Volcano,
    SCHEMA.LandmarksOrHistoricalBuildings,
    SCHEMA.LocalBusiness,
    SCHEMA.Residence,
    SCHEMA.ApartmentComplex,
    SCHEMA.GatedResidenceCommunity,
    SCHEMA.TouristAttraction,
    SCHEMA.TouristDestination
]
schema_event = [
    SCHEMA.Event,
    SCHEMA.BusinessEvent,
    SCHEMA.ChildrensEvent,
    SCHEMA.ComedyEvent,
    SCHEMA.CourseInstance,
    SCHEMA.DanceEvent,
    SCHEMA.DeliveryEvent,
    SCHEMA.EducationEvent,
    SCHEMA.EventSeries,
    SCHEMA.ExhibitionEvent,
    SCHEMA.Festival,
    SCHEMA.FoodEvent,
    SCHEMA.Hackathon,
    SCHEMA.LiteraryEvent,
    SCHEMA.MusicEvent,
    SCHEMA.PublicationEvent,
    SCHEMA.BroadcastEvent,
    SCHEMA.OnDemandEvent,
    SCHEMA.SaleEvent,
    SCHEMA.ScreeningEvent,
    SCHEMA.SocialEvent,
    SCHEMA.SportsEvent,
    SCHEMA.TheaterEvent,
    SCHEMA.UserInteraction,
    SCHEMA.UserBlocks,
    SCHEMA.UserCheckins,
    SCHEMA.UserComments,
    SCHEMA.UserDownloads,
    SCHEMA.UserLikes,
    SCHEMA.UserPageVisits,
    SCHEMA.UserPlays,
    SCHEMA.UserPlusOnes,
    SCHEMA.UserTweets,
    SCHEMA.VisualArtsEvent
]
schema_item = [
    SCHEMA.CreativeWork,
    SCHEMA.AmpStory,
    SCHEMA.ArchiveComponent,
    SCHEMA.Article,
    SCHEMA.AdvertiserContentArticle,
    SCHEMA.NewsArticle,
    SCHEMA.AnalysisNewsArticle,
    SCHEMA.AskPublicNewsArticle,
    SCHEMA.BackgroundNewsArticle,
    SCHEMA.OpinionNewsArticle,
    SCHEMA.ReportageNewsArticle,
    SCHEMA.ReviewNewsArticle,
    SCHEMA.Report,
    SCHEMA.SatiricalArticle,
    SCHEMA.ScholarlyArticle,
    SCHEMA.MedicalScholarlyArticle,
    SCHEMA.SocialMediaPosting,
    SCHEMA.BlogPosting,
    SCHEMA.LiveBlogPosting,
    SCHEMA.DiscussionForumPosting,
    SCHEMA.TechArticle,
    SCHEMA.APIReference,
    SCHEMA.Atlas,
    SCHEMA.Blog,
    SCHEMA.Book,
    SCHEMA.Audiobook,
    SCHEMA.Certification,
    SCHEMA.Chapter,
    SCHEMA.Claim,
    SCHEMA.Clip,
    SCHEMA.MovieClip,
    SCHEMA.RadioClip,
    SCHEMA.TVClip,
    SCHEMA.VideoGameClip,
    SCHEMA.Code,
    SCHEMA.Collection,
    SCHEMA.ProductCollection,
    SCHEMA.ComicStory,
    SCHEMA.ComicCoverArt,
    SCHEMA.Comment,
    SCHEMA.Answer,
    SCHEMA.CorrectionComment,
    SCHEMA.Question,
    SCHEMA.Conversation,
    SCHEMA.Course,
    SCHEMA.CreativeWorkSeason,
    SCHEMA.PodcastSeason,
    SCHEMA.RadioSeason,
    SCHEMA.TVSeason,
    SCHEMA.CreativeWorkSeries,
    SCHEMA.BookSeries,
    SCHEMA.MovieSeries,
    SCHEMA.Periodical,
    SCHEMA.ComicSeries,
    SCHEMA.Newspaper,
    SCHEMA.PodcastSeries,
    SCHEMA.RadioSeries,
    SCHEMA.TVSeries,
    SCHEMA.VideoGameSeries,
    SCHEMA.DataCatalog,
    SCHEMA.Dataset,
    SCHEMA.DataFeed,
    SCHEMA.CompleteDataFeed,
    SCHEMA.DefinedTermSet,
    SCHEMA.CategoryCodeSet,
    SCHEMA.Diet,
    SCHEMA.DigitalDocument,
    SCHEMA.NoteDigitalDocument,
    SCHEMA.PresentationDigitalDocument,
    SCHEMA.SpreadsheetDigitalDocument,
    SCHEMA.TextDigitalDocument,
    SCHEMA.Drawing,
    SCHEMA.EducationalOccupationalCredential,
    SCHEMA.Episode,
    SCHEMA.PodcastEpisode,
    SCHEMA.RadioEpisode,
    SCHEMA.TVEpisode,
    SCHEMA.ExercisePlan,
    SCHEMA.Game,
    SCHEMA.VideoGame,
    SCHEMA.Guide,
    SCHEMA.HowTo,
    SCHEMA.Recipe,
    SCHEMA.HowToDirection,
    SCHEMA.HowToSection,
    SCHEMA.HowToStep,
    SCHEMA.HowToTip,
    SCHEMA.HyperToc,
    SCHEMA.HyperTocEntry,
    SCHEMA.LearningResource,
    SCHEMA.Course,
    SCHEMA.Quiz,
    SCHEMA.Syllabus,
    SCHEMA.Legislation,
    SCHEMA.LegislationObject,
    SCHEMA.Manuscript,
    SCHEMA.Map,
    SCHEMA.MathSolver,
    SCHEMA.MediaObject,
    SCHEMA['3DModel'], # Alternative notation due to number
    SCHEMA.AmpStory,
    SCHEMA.AudioObject,
    SCHEMA.AudioObjectSnapshot,
    SCHEMA.Audiobook,
    SCHEMA.DataDownload,
    SCHEMA.ImageObject,
    SCHEMA.Barcode,
    SCHEMA.ImageObjectSnapshot,
    SCHEMA.LegislationObject,
    SCHEMA.MusicVideoObject,
    SCHEMA.TextObject,
    SCHEMA.VideoObject,
    SCHEMA.VideoObjectSnapshot,
    SCHEMA.MediaReviewItem,
    SCHEMA.Menu,
    SCHEMA.MenuSection,
    SCHEMA.Message,
    SCHEMA.EmailMessage,
    SCHEMA.Movie,
    SCHEMA.MusicComposition,
    SCHEMA.MusicPlaylist,
    SCHEMA.MusicAlbum,
    SCHEMA.MusicRelease,
    SCHEMA.MusicRecording,
    SCHEMA.Painting,
    SCHEMA.Photograph,
    SCHEMA.Play,
    SCHEMA.Poster,
    SCHEMA.PublicationIssue,
    SCHEMA.ComicIssue,
    SCHEMA.PublicationVolume,
    SCHEMA.Quotation,
    SCHEMA.Review,
    SCHEMA.ClaimReview,
    SCHEMA.CriticReview,
    SCHEMA.ReviewNewsArticle,
    SCHEMA.EmployerReview,
    SCHEMA.MediaReview,
    SCHEMA.Recommendation,
    SCHEMA.UserReview,
    SCHEMA.Sculpture,
    SCHEMA.Season,
    SCHEMA.SheetMusic,
    SCHEMA.ShortStory,
    SCHEMA.SoftwareApplication,
    SCHEMA.MobileApplication,
    SCHEMA.VideoGame,
    SCHEMA.WebApplication,
    SCHEMA.SoftwareSourceCode,
    SCHEMA.SpecialAnnouncement,
    SCHEMA.Statement,
    SCHEMA.TVSeason,
    SCHEMA.TVSeries,
    SCHEMA.Thesis,
    SCHEMA.VisualArtwork,
    SCHEMA.CoverArt,
    SCHEMA.ComicCoverArt,
    SCHEMA.WebContent,
    SCHEMA.HealthTopicContent,
    SCHEMA.WebPage,
    SCHEMA.AboutPage,
    SCHEMA.CheckoutPage,
    SCHEMA.CollectionPage,
    SCHEMA.MediaGallery,
    SCHEMA.ImageGallery,
    SCHEMA.VideoGallery,
    SCHEMA.ContactPage,
    SCHEMA.FAQPage,
    SCHEMA.ItemPage,
    SCHEMA.MedicalWebPage,
    SCHEMA.ProfilePage,
    SCHEMA.QAPage,
    SCHEMA.RealEstateListing,
    SCHEMA.SearchResultsPage,
    SCHEMA.WebPageElement,
    SCHEMA.SiteNavigationElement,
    SCHEMA.Table,
    SCHEMA.WPAdBlock,
    SCHEMA.WPFooter,
    SCHEMA.WPHeader,
    SCHEMA.WPSideBar,
    SCHEMA.WebSite
]
