"""Host-neutral field contracts. No raster or host imports at dialog creation."""
from atiaf_core.tool_contract import CATALOG

GROUPS = {
    'Vegetation': ('Vegetation and chlorophyll', 'النبات والكلوروفيل'),
    'Water': ('Surface water', 'المياه السطحية'),
    'Moisture': ('Vegetation moisture', 'رطوبة النبات'),
    'Urban': ('Built-up surfaces', 'المناطق العمرانية'),
    'Soil': ('Bare soil', 'التربة المكشوفة'),
    'Burn': ('Burn', 'الحريق'), 'Snow': ('Snow', 'الثلوج'),
    'Transformation': ('Advanced transformations', 'التحويلات المتقدمة'),
    'Geology': ('Mineral alteration proxies', 'دلائل التحورات المعدنية'),
    'Calculations': ('Calculations', 'الحسابات'),
    'Temperature': ('Surface temperature', 'درجة حرارة السطح'),
    'Manual': ('Manual band mapping', 'تعيين الباندات يدويًا'),
    'Retrieval': ('NDVI-assisted thermal retrieval', 'اشتقاق الحرارة بمساعدة NDVI'),
    'Classification': ('Optional local classification', 'التصنيف المحلي الاختياري'),
}
ROLES = {
    'blue': ('Blue', 'الأزرق'), 'green': ('Green', 'الأخضر'), 'red': ('Red', 'الأحمر'),
    'nir': ('Near infrared', 'الأشعة تحت الحمراء القريبة'),
    'red_edge_1': ('Red edge 1', 'حافة الأحمر الأولى'),
    'red_edge_2': ('Red edge 2', 'حافة الأحمر الثانية'),
    'red_edge_3': ('Red edge 3', 'حافة الأحمر الثالثة'),
    'narrow_nir': ('Narrow NIR', 'القريب ضيق النطاق'),
    'swir_1': ('Shortwave infrared 1', 'الأشعة تحت الحمراء القصيرة الأولى'),
    'swir_2': ('Shortwave infrared 2', 'الأشعة تحت الحمراء القصيرة الثانية'),
    'thermal_1': ('Official surface temperature in Kelvin', 'حرارة سطح رسمية بالكلفن'),
}

def group_name(key, language='en'):
    return GROUPS.get(key, (key, key))[language == 'ar']

def ui_rows(tool):
    if tool == 'surface_temperature':
        return [dict(id='LST', en='Land surface temperature', ar='درجة حرارة سطح الأرض', category='Temperature')]
    return CATALOG[tool]

