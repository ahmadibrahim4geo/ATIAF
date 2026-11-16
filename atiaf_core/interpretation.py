"""Bilingual interpretation by scientific ID/variant, shared by docs, portal and reports."""
NASA = 'https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/'
USGS = 'https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices'
CONTEXT = {
    'en': 'Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.',
    'ar': 'يُفسر الناتج حسب المستشعر ومستوى المنتج والموسم والغطاء والتربة والغلاف الجوي والرطوبة والدقة. النطاقات الاسترشادية ليست معيار فئات عالميًا. يلزم تحقق محلي مستقل، وغياب البيانات وأقنعة الجودة ليست فئة غطاء أرضي.'}
GREEN = {
 'NDVI': ('Red/NIR contrast of green vegetation; higher positive values usually mean stronger greenness, with canopy saturation. A low value alone does not diagnose plant disease.', 'تباين الأحمر والقريب للنبات الأخضر؛ القيم الموجبة الأعلى تعني عادة إشارة خضرة أكبر مع تشبع الغطاء الكثيف. انخفاض القيمة وحده لا يشخص مرض النبات.'),
 'GNDVI': ('Green/NIR vegetation contrast with pigment sensitivity; higher values suggest a stronger green vegetation signal, not a calibrated chlorophyll concentration.', 'تباين الأخضر والقريب مع حساسية للأصباغ؛ الارتفاع يشير لإشارة نباتية أكبر وليس تركيز كلوروفيل معايرًا.'),
 'SAVI': ('Soil-adjusted red/NIR vegetation response; larger values suggest more greenness under the selected soil constant L.', 'استجابة نباتية معدلة لتأثير التربة؛ ارتفاعها يشير لخضرة أكبر وفق ثابت التربة المختار.'),
 'EVI': ('Enhanced canopy greenness using blue/red/NIR; high values suggest stronger canopy response; denominator and aerosol contamination can cause exceptional values.', 'خضرة محسنة باستخدام الأزرق والأحمر والقريب؛ القيم الأعلى تشير لاستجابة غطاء أكبر، وقد يسبب المقام أو الهباء قيمًا استثنائية.'),
 'NDRE1': ('NIR/red-edge vegetation contrast; useful for canopy pigment sensitivity only with appropriate red-edge wavelengths.', 'تباين القريب وحافة الأحمر مع حساسية لأصباغ الغطاء؛ يتطلب أطوالًا موجية مناسبة لحافة الأحمر.'),
 'MSAVI': ('Vegetation signal with adaptive soil adjustment; larger values generally indicate more greenness. Negative square-root arguments are invalid.', 'إشارة نباتية بتعديل تكيفي للتربة؛ الارتفاع يدل عمومًا على خضرة أكبر، ومدخل الجذر السالب غير صالح.'),
 'OSAVI': ('Soil-adjusted vegetation ratio; interpretation depends on the implemented normalization variant and 0.16 constant. Do not transfer NDVI classes.', 'نسبة نباتية معدلة للتربة؛ تعتمد على صيغة التطبيع المنفذة والثابت 0.16. لا تُنقل إليها فئات NDVI.'),
 'VARI': ('Visible-band greenness contrast; atmosphere-resistant does not mean atmosphere-free. Unstable denominators may yield large values.', 'تباين الخضرة من النطاقات المرئية؛ مقاومة الغلاف الجوي لا تعني انعدام تأثيره، وقد يعطي المقام غير المستقر قيمًا كبيرة.'),
 'GLI': ('Visible green-leaf contrast relative to red/blue; stronger positive response suggests greener surfaces, not a species diagnosis.', 'تباين الورق الأخضر بالنسبة للأحمر والأزرق؛ الاستجابة الموجبة الأكبر تشير لخضرة السطح ولا تحدد النوع النباتي.'),
 'EVI2': ('Two-band enhanced vegetation response without blue; quality and coefficient variant matter; no automatic NDVI class transfer.', 'استجابة نباتية محسنة بباندين دون الأزرق؛ تعتمد على الجودة وصيغة المعاملات ولا تُنقل لها فئات NDVI تلقائيًا.'),
 'NIRv': ('NIR reflectance attributed to vegetation using NDVI; related to vegetation/photosynthesis but not direct GPP, biomass or yield.', 'انعكاس القريب المنسوب للنبات باستخدام NDVI؛ مرتبط بالنبات والنشاط الضوئي وليس قياسًا مباشرًا للإنتاجية أو الكتلة الحيوية أو المحصول.'),
 'MTVI2': ('Modified triangular vegetation index 2; sensitive to green leaf area index and canopy cover, reducing soil background influence.', 'مؤشر الغطاء النباتي المثلثي المعدل 2؛ حساس لدليل مساحة الأوراق الخضراء ويقلل تأثير خلفية التربة.'),
 'MCARI2': ('Modified chlorophyll absorption in reflectance index 2; estimates green biomass and canopy chlorophyll while minimizing soil and non-photosynthetic effects.', 'مؤشر امتصاص الكلوروفيل المعدل 2؛ يقدّر الكتلة الحيوية الخضراء وكلوروفيل الغطاء مع تقليل تأثير التربة.'),
 'NDRE2': ('Red edge index variant using NIR and red-edge 2 bands; sensitive to high-biomass chlorophyll changes where NDVI saturates.', 'مؤشر حافة الأحمر 2 باستخدام القريب وحافة الأحمر 2؛ حساس لتغيرات الكلوروفيل في الغطاء الكثيف عند تشبع NDVI.'),
 'CIGREEN': ('Chlorophyll index green; related to total chlorophyll content in leaves and canopies based on green and NIR reflectance.', 'مؤشر الكلوروفيل الأخضر؛ يرتبط بالمحتوى الكلي للكلوروفيل في الأوراق والغطاء بناءً على انعكاس الأخضر والقريب.'),
 'CIREDEDGE': ('Chlorophyll index red-edge; sensitive to chlorophyll concentration across moderate to high canopy densities.', 'مؤشر الكلوروفيل لحافة الأحمر؛ حساس لتركيز الكلوروفيل في الكثافات النباتية المتوسطة إلى العالية.')}
