# Standard data types for mappings
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date, datetime
from rdflib import Namespace
from rdflib.term import Literal, URIRef, _is_valid_uri
from urllib.parse import quote, unquote

# Define namespaces
from rdflib.namespace import OWL, RDF, RDFS, XSD
NFDICORE = Namespace('https://nfdi.fiz-karlsruhe.de/ontology/')
CTO = Namespace('https://nfdi4culture.de/ontology#')
MO = Namespace('http://purl.org/ontology/mo/')
N4C = Namespace('https://nfdi4culture.de/id/')
GN = Namespace('http://sws.geonames.org/')
IC = Namespace('https://iconclass.org/')
AAT = Namespace('http://vocab.getty.edu/aat/')
GND = Namespace('https://d-nb.info/gnd/')
WD = Namespace('http://www.wikidata.org/entity/')
VIAF = Namespace('http://viaf.org/viaf/')
RISM = Namespace('https://rism.online/')
FG = Namespace('https://database.factgrid.de/entity/')
ISIL = Namespace('https://ld.zdb-services.de/resource/organisations/')
SCHEMA = Namespace('http://schema.org/')


class Uri:


    def __init__(self, uri:str|Literal|URIRef|None = None, normalize:bool = True):
        '''
        Generic URI node

            Parameters:
                uri (str|Literal|URIRef|None): Input to build the URI
                normalize (bool): Whether to normalize URI quirks
        '''

        # Content vars
        self.uri:str|None = None

        # Save URIRef
        if isinstance(uri, URIRef):
            if _is_valid_uri(str(uri)):
                if normalize:
                    self.uri = clean_namespaces(str(uri))
                else:
                    self.uri = str(uri)

        # Save Literal
        elif isinstance(uri, Literal):
            if _is_valid_uri(str(uri)):
                if normalize:
                    self.uri = clean_namespaces(str(uri))
                else:
                    self.uri = str(uri)

        # Save str
        elif isinstance(uri, str):
            if _is_valid_uri(str(uri)):
                if normalize:
                    self.uri = clean_namespaces(uri)
                else:
                    self.uri = uri


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if self.uri:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if self.uri:
            return 'URI: ' + self.uri
        else:
            return 'Empty URI'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if self.uri:
            return self.uri
        else:
            return ''


    def rdflib(self) -> URIRef|None:
        '''
        Return data as an RDFLib class

            Returns:
                URIRef|None: URI node
        '''

        # Return content
        if self.uri:
            return URIRef(self.uri)
        else:
            return None


class UriList:


    def __init__(self, uris:list|str|Literal|URIRef|None = None, normalize:bool = True):
        '''
        List of generic URI nodes

            Parameters:
                uris (list|str|Literal|URIRef|None): Input to build the URI nodes
                normalize (bool): Whether to normalize URI quirks
        '''

        # Content vars
        self.uris:list = []

        # Turn input into list if necessary
        if isinstance(uris, (str, URIRef, Literal)):
            uris = [uris]

        # Go through list
        if uris:
            for uri in uris:
                uri = Uri(uri, normalize)
                if uri:
                    self.uris.append(uri)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if len(self.uris) > 0:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if len(self.uris) > 0:
            return '[' + ', '.join(str(i) for i in self.uris) + ']'
        else:
            return 'Empty URI list'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if len(self.uris) > 0:
            return ', '.join(i.text() for i in self.uris)
        else:
            return ''


    def rdflib(self) -> list:
        '''
        Return data as an RDFLib class

            Returns:
                list: List of URI nodes
        '''

        # Return content
        if len(self.uris) > 0:
            return [uri.rdflib() for uri in self.uris]
        else:
            return []


