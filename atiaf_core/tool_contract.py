"""Dependency-free user tool catalog; dialogs must open without raster libraries."""
import json
from pathlib import Path

CATALOG = json.loads((Path(__file__).parent / 'data' / 'calculations.json').read_text('utf-8'))
from atiaf_core.catalog_additions import DEFINITIONS
CATALOG['spectral_indices'].extend(DEFINITIONS)
TITLES = {
    'spectral_indices': ('01. Spectral Indices', '01. المؤشرات الطيفية'),
    'surface_temperature': ('02. Surface Temperature', '02. درجة حرارة السطح'),
    'thermal_urban': ('03. Thermal & Urban Analysis', '03. التحليل الحراري والعمراني'),
    'environmental_drought': ('04. Environmental & Drought Analysis', '04. التحليل البيئي والجفاف'),
    'geological_analysis': ('05. Geological Analysis & Mineral Alteration', '05. التحليل الجيولوجي ونطاقات التحول المعدني'),
    'temporal_change': ('06. Temporal Analysis & Change Detection', '06. التحليل الزمني ورصد التغير'),
}
SENSORS = ['AUTO', 'LANDSAT_8_9_C2_L2', 'LANDSAT_7_C2_L2', 'LANDSAT_4_5_C2_L2',
           'SENTINEL_2_L2A', 'SENTINEL_2_L1C', 'ASTER_AST_07', 'ASTER_AST_08', 'EXPERT']
EXTRA = {
    'surface_temperature': [('LST_CELSIUS', 'Official L2 surface temperature (Celsius)', 'حرارة السطح الرسمية L2 بالمئوية'),
                            ('LST_KELVIN', 'Official L2 surface temperature (Kelvin)', 'حرارة السطح الرسمية L2 بالكلفن'),
                            ('EMISSIVITY_NDVI', 'NDVI emissivity (gated: method review)', 'الانبعاثية من NDVI (موقوفة لمراجعة الطريقة)')],
    'thermal_urban': [('UTFVI', 'UTFVI and classification', 'UTFVI وتصنيفه'),
                      ('HOTSPOTS', 'Thermal hotspots (z >= 2)', 'البؤر الحرارية (z >= 2)'),
                      ('SUHI', 'SUHI (gated: urban/rural references)', 'SUHI (يتطلب مرجعًا حضريًا وريفيًا)')],
    'environmental_drought': [('ALBEDO', 'Broadband albedo (Landsat TM/ETM+ only)', 'البياض السطحي (Landsat TM/ETM+ فقط)'),
                              ('TVDI', 'TVDI (gated: validated dry/wet edges)', 'TVDI (يتطلب حدود جفاف ورطوبة موثقة)'),
                              ('VCI_TCI_VHI', 'VCI / TCI / VHI (gated: historical baseline)', 'VCI / TCI / VHI (تتطلب مرجعًا تاريخيًا)')],
    'temporal_change': [('NDVI', 'NDVI difference (T2 - T1)', 'فرق NDVI (T2 - T1)'),
                        ('NBR', 'NBR difference (T2 - T1)', 'فرق NBR (T2 - T1)'),
                        ('LST', 'Surface temperature difference (T2 - T1)', 'فرق حرارة السطح (T2 - T1)')],
}
for tool, rows in EXTRA.items():
    CATALOG[tool] = [dict(id=i, en=e, ar=a, category='Calculations') for i, e, a in rows]
CATALOG['surface_temperature'].insert(0, dict(id='LST', en='Land surface temperature', ar='درجة حرارة سطح الأرض', category='Temperature'))
for row in CATALOG['spectral_indices']:
    if row['id'] in ('NDMI', 'NDWI_GAO'):
        row['category'] = 'Moisture'

METHOD_DETAILS = {
    'LST_CELSIUS': ('Kelvin - 273.15; Landsat C2 L2 Kelvin = DN * 0.00341802 + 149.0', 'USGS Landsat Collection 2 Level-2 Science Products'),
    'LST_KELVIN': ('Landsat C2 L2: DN * 0.00341802 + 149.0; other official products use their own verified profile', 'USGS Landsat Collection 2 Level-2 Science Products'),
    'UTFVI': ('(LST_K - mean(LST_K)) / mean(LST_K); reference = valid scene pixels', 'Existing UTFVI mean-normalized convention; classification requires independent real-product validation'),
    'HOTSPOTS': ('(LST_K - mean(LST_K)) / std(LST_K) >= 2; reference = valid scene pixels', 'Descriptive z-score threshold; not air temperature or urban/rural SUHI'),
    'ALBEDO': ('0.356*Blue + 0.130*Red + 0.373*NIR + 0.085*SWIR1 + 0.072*SWIR2 - 0.0018', 'Liang (2001), Narrowband to broadband conversions of land surface albedo; TM/ETM+ profile only'),
}
for rows in CATALOG.values():
    for row in rows:
        if row['id'] in METHOD_DETAILS:
            row['formula'], row['citation'] = METHOD_DETAILS[row['id']]
