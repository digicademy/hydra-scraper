# Schema.org store ingest
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Graph, Namespace

# Import script modules
from mapping import cto

# Define namespaces
from rdflib.namespace import RDF, SKOS
CTO = Namespace('https://nfdi4culture.de/ontology#')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
NFDICORE = Namespace('https://nfdi.fiz-karlsruhe.de/ontology/')
SCHEMA = Namespace('http://schema.org/')


# FEED ELEMENT ################################################################


class FeedElement:

    # Vars
    success = False
    feed_uri = None
    element_type = None
    element_uri = None
    element_uri_same = None
    label = None
    label_alt = None
    shelf_mark = None
    image = None
    lyrics = None
    text_incipit = None
    music_incipit = None
    source_file = None
    iiif_image_api = None
    iiif_presentation_api = None
    ddb_api = None
    oaipmh_api = None
    publisher = None
    license = None
    vocab_element_type = None
    vocab_subject_concept = None
    vocab_related_location = None
    vocab_related_event = None
    vocab_related_organization = None
    vocab_related_person = None
    vocab_further = None
    related_item = None
    birth_date = None
    death_date = None
    foundation_date = None
    dissolution_date = None
    start_date = None
    end_date = None
    creation_date = None
    creation_period = None
    destruction_date = None
    approximate_period = None
    existence_period = None


    def __init__(self, store:Graph, feed_uri:any, element_uri:any):
        '''
        Class that extracts feed element data from schema.org triple store

            Parameters:
                store (Graph): triples stored in a Graph
                feed_uri (any): URI of the feed to retrieve elements of
                element_uri (any): URI of the element to retrieve
        '''

        # Generic variables to use
        feed_publisher = None
        feed_license = None

        # Feed-wide data
        self.feed_uri = feed_uri
        if self.feed_uri:
            if len(store.triples((self.feed_uri, SCHEMA.dataFeedElement, None, True))) > 0 or len(store.triples((None, SCHEMA.isPartOf, self.feed_uri, True))) > 0:
                self.success = True

                # Feed publisher (to use in elements)
                catalog_uri = next(store.objects((self.feed_uri, SCHEMA.includedInDataCatalog, True)), None)
                if catalog_uri:
                    feed_publisher = store.objects((catalog_uri, SCHEMA.publisher, True))

                # Feed licence (to use in elements)
                feed_license = store.objects((self.feed_uri, SCHEMA.licence, True))

                # Element URI
                self.element_uri = element_uri

                # Element type
                self.element_type = next(store.objects(self.element_uri, RDF.type, True), None)

                # Same as element URI
                self.element_uri_same = store.objects((self.element_uri, SCHEMA.sameAs, True))

                # Label
                self.label = store.objects((self.element_uri, SCHEMA.name, True))

                # Alternative label (if CTO used in schema.org)
                self.label_alt = store.objects((self.element_uri, SKOS.altLabel, True))

                # Shelf mark (if CTO used in schema.org)
                self.shelf_mark = store.objects((self.element_uri, CTO.shelfMark, True))

                # Image
                self.image = store.objects((self.element_uri, SCHEMA.image, True))

                # Lyrics
                for wrapper in store.objects((self.element_uri, SCHEMA.lyrics, True)):
                    self.lyrics = next(store.objects((wrapper, SCHEMA.text, True)), None)

                # Text incipit
                self.text_incipit = store.objects((self.element_uri, SCHEMA.text, True))

                # Music incipit
                #self.music_incipit = 

                # Source file
                #self.source_file = 

                # IIIF image API (if CTO used in schema.org)
                self.iiif_image_api = store.objects((self.element_uri, CTO.iiifImageAPI, True))

                # IIIF presentation API (if CTO used in schema.org)
                self.iiif_presentation_api = store.objects((self.element_uri, CTO.iiifPresentationAPI, True))

                # DDB API (if CTO used in schema.org)
                self.ddb_api = store.objects((self.element_uri, CTO.ddbAPI, True))

                # OAI-PMH API (if CTO used in schema.org)
                self.oaipmh_api = store.objects((self.element_uri, CTO['oai-pmhAPI'], True))

                # Publisher
                self.publisher = set()
                if feed_publisher:
                    self.publisher.update(feed_publisher)
                element_publisher = store.objects((self.element_uri, SCHEMA.publisher, True))
                if element_publisher:
                    self.publisher.update(element_publisher)
                self.publisher = list(self.publisher)

                # License
                self.license = set()
                if feed_license:
                    self.license.update(feed_license)
                element_license = store.objects((self.element_uri, SCHEMA.license, True))
                if element_license:
                    self.license.update(element_license)
                self.license = list(self.license)

                # Vocabulary: element type
                #self.vocab_element_type = 

                # Vocabulary: subject concept
                #self.vocab_subject_concept = 

                # Vocabulary: related location
                #self.vocab_related_location = 

                # Vocabulary: related event
                #self.vocab_related_event = 

                # Vocabulary: related organization
                #self.vocab_related_organization = 

                # Vocabulary: related person
                #self.vocab_related_person = 

                # Vocabulary: related person
                #self.vocab_related_person = 

                # Further vocabulary terms
                self.vocab_further = store.objects((self.element_uri, SCHEMA.keywords, True))

                # Related item (if CTO used in schema.org)
                self.related_item = store.objects((self.element_uri, CTO.relatedItem, True))

                # Birth date
                self.birth_date = store.objects((self.element_uri, SCHEMA.birthDate, True))

                # Death date
                self.death_date = store.objects((self.element_uri, SCHEMA.deathDate, True))

                # Foundation date
                self.foundation_date = store.objects((self.element_uri, SCHEMA.foundingDate, True))

                # Dissolution date
                self.dissolution_date = store.objects((self.element_uri, SCHEMA.dissolutionDate, True))

                # Start date
                self.start_date = store.objects((self.element_uri, SCHEMA.startDate, True))

                # End date
                self.end_date = store.objects((self.element_uri, SCHEMA.endDate, True))

                # Creation date (if CTO used in schema.org)
                self.creation_date = store.objects((self.element_uri, CTO.creationDate, True))

                # Creation period
                for temporal_coverage in store.objects((self.element_uri, SCHEMA.temporalCoverage, True)):
                    if len(store.triples((temporal_coverage, RDF.type, SCHEMA.DateTime, True))) > 0:
                        self.creation_period = temporal_coverage

                # Destruction date (if CTO used in schema.org)
                self.destruction_date = store.objects((self.element_uri, CTO.destructionDate, True))

                # Approximate period
                for temporal_coverage in store.objects((self.element_uri, SCHEMA.temporalCoverage, True)):
                    if not len(store.triples((temporal_coverage, RDF.type, SCHEMA.DateTime, True))) > 0:
                        self.approximate_period = temporal_coverage

                # Existence period (if CTO used in schema.org)
                self.existence_period = store.objects((self.element_uri, CTO.existencePeriod, True))


