# Retrieve and extract data from ZIP files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from re import search

# Import script modules
from base.data import Uri, UriList, Date
from base.extract import ExtractFeedInterface


class Feed(ExtractFeedInterface):


    def retrieve(self):
        '''
        Extract feed data from ZIP files
        '''

        # Feed URI
        self.feed_uri = Uri(self.beacon_info('FEED'), normalize = False)
    
        # Same as feed
        #self.feed_uri_same = 
    
        # Next feed URI
        #self.feed_uri_next = 
    
        # Catalog URI
        #self.catalog_uri = 
    
        # Same as catalog
        #self.catalog_uri_same = 
    
        # Date modified # TODO????????????????
        #self.modified_date = 
    
        # Element URIs
        self.element_uris = UriList(self.zipped_files(), normalize = False)
    
        # Feed elements
        #if self.feed_elements == 


    def zipped_files(self) -> list:
        '''
        Unpack ZIP archive and retrieve file paths of its contents

            Returns:
                list: paths of files that were contained in the ZIP archive
        '''

        # Something
        pass
