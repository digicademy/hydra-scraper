# Generate nfdicore/cto-style triples
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from datetime import date
from hashlib import sha256
from rdflib import Graph, Namespace
from rdflib.term import BNode, Literal, URIRef

# Import script modules
from base.map import MapFeedInterface, MapFeedElementInterface
from base.lookup import schema_person, schema_organization, schema_location, schema_event, schema_item

# Define namespaces
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD
AAT = Namespace('http://vocab.getty.edu/aat/')
CTO = Namespace('https://nfdi4culture.de/ontology#')
FG = Namespace('https://database.factgrid.de/entity/')
GN = Namespace('http://sws.geonames.org/')
GND = Namespace('https://d-nb.info/gnd/')
IC = Namespace('https://iconclass.org/')
ISIL = Namespace('https://ld.zdb-services.de/resource/organisations/')
MO = Namespace('http://purl.org/ontology/mo/')
N4C = Namespace('https://nfdi4culture.de/id/')
NFDICORE = Namespace('https://nfdi.fiz-karlsruhe.de/ontology/')
RISM = Namespace('https://rism.online/')
SCHEMA = Namespace('http://schema.org/')
VIAF = Namespace('http://viaf.org/viaf/')
WD = Namespace('http://www.wikidata.org/entity/')

# Set up logging
logger = logging.getLogger(__name__)


class Feed(MapFeedInterface):


    def generate(self, prepare:str|None = None):
        '''
        Generate nfdicore/cto-style feed triples and fill the store attribute

            Parameters:
                prepare (str|None): Prepare cto output for this NFDI4Culture feed ID
        '''

        # Check requirements
        if not self.feed_uri:
            logger.error('Feed URI missing')
        else:
            self.rdf = namespaces()

            # Feed URI
            self.rdf.add((self.feed_uri.rdflib(), RDF.type, NFDICORE.Dataset))

            # Date modified
            if self.modified_date:
                self.rdf.add((self.feed_uri.rdflib(), SCHEMA.dateModified, self.modified_date.rdflib()))
            else:
                today = date.today()
                self.rdf.add((self.feed_uri.rdflib(), SCHEMA.dateModified, Literal(today.strftime('%Y-%M-%D'), datatype = XSD.date)))

            # Same as feed URI
            for i in self.feed_uri_same.rdflib():
                self.rdf.add((self.feed_uri.rdflib(), OWL.sameAs, i))

            # Catalog URI
            if self.catalog_uri:
                self.rdf.add((self.catalog_uri.rdflib(), RDF.type, NFDICORE.DataPortal))
                self.rdf.add((self.catalog_uri.rdflib(), NFDICORE.dataset, self.feed_uri.rdflib()))

                # Same as catalog URI
                for i in self.catalog_uri_same.rdflib():
                    self.rdf.add((self.catalog_uri.rdflib(), OWL.sameAs, i))

            # Add element triples after overwriting feed URI
            for i in self.feed_elements:
                o = FeedElement(i)
                o.feed_uri = self.feed_uri
                o.generate(prepare)
                self.rdf += o.rdf

            # Show that the data is stored
            self.success = True


