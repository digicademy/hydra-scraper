# Generate nfdicore/cto-style triples
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging

# Import script modules
from base.map import MapFeedInterface, MapFeedElementInterface

# Set up logging
logger = logging.getLogger(__name__)


class Feed(MapFeedInterface):


    def generate(self, prepare:list|None = None):
        '''
        Generate a CSV table of the feed and fill the content attribute

            Parameters:
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Set file extension
        self.file_extension = 'csv'

        # Basic set-up
        self.content = csv('feed_uri')
        self.content += csv('element_uri')
        self.content += csv('element_uri_same')
        self.content += csv('element_type')
        self.content += csv('label')
        self.content += csv('label_alt')
        self.content += csv('shelf_mark')
        self.content += csv('image')
        self.content += csv('lyrics')
        self.content += csv('text_incipit')
        self.content += csv('music_incipit')
        self.content += csv('source_file')
        self.content += csv('iiif_image_api')
        self.content += csv('iiif_presentation_api')
        self.content += csv('ddb_api')
        self.content += csv('oaipmh_api')
        self.content += csv('publisher')
        self.content += csv('license')
        self.content += csv('vocab_element_type')
        self.content += csv('vocab_subject_concept')
        self.content += csv('vocab_related_location')
        self.content += csv('vocab_related_event')
        self.content += csv('vocab_related_organization')
        self.content += csv('vocab_related_person')
        self.content += csv('vocab_further')
        self.content += csv('related_item')
        self.content += csv('birth_date')
        self.content += csv('death_date')
        self.content += csv('foundation_date')
        self.content += csv('dissolution_date')
        self.content += csv('start_date')
        self.content += csv('end_date')
        self.content += csv('creation_date')
        self.content += csv('creation_period')
        self.content += csv('destruction_date')
        self.content += csv('approximate_period')
        self.content += csv('existence_period', last = True)

        # Add line break if there are elements
        if self.feed_elements:
            self.content += '\n'

        # Add elements
        for i, e in enumerate(self.feed_elements):
            o = FeedElement(e)
            o.generate(prepare)
            self.content += o.content

            # Add line break if not the last element
            if i + 1 != len(self.feed_elements):
                self.content += '\n'

        # Show that the data is stored
        self.success = True


class FeedElement(MapFeedElementInterface):


    def generate(self, prepare:list|None = None):
        '''
        Generate a CSV table of the feed elements and fill the content attribute

            Parameters:
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Set file extension
        self.file_extension = 'csv'

        # Check requirements
        if not self.element_uri:
            logger.error('Feed element URI missing')
        else:
            self.content = ''

            # ELEMENT

            # Feed URI
            self.content += csv(self.feed_uri.text())

            # Element URI
            self.content += csv(self.element_uri.text())

            # Same as element URI
            self.content += csv(self.element_uri_same.text())

            # Element type
            if self.element_type:
                self.content += csv(self.element_type.text())
            else:
                self.content += csv(self.element_type_shorthand)

            # LABEL AND REFERENCE LITERALS

            # Main label
            self.content += csv(self.label.text())

            # Alternative label
            self.content += csv(self.label_alt.text())

            # Shelf mark
            self.content += csv(self.shelf_mark.text())

            # MEDIA LITERALS

            # Image
            self.content += csv(self.image.text())

            # Lyrics
            self.content += csv(self.lyrics.text())

            # Text incipit
            self.content += csv(self.text_incipit.text())

            # Music incipit
            self.content += csv(self.music_incipit.text())

            # Source file
            self.content += csv(self.source_file.text())

            # API LITERALS

            # IIIF Image API
            self.content += csv(self.iiif_image_api.text())

            # IIIF Presentation API
            self.content += csv(self.iiif_presentation_api.text())

            # DDB API
            self.content += csv(self.ddb_api.text())

            # OAI-PMH API
            self.content += csv(self.oaipmh_api.text())

            # RIGHTS URIS

            # Publisher
            self.content += csv(self.publisher.text())

            # License
            self.content += csv(self.license.text())

            # RELATED URIS AND FALLBACK LITERALS

            # Element type
            self.content += csv(self.vocab_element_type.text())

            # Subject concept
            self.content += csv(self.vocab_subject_concept.text())

            # Related location
            self.content += csv(self.vocab_related_location.text())

            # Related event
            self.content += csv(self.vocab_related_event.text())

            # Related organization
            self.content += csv(self.vocab_related_organization.text())

            # Related person
            self.content += csv(self.vocab_related_person.text())

            # Further vocabularies
            self.content += csv(self.vocab_further.text())

            # Related item
            self.content += csv(self.related_item.text())

            # DATES BY TYPE

            # Birth date
            self.content += csv(self.birth_date.text())

            # Death date
            self.content += csv(self.death_date.text())

            # Foundation date
            self.content += csv(self.foundation_date.text())

            # Dissolution date
            self.content += csv(self.dissolution_date.text())

            # Start date
            self.content += csv(self.start_date.text())

            # End date
            self.content += csv(self.end_date.text())

            # Creation date
            self.content += csv(self.creation_date.text())

            # Creation period
            self.content += csv(self.creation_period.text())

            # Destruction date
            self.content += csv(self.destruction_date.text())

            # Approximate period
            self.content += csv(self.approximate_period.text())

            # Existence period
            self.content += csv(self.existence_period.text(), last = True)

            # Show that the data is stored
            self.success = True


def csv(input:str, last:bool = False) -> str:
    '''
    Surround string with quotation marks and add a comma

        Parameters:
            input (str): String to surround with commas
            last (bool): Marker to decide whether to add a comma

        Returns:
            str: Quoted string
    '''

    # Set up new string
    input = input.replace('"', '\"')
    input = '"' + input + '"'
    if not last:
        input += ','

    # Return string
    return input
