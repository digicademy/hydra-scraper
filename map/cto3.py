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

# Define namespaces
from rdflib.namespace import OWL, RDF, RDFS, XSD
AAT = Namespace('http://vocab.getty.edu/aat/')
CTO = Namespace('https://nfdi4culture.de/ontology/')
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
ORCID = Namespace('https://orcid.org/')
ROR = Namespace('https://ror.org/')
DOI = Namespace('https://doi.org/')
TGN = Namespace('https://vocab.getty.edu/tgn/')
OBO = Namespace('http://purl.obolibrary.org/obo/')
CERL = Namespace('http://data.cerl.org/thesaurus/')
GV = Namespace('http://partage.vocnet.org/')
HS = Namespace('http://www.mimo-db.eu/HornbostelAndSachs/')
MIMO = Namespace('http://www.mimo-db.eu/InstrumentsKeywords/')
MATCULT = Namespace('http://matcult-the.vocnet.org/')
UNESCO = Namespace('http://vocabularies.unesco.org/thesaurus/')
WNK = Namespace('http://lvr.vocnet.org/wnk/')
LCSH = Namespace('http://id.loc.gov/authorities/subjects/')
MOP = Namespace('http://iflastandards.info/ns/unimarc/terms/mop/') # TODO Maybe use UNIMARC MOP as the label because UNIMARC refers to 52 different vocabularies
FPCAT = Namespace('https://filmportal.de/material/') # TODO Unclear whether this is the namespace the classifier refers to

# Set up logging
logger = logging.getLogger(__name__)


class Feed(MapFeedInterface):


    def generate(self, prepare:list|None = None):
        '''
        Generate nfdicore/cto-style feed triples and fill the store attribute

            Parameters:
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID, disable license check optionally by adding 'no_license_check'.
        '''

        # Check requirements
        if not self.feed_uri:
            logger.error('Feed URI missing')
        else:
            self.rdf = namespaces()

            # Feed URI
            if prepare != None and len(prepare) >= 2:
                feed_uri = URIRef(str(N4C) + prepare[0])
            else:
                feed_uri = self.feed_uri.rdflib()
            self.rdf.add((feed_uri, RDF.type, NFDICORE.NFDI_0000009)) # dataset
            self.rdf.add((feed_uri, RDF.type, SCHEMA.DataFeed))

            # Date modified
            if self.modified_date:
                self.rdf.add((feed_uri, SCHEMA.dateModified, self.modified_date.rdflib()))
            else:
                today = date.today()
                self.rdf.add((feed_uri, SCHEMA.dateModified, Literal(str(today.isoformat()), datatype = XSD.date)))

            # Same as feed URI
            if prepare != None and len(prepare) >= 2:
                self.rdf.add((feed_uri, SCHEMA.sameAs, self.feed_uri.rdflib()))
            for i in self.feed_uri_same.rdflib():
                self.rdf.add((feed_uri, SCHEMA.sameAs, i))

            # Catalog URI
            if prepare != None and len(prepare) >= 2:
                catalog_uri = URIRef(str(N4C) + prepare[1])
            else:
                catalog_uri = self.catalog_uri.rdflib()

            if catalog_uri:
                self.rdf.add((catalog_uri, RDF.type, NFDICORE.NFDI_0000123)) # data portal
                self.rdf.add((catalog_uri, NFDICORE.NFDI_0000125, feed_uri)) # has data set

                # Same as catalog URI
                if prepare != None and len(prepare) >= 2:
                    self.rdf.add((catalog_uri, SCHEMA.sameAs, self.catalog_uri.rdflib()))
                for i in self.catalog_uri_same.rdflib():
                    self.rdf.add((catalog_uri, SCHEMA.sameAs, i))

            # Add element triples after overwriting feed URI
            for i in self.feed_elements:
                o = FeedElement(i)
                o.feed_uri = self.feed_uri
                o.generate(prepare)
                self.rdf += o.rdf

            # Show that the data is stored
            self.success = True