class Label:


    def __init__(self, label:str|Literal|URIRef|None = None, data_type:str|Literal|URIRef|None = None):
        '''
        Generic string literal node

            Parameters:
                label (str|Literal|URIRef|None): Input to build the string literal
                data_type (str|Literal|URIRef|None): Data type of the literal
        '''

        # Content vars
        self.label:str|None = None
        self.language:str|None = None
        self.data_type:Uri = Uri()

        # Save URIRef
        if isinstance(label, URIRef):
            if label:
                if str(label) != '':
                    self.label = str(label)

        # Save Literal
        elif isinstance(label, Literal):
            if label:
                if str(label) != '':
                    self.label = str(label)
                    if label.language:
                        self.language = label.language

        # Save str
        elif isinstance(label, str):
            if label and label != '':
                self.label = label

        # Save data type
        if data_type:
            self.data_type = Uri(data_type)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if self.label:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if self.label:
            output = 'Label: ' + self.label
            if self.language or self.data_type:
                output += ' ('
                if self.language:
                    output += self.language
                if self.data_type:
                    if self.language:
                        output += ', '
                    output += self.data_type
                output += ')'
            return output
        else:
            return 'Empty label'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if self.label:
            output = self.label
            if self.language:
                output += ' (' + self.language + ')'
            return output
        else:
            return ''


    def rdflib(self) -> Literal|None:
        '''
        Return data as an RDFLib class

            Returns:
                Literal|None: String literal node
        '''

        # Return content
        if self.label and self.language and self.data_type:
            return Literal(self.label, lang = self.language, datatype = self.data_type)
        elif self.label and self.language:
            return Literal(self.label, lang = self.language)
        elif self.label and self.data_type:
            return Literal(self.label, datatype = self.data_type)
        elif self.label:
            return Literal(self.label)
        else:
            return None


class LabelList:


    def __init__(self, labels:list|str|Literal|URIRef|None = None, data_type:str|Literal|URIRef|None = None):
        '''
        List of generic string literal nodes

            Parameters:
                labels (list|str|Literal|URIRef|None): Input to build the string literals
                data_type (str|Literal|URIRef|None): Data type of the literals
        '''

        # Content vars
        self.labels:list = []

        # Turn input into list if necessary
        if isinstance(labels, (str, URIRef, Literal)):
            labels = [labels]

        # Go through list
        if labels:
            for label in labels:
                label = Label(label, data_type)
                if label:
                    self.labels.append(label)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if len(self.labels) > 0:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if len(self.labels) > 0:
            return '[' + ', '.join(str(i) for i in self.labels) + ']'
        else:
            return 'Empty label list'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if len(self.labels) > 0:
            return ', '.join(i.text() for i in self.labels)
        else:
            return ''


    def rdflib(self) -> list:
        '''
        Return data as an RDFLib class

            Returns:
                list: List of string literal nodes
        '''

        # Return content
        if len(self.labels) > 0:
            return [label.rdflib() for label in self.labels]
        else:
            return []


class UriLabel:


    def __init__(self, uri:str|Literal|URIRef|None = None, labels:list|str|Literal|URIRef|None = None, combined:str|tuple|Literal|URIRef|None = None):
        '''
        Combined node of a URI and a list of string literals

            Parameters:
                uri (str|Literal|URIRef|None): Input to build the URI
                labels (list|str|Literal|URIRef|None): Input to build the string literals
                combined (str|tuple|Literal|URIRef|None): Input to build URI, string literals, or both
        '''

        # Content vars
        self.uri:Uri = Uri()
        self.labels:LabelList = LabelList()

        # Save combined input
        if combined:

            # URI is URI
            if isinstance(combined, URIRef):
                self.uri = Uri(combined)

            # Literal and string may be URI or label
            if isinstance(combined, Literal):
                if _is_valid_uri(str(combined)):
                    self.uri = Uri(str(combined))
                else:
                    self.labels = LabelList(combined)
            if isinstance(combined, str):
                if _is_valid_uri(combined):
                    self.uri = Uri(combined)
                else:
                    self.labels = LabelList(combined)

            # Tuples should be clear
            if isinstance(combined, tuple):
                if len(combined) == 2:
                    if combined[0]:
                        self.uri = Uri(combined[0])
                    if combined[1]:
                        self.labels = LabelList(combined[1])

        # Save URI and labels
        else:
            if uri:
                self.uri = Uri(uri)
            if labels:
                self.labels = LabelList(labels)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if self.uri or self.labels:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if self.uri or self.labels:
            return '<' + str(self.uri) + ', ' + str(self.labels) + '>'
        else:
            return 'Empty URI and label'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if self.uri and self.labels:
            return self.uri.text() + ' (' + self.labels.text() + ')'
        elif self.uri:
            return self.uri.text()
        elif self.labels:
            return self.labels.text()
        else:
            return ''


    def rdflib(self) -> tuple|None:
        '''
        Return data as an RDFLib class

            Returns:
                tuple: Tuple of URI node and string literal nodes
        '''

        # Return content
        if self.uri and self.labels:
            return (self.uri.rdflib(), self.labels.rdflib())
        elif self.uri:
            return (self.uri.rdflib(), None)
        elif self.labels:
            return (None, self.labels.rdflib())
        else:
            return None


