# Entry-point script
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


# Collect configuration info
command = HydraCommand(argv)

#report = HydraReport()
#morph = HydraMorph(command)
#output = HydraOutput(command)

# Run main retrieval job
#retrieve = HydraRetrieve(command, output, report, morph)
