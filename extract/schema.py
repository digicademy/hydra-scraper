# Retrieve and extract data from schema.org triples
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Namespace

# Import script modules
from base.data import Uri, UriList, Label, LabelList, UriLabelList, Date, DateList
from base.extract import ExtractFeedInterface, ExtractFeedElementInterface
from base.lookup import schema_feed

# Define namespaces
from rdflib.namespace import RDF, SDO, SKOS
CTO = Namespace('https://nfdi4culture.de/ontology#')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
SCHEMA = Namespace('http://schema.org/')


class Feed(ExtractFeedInterface):


    def retrieve(self):
        '''
        Extract feed data from schema.org triples
        '''

        # Check for schema.org content
        feed_uris = self.rdf_all_subjects([RDF.type, SCHEMA.additionalType, SDO.additionalType], schema_feed)
        if feed_uris == None:
            self.success = False
        else:

            # Retrieve first feed that contains data (feed and single-element notation)
            for feed_uri in feed_uris:
                if not self.feed_uri and (self.rdf_all_triples(feed_uri, [SCHEMA.dataFeedElement, SDO.dataFeedElement, HYDRA.member], None, True) > 0 or self.rdf_all_triples(None, [SCHEMA.isPartOf, SDO.isPartOf], feed_uri, True) > 0):

                    # Feed URI
                    self.feed_uri = Uri(feed_uri, normalize = False)

                    # Same as feed
                    self.feed_uri_same = UriList(self.rdf_all_objects(self.feed_uri.rdflib(), [SCHEMA.sameAs, SDO.sameAs]), normalize = False)

                    # Next feed URI
                    pagination_current = self.rdf_first_object(self.feed_uri.rdflib(), HYDRA.view)
                    if pagination_current:
                        pagination_next = self.rdf_first_object(pagination_current, HYDRA.next)
                        pagination_last = self.rdf_first_object(pagination_current, HYDRA.last)
                        if pagination_next and pagination_last:
                            if pagination_current != pagination_last:
                                self.feed_uri_next = Uri(pagination_next, normalize = False)

                    # Catalog URI
                    self.catalog_uri = Uri(self.rdf_first_object(self.feed_uri.rdflib(), [SCHEMA.includedInDataCatalog, SDO.includedInDataCatalog]), normalize = False)
                    if self.catalog_uri:

                        # Same as catalog
                        self.catalog_uri_same = UriList(self.rdf_all_objects(self.catalog_uri.rdflib(), [SCHEMA.sameAs, SDO.sameAs]), normalize = False)
    
                    # Date modified
                    self.modified_date = Date(self.rdf_first_object(self.feed_uri.rdflib(), [SCHEMA.dateModified, SDO.dateModified]))

                    # Element URIs (feed and single-element notation)
                    wrappers = self.rdf_all_objects(self.feed_uri.rdflib(), [SCHEMA.dataFeedElement, SDO.dataFeedElement])
                    if wrappers != None:
                        for wrapper in wrappers:
                            if (wrapper, RDF.type, SCHEMA.DataFeedItem) in self.file.rdf or (wrapper, RDF.type, SDO.DataFeedItem) in self.file.rdf:
                                self.element_uris.append(self.rdf_first_object(wrapper, [SCHEMA.item, SDO.item]))
                    elements = self.rdf_all_subjects([SCHEMA.isPartOf, SDO.isPartOf], self.feed_uri.rdflib())
                    if elements != None:
                        for element in elements:
                            self.element_uris.append(element)
                    elements = self.rdf_all_objects(self.feed_uri.rdflib(), HYDRA.member)
                    if elements != None:
                        for element in elements:
                            self.element_uris.append(element)
                    self.element_uris = list(set(self.element_uris))

                    # Feed elements
                    if self.elements_in_feed:
                        for element_uri in self.element_uris:
                            self.feed_elements.append(FeedElement(self.file, self.feed_uri.uri, element_uri))


