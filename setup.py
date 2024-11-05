# Set-up file
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from distutils.core import setup


# Add set-up information
setup(
    name = 'hydra-scraper',
    version = '0.9.2-pre',
    description = 'Comprehensive scraper for paginated APIs, RDF, XML, file dumps, and Beacon files',
    author = 'Jonatan Jalle Steller',
    author_email = 'jonatan.steller@adwmainz.de',
    url = 'https://github.com/digicademy/hydra-scraper',
    #py_modules = [
    #    'go'
    #],
    classifiers = [
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)
