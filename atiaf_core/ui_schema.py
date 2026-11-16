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
    'Composites': ('RGB composition methods', 'طرق التراكيب اللونية'),
    'CompositeSettings': ('RGB channels and presets', 'قنوات RGB والتركيبات المحفوظة'),
    'Display': ('Display and temporary preview', 'العرض والمعاينة المؤقتة'),
    'Stack': ('Explicit multiband input', 'إدخال متعدد الباندات بتعيين صريح'),
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
    if tool == 'geological_composites':
        return [r for r in CATALOG[tool] if r['id'] in ('DIRECT_RGB', 'RATIO_RGB')]
    return CATALOG[tool]

def fields(tool):
    """(name, type, English, Arabic, default, choices, group, visibility condition)."""
    result = []
    def add(name, kind, en, ar, default=None, choices=None, group='Manual', when='manual_mode'):
        result.append(dict(name=name, kind=kind, en=en, ar=ar, default=default,
                           choices=choices, group=group, when=when))
    if tool == 'geological_composites':
        from atiaf_core.composites.registry import PRESETS
        def field(name,kind,en,ar,default=None,choices=None,group='CompositeSettings',when=None):
            add(name,kind,en,ar,default,choices,group,when)
        field('direct_preset','enum','Direct RGB preset','التركيب المباشر المحفوظ','AUTO',
            [('AUTO','Sensor default','افتراضي حسب المستشعر')]+[(p['id'],p['en'],p['ar']) for p in PRESETS if p['method']=='DIRECT_RGB'])
        field('ratio_preset','enum','Ratio RGB preset','تركيب النسب المحفوظ','AUTO',
            [('AUTO','Sensor default','افتراضي حسب المستشعر')]+[(p['id'],p['en'],p['ar']) for p in PRESETS if p['method']=='RATIO_RGB'])
        field('direct_channels','str','Manual direct R;G;B (e.g. B7;B5;B3)','الباندات المباشرة للقنوات R;G;B (مثل B7;B5;B3)')
        field('ratio_channels','str','Custom ratio R;G;B expressions','معادلات النسب المخصصة للقنوات R;G;B')
        field('custom_source','str','Custom preset reference / local justification','مرجع التركيب المخصص أو مبرره المحلي')
        field('preset_file','file','Import saved composite preset JSON (optional)','استيراد تركيب محفوظ بصيغة JSON (اختياري)')
        field('restore_preset_display','bool','Restore saved display bounds and settings','استعادة حدود العرض وإعداداته المحفوظة',False)
        field('allow_experimental','bool','Allow clearly labeled experimental presets','السماح بالتركيبات الموسومة تجريبية',False)
        field('allow_toa','bool','Allow calibrated TOA (no atmospheric correction)','السماح بانعكاس TOA المعاير (دون تصحيح جوي)',False)
        field('ratio_epsilon','float','Minimum absolute ratio denominator','أصغر قيمة مطلقة لمقام النسبة',1e-8)
        field('display_mode','enum','Color enhancement','تحسين العرض اللوني','balanced',[
            ('quiet','Quiet','هادئ'),('balanced','Balanced','متوازن'),('enhanced','Enhanced','قوي'),('custom','Custom','مخصص')],group='Display')
        field('display_clip','float','Custom percent clip per tail','نسبة القص المخصصة لكل طرف',2.,group='Display')
        field('stretch_method','enum','Display stretch method','طريقة تمديد العرض','percentile',[
            ('percentile','Percentile','المئينات'),('linear','Linear minimum to maximum','خطي من الأدنى إلى الأعلى'),
            ('stddev','Mean plus/minus standard deviations','المتوسط وعدد الانحرافات المعيارية')],group='Display')
        field('display_stddev','float','Standard deviation multiplier','عدد الانحرافات المعيارية',2.,group='Display')
        field('display_gamma','float','Custom gamma','جاما المخصصة',1.,group='Display')
        field('display_saturation','float','Custom saturation (0 to 3)','التشبع المخصص (من 0 إلى 3)',1.,group='Display')
        field('display_limits','str','Fixed Rmin,Rmax,Gmin,Gmax,Bmin,Bmax (optional)','حدود ثابتة Rmin,Rmax,Gmin,Gmax,Bmin,Bmax (اختياري)',group='Display')
        field('save_display','bool','Save separate display RGB GeoTIFF','حفظ GeoTIFF منفصل للعرض الملون',True,group='Display')
        field('save_intermediates','bool','Save individual analytical channels in Work','حفظ القنوات التحليلية منفردة في Work',False,group='Display')
        field('preview_only','bool','Temporary before/after preview only (no final rasters)','معاينة مؤقتة قبل وبعد فقط (دون راستر نهائي)',False,group='Display')
        field('stack_mode','bool','Use an explicitly mapped multiband raster','استخدام راستر متعدد الباندات بتعيين صريح',False,group=None)
        for name,en,ar in [('stack_raster','Multiband raster','الراستر متعدد الباندات'),
            ('stack_band_ids','Scientific IDs in file order, comma-separated','معرفات الباندات العلمية بترتيب الملف وبفواصل'),
            ('stack_scales','Explicit scale(s), comma-separated','معاملات القياس الصريحة مفصولة بفواصل'),
            ('stack_offsets','Explicit offset(s), comma-separated','الإزاحات الصريحة مفصولة بفواصل'),
            ('stack_date','Acquisition date (YYYY-MM-DD)','تاريخ الالتقاط (YYYY-MM-DD)'),
            ('stack_provenance','Calibration / sensor / product provenance','توثيق المعايرة والمستشعر ومستوى المنتج')]:
            field(name,'file' if name=='stack_raster' else 'str',en,ar,group='Stack',when='stack_mode')
        field('stack_level','enum','Physical reflectance level','مستوى الانعكاس الفيزيائي','surface_reflectance',[
            ('surface_reflectance','Surface reflectance','انعكاسية سطحية'),('toa_reflectance','TOA reflectance','انعكاسية أعلى الغلاف الجوي')],group='Stack',when='stack_mode')
        return result
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
    if tool in ('spectral_indices', 'geological_analysis'):
        add('allow_toa','bool','Allow diagnostic calculations from calibrated TOA (not surface reflectance)',
            'السماح بالحسابات التشخيصية من TOA المعاير (ليس انعكاسًا سطحيًا)',False,group='Calculations',when=None)
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
