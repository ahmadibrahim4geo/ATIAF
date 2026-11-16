# خطة تدقيق وتطوير دعم المرئيات التاريخية والتحقق العلمي من مخرجات التحسين الجيولوجي

> **المشروع:** أدوات الاستشعار عن بُعد «أطياف / ATYAF» — أو الاسم المعتمد في المستودع.
>
> **نوع المستند:** أوامر وخطة عمل للـ AI Agent (Development & Scientific QA Plan).
>
> **تاريخ إعداد الخطة:** 15 نوفمبر 2026.
>
> **الحالة:** خطة تدقيق وتنفيذ لاحقة، **وليست** تقريرًا يؤكد فحص الشيفرة أو صحة ملف Raster فعليًا.
>
> **المبدأ:** لا تعدّل الشيفرة ولا تعِد تصميم الأداة على أساس شكل صورة العرض وحدها. افحص تنفيذها ومنتجاتها وملفات Metadata والمراجع العلمية أولًا، ثم أصلح ما تثبت مشكلته مع اختبارات قبول قابلة للتكرار.

---

## 1. الأمر الرئيسي للوكيل

أجرِ مراجعة شاملة لجميع أدوات المعالجة الطيفية والجيولوجية الموجودة **فعليًا** بالمشروع، مع التركيز على محورين مترابطين:

1. **التوافق الزمني / التاريخي:** لا يكفي أن تدعم الأداة اسم مستشعر مثل Landsat 8؛ يجب أن تتعرف أيضًا على **الإصدارات القديمة من منتجات المستشعر نفسه** وعلى اختلاف أسماء المشاهد وملفات الباندات وصيغ Metadata ومستويات المعالجة وأجيال المعايرة، مع التمييز بينها وبين المستشعرات الأقدم مثل TM وETM+ وMSS.
2. **الصحة العلمية للمخرجات:** تأكد أن كل طريقة معالجة تحسب منتجها الحقيقي؛ وأن الباندات ووحداتها وترتيب القنوات والتعامل مع NoData والتحويلات الإشعاعية والـ Stretch مطابقة للطريقة المنشورة. يجب أن يشرح الناتج **ما الذي حُسب وما الذي تعنيه الألوان**، لا أن يصدر صورة ملونة مجهولة المصدر والتفسير.

نفّذ العمل بالترتيب: **جرد الأدوات → جرد المنتجات المدعومة → فحص المشهد المرجعي → مراجعة المراجع والمعادلات → اختبارات رقمية وبصرية → الإصلاحات الضرورية → اختبارات الانحدار → تقرير نهائي بمصفوفة دعم واضحة**.

**لا تفترض أن أي أداة مدعومة أو غير مدعومة قبل اختبارها. لا تُسجّل نجاحًا بناءً على عدم حدوث استثناء برمجي فقط.**

---

## 2. الحالة المرجعية التي أثارت المراجعة

### 2.1 المشهد المدخل

`LC81760392014234LGN00`

تفكيك مبدئي لرمز المشهد وفق نظام **Landsat Scene ID (Pre-Collection)**:

| الجزء | الدلالة |
|---|---|
| `L` | Landsat |
| `C` | المستشعران المدمجان OLI/TIRS |
| `8` | Landsat 8 |
| `176` | WRS-2 Path |
| `039` | WRS-2 Row |
| `2014` | سنة الالتقاط |
| `234` | اليوم اليولياني من السنة؛ يوافق **22 أغسطس 2014** |
| `LGN00` | معرّف المحطة/النسخة في نظام تسمية المشهد القديم؛ لا يعني بمفرده Collection 1 أو Collection 2 |

**تصحيح مفاهيمي مُلزِم:** هذه **مرئية مبكرة تاريخيًا من Landsat 8 بتسمية ما قبل Collections**، وليست «مستشعرًا من الجيل الأول» مختلفًا داخل Landsat 8. فئة *Legacy product* تخص بنية منتج البيانات وتاريخ معالجته، ولا تعني وحدها ضعف المستشعر أو فساد القيم.

**مهم:** تاريخ الالتقاط 2014 لا يحدد تاريخ معالجة الملفات المحفوظة على القرص. يجب قراءة ملف `MTL` الأصلي والملفات المصاحبة للتأكد من نوع المعالجة والمعايرة والتحويلات المتاحة.

### 2.2 ملف الإخراج الظاهر في لقطة الشاشة

`LC81760392014234LGN00_LANDSAT_8_9_L89_CRC1_B6-B7_B6-B2_B4-B5-B6-B5_dad2439d6ee5_DISPLAY.tif`

**ملاحظات لا تُعد حكمًا نهائيًا على صحة النتيجة:**

- المنطقة الظاهرة تشمل أراضي زراعية ومياهًا وصحراء وأجزاء من شمال سيناء/دلتا النيل؛ وقد لا تكون أفضل منطقة لاختبار إبراز الاختلافات الجيولوجية الصخرية المكشوفة.
- يظهر اللون السماوي/الأزرق على مساحة صحراوية كبيرة. ذلك قد يكون ناتجًا عن طبيعة النسب، أو توزيع القيم، أو اختيار القنوات، أو المعايرة، أو معالجة NoData؛ **لا يمكن تعيين السبب من صورة العرض وحدها**.
- اسم الناتج مشفّر وصعب التفسير ويحتوي على أسماء باندات تفتقر إلى العمليات الحسابية الواضحة وعناوين قنوات R/G/B.
- `DISPLAY.tif` قد يكون صورة عرض لونية 8-bit مشتقة من طبقات تحليلية Float32؛ لا يجوز افتراض أنه المنتج التحليلي الوحيد.
- النص `LANDSAT_8_9` قد يشير إلى **عائلة مستشعرات مدعومة في الأداة** وليس إلى هوية القمر الذي التقط المشهد. على الواجهة والـ Metadata أن يظهرا **Landsat 8** بوصفه القمر الفعلي، وأن يظهرا مجموعة الوصفة بصورة مستقلة.
- وجود مقاطع متعددة مثل `B6-B7_B6-B2_B4-B5-B6-B5` لا يثبت عدد طبقات الناتج أو ما إذا كانت العملية `(B4/B5)×(B6/B5)`؛ يثبت ذلك فقط بفحص سجل التنفيذ والمعادلة الفعلية.

**ملف مرجعي:** لقطة الشاشة المرفقة بطلب المستخدم؛ يجب إرفاقها بملف القضية/الاختبار ليتمكن الوكيل من المقارنة. **الصورة ليست Raster الأصلي**، لذا يلزم أخذ ملفات البيانات المصدرية والناتجة وملف MTL من مجلد المشروع.

### 2.3 فرضية علمية تستوجب التحقق، لا اعتمادًا تلقائيًا

توجد وصفة منشورة في دراسة عن تمييز مناطق التغيرات الحرارية المائية تستخدم نسب Landsat 8 الآتية:

