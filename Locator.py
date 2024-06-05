class Locator():
  '''A class for localizing intracranial contacts.  To obtain a list of
     contact labels matched to each region, one can use this like:

       Locator(None).hippocampus_regions
     
     Available region lists are (note, some are subsets of others!):
     hippocampus_regions, mtl_regions, ltc_regions, temporal_regions,
     pfc_regions, cingulate_regions, parietal_regions, other_regions.

     To obtain a boolean mask of pairs, you pass a reader for a session
     in, and can use one of these approaches:

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

     Available functions for returning region specific matches:
       Hippocampus, MTL, LTC, Temporal, PFC, Cingulate, Parietal.
     Also each of those with Left or Right like LeftMTL or RightMTL.

     Don't know what you're doing but need three regions?  Try MTL, LTC,
     and PFC.  Don't know what you're doing but need five regions?  Try
     MTL, LTC, PFC, Cingulate, and Parietal.

     The call Locator(reader).All() returns a list of the
     "best available" labels for every pair.'''

  __version__ = '2024.06.05'

  def __init__(self, reader):
    '''Throws an exception from reader.load('pairs') if pairs.json does
       not exist.'''
    self.reader = reader
    self.hippocampus_regions = \
        ['CA1', 'CA2', 'CA3', 'CA4', 'Hippocampal', 'Hippocampus', 'Sub',
         'DG', 'ba35', 'ba35', '"dg"', '"ca1"', '"sub"', '"ba35"', '"ba35"']
    self.mtl_regions = \
        [*self.hippocampus_regions, 'prc', 'ec', 'phc', 'mtl wm', 'amy',
         'parahippocampal', 'entorhinal', 'temporalpole', 'amygdala',
         'ent entorhinal area', 'hippocampus', 'phg parahippocampal gyrus',
         'tmp temporal pole', '"erc"', '"phc"', 'erc']
    self.ltc_regions = \
        ['middle temporal gyrus', 'stg', 'mtg', 'itg',
         'inferior temporal gyrus', 'superior temporal gyrus', 'tc',
         'bankssts', 'middletemporal', 'inferiortemporal', 'superiortemporal',
         'itg inferior temporal gyrus', 'mtg middle temporal gyrus',
         'stg superior temporal gyrus']
    self.temporal_regions = \
        [*self.mtl_regions, *self.ltc_regions, 'fusiform gyrus wm',
         'fusiform', 'transversetemporal']
    self.pfc_regions = \
        ['caudal middle frontal cortex', 'dlpfc', 'precentral gyrus',
         'precentral gyrus', 'superior frontal gyrus',
         'mfg middle frontal gyrus',
         'trifg triangular part of the inferior frontal gyrus',
         'caudalmiddlefrontal', 'frontalpole', 'lateralorbitofrontal',
         'medialorbitofrontal', 'parsopercularis', 'parsorbitalis',
         'parstriangularis', 'rostralmiddlefrontal', 'superiorfrontal']
    self.cingulate_regions = \
        ['mcg', 'acg', 'pcg', 'caudalanteriorcingulate',
         'isthmuscingulate', 'posteriorcingulate',
         'rostralanteriorcingulate']
    self.parietal_regions = \
        ['supramarginal gyrus', 'supramarginal gyrus', 'inferiorparietal',
         'postcentral', 'precuneus', 'superiorparietal',
         'supramarginal']
    self.other_regions = \
        ['precentral gyrus', 'none', 'insula', 'precentral gyrus', 'nan',
         'misc', 'insula', 'precentral', 'paracentral', 'inf lat vent'
         'cerebral white matter', 'lateral ventricle']

    if reader is not None:
      self.__locations = self.__LoadLocations()


  def __LoadLocations(self):
    def SetIfValid(reg, ri):
      if not isinstance(reg, str):
        return
      reg = reg.strip()
      if reg in ['unknown', 'misc', 'None', 'nan', '']:
        return
      locations[ri] = reg

    def UpdateLocations(regionlabel):
      if regionlabel in pairs.columns:
        for ri in range(chan_cnt):
          if locations[ri] is not None:
            continue
          reg = pairs[regionlabel][ri]
          SetIfValid(reg, ri)

    pairs = self.reader.load('pairs')
    chan_cnt = len(pairs)
    locations = [None for _ in range(chan_cnt)]

    UpdateLocations('stein.region')
    UpdateLocations('das.region')

    try:
      locjson = self.reader.load('localization')
      whbr = locjson.loc['contacts']['atlases.whole_brain']

      # Match pairs to contacts that are both in the same region
      labels = self.reader.load('pairs').label
      if len(labels) != chan_cnt:
        raise IndexError('label mismatch')
      for ri in range(chan_cnt):
        if locations[ri] is not None:
          continue
        label = labels[ri]
        spl = label.split('-')
        if spl[0] in whbr.keys() and spl[1] in whbr.keys():
          if whbr[spl[0]] == whbr[spl[1]]:
            reg = whbr[spl[0]]
            SetIfValid(reg, ri)
    except:
      pass

    UpdateLocations('mni.region')
    UpdateLocations('ind.region')

    locations = [s.strip() if isinstance(s, str) else None for s in locations]

    return locations


  def All(self):
    '''Returns a list of the best available localizations for each channel
       in reader.load('pairs').  Prioritization goes in order of
       stein.region, das.region, load('localization') when both contacts
       are in the same region, mni.region, ind.region.'''
    return [s for s in self.__locations]


  def Matching(self, regions):
    '''Returns a boolean mask of reader.load('pairs') channels exactly
       matching the giving regions, case insensitive, and ignoring outer
       whitespace.'''
    if isinstance(regions, str):
      regions = [regions]
    valid = [s.lower().strip() for s in regions]
    locarr = [s.lower().strip() in valid \
      if isinstance(s, str) else False for s in self.__locations]
    return locarr


  def Regions(self, regions):
    '''Returns a boolean mask of left or right reader.load('pairs') channels in
       the given regions.'''
    if regions is None:
      return [True for s in self.__locations]
    if isinstance(regions, str):
      regions = [regions]
    bothsides = [s for s in regions]
    bothsides.extend('Left '+s for s in regions)
    bothsides.extend('Right '+s for s in regions)
    return self.Matching(bothsides)


  def LeftRegions(self, regions):
    '''Returns a boolean mask of left reader.load('pairs') channels in
       the given regions.'''
    if isinstance(regions, str):
      regions = [regions]
    return self.Matching(['Left '+s for s in regions])


  def RightRegions(self, regions):
    '''Returns a boolean mask of right reader.load('pairs') channels in
       the given regions.'''
    if isinstance(regions, str):
      regions = [regions]
    return self.Matching(['Right '+s for s in regions])


  def Hippocampus(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       hippocampus.'''
    return self.Regions(self.hippocampus_regions)


  def LeftHippocampus(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       left hippocampus.'''
    return self.LeftRegions(self.hippocampus_regions)


  def RightHippocampus(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       right hippocampus.'''
    return self.RightRegions(self.hippocampus_regions)


  def MTL(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       Medial Temporal Lobe.'''
    return self.Regions(self.mtl_regions)


  def LeftMTL(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       left Medial Temporal Lobe.'''
    return self.LeftRegions(self.mtl_regions)


  def RightMTL(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       right Medial Temporal Lobe.'''
    return self.RightRegions(self.mtl_regions)


  def LTC(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       Lateral Temporal Cortex.'''
    return self.Regions(self.ltc_regions)


  def LeftLTC(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       left Lateral Temporal Cortex.'''
    return self.LeftRegions(self.ltc_regions)


  def RightLTC(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       right Lateral Temporal Cortex.'''
    return self.RightRegions(self.ltc_regions)


  def Temporal(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       Temporal Lobe.'''
    return self.Regions(self.temporal_regions)


  def LeftTemporal(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       left Temporal Lobe.'''
    return self.LeftRegions(self.temporal_regions)


  def RightTemporal(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       right Temporal Lobe.'''
    return self.RightRegions(self.temporal_regions)


  def PFC(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       Prefrontal Cortex.'''
    return self.Regions(self.pfc_regions)


  def LeftPFC(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       left Prefrontal Cortex.'''
    return self.LeftRegions(self.pfc_regions)


  def RightPFC(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       right Prefrontal Cortex.'''
    return self.RightRegions(self.pfc_regions)


  def Cingulate(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       Cingulate Cortex.'''
    return self.Regions(self.cingulate_regions)


  def LeftCingulate(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       left Cingulate Cortex.'''
    return self.LeftRegions(self.cingulate_regions)


  def RightCingulate(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       right Cingulate Cortex.'''
    return self.RightRegions(self.cingulate_regions)


  def Parietal(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       Parietal Lobe.'''
    return self.Regions(self.parietal_regions)


  def LeftParietal(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       left Parietal Lobe.'''
    return self.LeftRegions(self.parietal_regions)


  def RightParietal(self):
    '''Returns a boolean mask of reader.load('pairs') channels in the
       right Parietal Lobe.'''
    return self.RightRegions(self.parietal_regions)