class FeedElement(MapFeedElementInterface):


    def generate(self, prepare:list|None = None):
        '''
        Generate nfdicore/cto-style feed element triples and fill the store attribute

            Parameters:
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID, disable license check optionally by adding 'no_license_check'.
        '''

        # Check requirements
        if not self.element_uri:
            logger.error('Feed element URI missing')
        elif not self.feed_uri:
            logger.error('Feed URI missing')
        elif not self.license and len(prepare) == 2:
            logger.warning(f'No license attached to feed element {self.element_uri}.')
        else:
            self.rdf = namespaces()


            # TODO Open questions:
            # 1. The properties `schema:associatedMedia`, `is about real world entity`, `has related event`, `has related location`, `has related organization`, `has related person`, `has lyrics` (and probably `has incipit` if there is no provider URI) now require the generation of ARK IDs. Which data do we base their generation on? Do we have a look-up in place for this to work during harvesting (instead of blank nodes)?
            # 2. As we have datasets that use it, is an additional `TGN identifier` for Getty TGN parallel to the `GeoNames identifier` on the horizon?
            # 3. `schema:associatedMedia` appears to only allow for `schema:ImageObject` or `schema:AudioObject`, rather than a wider range of [`schema:MediaObject`s](https://schema.org/MediaObject). Why?
            # 4. How do we justify that there are multiple properties around music lyrics and music incipits, but nothing of this sort for text, video, and other media?
            # 5. Is there an option to decouple `has source file` from the superproperty `has url`? For file dumps we can only list individual file names here, which do not conform to `xsd:anyURI` (which `has url` requires).
            # 6. The illustrations diverge from the ontology a bit, especially around lyrics and incipits. Is it safe to assume that the use of `rdfs:label` and `has text` for lyrics (as well the incipit attached to the lyrics) are errors?
            # 7. Why do `has creation date` and `has destruction date` take a `xsd:dateTime` instead of a `xsd:date`?
            # 8. Could someone explain what the BFO 2020-compliant replacements for what used to be `start date` and `end date` in events are? And why we cannot have simple `xsd:date` properties in addition to whatever needs to be done to please the BFO?
            # 9. Why does `is about real world entity` not also take `organization` and `place` like we use them in the `related` properties? And why is `schema:Sculpture` listed as range but not other relevant classes of objects?
            # 10. Is there an option to clarify the UNIMARC classifier as UNIMARC MOP? And where do I find information about the filmportal.de category vocabulary?


            # ELEMENT

            # Basics
            self.rdf.add((self.element_uri.rdflib(), RDF.type, CTO.CTO_0001005)) # source item
            self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0001008, Literal(self.element_uri.uri, datatype = XSD.anyURI))) # has url

            # Feed URI
            if prepare != None and len(prepare) >= 2:
                feed_uri = URIRef(str(N4C) + prepare[0])
            else:
                feed_uri = self.feed_uri.rdflib()
            self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001006, feed_uri)) # is referenced in

            # Optional wrapper
            if prepare != None and len(prepare) >= 2:
                wrapper = element_ark(self.element_uri.text(), prepare[0])
                self.rdf.add((feed_uri, SCHEMA.dataFeedElement, wrapper))
                self.rdf.add((wrapper, RDF.type, SCHEMA.DataFeedItem))
                self.rdf.add((wrapper, SCHEMA.item, self.element_uri.rdflib())) # TODO Discussions are ongoing whether to use OBO.IAO_0000136 (is about)
                
                # Date modified
                today = date.today()
                self.rdf.add((wrapper, SCHEMA.dateModified, Literal(str(today.isoformat()), datatype = XSD.date)))

            # Element type shorthand
            if self.element_type_short in ['person', 'organisation', 'organization', 'event', 'date', 'place', 'location', 'book', 'structure', 'sculpture', 'sheet-music', 'theater-event', 'item']:
                realworld = BNode() # TODO This is supposed to be an ARK ID per real-world object, which requires a look-up service
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001025, realworld)) # is about real world entity
                if self.element_type_short == 'person':
                    self.rdf.add((realworld, RDF.type, NFDICORE.NFDI_0000004)) # person
                elif self.element_type_short == 'organisation' or self.element_type_short == 'organization':
                    self.rdf.add((realworld, RDF.type, NFDICORE.NFDI_0000003)) # organization TODO This is currently a non-standard type
                elif self.element_type_short == 'event' or self.element_type_short == 'date':
                    self.rdf.add((realworld, RDF.type, NFDICORE.NFDI_0000131)) # event
                elif self.element_type_short == 'place' or self.element_type_short == 'location':
                    self.rdf.add((realworld, RDF.type, NFDICORE.NFDI_0000005)) # place TODO This is currently a non-standard type
                elif self.element_type_short == 'book':
                    self.rdf.add((realworld, RDF.type, SCHEMA.Book))
                elif self.element_type_short == 'structure':
                    self.rdf.add((realworld, RDF.type, SCHEMA.LandmarksOrHistoricalBuildings))
                elif self.element_type_short == 'sculpture':
                    self.rdf.add((realworld, RDF.type, SCHEMA.Sculpture))
                elif self.element_type_short == 'sheet-music':
                    self.rdf.add((realworld, RDF.type, SCHEMA.SheetMusic))
                elif self.element_type_short == 'theater-event':
                    self.rdf.add((realworld, RDF.type, SCHEMA.TheaterEvent))
                elif self.element_type_short == 'item':
                    if self.element_type:
                        self.rdf.add((realworld, RDF.type, self.element_type.rdflib())) # TODO These are currently non-standard types
                    else:
                        self.rdf.add((realworld, RDF.type, SCHEMA.CreativeWork)) # TODO This is currently a non-standard type

                # Same as element URI
                for i in self.element_uri_same.rdflib():
                    element_uri_same_type = type_identifier(i)
                    if element_uri_same_type:
                        self.rdf.add((realworld, NFDICORE.NFDI_0001006, i)) # has external identifier
                        self.rdf.add((i, RDF.type, element_uri_same_type))

            # Data concept shorthand
            if '3d-model' in self.data_concept_short:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001049, CTO.CTO_0001034)) # has data concept, 3D model
            if 'audio' in self.data_concept_short:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001049, CTO.CTO_0001043)) # has data concept, audio object
            if 'image' in self.data_concept_short:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001049, CTO.CTO_0001044)) # has data concept, image object
            if 'media' in self.data_concept_short:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001049, CTO.CTO_0001045)) # has data concept, media object
            if 'sheet-music' in self.data_concept_short:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001049, CTO.CTO_0001046)) # has data concept, sheet music
            if 'text' in self.data_concept_short:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001049, CTO.CTO_0001047)) # has data concept, text object
            if 'video' in self.data_concept_short:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001049, CTO.CTO_0001048)) # has data concept, video object

            # LABEL AND REFERENCE LITERALS

            # Main label
            for i in self.label.rdflib():
                self.rdf.add((self.element_uri.rdflib(), RDFS.label, i))

            # Alternative label
            for i in self.label_alt.rdflib():
                self.rdf.add((self.element_uri.rdflib(), OBO.IAO_0000118, i)) # alternative label TODO Or SKOS.altLabel as in CTO v2?

            # Holding organization
            if self.holding_org:
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001069, self.holding_org.rdflib())) # has holding organization

            # Shelf mark
            for i in self.shelf_mark.rdflib():
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001068, i)) # has shelf mark

            # MEDIA LITERALS

            # Media
            if self.media:
                media = BNode() # TODO This is supposed to be an ARK ID per associated media, but it's unclear how to reliably generate the ID
                self.rdf.add((self.element_uri.rdflib(), SCHEMA.associatedMedia, media))
                if self.media.type == 'image':
                    self.rdf.add((media, RDF.type, SCHEMA.ImageObject))
                elif self.media.type == 'audio':
                    self.rdf.add((media, RDF.type, SCHEMA.AudioObject))
                else:
                    self.rdf.add((media, RDF.type, SCHEMA.MediaObject))
                self.rdf.add((media, CTO.CTO_0001021, Literal(self.media.uri.uri, datatype = XSD.anyURI))) # has content url
                for i in self.media.license.rdflib():
                    if i[0]:
                        n4c_media_license = license_identifier(i[0])
                        if n4c_media_license:
                            self.rdf.add((media, NFDICORE.NFDI_0000142, n4c_media_license)) # has license
                        else:
                            n4c_media_rights = rights_identifier(i[0])
                            if n4c_media_rights:
                                self.rdf.add((media, CTO.CTO_0001022, n4c_media_rights)) # has rights statement
                for i in self.media.byline.rdflib():
                    self.rdf.add((media, CTO.CTO_0001007, i)) # has license statement

            # Lyrics
            if self.lyrics:
                lyrics = BNode() # TODO This is supposed to be an ARK ID per associated media, but it's unclear how to reliably generate the ID
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001077, lyrics)) # has lyrics
                for i in self.lyrics.rdflib():
                    self.rdf.add((lyrics, RDF.type, CTO.CTO_0001002)) # lyrics
                    self.rdf.add((lyrics, CTO.CTO_0001067, i)) # has lyrics text

            # Teaser
            #for i in self.teaser.rdflib():
                #self.rdf.add((self.element_uri.rdflib(), CTO.CTO_XXXXXX3, i)) # teaser TODO Not available

            # Incipit
            if self.incipit:
                incipit_data = self.incipit.rdflib()
                if incipit_data['uri']:
                    incipit = incipit_data['uri']
                else:
                    incipit = BNode() # TODO This is supposed to be an ARK ID per incipit, but it's unclear how to reliably generate the ID
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001065, incipit)) # has incipit
                self.rdf.add((incipit, RDF.type, CTO.CTO_0001024)) # incipit
                if incipit_data['clef']:
                    self.rdf.add((incipit, CTO.CTO_0001061, incipit_data['clef'])) # has clef
                if incipit_data['pattern']:
                    self.rdf.add((incipit, CTO.CTO_0001063, incipit_data['pattern'])) # has incipit pattern
                if incipit_data['time_sig']:
                    self.rdf.add((incipit, CTO.CTO_0001060, incipit_data['time_sig'])) # has incipit time signature
                if incipit_data['key']:
                    self.rdf.add((incipit, CTO.CTO_0001064, incipit_data['key'])) # has key
                if incipit_data['key_sig']:
                    self.rdf.add((incipit, CTO.CTO_0001062, incipit_data['key_sig'])) # has key signature

            # Source file
            if self.source_file:
                self.source_file.data_type = SCHEMA.URL # TODO This is supposed to be XSD.anyURI, but that does not work for file names
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001080, self.source_file.rdflib())) # has source file

            # Source type shorthand
            if 'cgif' in self.source_type_short:
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4022)) # has standard, RDF
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E6367)) # has standard, CGIF (TODO not currently a standard)
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4456)) # has standard, Schema.org
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3087)) # has media type, JSON
            if 'tei' in self.source_type_short:
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3948)) # has standard, TEI
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3081)) # has media type, XML
            if 'lido' in self.source_type_short:
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3947)) # has standard, LIDO
                #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4468)) # has standard, LIDO 1.1
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3081)) # has media type, XML
            
            # TODO CVMA additions (automate if possible)
            if prepare[0] == 'E5308':
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3947)) # has standard, LIDO
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E5401)) # has standard, XMP
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E6336)) # has standard, ISO 8601
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2971)) # has media type, JPEG
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2979)) # has media type, TIFF
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3079)) # has media type, HTML
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3081)) # has media type, XML

            # TODO Bildindex additions (automate if possible)
            if prepare[0] == 'E6161':
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2971)) # has media type, JPEG

            # TODO Fotothek additions (automate if possible)
            if prepare[0] == 'E6064':
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2971)) # has media type, JPEG
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4461)) # has standard, IIIF

            # TODO Optional set of further source types (standard, automate if possible)
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3947)) # has standard, LIDO
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3948)) # has standard, TEI
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3949)) # has standard, MEI
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3950)) # has standard, CIDOC-CRM
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E3951)) # has standard, MARC21
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4022)) # has standard, RDF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4091)) # has standard, DataCite Metadata Schema
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4092)) # has standard, Dublin Core Metadata Element Set
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4428)) # has standard, METS
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4432)) # has standard, MODS
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4456)) # has standard, Schema.org
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4461)) # has standard, IIIF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E4468)) # has standard, LIDO 1.1
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E5401)) # has standard, XMP
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E5939)) # has standard, Europeana Data Model
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E6070)) # has standard, BEACON
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E6332)) # has standard, ISO 639-2
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E6334)) # has standard, ISO 639-3
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000207, N4C.E6336)) # has standard, ISO 8601

            # TODO Optional set of further source types (media type, automate if possible)
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2962)) # has media type, CSV
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2965)) # has media type, DOCX
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2967)) # has media type, BMP
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2969)) # has media type, GIF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2971)) # has media type, JPEG
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2973)) # has media type, JP2
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2975)) # has media type, PNG
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2977)) # has media type, PSD
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2979)) # has media type, TIFF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2981)) # has media type, SVG
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2983)) # has media type, ODG
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2985)) # has media type, AAC
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2987)) # has media type, AIFF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2989)) # has media type, AC3
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2991)) # has media type, FLAC
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2992)) # has media type, MP3
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2994)) # has media type, VOX
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2996)) # has media type, WAV
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E2998)) # has media type, WMA
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3000)) # has media type, TXT
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3002)) # has media type, RTF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3003)) # has media type, H.264
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3008)) # has media type, MPEG-2
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3009)) # has media type, MPEG-4
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3010)) # has media type, OGG
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3018)) # has media type, RM
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3019)) # has media type, MPEG-2 TS
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3020)) # has media type, WebM
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3021)) # has media type, WMV
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3022)) # has media type, DAE
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3023)) # has media type, KMZ
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3024)) # has media type, OBJ
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3025)) # has media type, PLY
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3026)) # has media type, VRML
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3027)) # has media type, X3D
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3028)) # has media type, U3D
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3037)) # has media type, MOV
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3038)) # has media type, MKV
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3039)) # has media type, ZIP
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3040)) # has media type, DWG
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3041)) # has media type, DXF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3050)) # has media type, 3DS
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3052)) # has media type, STL
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3054)) # has media type, XLSX
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3055)) # has media type, PDF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3057)) # has media type, ODT
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3059)) # has media type, ODS
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3061)) # has media type, ODP
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3062)) # has media type, OTT
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3064)) # has media type, OTF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3066)) # has media type, OTP
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3068)) # has media type, ODF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3069)) # has media type, PPT
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3070)) # has media type, PPTX
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3071)) # has media type, PDF/A
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3073)) # has media type, SXC
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3075)) # has media type, SXI
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3077)) # has media type, SXW
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3079)) # has media type, HTML
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3081)) # has media type, XML
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3083)) # has media type, WARC
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3085)) # has media type, SQL
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3087)) # has media type, JSON
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3114)) # has media type, MP4
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E3116)) # has media type, webdvd.zip
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E6073)) # has media type, VTT
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E6392)) # has media type, WebP
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E6440)) # has media type, MXF
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E6443)) # has media type, SIARD
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E6445)) # has media type, DPX
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E6447)) # has media type, GZIP
            #self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000146, N4C.E6449)) # has media type, GLTF

            # RIGHTS URIS

            # Publisher
            for i in self.publisher.rdflib():
                self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000191, i)) # published by

            # License
            for i in self.license.rdflib():
                if i[0]:
                    n4c_license = license_identifier(i[0])
                    if n4c_license:
                        self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000142, n4c_license)) # has license
                    else:
                        n4c_rights = rights_identifier(i[0])
                        if n4c_rights:
                            self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001022, n4c_rights)) # has rights statement

            # Byline
            for i in self.byline.rdflib():
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001007, i)) # has license statement

            # RELATED URIS AND FALLBACK LITERALS

            # Classifier
            for i in self.vocab_classifier.rdflib():
                if i[0]:
                    classifier_type = type_classifier(i[0])
                    if classifier_type:
                        self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001026, i[0])) # has external classifier
                        self.rdf.add((i[0], RDF.type, classifier_type))
                        if i[1]:
                            for e in i[1]:
                                self.rdf.add((i[0], RDFS.label, e))

            # Related location
            for i in self.vocab_related_location.rdflib():
                related_location = BNode() # TODO This is supposed to be an ARK ID per location, which requires a look-up service
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001011, related_location)) # has related location
                self.rdf.add((related_location, RDF.type, NFDICORE.NFDI_0000005)) # place
                if i[0]:
                    related_location_type = type_identifier(i[0])
                    if related_location_type:
                        self.rdf.add((related_location, NFDICORE.NFDI_0001006, i[0])) # has external identifier
                        self.rdf.add((i[0], RDF.type, related_location_type))
                if i[1]:
                    for e in i[1]:
                        self.rdf.add((related_location, RDFS.label, e))

            # Related event
            for i in self.vocab_related_event.rdflib():
                related_event = BNode() # TODO This is supposed to be an ARK ID per event, which requires a look-up service
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001012, related_event)) # has related event
                self.rdf.add((related_event, RDF.type, NFDICORE.NFDI_0000131)) # event
                if i[0]:
                    related_event_type = type_identifier(i[0])
                    if related_event_type:
                        self.rdf.add((related_event, NFDICORE.NFDI_0001006, i[0])) # has external identifier
                        self.rdf.add((i[0], RDF.type, related_event_type))
                if i[1]:
                    for e in i[1]:
                        self.rdf.add((related_event, RDFS.label, e))

            # Related organization
            for i in self.vocab_related_organization.rdflib():
                related_organization = BNode() # TODO This is supposed to be an ARK ID per organization, which requires a look-up service
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001010, related_organization)) # has related organization
                self.rdf.add((related_organization, RDF.type, NFDICORE.NFDI_0000003)) # organization
                if i[0]:
                    related_organization_type = type_identifier(i[0])
                    if related_organization_type:
                        self.rdf.add((related_organization, NFDICORE.NFDI_0001006, i[0])) # has external identifier
                        self.rdf.add((i[0], RDF.type, related_organization_type))
                if i[1]:
                    for e in i[1]:
                        self.rdf.add((related_organization, RDFS.label, e))

            # Related person
            for i in self.vocab_related_person.rdflib():
                related_person = BNode() # TODO This is supposed to be an ARK ID per person, which requires a look-up service
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001009, related_person)) # has related person
                self.rdf.add((related_person, RDF.type, NFDICORE.NFDI_0000004)) # person
                if i[0]:
                    related_person_type = type_identifier(i[0])
                    if related_person_type:
                        self.rdf.add((related_person, NFDICORE.NFDI_0001006, i[0])) # has external identifier
                        self.rdf.add((i[0], RDF.type, related_person_type))
                if i[1]:
                    for e in i[1]:
                        self.rdf.add((related_person, RDFS.label, e))

            # Related item
            for i in self.related_item.rdflib():
                self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001019, i)) # has related item

            # DATES BY TYPE

            # For persons
            if self.element_type_short == 'person':

                # Birth date
                if self.birth_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000105, self.birth_date.rdflib(True))) # birth date

                # Death date
                if self.death_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000127, self.death_date.rdflib(True))) # death date

            # For organizations
            elif self.element_type_short == 'organization' or self.element_type_short == 'organisation':

                # Foundation date
                if self.foundation_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000136, self.foundation_date.rdflib(True))) # foundation date

                # Dissolution date
                if self.dissolution_date:
                    self.rdf.add((self.element_uri.rdflib(), NFDICORE.NFDI_0000128, self.dissolution_date.rdflib(True))) # dissolution date

            # For places
            elif self.element_type_short == 'place' or self.element_type_short == 'location' or self.element_type_short == 'structure':
                pass

            # For events
            elif self.element_type_short == 'event' or self.element_type_short == 'date' or self.element_type_short == 'theater-event':

                # Start date
                if self.start_date:
                    self.rdf.add((self.element_uri.rdflib(), CTO.CTO_XXXXXX1, self.start_date.rdflib(True))) # start date TODO Not available, and BFO event start/end properties not allowed in a continuant

                # End date
                if self.end_date:
                    self.rdf.add((self.element_uri.rdflib(), CTO.CTO_XXXXXX2, self.end_date.rdflib(True))) # end date TODO Not available, and BFO event start/end properties not allowed in a continuant

            # For items
            else:

                # Creation date
                if self.creation_date:
                    self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001072, self.creation_date.rdflib())) # has creation date TODO Ontology does not allow for XSD.date and SCHEMA.DateTime in addition to XSD.dateTime

                # Creation period
                for i in self.creation_period.rdflib(True):
                    self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001073, i)) # has creation period

                # Destruction date
                if self.destruction_date:
                    self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001074, self.destruction_date.rdflib())) # has destruction date TODO Ontology does not allow for XSD.date and SCHEMA.DateTime in addition to XSD.dateTime

                # Approximate period
                for i in self.approximate_period.rdflib(True):
                    self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001071, i)) # has approximate period

                # Existence period
                for i in self.existence_period.rdflib(True):
                    self.rdf.add((self.element_uri.rdflib(), CTO.CTO_0001075, i)) # has existence period

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
    output.bind('obo', OBO)

    # Vocabularies and others
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
    output.bind('orcid', ORCID)
    output.bind('ror', ROR)
    output.bind('doi', DOI)
    output.bind('tgn', TGN)
    output.bind('cerl', CERL)
    output.bind('gv', GV)
    output.bind('hs', HS)
    output.bind('mimo', MIMO)
    output.bind('matcult', MATCULT)
    output.bind('unesco', UNESCO)
    output.bind('wnk', WNK)
    output.bind('lcsh', LCSH)
    output.bind('mop', MOP)
    output.bind('fpcat', FPCAT)

    # Return graph
    return output