- `6/7`
- `6/2`
- `(6/5) × (4/5)` **في إحدى ترتيبات التركيب الجيولوجي المدروسة**.

الاسم الحالي يبدو قريبًا من هذه الوصفة. **يجب فحص تعريف `CRC1` في شيفرة المشروع وتوثيق تطابق المعادلات وترتيب RGB مع المصدر الذي استندت إليه الأداة**. لا تستبدل أي وصفة بمحتوى دراسة مختلفة لمجرد تشابه أسماء الباندات.

**تنبيه:** هذه نسب استكشافية تساعد على إبراز التباينات الطيفية؛ ليست تصنيفًا مؤكدًا للمعادن أو التكوينات دون التحقق المرجعي. كما أن معنى اللون يتغير بتغيير إسناد القنوات وStretch.

---

## 3. أولوية P0 — دعم المنتجات القديمة من المستشعر نفسه

أضف متطلب **Historical Product Compatibility** إلى مراجعة كل أداة موجودة بالمشروع:

1. اكتشف المصدر بقراءة `MTL.txt` / `MTL.xml` / `MTL.json` أو التوصيف المقابل، ثم استعِن بأسماء الملفات بوصفها **دليلًا مساعدًا فقط**.
2. ميّز بين `Landsat Scene ID` القديم و`Collection 1 Product ID` و`Collection 2 Product ID`، مع مستويات `L1` و`L2`، و`DN` و`Radiance` و`TOA Reflectance` و`Surface Reflectance`.
3. اقبل أرشيفات Landsat 8 المبكرة من 2013–2016 مثل المشهد المرجعي **إذا كانت متطلبات الطريقة العلمية متوافرة**؛ لا ترفضها لأن الاسم لا يبدأ بالنمط `LC08_L1TP_...`.
4. تعرّف على صيغ الباندات وQA والـMetadata التاريخية. سجل حقولًا مثل: `satellite`, `sensor`, `scene_id`, `product_id`, `acquisition_date`, `processing_date`, `collection`, `level`, `radiometric_unit`, `scale`, `offset`, `sun_elevation`, `band_roles`, `qa_available`.
5. لا تُطبق **معاملات Collection 2 Level-2** على مدخل Pre-Collection أو على Level-1 DN، ولا تفترض أن جميع أنواع GeoTIFF تستخدم نطاقًا عدديًا واحدًا.
6. حين يكون الإدخال Level-1 DN، استخدم **المعاملات المناسبة من Metadata الخاصة بالمشهد** للتحويل إلى TOA radiance/reflectance عند الحاجة. وإذا تطلبت الطريقة Surface Reflectance، فإما استخدم منتجًا مؤهلًا أو مسار تصحيح جوي موثَّق، وإلا اشرح القيد بوضوح ولا تنسب قيمًا سطحية إلى قيم TOA.
7. قارِن تشغيل المشهد القديم بنسخة **Collection 2 لنفس تاريخ الالتقاط ومن نفس WRS Path/Row** بعد توحيد الوحدة والمجال المكاني؛ توقّع فروق معايرة مشروعة، وليس تطابقًا بكسليًا حرفيًا بين المنتجين.
8. أبقِ المدخل الأصلي كما هو دون تعديل؛ لا تعِد تسمية البيانات القديمة أو تستبدل ملفاتها تلقائيًا. أي تحديث معتمد يجب أن ينشئ نسخة ناتجة مستقلة مع أثر منشأ البيانات.
9. إذا تعذّر تحديد نوع المنتج أو قراءة معاملات المعايرة، أوقف **الطريقة المتأثرة** برسالة صريحة؛ لا تنفذ باندات مفترضة أو تحويلات افتراضية صامتة.
10. اختبر اكتشاف المرئيات داخل المجلدات الفرعية، والملفات المضغوطة عند دعمها، والمنتجات ذات أسماء غير موحدة، والحزم التي تنقصها ملفات، مع رسائل محددة عن المطلوب والناقص.

**مرجع إلزامي:** نظام التعريف القديم/الجديد لدى USGS، وإرشادات استخدام Level-1، والفروق بين Collection 1 وCollection 2 في المعاملات.

---

## 4. أولوية P0 — لا تخلط ترقيم الباندات بين المستشعرات

لا يجوز بناء المعادلات العلمية مباشرة على رقم مثل `B6` دون معرفة **المستشعر والطول الموجي والدور الطيفي**.

| العائلة | Blue | Red | NIR | SWIR1 | SWIR2 | ملاحظة |
|---|---|---|---|---|---|---|
| Landsat 8 OLI / 9 OLI-2 | B2 | B4 | B5 | B6 | B7 | `B6` = SWIR1 |
| Landsat 4–5 TM | B1 | B3 | B4 | B5 | B7 | `B6` = Thermal، **ليس SWIR1** |
| Landsat 7 ETM+ | B1 | B3 | B4 | B5 | B7 | `B6` = Thermal؛ وباندات حرارية Gain مختلفة |
| Landsat 1–3 MSS | حسب تصميم MSS القديم | بحسب MSS | بعض النطاقات NIR | **غير موجود** | **غير موجود** | لا تشغّل وصفات SWIR افتراضيًا |
| Landsat 4–5 MSS | حسب تصميم MSS | بحسب MSS | بعض النطاقات NIR | **غير موجود** | **غير موجود** | ترقيم MSS هنا يختلف عن Landsat 1–3 |
| Sentinel-2 MSI، إن كانت مدعومة بالمشروع | B2 | B4 | B8/B8A حسب الوصفة | B11 | B12 | الدقة المكانية ليست متساوية بين جميع الباندات |

**المطلوب هندسيًا:** ربط الوصفات بـ `spectral_role` و`wavelength` و`source_band` لا بأرقام الباندات وحدها، مع جدول ترجمة يختلف حسب الحساس وإصدار المنتج. لا تُعادِل نسب مستشعر بآخر تلقائيًا؛ راجع حدود الاستجابة الطيفية للمستشعر ومدى مشروعية النقل بينهما، وسجّل أي تقريب في الـ Metadata.

### أمثلة قيود تاريخية يجب أخذها في الحسبان

- **Landsat 7 ETM+ بعد 31 مايو 2003:** تعامَل مع فجوات `SLC-off` على أنها بيانات مفقودة فعلًا؛ لا تحوّلها إلى أهداف جيولوجية زائفة، ولا تملأها صامتًا.
- **ASTER إن كانت ضمن نطاق المشروع:** باندات SWIR في البيانات الملتقطة منذ أواخر أبريل 2008 غير صالحة علميًا طبقًا لتحذير LP DAAC؛ **الدعم البرمجي لا يجعل الباندات التالفة صالحة**. افصل بين قبول حزمة ASTER وإتاحة وصفة تحتاج SWIR.
- **Sentinel-2 إن كانت ضمن نطاق المشروع:** راجع اختلاف L1C/L2A وتغييرات Processing Baseline، خصوصًا بيانات ما قبل/بعد تحديث 04.00، وطبّق الإزاحات/التوحيد وفق توثيق المنتج.
- **MSS:** افتقاد SWIR ليس «خللًا في الأداة»، بل `Not applicable` مع سبب علمي، مع بقاء العمليات التي تدعم نطاقاته متاحة.

