# Generate a Beacon list
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from datetime import date

# Import script modules
from base.map import MapFeedInterface, MapFeedElementInterface

# Set up logging
logger = logging.getLogger(__name__)


class Feed(MapFeedInterface):


    def generate(self, prepare:list|None = None):
        '''
        Generate a Beacon list of the feed and fill the content attribute

            Parameters:
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Set file extension
        self.file_extension = 'txt'

        # Basic set-up
        self.content = '#FORMAT: BEACON'

        # Feed URI
        if self.feed_uri:
            self.content += '\n#FEED: ' + self.feed_uri.text()

        # Date modified
        if self.modified_date:
            self.content += '\n#TIMESTAMP: ' + self.modified_date.text()
        else:
            today = date.today()
            self.content += '\n#TIMESTAMP: ' + str(today.isoformat())

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
        Generate a Beacon list of the feed elements and fill the content attribute

            Parameters:
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Set file extension
        self.file_extension = 'txt'

        # Check requirements
        if not self.element_uri:
            logger.error('Feed element URI missing')
        else:

            # Element URI
            self.content = self.element_uri.text()

            # Show that the data is stored
            self.success = True