class UriLabelList:


    def __init__(self, uri_labels:list|str|tuple|Literal|URIRef|None = None):
        '''
        List of combined nodes of a URI and a list of string literals

            Parameters:
                uri_labels (list|str|tuple|Literal|URIRef|None): Input to build the combined URI node and string literal nodes
        '''

        # Content vars
        self.uri_labels:list = []

        # Turn input into list if necessary
        if isinstance(uri_labels, (str, tuple, URIRef, Literal)):
            uri_labels = [uri_labels]

        # Go through list
        if uri_labels:
            for uri_label in uri_labels:
                uri_label = UriLabel(combined = uri_label)
                if uri_label:
                    self.uri_labels.append(uri_label)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if len(self.uri_labels) > 0:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if len(self.uri_labels) > 0:
            return '[' + ', '.join(str(i) for i in self.uri_labels) + ']'
        else:
            return 'Empty URI and label list'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if len(self.uri_labels) > 0:
            return ', '.join(i.text() for i in self.uri_labels)
        else:
            return ''


    def rdflib(self) -> list:
        '''
        Return data as an RDFLib class

            Returns:
                list: List of combined URI node and string literal nodes
        '''

        # Return content
        if len(self.uri_labels) > 0:
            return [uri_labels.rdflib() for uri_labels in self.uri_labels]
        else:
            return []


class Date:


    def __init__(self, input:date|datetime|int|str|Literal|None = None):
        '''
        Generic date literal node

            Parameters:
                input (date|datetime|int|str|Literal|None): Input to build the date
        '''

        # Content vars
        self.start:date|None = None
        self.start_time:datetime|None = None
        self.end_time:datetime|None = None
        self.label:Label = Label()

        # Save date
        if isinstance(input, date):
            self.start = input

        # Save datetime
        elif isinstance(input, datetime):
            self.start_time = input

        # Save int (timestamp)
        elif isinstance(input, int):
            self.start_time = datetime.fromtimestamp(input)

        # Save str or Literal
        elif isinstance(input, (str, Literal)):

            # Convert Literal to str
            if isinstance(input, Literal):
                simple_input = str(input)
            else:
                simple_input = input

            # Split in two if str contains slash
            if '/' in simple_input:
                start_and_end = simple_input.split('/', 1)

                # Check if regular dates or proper datetimes were used
                try:
                    self.start_time = datetime.fromisoformat(start_and_end[0] + 'T00:00:00')
                except ValueError:
                    try:
                        self.start_time = datetime.fromisoformat(start_and_end[0])
                    except ValueError:
                        pass
                try:
                    self.end_time = datetime.fromisoformat(start_and_end[1] + 'T23:59:59')
                except ValueError:
                    try:
                        self.end_time = datetime.fromisoformat(start_and_end[1])
                    except ValueError:
                        pass

                # Save string as backup
                if not self.start_time and not self.end_time:
                    self.label = Label(input)

            # Convert regular str to date or datetime
            else:
                try:
                    self.start = date.fromisoformat(input)
                except ValueError:
                    try:
                        self.start_time = datetime.fromisoformat(input)
                    except ValueError:
                        self.label = Label(input)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if self.start or self.start_time or self.label:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if self.start:
            return 'Date: ' + self.start.strftime('%d/%m/%Y')
        elif self.start_time and self.end_time:
            return self.start_time.strftime('%d/%m/%Y, %H:%M:%S') + ' to ' + self.end_time.strftime('%d/%m/%Y, %H:%M:%S')
        elif self.start_time:
            return 'Date: ' + self.start_time.strftime('%d/%m/%Y, %H:%M:%S')
        elif self.label:
            return str(self.label)
        else:
            return 'Empty date'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if self.start:
            return str(self.start.isoformat())
        elif self.start_time and self.end_time:
            return str(self.start_time.isoformat()) + '/' + str(self.end_time.isoformat())
        elif self.start_time:
            return str(self.start_time.isoformat())
        elif self.label:
            return self.label.text()
        else:
            return ''


    def rdflib(self, allow_string:bool = False) -> Literal|None:
        '''
        Return data as an RDFLib class

            Parameters:
                allow_string (bool): Whether or not to allow for a string literal

            Returns:
                Literal: Date literal node
        '''

        # Return content
        if self.start:
            return Literal(self.start.isoformat(), datatype = XSD.date)
        elif self.start_time and self.end_time:
            return Literal(str(self.start_time.isoformat()) + '/' + str(self.end_time.isoformat()), datatype = SCHEMA.DateTime)
        elif self.start_time:
            return Literal(self.start_time.isoformat(), datatype = XSD.dateTime)
        else:
            if allow_string:
                return self.label.rdflib()
            else:
                return None


