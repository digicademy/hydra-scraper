# Classes to provide nfdicore/cto objects

The [cto.py](cto.py) library file provides two classes `Feed` and `FeedElement` that automatically create the right feed and element triples in accordance with nfdicore 2.0.0 and cto 2.2.0. The goal is to normalise various types of inputs for the available parameters and return properly typed, valid triples. The file [cto_sample.py](cto_sample.py) illustrates the use of these objects.

## Roadmap

- Possibly turn the library file into a component available via PIP
- Identify a simple way to generate the schema.org lists and possibly turn them into their own file
