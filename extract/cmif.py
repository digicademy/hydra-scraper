# Retrieve and extract data from CMIF files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import script modules
from base.data import Uri, UriList, Date
from base.extract import ExtractFeedInterface


class Feed(ExtractFeedInterface):


    def retrieve(self):
        '''
        Extract feed data from CMIF files
        '''

        # Feed URI
        self.feed_uri = Uri(self.xml_first_text('.//{T}teiHeader/{T}fileDesc/{T}publicationStmt/{T}idno[@type="url"]'), normalize = False)

        # Same as feed
        self.feed_uri_same = UriList(self.xml_first_attribute('.//{T}teiHeader/{T}fileDesc/{T}sourceDesc/{T}bibl/{T}ref[@target]', 'target'), normalize = False)

        # Next feed URI
        #self.feed_uri_next = 

        # Catalog URI
        #self.catalog_uri = 

        # Same as catalog
        #self.catalog_uri_same = 

        # Date modified
        self.modified_date = Date(self.xml_first_attribute('.//{T}teiHeader/{T}fileDesc/{T}publicationStmt/{T}date[@when]', 'when'))

        # Element URIs
        self.element_uris = UriList(self.xml_all_attributes('.//{T}teiHeader/{T}profileDesc/{T}correspDesc[@ref]', 'ref'), normalize = False)

        # Feed elements
        #if self.feed_elements == 