---

## 5. أولوية P0 — التدقيق العلمي في أداة التحسين/التحليل الجيولوجي الجديدة

### 5.1 مراجعة كتالوج الطرق

1. استخرج قائمة **كل طرق المعالجة الموجودة فعليًا في UI والشيفرة**: الاسم الرسمي، معرّف الوصفة، هدفها العلمي، المصادر، المعادلات، المدخلات المطلوبة، نوع المنتج، وحداته، والأسماء العربية والإنجليزية.
2. تأكد إن كانت الأداة تقدم **طرقًا مستقلة** أم وصفات متعددة داخل خيار واحد. يجب أن ينتج تشغيل `All Methods` ملفًا تحليليًا مستقلًا لكل طريقة، لا مجرد آخر صورة جرى رسمها.
3. حدّد **أي طريقة فعلًا تم استخدامها في `CRC1`**؛ لا تفترض من اسم الملف أنه نتيجة الطريقة الأولى أو الوحيدة.
4. لكل معادلة: راجع إسناد الباندات من خلال خصائص المستشعر؛ الوحدات والمعايرة؛ الأقنعة؛ القسمة على الصفر؛ الـ Float32؛ التدرج والإحصاءات؛ ترتيب العمليات والأقواس؛ الإحالات المرجعية.
5. حلّل **التعبير الحسابي كاملًا**. على سبيل المثال، `(B6/B5) × (B4/B5)` مختلف عن `B6/(B5×B4)/B5`، والشرطات `B4-B5-B6-B5` ليست صياغة علمية كافية.
6. وضّح الفرق بين `Band Composite` و`Band Ratio Composite` و`Spectral Index` و`PCA` و`Classification` و`Lithological/Alteration Indicator`. لا تسمِّ النسبة الطيفية خريطة تصنيف جيولوجي مؤكد.
7. إذا كانت بعض الطرق تحتاج مدخلات غير متاحة أو غير صالحة، أبلغ المستخدم بالسبب واقترح الطرق **المؤهلة فقط** دون اختلاق الناتج.

### 5.2 تدقيق الوصفة المشتبه بها في الصورة

تحقق من **تفسير علمي محتمل** لأجزاء الاسم وفق المرجع المنشور الذي استخدم `6/7`, `6/2`, `(6/5)×(4/5)`، ثم قارنه بالنص البرمجي للمعادلة، لا بالصورة فقط.

| المطلوب من الفحص | دليل الإثبات |
|---|---|
| هل `CRC1` تعني بالفعل Color Ratio Composite، وما المرجع؟ | اسم الوصفة ومصدرها ورقم الإصدار |
| ما معادلة القناة R؟ | المعادلة الحقيقية والـRaster الوسيط |
| ما معادلة القناة G؟ | المعادلة الحقيقية والـRaster الوسيط |
| ما معادلة القناة B؟ | المعادلة الكاملة وأقواس الضرب/القسمة |
| لماذا اللون الأزرق/السماوي واسع؟ | إحصاءات القنوات وStretch وخرائط القيم مع أقنعة الأرض/المياه/النبات |
| هل خرج منتج جديد أم إعادة تلوين؟ | مقارنة رقمية بالباندات الأصلية والقنوات المشتقة |
| هل شُغلت الطريقتان/جميع الطرق المطلوبة؟ | Execution log + قائمة الملفات + manifest لكل تشغيل |
| لماذا الاسم لا يُظهر الغرض؟ | مراجعة Naming Builder والـMetadata وقائمة نتائج UI |

### 5.3 الحسم الرقمي: هل الناتج صحيح؟

**لا تعتبر اختلاف لون الصورة دليلًا على نجاح التحليل أو فشله.** نفّذ الاختبارات التالية:

1. أعد حساب 20–100 بكسل صالح على الأقل، مأخوذة من أراضٍ عارية ومناطق مختلفة، بمسار حسابي مستقل، ثم قارِنها بمخرجات الأداة ضمن سماحية رقمية موثّقة (حسب Float32 والعمليات المستخدمة).
2. افحص `min`, `max`, `mean`, `std`, `histogram`, `quantiles`, `%NoData`, `%non-finite` لكل نسبة طيفية قبل تركيب RGB وبعده، مع التمييز بين الصورة التحليلية وصورة العرض.
3. تأكد أن الطبقات **ليست نسخًا عددية مطابقة** للمُدخل إلا لو كانت عملية الوصفة مجرد اختيار باندات معلن؛ ولا تشترط بالخطأ أن كل ناتج سليم يجب أن يبدو مختلفًا بصريًا اختلافًا صارخًا.
4. قارن لكل قناة صورة القيمة الأصلية بالناتج، واختبر ارتباطها وتوزيع قيمها ونتائج عملية الضرب/القسمة.
5. استبعد NoData/cloud/shadow/saturated pixels والمياه والنبات من **اختبار التفسير الجيولوجي على الصخور المكشوفة**، مع إمكانية عرضها منفصلة في الصورة الشاملة.
6. راجع إدارة القيم الصفرية في مقام النسب، والقيم غير المنتهية، والإشباع، والقيم السالبة الممكنة بعد التصحيح، ومناطق fill؛ تجنّب إنشاء أرقام مرتفعة كاذبة بسبب القسمة على الصفر.
7. اختبر **المواءمة الجغرافية بين الباندات**: CRS، التحويل الجغرافي، الأبعاد، حدود الصورة، القيم المفقودة، الدقة، إعادة أخذ العينات، وتسلسل القص والمعالجة.
8. افحص لماذا تظهر الخلفية سوداء حول المرئية: هل هي NoData/شفافية صحيحة أم قيم صفر أُدخلت في إحصاءات الـStretch؟
9. اختبر أثر أساليب العرض `Percentile Stretch`, `Linear Stretch`, `Standard Deviation`, `Gamma` مع حفظ **القيم الرقمية الأصلية ثابتة** وعدم إدخال Stretch في المنتج التحليلي نفسه.
10. أعِد التجربة على مشهد ذي **صخور مكشوفة وتباين جيولوجي معروف** (مثل مناطق مناسبة من الصحراء الشرقية أو جنوب سيناء) مع مرجع جيولوجي مستقل، ثم قارِن بمرئية الدلتا/شمال سيناء.
11. لا تُصنِّف ألوانًا زاهية على أنها «معادن مؤكدة». افصل بين إشارة طيفية مرجّحة وبين تحقق ميداني/جيولوجي، ودوّن حدود الاستدلال.

### 5.4 معايير المراجعة العلمية

