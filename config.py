# Configuration for Specific Scraping Run
# Copyright (C) 2022 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


# Formats to access
formats = [
    [ 'json', 'https://corpusvitrearum.de/id/about.json' ],
    [ 'rdf', 'https://corpusvitrearum.de/id/about.rdf' ],
    [ 'ttl', 'https://corpusvitrearum.de/id/about.ttl' ],
    [ 'cgif', 'https://corpusvitrearum.de/id/about.cgif' ]
]

# List of requests
requests = [
    'beacon and lists',
    'items',
    'table'
]

# Rest period in between API calls in seconds
rest = 0.1


# ITEM SETTINGS ###############################################################


# Use this field as the item's file name
fileNameField = '@id'
fileNameRemove = [
    'https://corpusvitrearum.de/id/',
    '/about.'
]

# Exclude resource items that produce errors
excludeItems = [
    # 'https://corpusvitrearum.de/id/F13073/about.json'
]


# TABLE SETTINGS ##############################################################


# Table headers
header = [
    'ID',
    'Title',
    'State',
    'City',
    'Building',
    'Location ID',
    'Location Latitude',
    'Location Longitude',
    'Date Beginning',
    'Date End',
    'Iconclasses'
]

# Fields to add to the table
fields = [
    '@id',
    'dc:Title',
    'Iptc4xmpExt:ProvinceState',
    'Iptc4xmpExt:City',
    'Iptc4xmpExt:Sublocation',
    'Iptc4xmpExt:LocationId',
    'exif:GPSLatitude',
    'exif:GPSLongitude',
    'cvma:AgeDeterminationStart',
    'cvma:AgeDeterminationEnd',
    'cvma:IconclassNotation'
]

# Search and replace patterns across all fields
cleanUps = [
    [ 'http://iconclass.org/', '' ],
    [ 'https://iconclass.org/', '' ]
]
