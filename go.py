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
from classes.hydrafetch import *
from classes.hydramunch import *
from classes.hydraoutput import *
from classes.hydrareport import *


# Collect configuration info
command = HydraCommand(argv[1:])

# Set up helper objects
report = HydraReport(command)
munch = HydraMunch(command)
output = HydraOutput(command)

# Run main fetch job
fetch = HydraFetch(command, output, report, munch)
