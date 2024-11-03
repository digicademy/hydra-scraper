# Retrieve and extract data from folders and ZIP files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import script modules
from base.data import UriList
from base.extract import ExtractFeedInterface


class Feed(ExtractFeedInterface):


    def retrieve(self):
        '''
        Extract feed data from folders and ZIP files
        '''

        # Feed URI
        #self.feed_uri = 
    
        # Same as feed
        #self.feed_uri_same = 
    
        # Next feed URI
        #self.feed_uri_next = 
    
        # Catalog URI
        #self.catalog_uri = 
    
        # Same as catalog
        #self.catalog_uri_same = 
    
        # Date modified
        #self.modified_date = 
    
        # Element URIs
        if self.file.directory:
            self.element_uris = self.file.directory
    
        # Feed elements
        #if self.feed_elements == 
