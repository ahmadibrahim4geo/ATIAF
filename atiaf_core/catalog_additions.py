"""Independent formula definitions; no remote catalog/code imported."""
DEFINITIONS = [
    dict(id='EVI2', en='Two-band Enhanced Vegetation Index (2.5/2.4 variant)', ar='مؤشر الغطاء النباتي المحسن بباندين (صيغة 2.5 و2.4)', category='Vegetation',
         formula='2.5 * (NIR - Red) / (NIR + 2.4 * Red + 1)', roles=['nir','red'],
         citation='Jiang et al. (2008), doi:10.1016/j.rse.2008.06.006; NOAA NDE Vegetation Products ATBD v4.0 (2018), Eq.3.6',
         source_url='https://www.ospo.noaa.gov/Products/documents/GVF_ATBD_V4.0.pdf'),
    dict(id='NIRv', en='Near-infrared reflectance of vegetation (unadjusted NDVI product)', ar='انعكاس القريب للنبات (حاصل ضرب NDVI دون تعديل)', category='Vegetation',
         formula='NIR * (NIR - Red) / (NIR + Red)', roles=['nir','red'],
         citation='Badgley et al. (2017), Canopy near-infrared reflectance and terrestrial photosynthesis, doi:10.1126/sciadv.1602244',
         source_url='https://doi.org/10.1126/sciadv.1602244'),
]