class DateList:


    def __init__(self, dates:list|date|datetime|int|str|Literal|None = None):
        '''
        List of generic date literal node

            Parameters:
                dates (list|date|datetime|int|str|Literal|None): Input to build the date literal nodes
        '''

        # Content vars
        self.dates:list = []

        # Turn input into list if necessary
        if isinstance(dates, (date, datetime, int, str, Literal)):
            dates = [dates]

        # Go through list
        if dates:
            for single_date in dates:
                single_date = Date(single_date)
                if single_date:
                    self.dates.append(single_date)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if len(self.dates) > 0:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if len(self.dates) > 0:
            return '[' + ', '.join(str(i) for i in self.dates) + ']'
        else:
            return 'Empty date list'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if len(self.dates) > 0:
            return ', '.join(i.text() for i in self.dates)
        else:
            return ''


    def rdflib(self, allow_string:bool = False) -> list:
        '''
        Return data as an RDFLib class

            Parameters:
                allow_string (bool): Whether or not to allow for a string literal

            Returns:
                list: List of date literal nodes
        '''

        # Return content
        if len(self.dates) > 0:
            return [single_date.rdflib(allow_string) for single_date in self.dates]
        else:
            return []


class Incipit:


    def __init__(self, uri:str|Literal|URIRef|None = None, clef:str|Literal|URIRef|None = None, key_sig:str|Literal|URIRef|None = None, time_sig:str|Literal|URIRef|None = None, pattern:str|Literal|URIRef|None = None):
        '''
        Music incipit node

            Parameters:
                uri (str|Literal|URIRef|None): Input to build the URI
                clef (str|Literal|URIRef|None): Input to build the string literal
                key_sig (str|Literal|URIRef|None): Input to build the string literal
                time_sig (str|Literal|URIRef|None): Input to build the string literal
                pattern (str|Literal|URIRef|None): Input to build the string literal
        '''

        # Content vars
        self.uri:Uri = Uri(uri)
        self.clef:Label = Label(clef)
        self.key_sig:Label = Label(key_sig)
        self.time_sig:Label = Label(time_sig)
        self.pattern:Label = Label(pattern)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        if self.uri or self.clef or self.key_sig or self.time_sig or self.pattern:
            return True
        else:
            return False


    def __str__(self) -> str:
        '''
        String representation of the object
        '''

        # Return string
        if self.uri or self.clef or self.key_sig or self.time_sig or self.pattern:
            return '<' + str(self.uri) + ', ' + str(self.clef) + ', ' + str(self.key_sig) + ', ' + str(self.time_sig) + ', ' + str(self.pattern) + '>'
        else:
            return 'Empty incipit'


    def text(self) -> str:
        '''
        Return data as plain text string
        '''

        # Return string
        if self.uri or self.clef or self.key_sig or self.time_sig or self.pattern:
            output = []
            if self.uri:
                output.append(self.uri.text())
            if self.clef:
                output.append(self.clef.text())
            if self.key_sig:
                output.append(self.key_sig.text())
            if self.time_sig:
                output.append(self.time_sig.text())
            if self.pattern:
                output.append(self.pattern.text())
            return ', '.join(output)
        else:
            return ''


    def rdflib(self) -> dict|None:
        '''
        Return data as an RDFLib class

            Returns:
                dict|None: Music incipit node
        '''

        # Return content
        if self.uri or self.clef or self.key_sig or self.time_sig or self.pattern:
            incipit = {
                'uri': self.uri.rdflib(),
                'clef': self.clef.rdflib(),
                'key_sig': self.key_sig.rdflib(),
                'time_sig': self.time_sig.rdflib(),
                'pattern': self.pattern.rdflib()
            }
            return incipit
        else:
            return None