def element_ark(element_uri:str, prepare_feed:str) -> URIRef:
    '''
    Generate an NFDI4Culture ARK ID for the wrapper of a data feed element

        Parameters:
            element_uri (str): URI of the element to produce an ARK ID for
            prepare_feed (str): NFDI4Culture IRI of the feed

        Returns:
            URIRef: ARK ID based on a hash of the element URI
    '''

    # Generate hash and ARK ID
    hash = sha256(element_uri.encode()).hexdigest()[:8]
    uri = 'https://nfdi4culture.de/id/ark:/60538/' + prepare_feed + '_' + hash

    # Return ARK ID as URI
    return URIRef(uri)


def type_identifier(identifier:URIRef) -> URIRef|None:
    '''
    Provide the CTO identifier type

        Parameters:
            identifier (URIRef): URI of the identifier to produce the type for

        Returns:
            URIRef|None: Identifier type if found
    '''

    # Check identifier namespace
    if identifier in FG:
        return NFDICORE.NFDI_0001015 # FactGrid identifier
    elif identifier in GND:
        return NFDICORE.NFDI_0001009 # GND identifier
    elif identifier in GN:
        return NFDICORE.NFDI_0001011 # GeoNames identifier
    elif identifier in ISIL:
        return NFDICORE.NFDI_0001014 # ISIL identifier
    elif identifier in ORCID:
        return OBO.IAO_0000708 # ORCID identifier
    elif identifier in RISM:
        return NFDICORE.NFDI_0001016 # RISM identifier
    elif identifier in ROR:
        return NFDICORE.NFDI_0001013 # ROR identifier
    elif identifier in VIAF:
        return NFDICORE.NFDI_0001010 # VIAF identifier
    elif identifier in WD:
        return NFDICORE.NFDI_0001012 # Wikidata identifier
    elif identifier in DOI:
        return NFDICORE.NFDI_0001037 # digital object identifier
    elif identifier in TGN:
        return NFDICORE.NFDI_0001055 # TGN identifier
    else:
        return None