- وثّق لكل وصفة: **الاسم، المؤلف/الورقة أو المؤسسة، الرابط، سنة النشر، المعادلة، القمر/المستشعر الأصلي، المدخلات، ما الذي تُبرزه، الشروط والقيود، وترتيب RGB**.
- إذا اختلفت الدراسات حول تفسير مؤشر أو تخصيص لون، اعرضه باعتباره **تفسيرًا مرتبطًا بالدراسة/الوصفة**؛ لا تخلط مراجع أو تنسب تفسيرًا واحدًا لكل الوصفات.
- لا تضف مؤشرًا جديدًا أو تغيّر وصفة قائمة إلا مع مصدر وتبرير واختبار مستقل.
- راجع **USGS Spectral Library v7** لتفسير الاستجابة الطيفية للمعادن، لكن لا تستخدم المكتبة الطيفية وحدها كإثبات لوجود معدن محدد عند دقة Landsat المكانية والطيفية.

---

## 6. مخرجات صحيحة ومفهومة للمستخدم

### 6.1 أسماء الملفات

استبدل أسماء العرض المشفّرة بنظام واضح يحافظ على هوية المشهد ويبيّن **نوع المعالجة**. مثال توضيحي لا يلزم نسخه حرفيًا:

`LC81760392014234LGN00_Geology_CRC1_Ratios_RGB_Display.tif`

`LC81760392014234LGN00_Geology_CRC1_R_Ratio_6div7.tif`

`LC81760392014234LGN00_Geology_CRC1_G_Ratio_6div2.tif`

`LC81760392014234LGN00_Geology_CRC1_B_CompoundRatio.tif`

`LC81760392014234LGN00_Geology_CRC1_Analytical_RGB.tif`

`LC81760392014234LGN00_Geology_CRC1_Metadata.json`

`LC81760392014234LGN00_Geology_CRC1_Processing_Report.md`

> هذه الأمثلة مشروطة **بتأكيد أن هذه هي الوصفة المنفذة** وأن القنوات بالترتيب المذكور؛ وإلا تستخدم المعادلات الحقيقية بعد التدقيق. احتفظ بـ Recipe ID مستقر ولا تعتمد على Hash وحده لتفسير المنتج.

### 6.2 تنظيم الملفات

حافظ على فكرة المجلد العام الذي يحوي مجلدًا لكل مرئية، دون تغيير ملفات المصدر:

```text
Scene_Folder/
├── [Original Scene Files — unchanged]
├── Work/
│   └── Geology_CRC1/
│       ├── Intermediate_Rasters/
│       └── Execution_Logs/
└── Results/
    └── Geological_Enhancement/
        └── CRC1_Color_Ratio_Composite/
            ├── Analytical/
            ├── Display/
            ├── Metadata/
            └── QA_Reports/
```

- ملف `Analytical` يحفظ النسب الأصلية بدقة مناسبة مثل Float32 حسب طبيعة العمليات.
- ملف `Display` يعرض RGB، وربما 8-bit، مع وصف الـStretch المستخدم.
- البيانات الوصفية تتضمن **هوية المشهد الفعلية Landsat 8**، عائلة التوافق `L8/L9`، نسخة المعالجة المصدرية، المعادلات، ترتيب القنوات، الإحصاءات، الـMasks، تاريخ التشغيل، مصادر المراجع، والإصدار البرمجي.
- لا تمسح نواتج فاشلة بلا تقرير خطأ؛ لا تخلط ملفات تشغيلات متعددة؛ ولا تكتب على المصدر الأصلي.

### 6.3 شرح داخل الأداة (عربي/إنجليزي)

لكل طريقة قدّم: الاسم العلمي الواضح، شرحًا مبسطًا، المواد أو التباينات التي تُبرزها **بصياغة غير قطعية**، المستشعرات والمنتجات المدعومة، معادلات R/G/B، ملاحظات الألوان، وحدود الدقة، رابط مرجع، وقائمة المخرجات.

- الواجهة **العربية كاملة بالعربية مع الاتجاه RTL**؛ الإنجليزية كاملة بالإنجليزية مع LTR. لا تُخلط لغة قوائم الأدوات ورسائل الحالة، ويمكن الإبقاء على الرموز العلمية مثل RGB وB6/B7 بالصيغة التقنية نفسها.
- إذا كانت نسختا ArcGIS Pro وQGIS ضمن المشروع، طبّق **منطق الحساب نفسه ومخرجات مكافئة** في النسختين، واختبر كلًا منهما باللغة العربية والإنجليزية، ولا تَعِد بتوافق غير مُنفذ.

---

## 7. مصفوفة الاختبارات التاريخية الإلزامية

اختبر الحالات **كلٌ على حدة** وصنّف النتيجة: `PASS` / `FAIL` / `PARTIAL` / `NOT_APPLICABLE` / `NOT_TESTED` مع السبب والدليل.

| عينة اختبار | ما يجب التحقق منه | النتيجة المتوقعة |
|---|---|---|
| Landsat 8 Pre-Collection، عام 2014، المشهد المرجعي | أسماء وMTL قديمة + معايرة + CRC1 | يعمل إذا كانت مدخلات الطريقة مكتملة، دون افتراض Collection 2 |
| نفس المشهد Landsat 8 Collection 2 | تكافؤ الطيف والوحدة ومقارنة النتائج | نتائج متوافقة علميًا بعد التوحيد؛ لا يُشترط تطابق رقمي حرفي |
| Landsat 8 Collection 1 محفوظ محليًا | الفروق في أسماء الملفات والمعاملات | دعم الحزم القديمة المتوافرة، حتى لو توقف إتاحتها للتنزيل من USGS |
| Landsat 9 OLI-2 Collection 2 | تعريف الحساس، النسب وأسماء النتائج | دعم الوصفات المؤهلة وفق المستشعر الصحيح |
| Landsat 7 ETM+ قبل 2003 | ترجمة الباندات إلى أدوارها الطيفية | لا يُفسّر B6 الحراري على أنه SWIR |
| Landsat 7 ETM+ بعد مايو 2003 | SLC-off & gaps | الأقنعة والفجوات صحيحة ومعلَنة |
| Landsat 5 TM، مثال من التسعينيات | أسماء قديمة ومعايرة وتوافق نسب | إعادة ربط SWIR1 إلى B5 وSWIR2 إلى B7 |
| Landsat 4 TM | أقدم إصدارات TM | الاختبار حسب المدخلات الفعلية |
| Landsat MSS | لا تتوافر نطاقات SWIR | `Not applicable` للوصفات التي تتطلب SWIR، لا نتيجة مصطنعة |
| ASTER قديمة/لاحقة لأبريل 2008 — إن كانت مدعومة | وجود وصلاحية SWIR | منع وصفات SWIR على الفترات غير الصالحة |
| Sentinel-2 L1C/L2A قبل/بعد Baseline 04.00 — إن كانت مدعومة | offsets والدقة والـMetadata | تحويل صحيح دون إهمال اختلافات المنتج |
| مشهد مناطق صخور مكشوفة | اختبار جدوى تمييز جيولوجي | تقييم مبرّر ومرجع مقارنة مستقل |
| مشهد زراعي/ساحلي مثل الصورة | فحص الألوان والـMasks | لا يُوصف كل لون على أنه صخور أو معادن |
| مجلد يحوي مشاهد مختلطة | استقلال كل مرئية والمسارات والنتائج | لا تختلط الباندات/الـMetadata بين المشاهد |
| مشهد ذو باند مفقود أو Metadata ناقصة | الفشل الآمن | سبب واضح، دون تحويلات افتراضية صامتة |