OTHER = {
 'NDSI_SALINITY': ('Normalized difference salinity index from SWIR1 and NIR; highlights salt-affected bare soils and crusts.', 'مؤشر الفرق المعياري للملوحة من القصير الأول والقريب؛ يبرز الترب المتملحة والقشور الملحية المكشوفة.'),
 'DIRECT_RGB': ('Three calibrated scientific bands assigned to red, green and blue. Spectral colors retain continuous terrain detail; they do not identify rock classes.', 'ثلاثة باندات علمية معايرة تسند إلى الأحمر والأخضر والأزرق. تحتفظ الألوان الطيفية بتفاصيل التضاريس المستمرة ولا تحدد فئات الصخور.'),
 'RATIO_RGB': ('Three independently calculated spectral expressions displayed as RGB; ratio contrast is not a confirmed rock/mineral classification.', 'ثلاث معادلات طيفية محسوبة بصورة مستقلة تعرض بقنوات RGB؛ تباين النسب ليس تصنيفًا مؤكدًا للصخور أو المعادن.'),
 'NDWI_MCFEETERS': ('Green/NIR open-water contrast; larger values can favor open water but shadows/built surfaces can confuse it.', 'تباين الأخضر والقريب للمياه المفتوحة؛ قد ترجح القيم الأعلى المياه لكن الظلال والعمران قد يتداخلان.'),
 'MNDWI': ('Green/SWIR open-water enhancement; positive response is evidence to investigate, not a universal water mask.', 'إبراز المياه المفتوحة بالأخضر والقصير؛ الاستجابة الموجبة دليل للفحص وليست قناع مياه عالميًا.'),
 'NDMI': ('NIR/SWIR vegetation-moisture proxy; larger values often suggest more canopy moisture, not measured soil moisture.', 'دليل رطوبة النبات من القريب والقصير؛ الارتفاع قد يشير لرطوبة الغطاء ولا يقيس رطوبة التربة مباشرة.'),
 'NDWI_GAO': ('Original Gao water-content index depends on wavelength choice; this catalog variant remains gated for wavelength review.', 'مؤشر جاو لمحتوى الماء يعتمد على اختيار الطول الموجي؛ الصيغة هنا موقوفة لمراجعة الأطوال.'),
 'NDBI': ('SWIR/NIR built-surface contrast; bare soil can respond similarly. High values are not confirmed buildings.', 'تباين القصير والقريب للعمران؛ قد تستجيب التربة المكشوفة بشكل مشابه، والارتفاع لا يثبت وجود مبانٍ.'),
 'UI': ('SWIR2/NIR urban-surface contrast; distinguish dry bare land and mixed pixels using independent evidence.', 'تباين القصير الثاني والقريب للأسطح العمرانية؛ تُفصل التربة الجافة والبكسلات المختلطة بأدلة مستقلة.'),
 'BSI': ('Bare-soil spectral contrast; positive response may favor exposed soil but varies with soil color, moisture and built surfaces.', 'تباين طيفي للتربة المكشوفة؛ قد ترجح الاستجابة الموجبة التربة ويتغير ذلك باللون والرطوبة والعمران.'),
 'NBR': ('NIR/SWIR2 burn-sensitive contrast. A single low NBR does not establish burn severity; compare compatible pre/post observations.', 'تباين القريب والقصير الثاني الحساس للحريق؛ الانخفاض منفردًا لا يحدد شدة الحريق، ويلزم مقارنة مشاهد متوافقة.'),
 'NBR2': ('SWIR1/SWIR2 contrast sensitive to burn-related moisture changes; a low/high value needs scene/date context.', 'تباين القصير الأول والثاني الحساس لتغير الرطوبة المرتبط بالحريق؛ يحتاج الارتفاع والانخفاض سياق المشهد والتاريخ.'),
 'NDSI': ('Green/SWIR snow contrast; water/cloud/background can overlap. Apply appropriate quality and snow-context checks.', 'تباين الأخضر والقصير للثلوج؛ قد يتداخل الماء والسحب والخلفية، وتلزم جودة وسياق ثلجي مناسبان.'),
 'AWEISH': ('Water enhancement reducing some shadow confusion; compare local water/reference samples before choosing a threshold.', 'إبراز المياه وتقليل بعض التباس الظلال؛ تُراجع عينات المياه والمرجع محليًا قبل اختيار حد.'),
 'AWEINSH': ('Water enhancement for scenes without substantial shadow interference; thresholds are locally evaluated.', 'إبراز المياه للمشاهد دون تداخل ظلال كبير؛ تُقيّم الحدود محليًا.'),
 'TCB': ('Sensor-specific brightness component; coefficients/product level remain gated. It has no universal physical class breaks.', 'مكون سطوع خاص بالمستشعر؛ المعاملات والمستوى موقوفان للمراجعة، ولا توجد حدود فئات فيزيائية عامة.'),
 'TCG': ('Sensor-specific greenness component; not interchangeable with NDVI. Coefficients/product level remain gated.', 'مكون خضرة خاص بالمستشعر لا يكافئ NDVI؛ المعاملات والمستوى موقوفان للمراجعة.'),
 'TCW': ('Sensor-specific wetness component; not a direct moisture measurement. Coefficients/product level remain gated.', 'مكون بلل خاص بالمستشعر وليس قياس رطوبة مباشرًا؛ المعاملات والمستوى موقوفان للمراجعة.'),
 'IRON_OXIDE': ('Red/blue iron-oxide spectral indication; higher ratios may highlight ferruginous surfaces, not mineral concentration or confirmed ore.', 'دلالة طيفية لأكاسيد الحديد بنسبة الأحمر للأزرق؛ قد يبرز الارتفاع أسطحًا حديدية ولا يحدد التركيز أو الخام المؤكد.'),
 'FERRIC_IRON': ('Red/green ferric-related surface contrast; spectral proxy needing field/spectral confirmation.', 'تباين الأحمر والأخضر المرتبط بأسطح الحديد الثلاثي؛ دليل يحتاج تأكيدًا ميدانيًا أو طيفيًا.'),
 'FERROUS_IRON': ('SWIR1/NIR ferrous-related surface contrast; mixed minerals/cover can alter the response.', 'تباين القصير الأول والقريب المرتبط بالحديد الثنائي؛ يتأثر باختلاط المعادن والغطاء.'),
 'CLAY_ALTERATION': ('SWIR hydroxyl/clay alteration indication; cannot uniquely identify a clay mineral.', 'دلالة تحور طيني أو هيدروكسيل من القصير؛ لا تحدد معدنًا طينيًا منفردًا.'),
 'GOSSAN': ('Gossan-related band-ratio response; not confirmation of mineralization or economic value.', 'استجابة نسب باندات مرتبطة بالجوسان؛ لا تثبت التمعدن أو القيمة الاقتصادية.'),
 'ASTER_QUARTZ': ('ASTER TIR quartz proxy; exact product/band emissivity semantics remain gated.', 'دليل كوارتز من ASTER الحراري؛ دلالات المنتج والباندات والانبعاثية موقوفة للمراجعة.'),
 'ASTER_CARBONATE': ('ASTER TIR carbonate proxy; exact product/band emissivity semantics remain gated.', 'دليل كربونات من ASTER الحراري؛ دلالات المنتج والباندات والانبعاثية موقوفة للمراجعة.'),
 'ASTER_MAFIC': ('ASTER TIR mafic proxy; exact product/band emissivity semantics remain gated.', 'دليل صخور مافية من ASTER الحراري؛ دلالات المنتج والباندات والانبعاثية موقوفة للمراجعة.'),
 'LST': ('Land surface temperature, not 2 m air temperature; official L2 extraction or explicitly selected local NDVI/RTE derivation are distinct methods.', 'درجة حرارة السطح وليست حرارة الهواء على ارتفاع مترين؛ استخراج L2 الرسمي يختلف عن الاشتقاق المحلي المختار صراحة بمساعدة NDVI.'),
 'LST_CELSIUS': ('Official surface temperature in Celsius; Celsius = Kelvin - 273.15. Hot/cold classes depend on location, season and reference.', 'حرارة سطح رسمية بالمئوية؛ المئوية = الكلفن − 273.15. فئات الحار والبارد تعتمد على المكان والموسم والمرجع.'),
 'LST_KELVIN': ('Official surface temperature in Kelvin; same physical quantity as Celsius, with a different zero point.', 'حرارة سطح رسمية بالكلفن؛ نفس كمية المئوية بنقطة صفر مختلفة.'),
 'EMISSIVITY_NDVI': ('Dimensionless thermal emission efficiency estimated with an NDVI model, not temperature or NDVI itself; legacy choice remains gated.', 'كفاءة إصدار حراري بلا وحدة تُقدّر بنموذج NDVI، وليست حرارة أو NDVI نفسه؛ الاختيار القديم موقوف.'),
 'UTFVI': ('LST departure from the valid-scene mean normalized by mean Kelvin temperature; categories are convention/reference dependent, not air heat risk.', 'انحراف حرارة السطح عن متوسط المشهد الصالح مقسومًا على متوسط الكلفن؛ الفئات مرتبطة بالمرجع والطريقة ولا تعني خطر حرارة الهواء.'),
 'HOTSPOTS': ('Binary pixels with scene-relative thermal z-score >= 2; descriptive high-temperature anomaly, not spatial significance or confirmed SUHI.', 'بكسلات ثنائية بدرجة معيارية حرارية للمشهد أكبر من أو تساوي 2؛ شذوذ وصفي وليس دلالة مكانية إحصائية أو جزيرة حرارية مؤكدة.'),
 'SUHI': ('Urban-versus-rural surface temperature difference requires defined reference masks; currently gated.', 'فرق حرارة السطح بين الحضر والريف يتطلب أقنعة مرجعية محددة؛ موقوف حاليًا.'),
 'ALBEDO': ('Broadband reflected/incident shortwave fraction using the restricted TM/ETM+ conversion; no universal land-cover classes.', 'نسبة الإشعاع القصير المنعكس إلى الساقط وفق تحويل TM/ETM+ المقيد؛ لا تعطي فئات غطاء أرضي عامة.'),
 'TVDI': ('NDVI/temperature dry-wet edge position; genuine fitted edges are required and current calculation is gated.', 'موضع الحرارة وNDVI بين حدي الجفاف والرطوبة؛ يتطلب حدودًا مقدرة فعليًا والحساب موقوف.'),
 'VCI_TCI_VHI': ('Historical vegetation/temperature condition indices require compatible seasonal baselines; current calculation is gated.', 'مؤشرات حالة النبات والحرارة التاريخية تتطلب مرجعًا موسميًا متوافقًا؛ الحساب موقوف.'),
 'FEAI': ('Ferric Iron Alteration Index (FEAI) from SWIR2/NIR and Green/Red; highlights ferric iron alteration zones.', 'مؤشر تحورات الحديد ثلاثي التكافؤ (FEAI) من SWIR2/NIR والأخضر/الأحمر؛ يبرز نطاقات تحورات الحديد الثلاثي.'),
 'FEI': ('Ferrous Iron Index (FEI) from (SWIR2+NIR)/(Green+Red); highlights ferrous iron minerals.', 'مؤشر الحديد ثنائي التكافؤ (FEI)؛ يبرز معادن الحديد الثنائي.'),
 'FESI': ('Ferrous Silicates Index (FESI) from SWIR2/SWIR1; highlights ferrous silicate rock units.', 'مؤشر سيليكات الحديد (FESI) من نسبة SWIR2/SWIR1؛ يبرز الوحدات الصخرية الحاوية على سيليكات الحديد.'),
 'LATI': ('Laterite Index (LATI) from SWIR1/Green; highlights laterite and ferric weathered soils.', 'مؤشر صخور اللاتريت (LATI) من نسبة SWIR1/الأخضر؛ يبرز صخور اللاتريت والتربة الغنية بالتجوية الحديدية.'),
 'L89_753': ('Landsat 8/9 7-5-3 Direct RGB: assigns SWIR2, NIR and Green bands to RGB; standard geological composite for rock and vegetation contrast.', 'تركيب 7-5-3 مباشر لـ Landsat 8/9: يسند SWIR2 و NIR والأخضر لقنوات RGB؛ تركيب جيولوجي قياسي لتباين الصخور والغطاء النباتي.'),
 'L89_762': ('Landsat 8/9 7-6-2 Direct RGB: assigns SWIR2, SWIR1 and Blue bands to RGB; highlights lithological boundaries and structural features.', 'تركيب 7-6-2 مباشر لـ Landsat 8/9: يسند SWIR2 و SWIR1 والأزرق لقنوات RGB؛ يبرز الحدود الليثولوجية والمعالم التركيبية.'),
 'L89_CRC1': ('Landsat 8/9 Sultan CRC1 Ratio RGB: assigns B6/B7, B6/B2, and (B4/B5)*(B6/B5) to RGB; highlights ophiolitic and carbonate rocks.', 'تركيب نسب السلطان CRC1 لـ Landsat 8/9: يسند نسب الباندات لقنوات RGB؛ يبرز صخور الأفيوليت والوحدات الكربوناتية.'),
 'L89_CRC2': ('Landsat 8/9 Sultan CRC2 Ratio RGB: assigns B4/B6, B4/B2, and B6/B7 to RGB; highlights hydrothermal alteration zones.', 'تركيب نسب السلطان CRC2 لـ Landsat 8/9: يسند نسب الباندات لقنوات RGB؛ يبرز نطاقات التحورات المائية الحرارية.'),
 'S2_12112': ('Sentinel-2 12-11-2 Direct RGB: assigns B12, B11 and B2 to RGB; standard geological composite for lithology and structures.', 'تركيب 12-11-2 مباشر لـ Sentinel-2: يسند B12 و B11 و B2 لقنوات RGB؛ تركيب جيولوجي قياسي للصخور والتراكيب.'),
 'S2_12114': ('Sentinel-2 12-11-4 Direct RGB: assigns B12, B11 and B4 to RGB; highlights rock units and soil discrimination.', 'تركيب 12-11-4 مباشر لـ Sentinel-2: يسند B12 و B11 و B4 لقنوات RGB؛ يبرز التمييز الصخري والتربة.'),
 'ASTER_468': ('ASTER 4-6-8 Direct RGB: assigns SWIR bands B4, B6 and B8 to RGB; highlights mineral alteration zones.', 'تركيب 4-6-8 مباشر لـ ASTER: يسند باندات SWIR لقنوات RGB؛ يبرز نطاقات التحور المعدني.'),
 'ASTER_FAWAKHEIR': ('ASTER Fawakheir Ratio RGB: assigns band ratios (B2+B4)/B3N, (B5+B7)/B6, (B7+B9)/B8 to RGB; highlights hydrothermal mineralization.', 'تركيب نسب الفواخير لـ ASTER: يسند نسب الباندات لقنوات RGB؛ يبرز التمعدنات والتحورات الحرارية المائية.')}