def clean_namespaces(input:str) -> str:
    '''
    Normalise common 'http' and 'https' mistakes in namespaces of incoming URIs

        Parameters:
            input (str): Variable to check and transform

        Returns:
            str: Clean URIRef
    '''

    # Remove trailing slashes
    if input.endswith('/'):
        input = input[:-1]

    # Avoid known Wikidata issues
    if input.startswith('http://www.wikidata.org/wiki/'):
        input = input.replace('http://www.wikidata.org/wiki/', str(WD), 1)
    elif input.startswith('https://www.wikidata.org/wiki/'):
        input = input.replace('https://www.wikidata.org/wiki/', str(WD), 1)

    # Avoid known Getty AAT issues
    if input.startswith('http://vocab.getty.edu/page/aat/'):
        input = input.replace('http://vocab.getty.edu/page/aat/', str(AAT), 1)
    elif input.startswith('https://vocab.getty.edu/page/aat/'):
        input = input.replace('https://vocab.getty.edu/page/aat/', str(AAT), 1)

    # Avoid known GeoNames issues
    if input.startswith('http://www.geonames.org/'):
        input = input.replace('http://www.geonames.org/', str(GN), 1)
    elif input.startswith('https://www.geonames.org/'):
        input = input.replace('https://www.geonames.org/', str(GN), 1)

    # List namespaces to check
    checks = [
        str(CTO),
        str(MO),
        str(NFDICORE),
        str(OWL),
        str(RDF),
        str(RDFS),
        str(SCHEMA), # Not using SDO here later helps unifying SDO to SCHEMA
        str(XSD),
        str(N4C),
        str(GN),
        str(IC),
        str(AAT),
        str(GND),
        str(WD),
        str(VIAF),
        str(RISM),
        str(FG),
        str(ISIL)
    ]

    # Prepare additional http/https check if not a regular namespace
    found = False
    for check in checks:
        if found == False and check not in input:

            # Switch http and https and test again
            if input.startswith('http://'):
                input_copy = input.replace('http://', 'https://', 1)
                if check in input_copy:
                    input = input_copy
                    found == True
            elif input.startswith('https://'):
                input_copy = input.replace('https://', 'http://', 1)
                if check in input_copy:
                    input = input_copy
                    found == True

    # Avoid known Iconclass issues (i.e., brackets, spaces, and other characters in IRIs)
    if input.startswith(str(IC)):
        index = len(str(IC))
        input_iri = input[index:]
        input_iri_decoded = unquote(input_iri)
        if input_iri == input_iri_decoded:
            input_iri_encoded = quote(input_iri)
            if input_iri != input_iri_encoded:
                input = str(IC) + input_iri_encoded

    # Return URI
    return input