for row in CATALOG['temporal_change']:
    row['formula'] = f"{row['id']}(T2) - {row['id']}(T1)"
    row['citation'] = 'Arithmetic difference; identical sensor, level and compatible epochs required'

from atiaf_core.interpretation import describe
for tool, rows in CATALOG.items():
    for row in rows:
        row['interpretation'] = describe(tool, row)

LABELS = {
    'sensor_product': ('Sensor / Product', 'المستشعر ومستوى المنتج'),
    'input_folder': ('Input Data Folder', 'مجلد بيانات الإدخال'),
    'second_folder': ('Second epoch scene or parent folder', 'مجلد مرئيات التاريخ الثاني'),
    'expert_mapping': ('Import saved band mapping (optional JSON)', 'استيراد تعيين باندات محفوظ (JSON اختياري)'),
    'apply_qa_mask': ('Apply quality, cloud and shadow masks', 'تطبيق أقنعة الجودة والسحب والظلال'),
    'enable_mosaic': ('Mosaic compatible scenes (optional)', 'دمج المشاهد المتوافقة (اختياري)'),
    'aoi_features': ('Study area polygon (optional)', 'مضلع منطقة الدراسة (اختياري)'),
    'output_crs': ('Output projected CRS in metres (native picker)', 'نظام الإحداثيات المسقط بالمتر'),
    'add_to_map': ('Add results to active map', 'إضافة النتائج إلى الخريطة'),
    'output_folder': ('Output folder (defaults to input)', 'مجلد الحفظ (الافتراضي هو الإدخال)'),
}

def title(tool, language='en'):
    return TITLES[tool][language == 'ar']

def label(name, language='en'):
    return LABELS[name][language == 'ar']

def calculations(tool, language='en'):
    return [(r['id'], f"{r['id']} — {r[language]}") for r in CATALOG[tool]]

def help_text(tool, language='en'):
    if language == 'ar':
        return (title(tool, language) + '\nاختر المستشعر ثم مجلد بيانات الإدخال؛ يقبل مرئية مفكوكة أو مجلدًا يضم عدة مرئيات. فعّل الحسابات المطلوبة فقط. '
                'عند نقص الميتاداتا فعّل تعيين الباندات يدويًا واختر الملفات المتاحة مع توثيق المعايرة. '
                'الحسابات غير محددة افتراضيًا. يُفحص توافق المستشعر والباندات والمستوى قبل إنشاء أي ناتج. '
                'الدمج والقص مستقلان واختياريان. اختر مسقطًا بالمتر أو اتركه لاستخدام مسقط المصدر الملائم. '
                'مجلد الحفظ آخر إعداد، والنتائج السابقة محفوظة. راجع documentation/ar/QUICK_START.md. '
                'الحساب الموقوف يذكر المتطلبات الناقصة؛ وجوده في الدليل لا يعني دعمه.')
    return (title(tool) + '\nChoose sensor, then Input Data Folder (one unpacked scene or a folder containing scenes). Select calculations by theme. '
            'For incomplete metadata enable manual mapping and supply only available bands with explicit calibration provenance. '
            'Nothing is selected by default. Sensor, bands and level are checked before outputs. '
            'Mosaic and polygon clip are independent optional steps. Choose a projected metre CRS, '
            'or reuse a suitable source CRS. Output folder is last and defaults to input. Prior results are preserved. '
            'See documentation/en/QUICK_START.md. Gated calculations explain missing prerequisites; catalog presence is not support.')


