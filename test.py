# Testing for extractors and mappings
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging

# Import script modules
import extract.beacon as beacon
import extract.cmif as cmif
import extract.lido as lido
import extract.schema as schema
from base.data import Uri
from base.file import File
from base.lookup import Lookup

# Set up logging
logger = logging.getLogger(__name__)
open('downloads/test.log', 'w').close()
logging.basicConfig(filename = 'downloads/test.log', level = logging.INFO)


# List of tests to run
tests = [
    'beacon-feed-a',
    'beacon-feed-b',
    'cmif-feed-a',
    'lido-element-a',
    'lido-element-b',
    'schema-feed-a',
    'schema-feed-b',
    'schema-element-a',
    'lookup'
]

# Beacon feed A
if 'beacon-feed-a' in tests:
    file = File('https://kba.karl-barth.ch/api/actors?format=beacon')
    extract = beacon.Feed(file)
    #print(extract)
    extract.map_and_save('beacon', 'downloads/test-beacon-feed-a')
    extract.map_and_save('csv', 'downloads/test-beacon-feed-a')
    extract.map_and_turtle('cto', 'downloads/test-beacon-feed-a')

# Beacon feed B
if 'beacon-feed-b' in tests:
    file = File('http://www.bib-bvb.de/OpenData/beacon_bvb01.txt')
    extract = beacon.Feed(file)
    #print(extract)
    extract.map_and_save('beacon', 'downloads/test-beacon-feed-b')
    extract.map_and_save('csv', 'downloads/test-beacon-feed-b')
    extract.map_and_turtle('cto', 'downloads/test-beacon-feed-b')

# CMIF feed A
if 'cmif-feed-a' in tests:
    file = File('https://gregorovius-edition.dhi-roma.it/api/cmif')
    extract = cmif.Feed(file)
    #print(extract)
    extract.map_and_save('beacon', 'downloads/test-cmif-feed-a')
    extract.map_and_save('csv', 'downloads/test-cmif-feed-a')
    extract.map_and_turtle('cto', 'downloads/test-cmif-feed-a')

# LIDO feed element A
if 'lido-element-a' in tests:
    file = File('https://corpusvitrearum.de/id/F13494/about.lido')
    extract = lido.FeedElement(file)
    #print(extract)
    extract.feed_uri = Uri('https://corpusvitrearum.de/cvma-digital/bildarchiv.html')
    extract.map_and_turtle('cto', 'downloads/test-lido-element-a')

# LIDO feed element B
if 'lido-element-b' in tests:
    file = File('https://www.graphikportal.org/lido-examples/Technisches_Beispiel.xml')
    extract = lido.FeedElement(file)
    #print(extract)
    extract.feed_uri = Uri('https://www.graphikportal.org/lido-examples')
    extract.map_and_turtle('cto', 'downloads/test-lido-element-b')

# Schema.org feed and elements A
if 'schema-feed-a' in tests:
    file = File('https://corpusvitrearum.de/id/about.cgif?tx_vocabulary_about[page]=40')
    extract = schema.Feed(file, True)
    #print(extract)
    extract.map_and_save('beacon', 'downloads/test-schema-feed-a')
    extract.map_and_save('csv', 'downloads/test-schema-feed-a')
    extract.map_and_turtle('cto', 'downloads/test-schema-feed-a', prepare = ['E1234', 'E5678'])

# Schema.org feed and elements B
if 'schema-feed-b' in tests:
    file = File('https://gn.biblhertz.it/fotothek/seo')
    extract = schema.Feed(file, True)
    #print(extract)
    extract.map_and_save('beacon', 'downloads/test-schema-feed-b')
    extract.map_and_save('csv', 'downloads/test-schema-feed-b')
    extract.map_and_turtle('cto', 'downloads/test-schema-feed-b')

# Schema.org element A
if 'schema-element-a' in tests:
    file = File('https://corpusvitrearum.de/cvma-digital/bildarchiv.html?tx_cvma_archive[image]=13494&tx_cvma_archive[action]=show&tx_cvma_archive[controller]=Gallery&cHash=0c57f24f32400787b3ae9b00daed634e')
    extract = schema.FeedElement(file)
    #print(extract)
    extract.map_and_turtle('cto', 'downloads/test-schema-element-a')

# Lookup
if 'lookup' in tests:
    lookup = Lookup('downloads/test-lookup')
    print(lookup.check('http://www.wikidata.org/entity/Q254'))
    #print(lookup.check('https://d-nb.info/gnd/7766321-4'))
    lookup.save()
