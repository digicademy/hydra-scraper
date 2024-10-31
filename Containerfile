# Service container that can run Hydra Scraper
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.

# Get Debian with an up-to-date Python 3
FROM docker.io/library/python:3
RUN apt update

# Set up working directory
WORKDIR /usr/src/hydra-scraper

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy repo into container
COPY . .

# Set container's main executable
ENTRYPOINT [ "python", "./go.py" ]