def arabic_error(message):
    """Translate diagnostic families while keeping internal IDs and file paths stable."""
    translations = [
        ('NDVI classification', 'يتطلب تصنيف NDVI اختياره وحدودًا داخلية ثلاثة متصاعدة ومبررًا محليًا موثقًا؛ ليس معيارًا دوليًا.'),
        ('NDVI retrieval', 'اشتقاق الحرارة بمساعدة NDVI يتطلب مدخلات حرارية وغلافًا جويًا وانبعاثية صريحة وموثقة، وملفات متوافقة في المشهد والإحداثيات والشبكة؛ راجع دليل الحرارة.'),
        ('Manual mapping requires', 'اختر المستشعر ومستوى المنتج الفعلي للتعيين اليدوي؛ لا تستخدم AUTO.'),
        ('Manual platform', 'اسم القمر المدخل يدويًا لا يتوافق مع المستشعر ومستوى المنتج المختارين.'),
        ('manual calibration', 'أدخل معامل القياس والإزاحة الصريحين ووثّق مصدر المعايرة لكل نوع من البيانات؛ لا نفترض معايرة مفقودة.'),
        ('Manual calibration', 'أدخل معامل القياس والإزاحة الصريحين ووثّق مصدر المعايرة؛ لا نفترض معايرة مفقودة.'),
        ('Imported manual mapping', 'ملف التعيين المستورد لا يتوافق مع المستشعر أو مستوى المنتج المختار.'),
        ('Select at least one', 'اختر حسابًا واحدًا على الأقل؛ جميع الحسابات غير محددة افتراضيًا.'),
        ('Sensor/product mismatch', 'اختيار المستشعر أو مستوى المنتج يتعارض مع الميتاداتا. اختر AUTO أو المستشعر الصحيح.'),
        ('Missing physical band', 'الباند الفيزيائي المطلوب غير موجود في المرئية: ' + message.rsplit(':', 1)[-1].strip()),
        ('Official surface temperature', 'يتطلب الحساب باند حرارة سطح رسميًا بالكلفن؛ المرئيات البصرية وحدها لا تعطي حرارة السطح.'),
        ('surface reflectance product', 'يتطلب الحساب انعكاسية سطحية موثقة؛ لا يجوز التعامل مع TOA أو DN كانعكاسية سطحية.'),
        ('coefficients require', 'معاملات المستشعر والأطوال الموجية ومستوى المنتج تحتاج مراجعة علمية قبل إتاحة الحساب.'),
        ('dry/wet edges', 'يتطلب TVDI حدود جفاف ورطوبة تعتمد على NDVI؛ التطبيع بأدنى وأعلى حرارة ليس TVDI.'),
        ('historical reference', 'يتطلب الحساب مرجعًا تاريخيًا مبررًا ومتوافقًا.'),
        ('Urban and rural', 'يتطلب SUHI مضلعي أو قناعي مرجع حضري وريفي.'),
        ('Emissivity method', 'طريقة الانبعاثية وحدود NDVI على مستوى المرئية تحتاج مراجعة علمية.'),
        ('albedo coefficients', 'معاملات البياض الحالية مقصورة على Landsat TM/ETM+؛ بقية المستشعرات تحتاج مراجعة.'),
        ('band/date restrictions', 'شروط المستشعر والباندات والتاريخ غير مستوفاة، ومنها تعطل ASTER SWIR بعد أبريل 2008.'),
        ('ASTER band semantics', 'قارئ منتج ASTER ودلالات بانداته الدقيقة تحتاج تحققًا علميًا.'),
        ('Decision D-007', 'اختر نظام إحداثيات مسقطًا بوحدة المتر من منتقي المساقط الأصلي.'),
        ('quality mask', 'قناع الجودة المطلوب غير موجود؛ أضفه أو ألغِ تطبيق الجودة صراحةً مع مراعاة القيود العلمية.'),
        ('Unknown source CRS', 'نظام إحداثيات المصدر مجهول؛ عرّف مسقطه الصحيح قبل إعادة الإسقاط.'),
        ('Missing dependency', 'أحد اعتماديات المحرك غير متاح. راجع documentation/ar/INSTALLATION.md؛ تظل قائمة الحسابات ظاهرة.'),
        ('Mosaic requires', 'الدمج يتطلب المستشعر والمستوى ويوم الالتقاط نفسه؛ دمج تواريخ مختلفة يحتاج طريقة موثقة.'),
        ('EXPERT requires', 'اختيار EXPERT يتطلب ملف تعيين JSON صريحًا. راجع documentation/ar/EXPERT_MAPPING.md.'),
        ('No recognized', 'لم يُعثر على ميتاداتا وباندات منتج معروف في مجلد الإدخال.'),
        ('Map loading failed', 'تعذرت إضافة إحدى الطبقات إلى الخريطة؛ المنتجات المحفوظة باقية.'),
        ('canceled', 'أُلغي التشغيل؛ المنتجات المحفوظة سابقًا باقية.'),
        ('AOI', 'منطقة الدراسة تحتاج مضلعًا صالحًا غير فارغ ونظام إحداثيات مصدر معروفًا.'),
        ('Epoch dates', 'تاريخا المقارنة يجب أن يكونا معروفين ومختلفين، والتاريخ الأول أسبق من الثاني.'),
        ('Temporal comparison', 'المقارنة الحالية تتطلب مرئية واحدة لكل تاريخ مع تطابق المستشعر ومستوى المنتج.'),
        ('datum transformation', 'تحويل المرجع أو شبكته المطلوبة غير متاح؛ لا تُنزّل الشبكات تلقائيًا.'),
    ]
    for fragment, translation in translations:
        if fragment.casefold() in message.casefold():
            return translation
    return 'تعذر التحقق أو التنفيذ. راجع سجل التشغيل ودليل استكشاف الأخطاء في documentation/ar/TROUBLESHOOTING.md.'
