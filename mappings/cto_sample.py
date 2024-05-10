# Sample use of nfdicore/cto classes
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import cto
from rdflib import Namespace
from rdflib.term import Literal

# Define namespaces
from rdflib.namespace import SDO
N4C = Namespace('https://nfdi4culture.de/id/')

# Set up feed
feed = cto.Feed(
    feed_uri         = N4C.E123, # URI as str, Literal, or URIRef
    feed_uri_same    = [ # URI as str, Literal, URIRef, or list thereof
        'https://example.org/project',
        'https://cold-storage.org/project'
    ],
    connect          = True, # False leaves out schema.org wrappers for ARK IDs
    catalog_uri      = N4C.E321, # URI as str, Literal, or URIRef
    catalog_uri_same = 'https://example.org' # URI as str, Literal, URIRef, or list thereof
)

# Set up at least one feed element
element = cto.FeedElement(
    feed_uri         = N4C.E123, # URI as str, Literal, or URIRef
    element_type     = SDO.Manuscript, # URI as str, Literal, or URIRef or generic string like 'person'
    element_uri      = 'https://example.org/project/id/1', # URI as str, Literal, or URIRef
    element_uri_same = 'https://cold-storage.org/project/id/1', # URI as str, Literal, URIRef, or list thereof
    connect          = True, # False leaves out schema.org wrappers for ARK IDs
    label            = [ # String as str, Literal, URIRef, or list thereof
        Literal('Short title', lang='en'),
        Literal('Kurzer Titel', lang='de')
    ],
    label_alt        = [ # String as str, Literal, URIRef, or list thereof
        Literal('Slightly longer, alternative title', lang = 'en'),
        Literal('Etwas längerer Alternativtitel', lang = 'de')
    ],
    shelf_mark       = Literal('Libr. Op. E123-1', lang = 'de'), # String as str, Literal, URIRef, or list thereof
    image            = 'https://example.org/project/id/1/img', # URL as str, Literal, URIRef, or list thereof
    lyrics           = Literal('I am an example / And this is my jam', lang = 'en'), # String as str, Literal, URIRef, or list thereof
    text_incipit     = Literal('I am an example', lang = 'en'), # String as str, Literal, URIRef, or list thereof
    music_incipit    = { # Dict or list of dicts containing one optional URI and four strings as str, Literal, URIRef, or list thereof
        'uri': 'https://example.org/project/id/1/inc',
        'clef': 'G-2',
        'key_sig': 'xF',
        'time_sig': '3/4',
        'pattern': "4'D/8.6GB4AG/8.6''EC2'A/4.''D8'BAG/4BA"
    },
    source_file      = 'https://example.org/project/id/1/xml', # URL as str, Literal, URIRef, or list thereof
    iiif_image_api   = 'https://example.org/project/id/1/iiif', # URL as str, Literal, URIRef, or list thereof
    iiif_presentation_api = 'https://example.org/project/id/1/iiifmanifest', # URL as str, Literal, URIRef, or list thereof
    ddb_api          = 'https://example.org/project/id/1/ddb', # URL as str, Literal, URIRef, or list thereof
    oaipmh_api       = 'https://example.org/project/id/1/oaipmh', # URL as str, Literal, URIRef, or list thereof
    publisher        = N4C.E456, # URI as str, Literal, URIRef, or list thereof
    license          = 'https://creativecommons.org/licenses/by/4.0/', # URI as str, Literal, URIRef, or list thereof
    vocab_element_type = 'http://vocab.getty.edu/aat/300026877', # Getty AAT URI as str, Literal, URIRef, or list thereof
    vocab_subject_concept = 'https://iconclass.org/123', # URI as str, Literal, URIRef, or list thereof
    vocab_related_location = [ # URI as str, Literal, URIRef, or list thereof
        'http://sws.geonames.org/1234567',
        'https://www.geonames.org/7654321' # Some wrong URIs are auto-corrected
    ],
    vocab_related_event = 'http://www.wikidata.org/entity/Q123', # URI as str, Literal, URIRef, or list thereof
    vocab_related_organization = 'http://d-nb.info/gnd/987654321', # URI as str, Literal, URIRef, or list thereof
    vocab_related_person = 'http://d-nb.info/gnd/123456789', # URI as str, Literal, URIRef, or list thereof
    vocab_further    = 'https://database.factgrid.de/wiki/Item:4321', # URI as str, Literal, URIRef, or list thereof
    related_item     = [ # URI as str, Literal, URIRef, or list thereof
        'https://example.org/project/id/5',
        'https://example.org/project/id/9/' # Trailing slashes in URIs are auto-removed
    ],
    birth_date       = '2004-01-01', # Date or date time as str, date, or datetime, timestamp as int, or list therof
    death_date       = '2024-01-01', # Date or date time as str, date, or datetime, timestamp as int, or list therof
    foundation_date  = '2004-01-01', # Date or date time as str, date, or datetime, timestamp as int, or list therof
    dissolution_date = '2024-01-01', # Date or date time as str, date, or datetime, timestamp as int, or list therof
    start_date       = 1704130200, # Date or date time as str, date, or datetime, timestamp as int, or list therof
    end_date         = '2024-01-01', # Date or date time as str, date, or datetime, timestamp as int, or list therof
    creation_date    = '2004-01-01', # Date or date time as str, date, or datetime, timestamp as int, or list therof
    creation_period  = '2024-01-01T00:00:00/2004-01-01T23:59:59', # Date string as str, Literal, or list therof
    destruction_date = '2024-01-01T18:30:00', # Date or date time as str, date, or datetime, timestamp as int, or list therof
    approximate_period = [ # Date string as str, Literal, or list therof
        Literal('Noughties', lang = 'en'),
        Literal('Nullerjahre', lang = 'de')
    ],
    existence_period = [ # Date string as str, Literal, or list therof
        Literal('First quarter of the 21st century', lang = 'en'),
        Literal('Erstes Viertel des 21. Jahrhunderts', lang = 'de')
    ]
)

# Combine feed and elements
feed += element

# Save as Turtle file
feed.serialize(destination = 'cto_sample.ttl')