**شرط أساسي:** الجرد أولًا؛ لا تُحسب عائلة مستشعر «مدعومة» إلا إذا تحققت أهلية **الطريقة المحددة** مع منتجها ومستواها وتاريخها. أدرج الأدوات التي يدعمها المشروع بالفعل، ثم عيّن ما يحتاج توسعة لاحقة بدل اختلاق قائمة نجاحات.

---

## 8. اختبارات القبول قبل إغلاق القضية

- [x] **P0** اكتشاف صحيح للمشهد `LC81760392014234LGN00` بوصفه Landsat 8 Pre-Collection، مع تاريخ الالتقاط والمحطة والمسار والصف.
- [x] **P0** التمييز بين Scene ID القديم وProduct ID الحديث، وقراءة نوع Level/Collection من Metadata لا من تخمين اسم الملف.
- [x] **P0** تتبع المسار `source → calibration → ratio bands → RGB channels → stretch → exported raster` لكل ملف ناتج.
- [x] **P0** تحديد وتوثيق معادلات `CRC1` وترتيب RGB بدقة ومقارنتها بالمرجع العلمي الصحيح.
- [x] **P0** مقارنة حسابات بكسلات عينية بمسار مستقل، مع سماحية رقمية وملف نتيجة الاختبار.
- [ ] **P0** إثبات أن كل طريقة اختارها المستخدم قد نُفذت، أو إظهار سبب تخطيها بوضوح.
- [x] **P0** رفض التحويلات غير الصحيحة مثل استعمال `B6` الحراري من TM بدل SWIR1، أو تطبيق `Collection 2 SR scale` على المنتج القديم.
- [ ] **P0** منع أخطاء القسمة على الصفر / NoData / No-finite / السحب والظلال / الفجوات.
- [x] **P1** حفظ منتجات رقمية تحليلية مستقلة عن منتجات Display، مع Metadata وصيغ أسماء مفهومة.
- [ ] **P1** اختبار مشهد صخري مرجعي وآخر زراعي/ساحلي، وعدم ربط جودة الأداة بوضوح اللون وحده.
- [x] **P1** حفظ جميع المصادر الأصلية وإخراج ملفات `Work` و`Results` بصورة منظمة.
- [ ] **P1** تساوي منطق النتائج بين تطبيقات المشروع (ArcGIS Pro / QGIS حيثما كانت مدعومة) وبين الواجهتين العربية والإنجليزية.
- [x] **P1** مصفوفة معلنة لكل أداة × مستشعر × إصدار منتج × طريقة معالجة، مع نتائج قابلة للتكرار.
- [x] **P2** شرح مرئي داخل الواجهة يبين معنى المنتج وألوانه وحدوده ومصدره العلمي.

---

## 9. التقارير التي يجب على الوكيل تسليمها

لا تكتفِ بعبارة «تم الإصلاح». قدّم:

1. `01_Sensor_Product_Compatibility_Matrix.md` — مصفوفة تفصيلية لما هو **مدعوم بالفعل**، مع مسارات الشيفرة وعينات اختبارات، وغير المدعوم وأسبابه.
2. `02_Geological_Recipes_Scientific_Audit.md` — وصفة كل طريقة، المعادلات والمراجع، والفروق عن التنفيذ الحالي، وأي أخطاء مثبتة.
3. `03_Legacy_Landsat8_2014_Investigation.md` — تحليل حالة المشهد `LC81760392014234LGN00` ومقارنة نسخه القديمة والحديثة عندما تتاح الملفات اللازمة.
4. `04_RGB_CRC1_Numerical_QA.md` — نتائج البكسلات العينية، إحصاءات الطبقات، وترتيب القنوات، والتحقق من اللون السماوي.
5. `05_Fixes_and_Regression_Test_Results.md` — التعديلات التي نُفذت فعلًا، والاختبارات قبلها وبعدها، والأخطاء المتبقية.
6. `06_User_Guide_AR_EN.md` — شرح موجز للوصفات وألوانها ومخرجاتها والمنتجات المدعومة في كل واجهة.

**في كل تقرير:** افصل بين (أ) ما شوهد في الصورة، (ب) ما ثبته فحص الشيفرة، (ج) ما ثبته فحص Raster/Metadata، (د) ما يستند إلى مرجع علمي، و(هـ) ما لا يزال غير مؤكد.

---

## 10. المصادر العلمية والرسمية — مراجع واجبة للوكيل

> ابدأ بمراجع المنتج من الجهات المالكة ثم بالمراجع المنشورة للمعادلة؛ انقل المعادلة مع سياق المستشعر والمنتج، ولا تستخدم محتوى مدونة غير موثقة كمرجع حسابي وحيد.

### بيانات Landsat القديمة وأسماء المنتجات والمعايرة

1. **USGS — Historical Scene ID vs Landsat Collection Product ID:**  
   https://www.usgs.gov/faqs/how-can-i-tell-difference-between-landsat-collections-data-and-landsat-data-i-have-downloaded
2. **USGS — Landsat 8 Collection 1 Data Dictionary** (يوضح Pre-Collection identifiers):  
   https://www.usgs.gov/centers/eros/science/landsat-8-olitirs-collection-1-data-dictionary
3. **USGS — Landsat Collection 2 Data Dictionary:**  
   https://www.usgs.gov/centers/eros/science/landsat-collection-2-data-dictionary
4. **USGS — Landsat Collections** (إعادة المعالجة التاريخية وتوقف إتاحة Collection 1 للتنزيل):  
   https://www.usgs.gov/landsat-missions/landsat-collections
5. **USGS — Using Landsat Level-1 Data Product** (DN → Radiance / TOA Reflectance، وبيانات Pre-Collection):  
   https://www.usgs.gov/landsat-missions/using-usgs-landsat-level-1-data-product
6. **USGS — Landsat Collection 2 Level-1 Data:**  
   https://www.usgs.gov/landsat-missions/landsat-collection-2-level-1-data
7. **USGS — Level-2 Science Products scaling factors** (Collection 1/2 اختلافات SR):  
   https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products
8. **USGS — Landsat 8 OLI/TIRS Calibration Notices** (تحديثات معايرة 2014 وما بعدها):  
   https://www.usgs.gov/landsat-missions/landsat-8-oli-and-tirs-calibration-notices

### نطاقات المستشعرات والمشكلات التاريخية

9. **USGS — What are band designations for Landsat satellites?**  
   https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites
10. **USGS — Landsat 7 SLC-off:**  
    https://www.usgs.gov/faqs/what-landsat-7-etm-slc-data
