# Locator

A class for localizing intracranial contacts into regions with cmlreaders.

Installation
------------

git clone this repository, then:
  ```bash
  pip install -e Locator
  ```

Usage
------------
To obtain a list of contact labels matched to each region, one can use this
like:

  ```python
  from Locator import Locator
  Locator(None).hippocampus_regions
  ```
     
Available region lists are (note, some are subsets of others!):
- hippocampus\_regions
- mtl\_regions
- ltc\_regions
- temporal\_regions
- pfc\_regions,
- cingulate\_regions
- parietal\_regions
- other\_regions.

To obtain a boolean mask of pairs, you pass a reader for a session in, and
can use one of these approaches:

  ```python
  # Matches left, right, or unspecified side.
  mask = Locator(reader).Hippocampus()
  mask = Locator(reader).LeftHippocampus()

  # e.g., you can store this list in your settings, to write
  # generic code that processes many regions, switched by settings.
  regions = Locator(None).hippocampus_regions
  # Regions by default matches left, right, or unspecified side.
  mask = Locator(reader).Regions(regions)
  mask = Locator(reader).RightRegions(regions)

  mask = Locator(reader).Matching(['left CA1', 'right CA3'])
  ```

Available class functions for returning region specific matches:
- Hippocampus
- MTL
- LTC
- Temporal
- PFC
- Cingulate
- Parietal

Also each of those with Left or Right like LeftMTL or RightMTL.

Don't know what you're doing but need three regions?  Try MTL, LTC, and PFC.
Don't know what you're doing but need five regions?  Try MTL, LTC, PFC,
Cingulate, and Parietal.

The call Locator(reader).All() returns a list of the "best available"
labels for every pair.

