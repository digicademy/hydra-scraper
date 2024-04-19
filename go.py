# Main script
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from sys import argv

# Import script modules
from classes.command import *
from classes.morph import *
from classes.output import *
from classes.report import *
from classes.retrieve import *


# Set up config and reporting
command = HydraCommand(argv)
report = HydraReport(command.quiet)

#

list = HydraRetrieveList() # read, save, _remove_blank_lines
file = HydraRetrieveFile() # read, save, morph, _morph_lido_to_nfdi
graph = HydraRetrieveGraph() # read, save, morph, _morph_cgif_to_nfdi

#

# Produce final report
report.finish()