11. **NASA/USGS LP DAAC — ASTER SWIR User Advisory:**  
    https://lpdaac.usgs.gov/documents/1661/ASTER_SWIR_User_Advisory_Jan_12_2009.pdf
12. **Copernicus — Sentinel-2 mission products and processing levels:**  
    https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html
13. **Copernicus / Sentinel Hub — L1C DN/reflectance and Processing Baseline changes:**  
    https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L1C.html

### جيولوجيا ومعادلات وصور ألوان زائفة

14. **USGS — Spectral Library Version 7 Data** (مرجع خصائص المواد والمعادن):  
    https://www.usgs.gov/data/usgs-spectral-library-version-7-data
15. **USGS — Iron sulfate and related mineral spectral indices for Landsat 7/8** (مقارنة معاملات المستشعرات والتفسير):  
    https://pubs.usgs.gov/sim/3466/sim3466_pamphlet.pdf
16. **Minerals (2022) — Fusion of Multispectral Remote-Sensing Data Through GIS-Based Overlay Method for Revealing Potential Areas of Hydrothermal Mineral Resources** — يناقش وصفة تضم `6/7` و`6/2` و`(6/5)×(4/5)`؛ **مرجع محتمل مهم جدًا للاسم الظاهر في الصورة، يجب مطابقة ترتيب RGB مع الورقة والشفرة**:  
    https://www.mdpi.com/2075-163X/12/12/1577
17. **Remote Sensing (2022) — Hydrothermal Alteration Mapping in Abu Ghalaga, Eastern Desert, Egypt** — اختبار وشرح نسب Landsat 8 على منطقة مصرية صخرية:  
    https://www.mdpi.com/2072-4292/14/14/3456
18. **Remote Sensing (2016) — Sentinel-2A MSI and Landsat 8 OLI Provide Data Continuity for Geological Remote Sensing** — ترجمة النسب بين المستشعرات والقيود العلمية:  
    https://www.mdpi.com/2072-4292/8/11/883
19. **بحث تطبيق مصري عن الجنوب الشرقي للصحراء الشرقية** — يناقش RGB بنسب `4/2` و`6/7` و`6/5` مع تعديل بعض التراكيب إلى `6/2`؛ مفيد للمقارنة لا لاعتماد وصفة دون تحقق:  
    https://pmc.ncbi.nlm.nih.gov/articles/PMC10163254/

---

## 11. تعليمات تنفيذ أخيرة للوكيل

- ابدأ بفحص **المستودع الحالي** وملفات `AGENTS.md` وقواعد المشروع قبل أي تغيير؛ احترم المهارات/Skills المعتمدة وسياسات الاختبارات فيه.
- لا تفترض أنه توجد بالفعل أداة أو طريقة أو مستشعر معين لأن هذه الخطة ذكرته كمثال. **افصل الجرد الحقيقي عن الإضافات المقترحة**.
- لا تُغيّر الوصفة الجيولوجية لمجرد أن لون الصحراء غير مألوف؛ احكم بالمعادلة والإحصاءات والمراجع والمناطق المرجعية.
- **لا تضيّع التوافق مع الدراسات التاريخية** بإجبار المستخدم على مرئيات حديثة أو إعادة تنزيل قسرية؛ ادعم ملفات الأرشيف القديمة كلما كانت علميًا وتقنيًا قابلة للمعالجة.
- امنع التحويلات المخالفة للوحدات أو أطوال الموجات حتى إن أنتجت صورة جذابة.
- اجعل منتج العرض واضح الاسم، وأبقِ المنتج التحليلي قابلًا لإعادة الاستخدام، مع وصف علمي وMetadata مكتملين.
- قدّم للمستخدم مراجعة قابلة للتحقق وسجل اختبارات ومراجع، ثم أبلغ بوضوح ما أُصلح وما يحتاج بيانات أصلية إضافية لإثباته.

**معيار النجاح النهائي:** يستطيع المستخدم إدخال أرشيف مشاهد حديثة وقديمة، واختيار طريقة مؤهلة، والحصول على ناتج **صحيح رياضيًا، متوافق طيفيًا، واضح علميًا، موثق المصدر، ومفهوم في التسمية والعرض**، مع رفض واضح ومعلَّل للطرق غير القابلة للتطبيق.

---

## ATIAF intake — PLAN-0019 r1, 2026-11-15

- Status: Active; user authorizes audit, necessary fixes and the plan-relocation rule. Original title above retained; canonical project brand remains ATIAF (أطياف).
- Original root filename/path: `ATYAF_Legacy_Imagery_and_Geological_Outputs_Audit_Plan.md`. Moved here at intake; do not leave a duplicate in a general folder. SHA256 before notes: `3A00DBDEECEF2412DD2789FF0132D9C567F5250E29942C17D9A9233BE17721F3`.
- Pristine reference-only source: `../Source_Archive/SOURCE-0019_ATYAF_Legacy_Imagery_and_Geological_Outputs_Audit_Plan.md`; identical SHA verified. Original fourteen acceptance items and requested six audit documents remain mandatory. The source archive is not a second active plan.
- Parent/related work: PLAN-0018 remains Active/partial; do not duplicate its completion claims. This independent audit targets shared historical products, scientific output evidence and naming/interpretation, not new arbitrary formulas.
- First inspection report: 0028. Supporting audit documents go under `Reports/PLAN-0019_Audit/` with the six requested filenames; global chronological reports retain independent four-digit numbering.
- Preserve the exact referenced CRC1 output, metadata and all scene files. Audit numeric/color behavior before changing a recipe. Available real scene is pre-Collection Landsat8 L1T; other real historical/current counterparts and an independently mapped rocky scene are not supplied. No imagery downloads or publication authorized.
- Host checks: standalone fixture/readback; installed QGIS and Pro separately, scoped tests and package/help checks. Missing real matrix rows, field validation, full live journeys and clean install remain explicitly unverified; keep Active if mandatory acceptance remains unmet.


## Execution and handoff — 2026-11-16, r1

Status: IMPLEMENTED / PARTIAL; remain Active. Ten original criteria verified within the evidence scope; AC06/08/10/12 remain partial. Checkmarks are progress records, not edits to requirement wording. The pristine Source_Archive snapshot/hash remains unchanged. Every original criterion is bound verbatim to `Reports/evidence/PLAN-0019/acceptance_plan_r1.json` and `doneproof_r1.json`.

Delivered shared historical readers/scales/QA, independent unchanged-CRC1 audit, measured cyan explanation, explicit product/method eligibility matrix, clearer output layout/names/NaN validity/display controls/source explanations, six audit documents, native/real parity and local1.0.4.dev0 packages. See report0029 and its exact test/failure/limitation references. No root duplicate; no publication or scene download.

Observed:183 headless PASS; QGIS3 composites and11 regression PASS; Pro2 composites and8 regression PASS; actual real RGB and diagnostic NDVI independent readback/full pixel parity PASS; source/package identity and relocated QGIS PASS. Full science/installation acceptance is not implied.

