# Retrieve and extract data from Beacon files or plain-text URI lists
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from re import search

# Import script modules
from base.data import Uri, UriList, Date
from base.file import strip_lines
from base.extract import ExtractFeedInterface


class Feed(ExtractFeedInterface):


    def retrieve(self):
        '''
        Extract feed data from Beacon files or plain-text URI lists
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

        # Date modified
        self.modified_date = Date(self.beacon_info('TIMESTAMP'))

        # Element URIs
        self.element_uris = UriList(self.beacon_uris(), normalize = False)

        # Feed elements
        #if self.feed_elements == 


    def beacon_info(self, pattern:str) -> str|None:
        '''
        Retrieve information from Beacon headers

            Parameters:
                pattern (str): RegEx pattern to find

            Returns:
                str|None: Requested information
        '''

        # Find match
        regex = r"(?<=#" + pattern + ":).*(?<!\n)"
        match = search(regex, self.file.text)
        if match:
            return match.group().strip()
        else:
            return None


    def beacon_uris(self) -> list:
        '''
        Retrieve URIs from Beacon files and plain-text URI lists

            Returns:
                list: URIs listed in Beacon or plain-text files
        '''

        # Identify and check the ID pattern if provided
        pattern = self.beacon_info('TARGET')
        if pattern:
            if pattern.find('{ID}') == -1:
                pattern = None

        # Remove empty lines and comments
        lines = strip_lines(self.file.text)
        lines = lines.splitlines()

        # In each line, remove additional Beacon features
        for i in range(len(lines)):
            line_option1 = lines[i].find(' |')
            line_option2 = lines[i].find('|')
            if line_option1 != -1:
                lines[i] = lines[i][:line_option1]
            elif line_option2 != -1:
                lines[i] = lines[i][:line_option2]

            # Resolve ID pattern
            if pattern:
                lines[i] = pattern.replace('{ID}', lines[i])

        # Return unique results
        return list(set(lines))
