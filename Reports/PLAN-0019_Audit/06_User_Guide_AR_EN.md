# PLAN-0019 r1 — 06 User guide / دليل المستخدم

## English

Open the updated Pro toolbox or matching local QGIS package and reopen old dialogs. For archived products choose AUTO: actual metadata determines satellite, collection and level. Choose **Direct RGB**, **Ratio RGB**, or both. L8/9 CRC1 is R6/7, G6/2, B(4/5)×(6/5); 753 is direct B7/B5/B3. They are separate continuous spectral products. Other presets labeled experimental require explicit consent; exact ASTER inputs/date/calibration remain mandatory.

Keep QA enabled where available. For this L1T scene enable calibrated **TOA** deliberately; the tool will not make it surface reflectance. T01 NDVI has its own TOA diagnostic checkbox and NDVI_TOA name; most other SR-dependent methods remain unavailable on L1. Thermal brightness temperature is not LST. Missing ancillary inputs produce an explicit reason.

Preview before/after, select quiet/balanced/enhanced/custom, then linear/percentile/stddev stretch; gamma/saturation and fixed channel bounds affect display only. Cyan means stronger display G/B than R for this recipe, not a named mineral. Vegetation/water/bare diagnostics in this audit are not rock classification. Use a matching independent geological reference for interpretation.

Choose polygon AOI independently of mosaic, suitable native metre CRS, optional Add Results to Map and output folder last. Mixed generations/dates cannot silently mosaic. New names contain actual satellite and recipe, for example `LC81760392014234LGN00_Landsat8_Geology_CRC1_Ratios_RGB_Analytical.tif` under a unique run's Analytical folder. Display holds `_DISPLAY.tif` and previews; Metadata holds JSON with equations/calibration/source/grid/stats; QA_Reports points to complete bilingual reports under Results/Reports. Optional R/G/B intermediates are in Work. Analytical Float32 NaN NoData and display UInt8 zero NoData are distinct; load the display product for visual inspection and analytical product for numeric reuse. All old outputs and sources are preserved.

Only the supplied real L8 pre-Collection case was tested as a real acquisition in this audit. Use [matrix01](01_Sensor_Product_Compatibility_Matrix.md) and [numeric04](04_RGB_CRC1_Numerical_QA.md) for exact limits; an eligible catalog item is not proof of real-product validation.

## العربية

افتح أدوات Pro المحدثة أو حزمة QGIS المحلية المطابقة وأعد فتح النوافذ القديمة. للمرئيات الأرشيفية اختر AUTO؛ تُقرأ هوية المستشعر والمجموعة والمستوى من البيانات الأصلية. اختر الدمج المباشر أو دمج النسب أو كليهما. الوصفة CRC1 هي R6/7 وG6/2 وB(4/5)×(6/5)، بينما 753 تركيب مباشر؛ كلاهما صور طيفية مستمرة وليس تصنيفًا للصخور. التركيبات التجريبية تتطلب تفعيلها صراحة، ومدخلات ASTER المعايرة والتاريخ الصحيح لازمان.

أبقِ الجودة مفعّلة عندما يتوافر القناع. لهذه المرئية L1T فعّل السماح بمعايرة TOA عمدًا؛ لا يتحول الناتج إلى انعكاس سطحي. للمؤشر NDVI خيار تشخيص TOA مستقل واسم NDVI_TOA واضح؛ تظل الطرق المحتاجة لانعكاس سطحي أو مدخلات إضافية موقوفة مع بيان السبب. السطوع الحراري ليس حرارة سطح الأرض.

راجع المعاينة قبل وبعد، واختر تحسينًا هادئًا أو متوازنًا أو قويًا أو مخصصًا، وتمديدًا خطيًا أو بالمئينات أو بالانحراف المعياري. جاما والتشبع والحدود الثابتة تغير العرض فقط. السماوي يعني ارتفاع الأخضر والأزرق بالنسبة للأحمر بعد التمديد حسب الوصفة؛ لا يثبت معدنًا. مؤشرات الغطاء في هذا التدقيق تقريبية، والتفسير يحتاج خريطة جيولوجية مستقلة مناسبة.

القص المضلعي مستقل عن الدمج. اختر المسقط المناسب بالمتر من المضيف، والإضافة للخريطة اختيارية، ومجلد الإخراج آخر إعداد. لا تُدمج مستويات ومجموعات وتواريخ غير متوافقة بصمت. اسم الراستر يذكر Landsat8 والوصفة. داخل تشغيل مستقل توجد مجلدات التحليل والعرض والميتاداتا وتقارير الجودة؛ دليل تقارير الجودة يشير للتقارير الكاملة في Results/Reports. يمكن حفظ القنوات منفردة في Work. التحليل عائم وغياب البيانات فيه NaN؛ العرض UInt8 والصفر فيه غياب بيانات. استخدم العرض للفحص البصري والتحليل لإعادة الحساب. لا تُمسح المصادر أو النتائج السابقة.

اختبار المرئية الحقيقية هنا يقتصر على Landsat8 القديمة المتاحة. أهلية الاختيار أو نجاح عينة صناعية لا يثبتان كل المستشعرات أو صحة التفسير الحقلي. الخطة نشطة، والخطة الأصلية محفوظة داخل مجلد الخطط فقط باسم ورقم واضحين.