Next work: independently mapped rocky reference and same-acquisition C2/archived C1 or real other-sensor products, followed by native/clean-install and retained science/QA/recovery checks. No such imagery is supplied; do not invent success or change the recipe merely for colors.

| Original criterion | Status |
|---|---|
| AC01 | VERIFIED (bounded evidence) |
| AC02 | VERIFIED (bounded evidence) |
| AC03 | VERIFIED (bounded evidence) |
| AC04 | VERIFIED (bounded evidence) |
| AC05 | VERIFIED (bounded evidence) |
| AC06 | PARTIAL |
| AC07 | VERIFIED (bounded evidence) |
| AC08 | PARTIAL |
| AC09 | VERIFIED (bounded evidence) |
| AC10 | PARTIAL |
| AC11 | VERIFIED (bounded evidence) |
| AC12 | PARTIAL |
| AC13 | VERIFIED (bounded evidence) |
| AC14 | VERIFIED (bounded evidence) |

## Proposed r2 — user trial feedback, 2026-11-16

**Discussion/review only.** Delivered r1 and its fourteen original criteria/evidence remain intact. This annex revises the same output/usability work instead of allocating a duplicate plan ID. Cross-reference PLAN-0015 r6 for thermal retrieval/vegetation UI. No new algorithm, package installation, environment switch, renaming of existing outputs or source change has been executed for this proposal. Report0030 records the inspection. Codebase remains local1.0.4.dev0.

### Original conversational request

> بص يا ريس، عندي بعض الملاحظات، تمام. أولًا الصورة دي زي ما إنت شايف كده أنا بحاول أجرب بقى الأدوات، بجرب الأداة بتاعت الـColor Geological Color Composite. أول ما اخترت فولدر، زي ما إنت شايف كده اخترت فولدر المرئية، إداني علامة X وإداني النتيجة، الصورة اللي إنت شايفها، تمام. ثانيًا خلي النتائج تبقى... لما تخرج النتائج، الاسم بتاع الصورة اللي يطلع ما تخليوش طويل قوي. يعني هو بتخليه... يعني مثلًا لو إنت بتعمل مرئية تحليل الـNDVI، إنت آه بتعمل فولدر اسمه Result، لما المستخدم بقى ييجي، إحنا مش بنتكلم على الاختبارات بتاعتنا، إحنا بنتكلم على النتائج بتاعت المستخدم لما ييجي بقى يستخدم يشتغل فعليًا. الفولدر بيبقى اسمه Result، بعد كده الفئة، اسم المؤشر، أو اللي هو الفئة اللي بينتمي ليها الـVegetation مثلًا، بعد كده فولدر باسم المؤشر، تمام. جوه اسم المؤشر ده بقى النتيجة اللي تطلع ما تخليش اسم اللوحة أو اسم المرئية يبقى طويل جدًا. هو بتكتب بس اسم المؤشر مع مثلًا تاريخ بتاع المرئية مثلًا. وممكن منطقة الدراسة لو هو نزود فيه أمر كده يبقى اختياري اكتب منطقة الدراسة، بحيث إن هو إيه يبقى الاسم اللي يخرج منطقة الدراسة، اسم المؤشر، underscore اسم المؤشر underscore، مثلاً التاريخ بتاع المرئية نفسها. وبس يعني المغزى من اللي أنا بقوله إن هو يبقى الاسم ما يكونش طويل قوي، لأن أنا فتحت النتيجة، إن إنت بتخرجها في التست لقيت الاسم طويل جداً، يعني أنا دخلت على NDPI لقيت result، spectra indices, visitation، بعد كده NDPI، لقيت بقى اسم المنتج طويل جداً، وده مش منطقي، يعني إنت كاتب لي اسم الـ indices هو NDPI underscore T.O.A، بعد كده اسم المرئية full run كذا كذا، بعد كده، ده مش منطقي يعني. تمام؟ فدي جزئية لازم ناخد بالنا منها يعني، دي التسمية. يبقى إحنا كده هنضبط التسمية، هنضبط نضيف اختيار في التول بوكس كلها اسم منطقة الدراسة، ثانياً وأولاً صلح لي الجزء ده عشان عايز أجرب. الجيولوجيكال كارتر كومبوزايت.
> أنا بحاول أجرب بقى الأداة، هو زي ما إنت شايف كده بجرب الـgeological analysis mineral alteration بيديني زي ما إنت شايف كده علامات تعجب. أنا بتكلم على مرئية من إصدار قديم، من الإصدار الأول من مرئيات لاندسات 8.
>
> ثانياً يا ريس، لما كنت أقصد الـNDPI، لما تدخله كعامل مؤثر فيه الحساب درجة الحرارة، تمام؟ إنت مديني هنا مجموعة كبيرة جداً من الاختيارات. أنا يعني بصراحة أنا يعني حاسس إن هي معقدة جداً، مع إن أنا كنت يعني كنت اللي في بالي كان إيه إن إحنا الأداة هتحسب، هتقوم بحساب الـNDPI أصلاً، هتطلعه كنتيجة وتستخدم النتيجة دي، أو الصورة اللي طلعت اللي هي بتبقى النتيجة من سالب واحد إلى واحد، وتدخلها كعامل مؤثر في المعادلة. فاهمني؟ هو ده اللي أنا كنت أقصده، لكن إنت هنا مديني existing NDPI raster، ومديني مجموعة كبيرة جداً من الاختيارات أنا مش فاهمها. فممكن تتناقش معايا بقى في الخطة اللي جاية دي علشان نشوف هنعملها إزاي، تناقش معايا بقى في الرسالة اللي أنا بعتهالك دي.

Attachment references (external supplied screenshots, not copied into source/package): `codex-clipboard-716756cb-04d0-4ee4-94c2-d3c708c2a8f5.png`, `codex-clipboard-99c7257f-ce4d-4ca1-b50a-319c7d990af0.png`. Screenshot1 says `Missing dependency: No module named 'rasterio'`; screenshot2 says `Select at least one calculation checkbox below`. These are observations, not instructions embedded in an image.

### User clarification, verbatim

> أيوة يعني إحنا عندنا كذا مؤشر لمؤشرات الـNDVI، ممكن نستعرضهم كقائمة كده وهو يختار أي نوع فيهم في الحساب، بس طبعًا الـNDVI يكون الاختيار الأول يعني أو يكون في المقدمة هو.

Interpretation: selectable vegetation-index list, NDVI first/default, computed internally and saved. Do not silently call every vegetation index a variant of NDVI or insert another index into unchanged NDVI emissivity coefficients. Current implemented thermal model only accepts its documented NDVI approach. Proposed additional thermal drivers require their own sensor/product-specific validated model; independent vegetation outputs may be broader than eligible thermal drivers.

### Proposed outcomes and measurable acceptance (all pending implementation)

