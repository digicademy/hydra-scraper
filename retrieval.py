# Retrieve Data from an API
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


def retrieveApiLists( formatParser:str, formatFolder:str, formatUrl:str ) -> list:
    '''
    Retrieves and paginates through API lists, saves them, and returns a beacon list

        Parameters:
            formatParser (str): Name od the parser to use
            formatFolder (str): Name of the folder to save data to
            formatUrl (str): Entry-point URL
        
        Returns:
            list: Beacon list containing item URLs generated from the API calls
    '''

    # Download list file
    # Save the file
    # Get data for the beacon
    # Repeat
    # Return the beacon list

    listContent = downloadFile( format[2] )
    saveFile( format[1] + '/' +  )