def type_classifier(classifier:URIRef) -> URIRef|None:
    '''
    Provide the CTO classifier type

        Parameters:
            classifier (URIRef): URI of the classifier to produce the type for

        Returns:
            URIRef|None: Classifier type if found
    '''

    # Check classifier namespace
    if classifier in AAT:
        return CTO.CTO_0001029 # AAT classifier
    elif classifier in RISM:
        return CTO.CTO_0001031 # RISM classifier
    elif classifier in IC:
        return CTO.CTO_0001030 # Iconclass classifier
    elif classifier in CERL:
        return CTO.CTO_0001055 # CERL thesaurus classifier
    elif classifier in FPCAT:
        return CTO.CTO_0001054 # Filmportal Category Vocabulary classifier
    elif classifier in GV:
        return CTO.CTO_0001053 # Graphikvokabular classifier
    elif classifier in HS:
        return CTO.CTO_0001052 # Hornbostel Sachs classifier
    elif classifier in LCSH:
        return CTO.CTO_0001050 # LCSH classifier
    elif classifier in MIMO:
        return CTO.CTO_0001051 # MIMO classifier
    elif classifier in MATCULT:
        return CTO.CTO_0001059 # Material Culture Thesaurus classifier
    elif classifier in UNESCO:
        return CTO.CTO_0001057 # UNESCO Thesaurus classifier
    elif classifier in MOP:
        return CTO.CTO_0001056 # UNIMARC classifier (MOP)
    elif classifier in WD:
        return CTO.CTO_0001079 # Wikidata classifier
    elif classifier in WNK:
        return CTO.CTO_0001058 # Wortnetz Kultur classifier
    else:
        return None


