# File Input and Output
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


# TODO

# Variables
requestInfo = ''
requestInfoSubinfo = ''
requestInfoSeparator = ', '
requestInfoBeginning = 'Requested: '

# Add 'beacon' string if applicable
if 'beacon-json' in requests or 'beacon-rdf' in requests or 'beacon-ttl' in requests or 'beacon-cgif' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'beacon ('

    # Go through individual 'beacon' formats
    if 'beacon-json' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'JSON-LD'
    if 'beacon-rdf' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'RDF'
    if 'beacon-ttl' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'TTL'
    if 'beacon-cgif' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CGIF'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Add 'listdump' string if applicable
if 'listdump-json' in requests or 'listdump-rdf' in requests or 'listdump-ttl' in requests or 'listdump-cgif' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'list dump ('

    # Go through individual 'dump' formats
    if 'listdump-json' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'JSON-LD'
    if 'listdump-rdf' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'RDF'
    if 'listdump-ttl' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'TTL'
    if 'listdump-cgif' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CGIF'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Add 'dump' string if applicable
if 'dump-json' in requests or 'dump-rdf' in requests or 'dump-ttl' in requests or 'dump-cgif' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'dump ('

    # Go through individual 'dump' formats
    if 'dump-json' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'JSON-LD'
    if 'dump-rdf' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'RDF'
    if 'dump-ttl' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'TTL'
    if 'dump-cgif' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CGIF'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Add 'table' string if applicable
if 'table-csv' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'table ('

    # Go through individual 'table' formats
    if 'table-csv' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CSV'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Output the info string
print( requestInfoBeginning + requestInfo )