NORMALIZED = {'NDVI','GNDVI','NDRE1','NDRE2','NDWI_MCFEETERS','NDWI_GAO','MNDWI','NDBI','UI','NBR','NBR2','NDSI','NDSI_SALINITY','BSI','NDMI','GLI'}

def describe(tool, row):
    key = row['id']
    if tool == 'temporal_change':
        meaning = (f'{key}(T2) minus {key}(T1); positive means increase, negative decrease. Direction alone does not establish a cause or burn severity.',
                   f'قيمة {key} في التاريخ الثاني ناقص الأول؛ الموجب زيادة والسالب نقص. الاتجاه وحده لا يحدد السبب أو شدة الحريق.')
        units = '°C difference' if key == 'LST' else 'dimensionless difference'
        units_ar = 'فرق مئوي' if key == 'LST' else 'فرق بلا وحدة'
        ranges = ('[-2,2] only when both valid input indices are within [-1,1]' if key != 'LST' else 'No universal fixed interval',
                  'من −2 إلى 2 فقط إذا كان المؤشران الصالحان ضمن −1 إلى 1' if key != 'LST' else 'لا يوجد مدى ثابت عام')
    else:
        meaning = (GREEN | OTHER)[key]  # Deliberate hard failure for uncovered methods.
        units, units_ar = ('temperature unit selected', 'وحدة الحرارة المختارة') if key.startswith('LST') else ('dimensionless', 'بلا وحدة')
        ranges = ('No universal fixed interval; use method assumptions and QA', 'لا يوجد مدى ثابت عام؛ تُراجع افتراضات الطريقة والجودة')
        if key in NORMALIZED:
            ranges = ('[-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions',
                      'من −1 إلى 1 للمدخلات المعايرة غير السالبة والمقام غير الصفري؛ تُراجع الاستثناءات بالجودة')
        if key in ('ALBEDO','EMISSIVITY_NDVI'):
            ranges = ('Physical fraction [0,1]; the model/product can be invalid or outside assumptions', 'نسبة فيزيائية من صفر إلى 1؛ قد يكون النموذج أو المنتج غير صالح أو خارج الافتراضات')
        if key == 'HOTSPOTS':
            ranges = ('0=not flagged, 1=flagged; 255=NoData in the binary raster', 'صفر=غير محدد، 1=محدد؛ 255=غياب بيانات في الراستر الثنائي')
            units, units_ar = 'binary flag', 'علامة ثنائية'
    result = {'classification_status': 'NO_VERIFIED_UNIVERSAL_CLASS_STANDARD',
              'reference': row.get('citation', 'Method-specific review required'),
              'reference_urls': [NASA, USGS] if key in GREEN else [],
              'class_preset': 'Optional local illustrative NDVI greenness only' if tool == 'spectral_indices' and key == 'NDVI' else 'No automatic ecological classification',
              'en': dict(meaning=meaning[0], units=units, range=ranges[0], caution=CONTEXT['en']),
              'ar': dict(meaning=meaning[1], units=units_ar, range=ranges[1], caution=CONTEXT['ar'])}
    if key == 'NDVI' and tool == 'spectral_indices':
        result['educational_examples'] = {
            'en': 'NASA examples: <=0.1 often rock/sand/snow; 0.2–0.3 shrub/grassland; 0.6–0.8 dense forest. These are overlapping-context illustrations, not exhaustive executable bins or a health standard. Negative values are not uniquely water.',
            'ar': 'أمثلة NASA: قرب 0.1 أو أقل صخر أو رمل أو ثلج غالبًا؛ 0.2–0.3 شجيرات ومراعٍ؛ 0.6–0.8 غابات كثيفة. أمثلة سياقية وليست فئات تشغيل شاملة أو معيار صحة. السالب ليس ماءً بالضرورة.'}
    return result
