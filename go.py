# Main scraping run
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from sys import argv

# Import script modules
from base.organise import Organise
from base.job import Job

# Set up logging
logger = logging.getLogger(__name__)


# Set up job and run it
organise = Organise(argv[1:])
job = Job(organise)