class FeedElement(MapFeedElementInterface):


    def generate(self, prepare:str|None = None):
        '''
        Generate nfdicore/cto-style feed element triples and fill the store attribute

            Parameters:
                prepare (str|None): Prepare cto output for this NFDI4Culture feed ID
        '''

        # Check requirements
        if not self.element_uri:
            logger.error('Feed element URI missing')
        elif not self.feed_uri:
            logger.error('Feed URI missing')
        else:
            self.rdf = namespaces()

            # ELEMENT

            # Feed URI
            self.rdf.add((self.element_uri.rdflib(), CTO.elementOf, self.feed_uri.rdflib()))

            # Same as element URI
            for i in self.element_uri_same.rdflib():
                if i in GN:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.geonames, i))
                elif i in IC:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.iconclass, i))
                elif i in AAT:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.aat, i))
                elif i in GND:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.gnd, i))
                elif i in WD:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.wikidata, i))
                elif i in VIAF:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.viaf, i))
                elif i in RISM:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.rism, i))
                elif i in FG:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.factgrid, i))
                elif i in ISIL:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.isil, i))
                else:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.externalVocabulary, i))

            # Element type and element type shorthand
            self.rdf.add((self.element_uri.rdflib(), RDF.type, CTO.DatafeedElement))
            # Element type: person
            if self.element_type_shorthand == 'person' or self.element_type.rdflib() in schema_person:
                self.rdf.add((self.element_uri.rdflib(), RDF.type, NFDICORE.Person))
             # Element type: organization
            elif self.element_type_shorthand == 'organization' or self.element_type_shorthand == 'organisation' or self.element_type.rdflib() in schema_organization:
                self.rdf.add((self.element_uri.rdflib(), RDF.type, NFDICORE.Organization))
            # Element type: place
            elif self.element_type_shorthand == 'place' or self.element_type_shorthand == 'location' or self.element_type.rdflib() in schema_location:
                self.rdf.add((self.element_uri.rdflib(), RDF.type, NFDICORE.Place))
            # Element type: event
            elif self.element_type_shorthand == 'event' or self.element_type_shorthand == 'date' or self.element_type.rdflib() in schema_event:
                self.rdf.add((self.element_uri.rdflib(), RDF.type, NFDICORE.Event))
            # Element type: item that is a schema.org creative work
            elif self.element_type.rdflib() in schema_item:
                self.rdf.add((self.element_uri.rdflib(), RDF.type, self.element_type.rdflib()))
            # Element type: generic item
            else:
                self.rdf.add((self.element_uri.rdflib(), RDF.type, CTO.Item))

            # Optional wrapper
            if prepare != None and prepare != '':
                wrapper = element_ark(self.element_uri.text(), prepare)
                self.rdf.add((self.feed_uri.rdflib(), SCHEMA.dataFeedElement, wrapper))
                self.rdf.add((wrapper, RDF.type, SCHEMA.DataFeedItem))
                self.rdf.add((wrapper, SCHEMA.item, self.element_uri.rdflib()))

            # LABEL AND REFERENCE LITERALS

            # Main label
            for i in self.label.rdflib():
                self.rdf.add((self.element_uri.rdflib(), RDFS.label, i))

            # Alternative label
            for i in self.label_alt.rdflib():
                self.rdf.add((self.element_uri.rdflib(), SKOS.altLabel, i))

            # Shelf mark
            for i in self.shelf_mark.rdflib():
                self.rdf.add((self.element_uri.rdflib(), CTO.shelfMark, i))

            # MEDIA LITERALS

            # URL
            if self.element_uri:
                self.rdf.add((self.element_uri.rdflib(), SCHEMA.url, Literal(self.element_uri.uri, datatype = SCHEMA.URL)))

            # Image
            if self.image:
                self.rdf.add((self.element_uri.rdflib(), SCHEMA.image, Literal(self.image.uri, datatype = SCHEMA.URL)))

            # Lyrics
            for i in self.lyrics.rdflib():
                wrapper = BNode()
                self.rdf.add((self.element_uri.rdflib(), MO.lyrics, wrapper))
                self.rdf.add((wrapper, RDF.type, MO.Lyrics))
                self.rdf.add((wrapper, MO.text, i))

            # Text incipit
            for i in self.text_incipit.rdflib():
                self.rdf.add((self.element_uri.rdflib(), CTO.textIncipit, i))

            # Music incipit
            if self.music_incipit:
                music_incipit = self.music_incipit.rdflib()
                if music_incipit['uri']:
                    uri_or_wrapper = music_incipit['uri']
                else:
                    uri_or_wrapper = BNode()
                self.rdf.add((uri_or_wrapper, RDF.type, CTO.Incipit))
                self.rdf.add((uri_or_wrapper, CTO.incipitOf, self.element_uri.rdflib()))
                if music_incipit['clef']:
                    self.rdf.add((uri_or_wrapper, CTO.clef, music_incipit['clef']))
                if music_incipit['key_sig']:
                    self.rdf.add((uri_or_wrapper, CTO.keySignature, music_incipit['key_sig']))
                if music_incipit['time_sig']:
                    self.rdf.add((uri_or_wrapper, CTO.timeSignature, music_incipit['time_sig']))
                if music_incipit['pattern']:
                    self.rdf.add((uri_or_wrapper, CTO.pattern, music_incipit['pattern']))

            # Source file
            if self.source_file:
                self.rdf.add((self.element_uri.rdflib(), CTO.sourceFile, Literal(self.source_file.uri, datatype = SCHEMA.URL)))

            # API LITERALS

            # IIIF Image API
            if self.iiif_image_api:
                self.rdf.add((self.element_uri.rdflib(), CTO.iiifImageAPI, Literal(self.iiif_image_api.uri, datatype = SCHEMA.URL)))

            # IIIF Presentation API
            if self.iiif_presentation_api:
                self.rdf.add((self.element_uri.rdflib(), CTO.iiifPresentationAPI, Literal(self.iiif_presentation_api.uri, datatype = SCHEMA.URL)))

            # DDB API
            if self.ddb_api:
                self.rdf.add((self.element_uri.rdflib(), CTO.ddbAPI, Literal(self.ddb_api.uri, datatype = SCHEMA.URL)))

            # OAI-PMH API
            if self.oaipmh_api:
                self.rdf.add((self.element_uri.rdflib(), CTO['oai-pmhAPI'], Literal(self.oaipmh_api.uri, datatype = SCHEMA.URL))) # Alternative notation due to hyphen

            # RIGHTS URIS

            # Publisher
            for i in self.publisher.rdflib():
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.publisher, i))

            # License
            for i in self.license.rdflib():
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.license, i))

            # RELATED URIS AND FALLBACK LITERALS

            # Element type
            for i in self.vocab_element_type.rdflib():
                if i[0]:
                    self.rdf.add((self.element_uri.rdflib(), CTO.elementType, i[0]))
                    if i[1]:
                        for e in i[1]:
                            self.rdf.add((i[0], RDFS.label, e))
                else:
                    self.rdf.add((self.element_uri.rdflib(), CTO.elementTypeLiteral, i[1]))

            # Subject concept
            for i in self.vocab_subject_concept.rdflib():
                if i[0]:
                    self.rdf.add((self.element_uri.rdflib(), CTO.subjectConcept, i[0]))
                    if i[1]:
                        for e in i[1]:
                            self.rdf.add((i[0], RDFS.label, e))
                else:
                    self.rdf.add((self.element_uri.rdflib(), CTO.subjectConceptLiteral, i[1]))

            # Related location
            for i in self.vocab_related_location.rdflib():
                if i[0]:
                    self.rdf.add((self.element_uri.rdflib(), CTO.relatedLocation, i[0]))
                    self.rdf.add((i[0], RDF.type, NFDICORE.Place))
                    if i[1]:
                        for e in i[1]:
                            self.rdf.add((i[0], RDFS.label, e))
                else:
                    for e in i[1]:
                        self.rdf.add((self.element_uri.rdflib(), CTO.relatedLocationLiteral, e))

            # Related event
            for i in self.vocab_related_event.rdflib():
                if i[0]:
                    self.rdf.add((self.element_uri.rdflib(), CTO.relatedEvent, i[0]))
                    self.rdf.add((i[0], RDF.type, NFDICORE.Event))
                    if i[1]:
                        for e in i[1]:
                            self.rdf.add((i[0], RDFS.label, e))
                else:
                    self.rdf.add((self.element_uri.rdflib(), CTO.relatedEventLiteral, i[1]))

            # Related organization
            for i in self.vocab_related_organization.rdflib():
                if i[0]:
                    self.rdf.add((self.element_uri.rdflib(), CTO.relatedOrganization, i[0]))
                    self.rdf.add((i[0], RDF.type, NFDICORE.Organization))
                    if i[1]:
                        for e in i[1]:
                            self.rdf.add((i[0], RDFS.label, e))
                else:
                    self.rdf.add((self.element_uri.rdflib(), CTO.relatedOrganizationLiteral, i[1]))

            # Related person
            for i in self.vocab_related_person.rdflib():
                if i[0]:
                    self.rdf.add((self.element_uri.rdflib(), CTO.relatedPerson, i[0]))
                    self.rdf.add((i[0], RDF.type, NFDICORE.Person))
                    if i[1]:
                        for e in i[1]:
                            self.rdf.add((i[0], RDFS.label, e))
                else:
                    self.rdf.add((self.element_uri.rdflib(), CTO.relatedPersonLiteral, i[1]))

            # Related item
            for i in self.related_item.rdflib():
                self.rdf.add((self.element_uri.rdflib(), CTO.relatedItem, i))

            # DATES BY TYPE

            # For persons
            if self.element_type_shorthand == 'person' or self.element_type.rdflib() in schema_person:

                # Birth date
                if self.birth_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.birthDate, self.birth_date.rdflib()))

                # Death date
                if self.death_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.deathDate, self.death_date.rdflib()))

            # For organizations
            elif self.element_type_shorthand == 'organization' or self.element_type_shorthand == 'organisation' or self.element_type.rdflib() in schema_organization:

                # Foundation date
                if self.foundation_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.foundationDate, self.foundation_date.rdflib()))

                # Dissolution date
                if self.dissolution_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.dissolutionDate, self.dissolution_date.rdflib()))

            # For places
            elif self.element_type_shorthand == 'place' or self.element_type_shorthand == 'location' or self.element_type.rdflib() in schema_location:
                pass

            # For events
            elif self.element_type_shorthand == 'event' or self.element_type_shorthand == 'date' or self.element_type.rdflib() in schema_event:

                # Start date
                if self.start_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.startDate, self.start_date.rdflib()))

                # End date
                if self.end_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.endDate, self.end_date.rdflib()))

            # For items
            else:

                # Creation date
                if self.creation_date:
                    self.rdf.add((self.element_uri.rdflib(), CTO.creationDate, self.creation_date.rdflib()))

                # Creation period
                for i in self.creation_period.rdflib(True):
                    self.rdf.add((self.element_uri.rdflib(), CTO.creationPeriod, i))

                # Destruction date
                if self.destruction_date:
                    self.rdf.add((self.element_uri.rdflib(), CTO.destructionDate, self.destruction_date.rdflib()))

                # Approximate period
                for i in self.approximate_period.rdflib(True):
                    self.rdf.add((self.element_uri.rdflib(), CTO.approximatePeriod, i))

                # Existence period
                for i in self.existence_period.rdflib(True):
                    self.rdf.add((self.element_uri.rdflib(), CTO.existencePeriod, i))

            # Show that the data is stored
            self.success = True


def namespaces() -> Graph:
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
    output.bind('schema', SCHEMA, replace = True) # "Replace" overrides the RDFLib schema namespace (SDO), which uses "https"
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


def element_ark(element_uri:str, prepare:str) -> URIRef:
    '''
    Generate an NFDI4Culture ARK ID for the wrapper of a data feed element

        Parameters:
            element_uri (str): URI of the element to produce an ARK ID for
            prepare (str): NFDI4Culture IRI of the feed

        Returns:
            URIRef: ARK ID based on a hash of the element URI
    '''

    # Generate hash and ARK ID
    hash = sha256(element_uri.encode()).hexdigest()[:8]
    uri = 'https://nfdi4culture.de/id/ark:/60538/' + prepare + '_' + hash

    # Return ARK ID as URI
    return URIRef(uri)