def fields(tool):
    """(name, type, English, Arabic, default, choices, group, visibility condition)."""
    result = []
    def add(name, kind, en, ar, default=None, choices=None, group='Manual', when='manual_mode'):
        result.append(dict(name=name, kind=kind, en=en, ar=ar, default=default,
                           choices=choices, group=group, when=when))
    add('manual_mode', 'bool', 'Assign available bands manually', 'تعيين الباندات المتاحة يدويًا', False, group=None, when=None)
    add('expert_mapping', 'file', 'Import saved mapping JSON (optional)', 'استيراد تعيين محفوظ بصيغة JSON (اختياري)')
    add('manual_platform', 'str', 'Exact platform (e.g. LANDSAT_8)', 'القمر بالتحديد (مثل LANDSAT_8)')
    add('manual_date', 'str', 'Acquisition date (YYYY-MM-DD)', 'تاريخ الالتقاط (YYYY-MM-DD)')
    add('manual_provenance', 'str', 'Calibration source / provenance', 'مصدر المعايرة وتوثيقها')
    add('manual_scale', 'float', 'Optical reflectance scale (explicit)', 'معامل قياس الانعكاس البصري (صريح)')
    add('manual_offset', 'float', 'Optical reflectance offset (explicit)', 'إزاحة الانعكاس البصري (صريحة)')
    for role, names in ROLES.items():
        add('band_' + role, 'file', names[0] + ' raster (optional)', 'ملف ' + names[1] + ' (اختياري)')
    add('manual_thermal_scale', 'float', 'Official ST scale to Kelvin (explicit)', 'معامل حرارة السطح الرسمية إلى كلفن (صريح)')
    add('manual_thermal_offset', 'float', 'Official ST offset to Kelvin (explicit)', 'إزاحة حرارة السطح الرسمية إلى كلفن (صريحة)')
    add('manual_qa', 'file', 'QA_PIXEL / SCL quality raster (optional)', 'ملف الجودة QA_PIXEL أو SCL (اختياري)')
    if tool == 'surface_temperature':
        add('temperature_unit', 'enum', 'Temperature output unit', 'وحدة إخراج الحرارة', 'Celsius',
            [('Celsius', 'Celsius', 'مئوية'), ('Kelvin', 'Kelvin', 'كلفن')], 'Temperature', None)
        add('ndvi_assisted', 'bool', 'Derive LST using NDVI emissivity and local atmospheric inputs',
            'اشتقاق الحرارة بانبعاثية NDVI ومدخلات غلاف جوي محلية', False, group='Temperature', when=None)
        add('ndvi_file', 'file', 'Existing NDVI raster (optional; otherwise compute red/NIR)',
            'ملف NDVI موجود (اختياري؛ وإلا يحسب من الأحمر والقريب)', group='Retrieval', when='ndvi_assisted')
        add('radiance_file', 'file', 'Calibrated at-sensor thermal radiance raster',
            'راستر الإشعاع الحراري المعاير عند المستشعر', group='Retrieval', when='ndvi_assisted')
        for name, en, ar in [
            ('planck_k1', 'Band Planck K1 (radiance units)', 'ثابت الباند K1 (بوحدات الإشعاع)'),
            ('planck_k2', 'Band Planck K2 (Kelvin)', 'ثابت الباند K2 (كلفن)'),
            ('transmittance', 'Atmospheric transmittance (0 < tau <= 1)', 'نفاذية الغلاف الجوي (أكبر من صفر وحتى 1)'),
            ('upwelling', 'Upwelling radiance (W/m²/sr/µm)', 'الإشعاع الصاعد (واط/م²/ستيراديان/ميكرومتر)'),
            ('downwelling', 'Downwelling radiance (W/m²/sr/µm)', 'الإشعاع الهابط (واط/م²/ستيراديان/ميكرومتر)'),
            ('ndvi_soil', 'Bare-soil NDVI threshold', 'حد NDVI للتربة المكشوفة'),
            ('ndvi_vegetation', 'Full-vegetation NDVI threshold', 'حد NDVI للنبات الكامل'),
            ('emissivity_soil', 'Band soil emissivity (0 < epsilon <= 1)', 'انبعاثية التربة للباند (أكبر من صفر وحتى 1)'),
            ('emissivity_vegetation', 'Band vegetation emissivity (0 < epsilon <= 1)', 'انبعاثية النبات للباند (أكبر من صفر وحتى 1)')]:
            add(name, 'float', en, ar, group='Retrieval', when='ndvi_assisted')
        add('retrieval_provenance', 'str', 'Thermal, NDVI, atmospheric and emissivity sources / assumptions',
            'مصادر وافتراضات الحرارة وNDVI والغلاف الجوي والانبعاثية', group='Retrieval', when='ndvi_assisted')
    if tool == 'spectral_indices':
        add('classify_ndvi', 'bool', 'Save optional local NDVI greenness classes', 'حفظ تصنيف محلي اختياري لخضرة NDVI',
            False, group='Classification', when=None)
        add('ndvi_breaks', 'str', 'NDVI class breaks (comma-separated, ascending)', 'حدود فئات NDVI (بفواصل وبترتيب تصاعدي)',
            '0.2,0.4,0.6', group='Classification', when='classify_ndvi')
        add('classification_basis', 'str', 'Local classification justification / validation basis',
            'مبرر التصنيف المحلي وأساس التحقق', group='Classification', when='classify_ndvi')
    return result

def selected_ui(tool, values):
    return [r['id'] for r in ui_rows(tool) if values.get('calc_' + r['id'])]