# FEED ########################################################################


class Feed:

    # Vars
    success = False
    feed_uri = None
    feed_uri_same = None
    catalog_uri = None
    catalog_uri_same = None
    list_of_elements = None


    def __init__(self, store:Graph):
        '''
        Class that extracts feed data from schema.org triple store

            Parameters:
                store (Graph): triples stored in a Graph
        '''

        # Retrieve feed URI that contains data
        for feed_uri in store.subjects((RDF.type, cto.schema_feed, True)):
            if self.success == False and (len(store.triples((feed_uri, SCHEMA.dataFeedElement, None, True))) > 0 or len(store.triples((None, SCHEMA.isPartOf, feed_uri, True))) > 0):
                self.success = True

                # Feed URI
                self.feed_uri = feed_uri

                # Same as feed
                self.feed_uri_same = store.objects((self.feed_uri, SCHEMA.sameAs, True))

                # Catalog
                self.catalog_uri = next(store.objects((self.feed_uri, SCHEMA.includedInDataCatalog, True)), None)
                if self.catalog_uri:

                    # Same as catalog
                    self.catalog_uri_same = store.objects((self.catalog_uri, SCHEMA.sameAs, True))

                # List of elements
                for wrapper in store.objects((self.feed_uri, SCHEMA.dataFeedElement, True)):
                    if (wrapper, RDF.type, SCHEMA.DataFeedItem) in store:
                        self.list_of_elements.append(next(store.objects((wrapper, SCHEMA.item, True)), None))
                for element in store.subjects((SCHEMA.isPartOf, self.feed_uri, True)):
                    self.list_of_elements.append(element)
