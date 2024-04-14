# Entry-point script
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from sys import argv

# Import script modules
from classes.hydracommand import *
from classes.hydramorph import *
from classes.hydraoutput import *
from classes.hydrareport import *
from classes.hydraretrieve import *


# Collect configuration info
command = HydraCommand(argv)

# Set up helper objects
report = HydraReport(command)
#morph = HydraMorph(command)
#output = HydraOutput(command)

# Run main retrieval job
#retrieve = HydraRetrieve(command, output, report, morph)