def license_identifier(identifier:URIRef) -> URIRef|None:
    '''
    Provide the N4C license identifier

        Parameters:
            identifier (URIRef): URI of the license to produce the N4C identifier for

        Returns:
            URIRef|None: N4C identifier if found
    '''

    # Check license identifier
    if 'creativecommons.org/publicdomain/zero/1.0' in identifier:
        return N4C.E3978
    elif 'creativecommons.org/licenses/by/4.0' in identifier:
        return N4C.E6404
    elif 'creativecommons.org/licenses/by/3.0' in identifier:
        return N4C.E6406
    elif 'creativecommons.org/licenses/by-nc/3.0' in identifier:
        return N4C.E6408
    elif 'creativecommons.org/licenses/by-nc/4.0' in identifier:
        return N4C.E6410
    elif 'creativecommons.org/licenses/by-nc-nd/3.0' in identifier:
        return N4C.E6413
    elif 'creativecommons.org/licenses/by-nc-nd/4.0' in identifier:
        return N4C.E6415
    elif 'creativecommons.org/licenses/by-nc-sa/3.0' in identifier:
        return N4C.E6417
    elif 'creativecommons.org/licenses/by-nc-sa/4.0' in identifier:
        return N4C.E6418
    elif 'creativecommons.org/licenses/by-nd/3.0' in identifier:
        return N4C.E6419
    elif 'creativecommons.org/licenses/by-nd/4.0' in identifier:
        return N4C.E6422
    elif 'creativecommons.org/licenses/by-sa/3.0' in identifier:
        return N4C.E6428
    elif 'creativecommons.org/licenses/by-sa/4.0' in identifier:
        return N4C.E6429
    elif 'opensource.org/license/mit' in identifier:
        return N4C.E3604
    elif 'opensource.org/license/apache-2-0' in identifier:
        return N4C.E3605
    elif 'opensource.org/license/gpl-3-0' in identifier:
        return N4C.E3606
    elif 'opensource.org/license/mpl-2-0' in identifier:
        return N4C.E3933
    elif 'opensource.org/license/agpl-v3' in identifier:
        return N4C.E4114
    elif 'opensource.org/license/cddl-1-0' in identifier:
        return N4C.E4197
    elif 'opensource.org/license/epl-2-0' in identifier:
        return N4C.E4206
    elif 'opensource.org/license/gpl-2-0' in identifier:
        return N4C.E4208
    elif 'opensource.org/license/lgpl-2-1' in identifier:
        return N4C.E4210
    elif 'opensource.org/license/lgpl-3-0' in identifier:
        return N4C.E4212
    elif 'opensource.org/license/lgpl-2-0' in identifier:
        return N4C.E4214
    elif 'opensource.org/license/bsd-2-clause' in identifier:
        return N4C.E4216
    elif 'opensource.org/license/bsd-3-clause' in identifier:
        return N4C.E4219
    elif 'creativecommons.org/publicdomain/mark/1.0' in identifier:
        return N4C.E5156
    elif 'opendatacommons.org/licenses/by/1-0' in identifier:
        return N4C.E6395
    elif 'opendatacommons.org/licenses/odbl/1-0' in identifier:
        return N4C.E6397
    elif 'opendatacommons.org/licenses/pddl/1.0' in identifier:
        return N4C.E6399
    else:
        return identifier


