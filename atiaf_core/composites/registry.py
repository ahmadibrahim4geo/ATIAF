"""Exact scientific band IDs, independently transcribed from cited primary sources.

Source-verified means the formula was checked, not real-product/field validation.
"""
DUWI = 'https://www.nature.com/articles/s41598-024-66199-3'
ASTER_ALERT = 'https://asterweb.jpl.nasa.gov/swir-alert.asp'
ASTER_PAPER = 'https://www.sciencedirect.com/science/article/pii/S1464343X09001071'
SPECTRAL_SOURCES = {
    'LANDSAT_8_9':'https://www.usgs.gov/landsat-missions/landsat-8',
    'SENTINEL_2':'https://s2.pages.eopf.copernicus.eu/msi/s2msi/1.3.0/context.html',
    'ASTER':'https://asterweb.jpl.nasa.gov/content/01_mission/03_instrument/01_Characteristics/default.htm'}
# Nominal approximate centers, never substituted for product-specific spectral response.
CENTERS_NM = {
 'LANDSAT_8_9':dict(B1=443,B2=482,B3=561,B4=655,B5=865,B6=1609,B7=2201,B8=590,B9=1373),
 'SENTINEL_2':dict(B1=443,B2=490,B3=560,B4=665,B5=705,B6=740,B7=783,B8=842,B8A=865,B9=945,B10=1375,B11=1610,B12=2190),
 'ASTER':dict(B1=560,B2=660,B3N=810,B4=1650,B5=2165,B6=2205,B7=2260,B8=2330,B9=2395)}
PRESETS = [
    dict(id='L89_753', sensor='LANDSAT_8_9', method='DIRECT_RGB', channels=['B7','B5','B3'],
         en='Duwi 7-5-3 (source checked)', ar='تركيب ضوي 7-5-3 (مرجعه مراجع)',
         status='source_verified', source=DUWI, source_location='FCC; Figure 3'),
    dict(id='L89_CRC1', sensor='LANDSAT_8_9', method='RATIO_RGB',
         channels=['B6/B7','B6/B2','(B4/B5)*(B6/B5)'],
         en='Duwi ratio composite 1 (source checked)', ar='تركيب نسب ضوي الأول (مرجعه مراجع)',
         status='source_verified', source=DUWI, source_location='CRC; Figure 10'),
    dict(id='L89_CRC2', sensor='LANDSAT_8_9', method='RATIO_RGB', channels=['B4/B6','B4/B2','B6/B7'],
         en='Duwi ratio composite 2 (source checked)', ar='تركيب نسب ضوي الثاني (مرجعه مراجع)',
         status='source_verified', source=DUWI, source_location='CRC; Figure 11'),
    dict(id='L89_762', sensor='LANDSAT_8_9', method='DIRECT_RGB', channels=['B7','B6','B2'],
         en='7-6-2 (experimental)', ar='تركيب 7-6-2 (تجريبي)', status='experimental',
         source='User plan: exploratory composition; no verified lithology claim', source_location='Section 3.1'),
    dict(id='S2_12114', sensor='SENTINEL_2', method='DIRECT_RGB', channels=['B12','B11','B4'],
         en='12-11-4 (experimental)', ar='تركيب 12-11-4 (تجريبي)', status='experimental',
         source='User plan: exploratory composition; no verified lithology claim', source_location='Section 3.1'),
    dict(id='S2_12112', sensor='SENTINEL_2', method='DIRECT_RGB', channels=['B12','B11','B2'],
         en='12-11-2 (experimental)', ar='تركيب 12-11-2 (تجريبي)', status='experimental',
         source='User plan: exploratory composition; no verified lithology claim', source_location='Section 3.1'),
    dict(id='ASTER_468', sensor='ASTER', method='DIRECT_RGB', channels=['B4','B6','B8'],
         en='Historical ASTER 4-6-8 (experimental)', ar='تركيب ASTER التاريخي 4-6-8 (تجريبي)',
         status='experimental', source=ASTER_ALERT, source_location='Validity advisory; composition proposed by user'),
    dict(id='ASTER_FAWAKHEIR', sensor='ASTER', method='RATIO_RGB',
         channels=['(B2+B4)/B3N','(B5+B7)/B6','(B7+B9)/B8'],
         en='Fawakheir ratios (source review pending)', ar='نسب الفواخير (مراجعة المرجع معلقة)',
         status='experimental', source=ASTER_PAPER, source_location='User plan transcription; full text not independently verified'),
]
DEFAULTS = {('LANDSAT_8_9','DIRECT_RGB'):'L89_753', ('LANDSAT_8_9','RATIO_RGB'):'L89_CRC1',
            ('SENTINEL_2','DIRECT_RGB'):'S2_12114', ('ASTER','DIRECT_RGB'):'ASTER_468',
            ('ASTER','RATIO_RGB'):'ASTER_FAWAKHEIR'}
DISCLAIMER = {
 'en':'Continuous false-color spectral imagery; colors do not confirm rock types or mineral deposits. No classification. Source verification is not field validation.',
 'ar':'صورة طيفية مستمرة بألوان تفسيرية؛ الألوان لا تؤكد نوع الصخور أو وجود خام. لا يوجد تصنيف، ومراجعة المرجع ليست تحققًا حقليًا.'}
