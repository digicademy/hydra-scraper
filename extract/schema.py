# Retrieve and extract data from schema.org triples
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Namespace

# Import script modules
from base.data import Uri, UriList, Label, LabelList, UriLabelList, Date, DateList, Media
from base.extract import ExtractFeedInterface, ExtractFeedElementInterface
from base.lookup import schema_feed, schema_person, schema_organisation, schema_location, schema_structure, schema_event, schema_theater, schema_item, schema_book, schema_sculpture, schema_music

# Define namespaces
from rdflib.namespace import RDF, SDO, SKOS
CTO2 = Namespace('https://nfdi4culture.de/ontology#')
CTO3 = Namespace('https://nfdi4culture.de/ontology/')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
SCHEMA = Namespace('http://schema.org/')
OBO = Namespace('http://purl.obolibrary.org/obo/')


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
                    feed_license = UriLabelList(self.rdf_all_objects(self.feed_uri.rdflib(), [SCHEMA.license, SDO.license]))

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
                    if self.element_type.rdflib() in schema_person:
                        self.element_type_short = 'person'
                    elif self.element_type.rdflib() in schema_organisation:
                        self.element_type_short = 'organisation'
                    elif self.element_type.rdflib() in schema_event:
                        self.element_type_short = 'event'
                    elif self.element_type.rdflib() in schema_location:
                        self.element_type_short = 'location'
                    elif self.element_type.rdflib() in schema_book:
                        self.element_type_short = 'book'
                    elif self.element_type.rdflib() in schema_structure:
                        self.element_type_short = 'structure'
                    elif self.element_type.rdflib() in schema_sculpture:
                        self.element_type_short = 'sculpture'
                    elif self.element_type.rdflib() in schema_music:
                        self.element_type_short = 'sheet-music'
                    elif self.element_type.rdflib() in schema_theater:
                        self.element_type_short = 'theater-event'
                    elif self.element_type.rdflib() in schema_item:
                        self.element_type_short = 'item'
                    else:
                        self.element_type_short = 'item'

                    # Data concept shorthand
                    if self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.image, SDO.image]):
                        self.data_concept_short.add('image')
                    if self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.audio, SDO.audio]):
                        self.data_concept_short.add('audio')
                    if self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.video, SDO.video]):
                        self.data_concept_short.add('video')
                    data_concept_show = self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.contentUrl, SDO.contentUrl, SCHEMA.associatedMedia, SDO.associatedMedia, SCHEMA.encoding, SDO.encoding])
                    if data_concept_show:
                        for i in data_concept_show:
                            if self.rdf_first_object(i, RDF.type) in [SCHEMA.ImageObject, SDO.ImageObject, SCHEMA.ImageObjectSnapshot, SDO.ImageObjectSnapshot, SCHEMA.Barcode, SDO.Barcode]:
                                self.data_concept_short.add('image')
                            if self.rdf_first_object(i, RDF.type) in [SCHEMA.AudioObject, SDO.AudioObject, SCHEMA.AudioObjectSnapshot, SDO.AudioObjectSnapshot, SCHEMA.Audiobook, SDO.Audiobook]:
                                self.data_concept_short.add('audio')
                            if self.rdf_first_object(i, RDF.type) in [SCHEMA.VideoObject, SDO.VideoObject, SCHEMA.VideoObjectSnapshot, SDO.VideoObjectSnapshot, SCHEMA.MusicVideoObject, SDO.MusicVideoObject]:
                                self.data_concept_short.add('video')
                            if self.rdf_first_object(i, RDF.type) in [SCHEMA.TextObject, SDO.TextObject]:
                                self.data_concept_short.add('text')
                            if self.rdf_first_object(i, RDF.type) in [SCHEMA['3DModel'], SDO['3DModel']]:
                                self.data_concept_short.add('3d-model')
                        if len(self.data_concept_short) == 0:
                            self.data_concept_short.add('media')
                    if self.element_type.rdflib() in schema_music:
                        self.data_concept_short.add('sheet-music')

                    # Label
                    self.label = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.name, SDO.name]))

                    # Alternative label (also check for CTO v2 or v3 used in schema.org)
                    self.label_alt = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.alternateName, SDO.alternateName, SKOS.altLabel, OBO.IAO_0000118]))

                    # Holding organization (if CTO v3 used in schema.org)
                    self.holding_org = Uri(self.rdf_first_object(self.element_uri.rdflib(), CTO3.CTO_0001069)) # has holding organization

                    # Shelf mark (if CTO v2 or v3 used in schema.org)
                    self.shelf_mark = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [CTO2.shelfMark, CTO3.CTO_0001068])) # has shelf mark

                    # Media (check properties, or media RDF type, or element RDF type)
                    self.media = Media(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.image, SDO.image]), type = 'image')
                    if not self.media:
                        self.media = Media(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.audio, SDO.audio]), type = 'audio')
                    #if not self.media:
                        #self.media = Media(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.video, SDO.video]), type = 'video')
                    if not self.media:
                        self.media = Media(self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.contentUrl, SDO.contentUrl, SCHEMA.associatedMedia, SDO.associatedMedia, SCHEMA.encoding, SDO.encoding]))
                        if self.media:
                            if self.rdf_first_object(self.media.uri.rdflib(), RDF.type) in [SCHEMA.ImageObject, SDO.ImageObject, SCHEMA.ImageObjectSnapshot, SDO.ImageObjectSnapshot, SCHEMA.Barcode, SDO.Barcode]:
                                self.media.type = 'image'
                            if self.rdf_first_object(self.media.uri.rdflib(), RDF.type) in [SCHEMA.AudioObject, SDO.AudioObject, SCHEMA.AudioObjectSnapshot, SDO.AudioObjectSnapshot, SCHEMA.Audiobook, SDO.Audiobook]:
                                self.media.type = 'audio'
                            #if self.rdf_first_object(mself.media.uri.rdflib(), RDF.type) in [SCHEMA.VideoObject, SDO.VideoObject, SCHEMA.VideoObjectSnapshot, SDO.VideoObjectSnapshot, SCHEMA.MusicVideoObject, SDO.MusicVideoObject]:
                                #self.media.type = 'video'
                            if not self.media.type:
                                if self.element_type.rdflib() in [SCHEMA.ImageObject, SDO.ImageObject, SCHEMA.ImageObjectSnapshot, SDO.ImageObjectSnapshot, SCHEMA.Barcode, SDO.Barcode]:
                                    self.media.type = 'image'
                                if self.element_type.rdflib() in [SCHEMA.AudioObject, SDO.AudioObject, SCHEMA.AudioObjectSnapshot, SDO.AudioObjectSnapshot, SCHEMA.Audiobook, SDO.Audiobook]:
                                    self.media.type = 'audio'
                                #if self.element_type.rdflib() in [SCHEMA.VideoObject, SDO.VideoObject, SCHEMA.VideoObjectSnapshot, SDO.VideoObjectSnapshot, SCHEMA.MusicVideoObject, SDO.MusicVideoObject]:
                                    #self.media.type = 'video'

                    # Media license
                    if self.media:
                        self.media.license = UriLabelList(self.rdf_all_objects(self.media.uri.rdflib(), [SCHEMA.license, SDO.license]))

                    # Media byline (use dedicated property or, alternatively, author or creator)
                    if self.media:
                        self.media.byline = LabelList(self.rdf_all_objects(self.media.uri.rdflib(), [SCHEMA.creditText, SDO.creditText]))
                        if not self.media.byline:
                            self.media.byline = LabelList(self.rdf_all_objects(self.media.uri.rdflib(), [SCHEMA.author, SDO.author]))
                        if not self.media.byline:
                            self.media.byline = LabelList(self.rdf_all_objects(self.media.uri.rdflib(), [SCHEMA.creator, SDO.creator]))

                    # Lyrics
                    wrapper = self.rdf_first_object(self.element_uri.rdflib(), [SCHEMA.lyrics, SDO.lyrics])
                    if wrapper != None:
                        self.lyrics = LabelList(self.rdf_all_objects(wrapper, [SCHEMA.text, SDO.text]))

                    # Teaser
                    self.teaser = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.text, SDO.text]))

                    # Incipit
                    #self.incipit = 

                    # Source file
                    self.source_file = Label(self.file.location, remove_path = self.file.directory_path)

                    # Source type shorthand
                    self.source_type_short.add('cgif')

                    # Publisher (observe element and feed)
                    self.publisher = UriList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.publisher, SDO.publisher]))
                    if not self.publisher and feed_publisher:
                        self.publisher = feed_publisher

                    # License (observe feed and element)
                    self.license = UriLabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.license, SDO.license]))
                    if self.license == None and feed_license != None:
                        self.license = feed_license

                    # Byline (use dedicated property or, alternatively, author or creator)
                    if not self.media.byline:
                        self.media.byline = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.creditText, SDO.creditText]))
                    else:
                        self.byline = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.creditText, SDO.creditText]))
                    if not self.byline:
                        self.byline = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.author, SDO.author]))
                    if not self.byline:
                        self.byline = LabelList(self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.creator, SDO.creator]))

                    # Vocabulary: element type
                    # Deprecated, remove along with CTO2
                    #self.vocab_element_type = 

                    # Vocabulary: subject concept
                    # Deprecated, remove along with CTO2
                    #self.vocab_subject_concept = 

                    # Vocabulary: classifier
                    #self.vocab_classifier =

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

                    # Related item (if CTO v2 or v3 used in schema.org)
                    self.related_item = UriList(self.rdf_all_objects(self.element_uri.rdflib(), [CTO2.relatedItem, CTO3.CTO_0001019])) # has related item

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

                    # Creation date (if CTO v2 or v3 used in schema.org)
                    self.creation_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [CTO2.creationDate, CTO3.CTO_0001072])) # has creation date

                    # Creation period (if date is date)
                    temporal_coverages = self.rdf_all_objects(self.element_uri.rdflib(), [SCHEMA.temporalCoverage, SDO.temporalCoverage])
                    if temporal_coverages != None:
                        for temporal_coverage in temporal_coverages:
                            if temporal_coverage.datatype == SCHEMA.DateTime or temporal_coverage.datatype == SDO.DateTime:
                                self.creation_period = DateList(temporal_coverage)

                    # Destruction date (if CTO v2 or v3 used in schema.org)
                    self.destruction_date = Date(self.rdf_first_object(self.element_uri.rdflib(), [CTO2.destructionDate, CTO3.CTO_0001074])) # has destruction date

                    # Approximate period (if date is string)
                    if temporal_coverages != None:
                        for temporal_coverage in temporal_coverages:
                            if temporal_coverage.datatype != SCHEMA.DateTime and temporal_coverage.datatype != SDO.DateTime:
                                self.approximate_period = DateList(temporal_coverage)

                    # Existence period (if CTO v2 or v3 used in schema.org)
                    self.existence_period = DateList(self.rdf_all_objects(self.element_uri.rdflib(), [CTO2.existencePeriod, CTO3.CTO_0001075])) # has existence period