def rights_identifier(identifier:URIRef) -> URIRef|None:
    '''
    Provide the N4C rights-statement identifier

        Parameters:
            identifier (URIRef): URI of the rights statement to produce the N4C identifier for

        Returns:
            URIRef|None: N4C identifier if found
    '''

    # Check rights-statement identifier
    if 'rightsstatements.org/vocab/CNE/1.0' in identifier:
        return N4C.E6214
    elif 'rightsstatements.org/vocab/UND/1.0' in identifier:
        return N4C.E6216
    elif 'rightsstatements.org/vocab/InC/1.0' in identifier:
        return N4C.E6206
    elif 'www.deutsche-digitale-bibliothek.de/content/lizenzen/rv-fz' in identifier:
        return N4C.E6206
    elif 'www.deutsche-digitale-bibliothek.de/content/lizenzen/rv-ez' in identifier:
        return N4C.E6206
    elif 'rightsstatements.org/vocab/InC-EDU/1.0' in identifier:
        return N4C.E6210
    elif 'rightsstatements.org/vocab/InC-OW-EU/1.0' in identifier:
        return N4C.E6207
    elif 'rightsstatements.org/vocab/InC-NC/1.0' in identifier:
        return N4C.E6208
    elif 'rightsstatements.org/vocab/InC-RUU/1.0' in identifier:
        return N4C.E6209
    elif 'rightsstatements.org/vocab/NoC-CR/1.0' in identifier:
        return N4C.E6213
    elif 'rightsstatements.org/vocab/NoC-NC/1.0' in identifier:
        return N4C.E6212
    elif 'rightsstatements.org/vocab/NoC-OKLR/1.0' in identifier:
        return N4C.E6211
    elif 'rightsstatements.org/vocab/NKC/1.0' in identifier:
        return N4C.E6215
    else:
        return identifier