class FeedElement(ExtractFeedElementInterface):


    def retrieve(self):
        '''
        Extract feed element data from schmema.org triples
        '''

        # Check for schema.org content
        feed_uris = self.rdf_all_subjects(RDF.type, schema_feed)
        if feed_uris == None:
            self.success = None
        else:

            # Retrieve indicated feed or first feed that contains data (feed and single-element notation)
            for feed_uri in feed_uris:
                if str(feed_uri) == self.feed_uri.uri or (not self.feed_uri and (self.rdf_all_triples(feed_uri, [SCHEMA.dataFeedElement, SDO.dataFeedElement], None, True) > 0 or self.rdf_all_triples(None, [SCHEMA.isPartOf, SDO.isPartOf], feed_uri, True) > 0)):

                    # Feed URI (if it has not been set)
                    if not self.feed_uri:
                        self.feed_uri = Uri(feed_uri, normalize = False)

                    # Feed publisher (to use in elements)
                    feed_publisher = None
                    catalog_uri = self.rdf_first_object(self.feed_uri.rdflib(), [SCHEMA.includedInDataCatalog, SDO.includedInDataCatalog])
                    if catalog_uri:
                        feed_publisher = UriList(self.rdf_all_objects(catalog_uri, [SCHEMA.publisher, SDO.publisher]))

                    # Feed license (to use in elements)
                    feed_license = UriList(self.rdf_all_objects(self.feed_uri.rdflib(), [SCHEMA.license, SDO.license]))

                    # Element URI (if it has not been set)
                    if not self.element_uri:
                        wrapper = self.rdf_first_object(self.feed_uri.rdflib(), [SCHEMA.dataFeedElement, SDO.dataFeedElement])
                        if wrapper != None:
                            if (wrapper, RDF.type, SCHEMA.DataFeedItem) in self.file.rdf or (wrapper, RDF.type, SDO.DataFeedItem) in self.file.rdf:
                                self.element_uri = Uri(self.rdf_first_object(wrapper, [SCHEMA.item, SDO.item]))
                        if not self.element_uri:
                            self.element_uri = Uri(self.rdf_first_subject([SCHEMA.isPartOf, SDO.isPartOf], self.feed_uri.rdflib()), normalize = False)

                    # Same as element URI
                    self.element_uri_same = UriList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.sameAs, SDO.sameAs]), normalize = False)

                    # Element type
                    self.element_type = Uri(self.rdf_first_object(self.element_uri.rdflib(), RDF.type))

                    # Element type shorthand
                    #self.element_type_shorthand = 

                    # Label
                    self.label = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.name, SDO.name]))

                    # Alternative label (if CTO used in schema.org)
                    self.label_alt = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), SKOS.altLabel))

                    # Shelf mark (if CTO used in schema.org)
                    self.shelf_mark = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), CTO.shelfMark))

                    # Image
                    self.image = Uri(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.image, SDO.image, SCHEMA.contentUrl, SDO.contentUrl]), normalize = False)

                    # Lyrics
                    wrapper = self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.lyrics, SDO.lyrics])
                    if wrapper != None:
                        self.lyrics = LabelList(self.rdf_all_objects(wrapper, [SCHEMA.text, SDO.text]))

                    # Text incipit
                    self.text_incipit = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.text, SDO.text]))

                    # Music incipit
                    #self.music_incipit = 

                    # Source file
                    self.source_file = Label(self.file.location, remove_path = self.file.directory_path)

                    # IIIF image API (if CTO used in schema.org)
                    self.iiif_image_api = Uri(self.rdf_all_objects(self.element_uri.rdflib(), CTO.iiifImageAPI))

                    # IIIF presentation API (if CTO used in schema.org)
                    self.iiif_presentation_api = Uri(self.rdf_all_objects(self.element_uri.rdflib(), CTO.iiifPresentationAPI))

                    # DDB API (if CTO used in schema.org)
                    self.ddb_api = Uri(self.rdf_all_objects(self.element_uri.rdflib(), CTO.ddbAPI))

                    # OAI-PMH API (if CTO used in schema.org)
                    self.oaipmh_api = Uri(self.rdf_all_objects(self.element_uri.rdflib(), CTO['oai-pmhAPI']))

                    # Publisher (observe element and feed)
                    self.publisher = UriList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.publisher, SDO.publisher]))
                    if not self.publisher and feed_publisher:
                        self.publisher = feed_publisher

                    # License (observe feed and element)
                    self.license = UriList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.license, SDO.license]))
                    if self.license == None and feed_license != None:
                        self.license = feed_license

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

                    # Further vocabulary terms
                    vocab_further = []
                    keywords = self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.keywords, SDO.keywords, SCHEMA.contentLocation, SDO.contentLocation])
                    if keywords != None:
                        keywords = list(set(keywords))
                        for keyword in keywords:
                            keyword_tuple = self.rdf_uri_label(keyword, [SCHEMA.name, SDO.name])
                            if keyword_tuple != None:
                                vocab_further.append(keyword_tuple)
                    self.vocab_further = UriLabelList(vocab_further)

                    # Related item (if CTO used in schema.org)
                    self.related_item = UriList(self.rdf_all_objects(self.element_uri.rdflib(), CTO.relatedItem))

                    # Birth date
                    self.birth_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.birthDate, SDO.birthDate]))

                    # Death date
                    self.death_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.deathDate, SDO.deathDate]))

                    # Foundation date
                    self.foundation_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.foundingDate, SDO.foundingDate]))

                    # Dissolution date
                    self.dissolution_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.dissolutionDate, SDO.dissolutionDate]))

                    # Start date
                    self.start_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.startDate, SDO.startDate]))

                    # End date
                    self.end_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.endDate, SDO.endDate]))

                    # Creation date (if CTO used in schema.org)
                    self.creation_date = Date(self.rdf_first_object(self.element_uri.rdflib(), CTO.creationDate))

                    # Creation period (if date is date)
                    temporal_coverages = self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.temporalCoverage, SDO.temporalCoverage])
                    if temporal_coverages != None:
                        for temporal_coverage in temporal_coverages:
                            if temporal_coverage.datatype == SCHEMA.DateTime or temporal_coverage.datatype == SDO.DateTime:
                                self.creation_period = DateList(temporal_coverage)

                    # Destruction date (if CTO used in schema.org)
                    self.destruction_date = Date(self.rdf_first_object(self.element_uri.rdflib(), CTO.destructionDate))

                    # Approximate period (if date is string)
                    if temporal_coverages != None:
                        for temporal_coverage in temporal_coverages:
                            if temporal_coverage.datatype != SCHEMA.DateTime and temporal_coverage.datatype != SDO.DateTime:
                                self.approximate_period = DateList(temporal_coverage)

                    # Existence period (if CTO used in schema.org)
                    self.existence_period = DateList(self.rdf_all_objects(self.element_uri.rdflib(), CTO.existencePeriod))