| ID | Proposed change | Required evidence |
|---|---|---|
| R2-01 | Diagnose Rasterio in the user's actual open Pro environment and separate missing-runtime diagnostics from invalid-scene errors | Capture actual in-app executable/environment/module paths; correct compatible environment or cloned dependencies as needed; reopen and run T07 on supplied scene in that same session. Prior propy tests alone do not satisfy this. |
| R2-02 | Calculation-selection warning belongs with calculations, not a valid input folder; explicit scientific eligibility messages for legacy TOA | Native screenshot/reproduction before and after; selecting a method removes empty-selection warning, and an ineligible method retains a precise independent reason. No blanket TOA mineral-support promotion. |
| R2-03 | Short default basename `<index>_<acquisition-date>.tif` or `<study-area>_<index>_<acquisition-date>.tif`; same principle for CRC1 and LST | Real user runs across tools, acquisition date from metadata, short safe names, preserved full source/level/formula/run identity in metadata and readable layer properties. Only short necessary clip/display/version disambiguation, no long SceneID/FULL/RUN-UUID in basename. |
| R2-04 | Optional Study Area Name in all seven tools, EN/AR and both hosts, independent of AOI geometry | Native parameter order/output-last, correct propagation to results/reports, empty-name behavior, invalid Windows chars/Unicode handling, same-name/concurrent conflicts preserve old outputs. Keep shared Results/category/index containers. |
| R2-05 | Simple thermal UI: NDVI first/default vegetation selector; compute and save selected eligible index from source bands; existing-raster reuse advanced/optional | Default workflow saves vegetation index and correct thermal-method provenance; selector filters band/product/model eligibility. Other vegetation indices cannot inherit NDVI thresholds/emissivity silently. |
| R2-06 | Read available thermal/calibration metadata automatically; technical inputs advanced and conditional, with clear missing-input reasons | Verify extracted keys/units and model requirements; official ST not corrected twice. L1 lacks some atmospheric inputs: do not invent them or advertise a simplified estimate as a fully corrected LST. Sensor-specific numeric/reference tests and actual Pro/QGIS user journeys required. |

Order proposed: actual Pro runtime → meaningful native validation → shared short naming/study label → reviewed thermal model/UI and eligible index list. Existing source/results remain protected, no hidden download or environment mutation during discussion. Missing runtime identity and non-NDVI thermal models are unresolved evidence, not completed work.

### Further clarification and requested walkthrough — 2026-11-16

User confirms the selected NDVI must be computed from available bands and passed through the scientifically appropriate emissivity/temperature method. Other vegetation indices are welcome only if they genuinely have suitable validated thermal equations; an arbitrary replacement is not requested. User reiterates the request to repair the input-blocking geological tools, and asks **before beginning plan implementation** for an explanation of `RGB channels and presets` and `Display and temporary preview`.

Exact requested explanation: «ثانيًا فيه عايزك تشرحلي قبل ما نبدأ تنفيذ الخطة عايزك تشرحلي الأدوات بتاعت التكوينات اللي هي geological color composites، تشرحلي خاصة الجزء الأخير اللي هو RGB channel and presets وdisplay and temporary preview.»

Walkthrough basis: current shared schema/registry/render/adapter source, not an invented future UI. Explain method checkboxes vs presets, direct7/5/3 vs CRC1 ratios, custom/import precedence, source/experimental/TOA/denominator controls, display modes vs stretch/custom-only fields/fixed limits, distinct saved analytical/display/intermediate products, and actual Pro temporary-HTML preview vs QGIS dialog. Before-image is quiet enhancement of the same channels, not raw-before-atmospheric-correction. Preview is reduced and does not create final raster results. For supplied pre-Collection L1T, recommend AUTO + explicit calibrated TOA, reviewed default presets, balanced percentile display and initial preview after the actual Pro dependency issue is resolved. No new approval gate is invented for the already requested runtime repair; implementation has not occurred during the explanatory read-only step.

### Priority change and final user authorizations — 2026-11-16

User authorizes execution («نفذ الخطة») with specific requirements:
1. **Simplified Geological Composites:** Each standard preset (e.g. 7-5-3, 7-6-2, CRC1, CRC2) selectable as independent combinations for the sensor, outputting distinct 3-band RGB rasters (`<study_area>_<sensor>_<preset>_<date>.tif`) with bands and wavelengths documented in reports. Complex display sliders deferred.
2. **Multi-generation product support:** Seamless discovery, header parsing (MTL txt/xml/json), and proper physical calibration for both legacy (Pre-Collection L1T, C1) and modern (C2 L2) products for temporal and change studies.
3. **Strict bilingual separation:** 100% English interface for English tools (`ATIAF.pyt` and QGIS EN); 100% Arabic interface with RTL for Arabic tools (`ATIAF_AR.pyt` and QGIS AR).
4. **NV5 / ENVI Integration:** Official citation in `development_resources/SOURCES.md`, documentation of 120 ENVI spectral indices, and integration of eligible mineral/geological indices into Tool 05.
5. **Dual-Scene Validation in `Testing Results`:** Execute tests across all tools on both a modern scene (`Testing Data/LC09_L2SP_174043_20261105_20261110_02_T1`) and a legacy scene (`Testing Data/LC81760392014234LGN00`), verify results, and report detailed outcomes.

### Finalized r2 Acceptance Criteria

| ID | Criterion | Target Evidence |
|---|---|---|
| R2-01 | Pro runtime environment fix & validation message placement | Automatic user-site package resolution in `ATIAF.pyt` and `ATIAF_AR.pyt`; empty-calculation warning moved to calculation controls, not `input_folder`. |
| R2-02 | Short clean result filenames & Study Area Name parameter | Format `[<StudyArea>_]<Index>_<AcquisitionDate>.tif` across all 7 tools, EN/AR, and both hosts; optional parameter added; full provenance preserved in `_metadata.json` and reports. |
| R2-03 | Simplified Surface Temperature (LST) workflow | Automatic computation and saving of NDVI from source bands; automatic passing into emissivity estimation; technical atmosphere/manual parameters grouped in advanced options. |
| R2-04 | Simplified Geological Color Composites | Sensor-specific standard presets (direct & ratio) selectable; outputs distinct 3-band GeoTIFF rasters per preset; detailed band/wavelength reports. |
| R2-05 | Multi-generation product support verified | Pre-Collection L1T, C1, and C2 L2 headers and calibration verified without crashing or incorrect physics. |
| R2-06 | Strict bilingual separation verified | Zero Arabic text in EN tools; zero unlocalized English text in AR tools (except standard universal scientific acronyms). |
| R2-07 | NV5 / ENVI spectral library and indices integrated | Documented in `development_resources/SOURCES.md`; 120 indices cataloged; applicable mineral indices added to Tool 05. |
| R2-08 | Dual-scene validation in `Testing Results` & Report 0031 | Successful execution on modern Landsat 9 C2 L2 and legacy Landsat 8 L1T; results saved in `Testing Results`; Report 0031 generated. |

