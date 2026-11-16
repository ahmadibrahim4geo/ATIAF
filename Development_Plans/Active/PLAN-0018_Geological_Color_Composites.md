# ATIAF — Geological Color Composites
## خطة تطوير موجّهة لوكيل البرمجة (Agent Development Plan)

**نوع المستند:** وثيقة متطلبات وخطة تنفيذ فقط — **ليست كودًا ولا تنفيذًا برمجيًا**  
**المشروع:** ATIAF — أدوات معالجة المرئيات والاستشعار عن بُعد  
**الوظيفة المقترحة:** Geological Color Composites / التراكيب اللونية الجيولوجية  
**المنصتان:** ArcGIS Pro + QGIS  
**اللغتان:** العربية (RTL) + English (LTR) لكل منصة  
**تاريخ إعداد الخطة:** 15 نوفمبر 2026  
**الحالة:** متطلبات تطوير يراجعها الوكيل عند بدء العمل.

---

## 1. الأمر الرئيسي الموجّه للـAgent

> **المطلوب منك:** افحص مشروع ATIAF الحالي، وبنيته، وأدواته الموجودة، وقواعد التطوير المعتمدة في جذر المشروع، ومهارات GIS المعتمدة. طوّر وظيفة مستقلة وظيفيًا بعنوان **Geological Color Composites** يمكن تشغيلها كأداة قائمة بذاتها أو دمجها ضمن مجموعة أدوات المعالجة الجيولوجية الموجودة، من دون تكرار منطق المعالجة. يجب أن تعمل على **ArcGIS Pro وQGIS**، ولكل منهما **واجهة عربية كاملة وواجهة إنجليزية كاملة**. نفّذ طريقتين واضحتين: **Direct RGB Band Composite** و**RGB Band Ratio Composite**؛ مع خيارات منفصلة ومحايدة لتحسين العرض اللوني. **لا تنفذ أي Classification تلقائيًا، ولا تفسر ألوان الصورة على أنها أسماء مؤكدة للصخور.** راجع المصادر العلمية والرسمية في نهاية هذه الوثيقة قبل اعتماد الصيغ والتركيبات. لا تُعدّل البيانات الأصلية، وأدرج اختبارات وظيفية وعلمية ولغوية لكلا النظامين. قبل البدء بالتنفيذ أعد ملخصًا بما اكتشفته في المشروع، والفجوات، وخطة الدمج، ثم نفّذ وفق قواعد المشروع.

**تنبيه على نطاق التكليف:** هذا المستند *يصف ما سيطوّره الوكيل لاحقًا*. إنشاء هذا الملف لا يعني أن الأداة بُرمجت أو عُدّلت الآن.

## 2. الهدف العلمي والنتيجة المرئية المطلوبة

- إظهار الاختلافات **الطيفية** بين الوحدات الصخرية والبنى الجيولوجية عبر صورة فضائية ملونة **مستمرة**، تبقى فيها الأودية والجبال والملامح السطحية مرئية.
- توفير نمط عرض «جيولوجي طبيعي نسبيًا» بألوان متوازنة، ونمط عرض أقوى عند الحاجة. لا يعني «طبيعي نسبيًا» أنه True Color؛ فالتركيب قد يحتوي حزم SWIR أو NIR.
- فصل **طريقة اشتقاق قيم البكسل** عن **كيفية عرض قيمه بالألوان**. اختلاف شدة الألوان أو التشبع لا يثبت وجود تصنيف.
- الهدف هو **Visual Lithological Discrimination** وليس إنشاء خريطة فئات أو تحديد أسماء الصخور آليًا.
- الناتج RGB يمكن أن يكون ذا ألوان شديدة أو هادئة في أي من الطريقتين، بحسب الاختيار الطيفي والتحسين والتصحيح المسبق.

### توضيح لا بد أن يظهر في دليل المستخدم

| المفهوم | المدخلات | ما يحدث | شكل الناتج | هل هو Classification؟ |
|---|---|---|---|---|
| Direct RGB Band Composite | 3 حزم أصلية | إسناد كل حزمة إلى R وG وB | صورة متعددة الألوان متصلة | لا |
| RGB Band Ratio Composite | 3 نسب/معادلات | حساب كل قناة ثم تجميعها في RGB | صورة متعددة الألوان متصلة | لا |
| Contrast / Color Enhancement | أي RGB سابق | تغيير أسلوب العرض أو تصدير نسخة محسنة | درجات هادئة أو قوية | لا |
| Lithological Classification | نموذج تصنيف وفئات | إسناد كل بكسل إلى فئة محددة | خريطة أصناف ذات تسميات | **نعم — خارج نطاق هذه الأداة** |

## 3. الوظائف الأساسية المطلوبة

### 3.1 الطريقة الأولى — Direct Geological RGB Composite

1. استلام مرئية Multiband واحدة، أو حزم منفصلة تنتمي إلى **المشهد ذاته**؛ ولا تدمج مشاهد مختلفة دون إجراء إعداد صريح.
2. قراءة أسماء الحزم وترقيمها وأطوالها الموجية من metadata، وربط **رقم الحزمة العلمي** بأسماء الملفات/الفهارس الفعلية؛ لا تفترض أن رقم موضع الحزمة داخل الملف هو رقم الحزمة في المستشعر.
3. إسناد الحزم الثلاث إلى Red / Green / Blue بالترتيب وبصورة قابلة للتعديل.
4. دعم Presets موثقة لكل مستشعر + اختيار Manual RGB + حفظ Custom Presets.
5. إظهار Preview مؤقتة سريعة دون كتابة ناتج نهائي، مع مقارنة قبل/بعد.
6. إخراج Raster متعدد الحزم مع الإسناد الجغرافي، وإمكانية إخراج نسخة RGB مرئية بنفس إعدادات العرض.

**تركيبات أولية للبحث والاختبار (RGB بالترتيب):**

- **Landsat 8/9 — 7,5,3:** تركيب منشور لدراسة Duwi Shear Belt بالصحراء الشرقية، مرجع توثيقي أولي صالح للإضافة بعد التحقق العملي [S11].
- **Landsat 8/9 — 7,6,2:** خيار تجريبي لإبراز التباينات الأرضية؛ **لا تصفه بأنه يحدد أنواع صخور محددة**. قيّم شكله مقارنة بالمراجع قبل إدراجه ضمن القائمة المعتمدة.
- **Sentinel-2 — 12,11,4 و12,11,2:** تركيبات مقترحة للاختبار؛ **لا تُعتمد كـPresets علمية نهائية إلا بعد مراجعة مرجع موثوق لكل وصف استخدام**.
- **ASTER — 4,6,8:** تجربة تركيب جيولوجي من SWIR **للمشاهد التاريخية الصالحة فقط**؛ يجب تطبيق تحذير ASTER الوارد بالقسم 8.
- **Custom:** أية ثلاث حزم متاحة ومتوافقة يختارها المستخدم مع عرض الاسم العلمي لكل حزمة.

**ممنوع:** افتراض أن لونًا معينًا يساوي «جرانيت» أو «حجر جيري» في جميع المناطق والمشاهد.

### 3.2 الطريقة الثانية — Geological RGB Band Ratio Composite

1. حساب نسبة أو معادلة طيفية مستقلة لكل قناة من R وG وB، ثم عرض الناتج في RGB.
2. دعم نسب بسيطة `A/B` ومعادلات مركبة موثقة بعد مراجعة علمية، مع التحقق من الحزم والبيانات قبل التشغيل.
3. إجراء الحسابات على بيانات مناسبة علميًا، والأفضل reflectance مصححة مع توضيح نوع المنتج.
4. التعامل صراحة مع المقامات الصفرية وشبه الصفرية، وNoData، والقيم اللانهائية، وعدم تحويلها إلى ألوان زائفة أو نتائج مضللة.
5. الاحتفاظ بكل قناة محسوبة في الناتج التحليلي العائم عند الحاجة، وعدم تقييدها مبكرًا إلى 8-bit.
6. تقديم مكتبة Presets مدعومة بمراجع؛ لا تستورد نسبًا من مستشعر مختلف من دون تحويل/تحقق من مواضع الحزم الطيفية.

**تركيب منشور وموثق لـLandsat 8/9 من دراسة Duwi [S11]:**

| قناة RGB | المعادلة |
|---|---|
| R | `B6 / B7` |
| G | `B6 / B2` |
| B | `(B4 / B5) × (B6 / B5)` |

**تركيب منشور آخر بنفس الدراسة [S11]:** `R = B4/B6`، `G = B4/B2`، `B = B6/B7`.

**تركيب ASTER منشور بمنطقة الفواخير بمصر [S12]:** `R = (B2+B4)/B3`، `G = (B5+B7)/B6`، `B = (B7+B9)/B8`؛ مقصور على بيانات ASTER SWIR التاريخية الصالحة وبالتحقق من الوحدات والتصحيح والمرجع.

**معيار قبول كل Preset:** اسم عربي وإنجليزي؛ المستشعر/المنتج؛ ترتيب القنوات؛ المعادلات؛ الهدف العلمي المحتمل؛ مرجع كامل ورابطه؛ ملاحظات القيود؛ وحالة الاعتماد (`verified` / `experimental`).

### 3.3 تحسين عرض الألوان — Display Enhancement (مستقل عن الطريقتين)

يجب أن يكون هذا **مجموعة إعدادات عرض** لا «الطريقة الثالثة لحساب صخور»:

- `Natural-looking / هادئ`: Stretch محافظ وتشبّع معتدل لإبراز التضاريس مع التباينات.
- `Balanced / متوازن` (**الافتراضي المقترح**): تحسين ملحوظ دون إفراط.
- `Enhanced / قوي`: تباين أعلى عند الحاجة مع تحذير أن الألوان تفسيرية لا فئات.
- `Custom / مخصص`: حدود العرض، Percent Clip، Gamma، Saturation بحسب القدرات المثبتة في المكتبات المضيفة.
- عدم تطبيق histogram enhancement بصورة مدمرة على بيانات reflectance أو ratio الأصلية؛ احفظ العرض أو نسخة عرض منفصلة عند اختيار المستخدم.
- واجهة المعاينة تعرض **التركيب والطريقة وإعدادات العرض** المستخدمة حتى لا يختلط سبب التباين.

## 4. دعم المستشعرات ومصادر الإدخال

**أولوية المرحلة الأولى:** Landsat 8/9 OLI، Sentinel-2 MSI، ASTER الصالح. دعم مستشعرات أخرى لاحقًا بعد توثيق خرائط الحزم علميًا.

- قبول GeoTIFF متعدد الحزم وحزم GeoTIFF منفصلة، وباقي صيغ GDAL/ArcGIS المتوافقة بعد اختبارها.
- دعم فحص مجلد رئيسي يحتوي مجلدًا فرعيًا لكل مرئية، والتعرف على Metadata والباندات تلقائيًا، وفق سياسة ATIAF القائمة.
- استخراج تاريخ الالتقاط، المستشعر، أسماء الحزم، مستوى المعالجة، قيم القياس، CRS، الدقة والموقع ونطاق NoData عند توافرها.
- عدم الخلط بين Sentinel-2 **B8** و**B8A** أو بين 10/20/60 متر؛ وضّح إعادة أخذ العينات في التقرير.
- عدم الخلط بين Landsat 8/9 وLandsat 5/7: **أرقام الحزم تختلف**، خصوصًا حزم SWIR والحراري.
- قراءة Scaling / Offset الخاصة بالمنتج قبل إجراء نسب طيفية. عدم قسمة قيم DN الخام باعتبارها reflectance بالضرورة.
- وضع تنبيه عند إدخال مشاهد ذات غيوم/ظلال أو بيانات غير مصححة، وإتاحة الأقنعة المناسبة دون اختلاقها.

## 5. التشغيل على ArcGIS Pro وQGIS

### 5.1 مبدأ مشترك

- **منطق علمي واحد ومخرجات متكافئة** بغض النظر عن المنصة؛ يمكن استخدام مكونات مشتركة محايدة على مستوى المعالجة، لكن يجب احترام قيود كل منصة.
- الواجهات والتكامل منفصلان حسب المنصة؛ لا تكتب واجهة واحدة تفترض أن ArcGIS Pro وQGIS لهما نفس APIs.
- راجع إصدار التطبيق الفعلي والتبعيات والتراخيص قبل اختيار الأداة/المكتبة. لا تفترض وجود إضافات مرخصة إضافيًا.
- يقرر الوكيل بناءً على المشروع ما إذا كان التكامل في ArcGIS Pro على هيئة Python Toolbox / Script Tool / Add-In مناسبًا، وفي QGIS كـProcessing Algorithm / Plugin مناسبًا؛ ولا يفرض هيكلًا جديدًا دون سبب.

### 5.2 ArcGIS Pro

- إدراج الأداة في المجموعة الجيولوجية الحالية، مع إمكانية الوصول إليها بصورة مستقلة.
- الاستفادة من مفاهيم **Composite Bands** و**Band Combination** و**Raster Functions** و**Stretch Symbology**، والتحقق من توفر كل إمكان وفق ترخيص ArcGIS الفعلي [S5–S8].
- إدراج النتيجة إلى الخريطة تلقائيًا عند تفعيل الخيار، مع عنوان واضح ووسيلة لاستعادة إعدادات العرض.
- لا تُعطِّل أدوات المشروع الحالية أو تغيّر مساراتها.

### 5.3 QGIS

- توفير نسخة عملية داخل QGIS، ليست مجرد واجهة شكلية؛ تتحقق فيها نفس الحسابات والحفظ والمعاينة.
- استخدام **Multiband Color Renderer** للعرض، وأدوات raster algebra وGDAL stack/VRT حيثما يناسب [S9–S10].
- إدراجها تحت مجموعة معالجة جيولوجية واضحة في Processing أو Plugin قائم، وفق هيكل المشروع الحالي.
- ترجمة كافة نصوص Plugin/Processing باستخدام آلية QGIS/Qt المناسبة، مع اختبار تفعيل لغة الواجهة [S14].

### 5.4 مصفوفة التسليم الإلزامية

| منصة التنفيذ | الواجهة العربية | English interface | Direct RGB | Ratio RGB | Preview | GeoTIFF |
|---|---|---|---|---|---|---|
| ArcGIS Pro | إلزامي | إلزامي | إلزامي | إلزامي | إلزامي | إلزامي |
| QGIS | إلزامي | إلزامي | إلزامي | إلزامي | إلزامي | إلزامي |

## 6. تجربة الاستخدام (UX) واللغات

**اسم القائمة بالعربية:** التراكيب اللونية الجيولوجية  
**الاسم بالإنجليزية:** Geological Color Composites

**تنظيم المقترح:**

1. **المدخلات / Inputs:** المرئية، المشهد، metadata، فحص الحزم.
2. **طريقة الدمج / Composition Method:** Direct RGB أو RGB Band Ratios.
3. **التركيبات / Presets:** حسب المستشعر، مع المرجع ووصف الاستخدام وحالة التوثيق.
4. **القنوات / RGB Channels:** تعيين الحزم أو المعادلات، مع ترتيب R/G/B الواضح.
5. **تحسين العرض / Display Enhancement:** هادئ، متوازن، قوي، مخصص.
6. **المعاينة / Preview:** قبل/بعد، مقياس/إحداثيات، تغييرات سريعة دون تعديل الأصل.
7. **الإخراج / Output:** حفظ صورة تحليلية/صورة عرض عند الطلب، المسار، الاسم، إضافة للخريطة.
8. **المعلومات / Scientific Notes:** المصدر، حدود التفسير، طريقة الحساب، التحذيرات.

**قواعد الترجمة الحاسمة:**

- في العربية: جمل وعناوين ورسائل عربية سليمة مع دعم RTL؛ مع السماح بالمصطلحات الفنية المحددة `RGB`, `SWIR`, `ASTER`, `Band 7` وأسماء ملفات/معادلات عند الضرورة.
- في الإنجليزية: لا تظهر جمل عربية في القوائم أو رسائل الخطأ أو التلميحات أو السجلات الموجهة للمستخدم.
- نفس الأدوات والخيارات في كلا اللغتين؛ **لا فرق وظيفيًا بين العربية والإنجليزية**.
- التبديل بين اللغتين لا يغير ترتيب القنوات أو الحسابات أو البيانات.
- تحقق من اتجاه الحقول والأرقام والمعادلات داخل RTL حتى لا ينعكس `B6 / B7` أو R/G/B.
- لا تترجم معرّفات الحزم العلمية أو المسارات وأسماء حقول Metadata ترجمات تغير معناها.

## 7. بنية المخرجات والتوثيق

عند تشغيل المرئية داخل مجلد مشهد، تُستخدم سياسة المشروع: الحفاظ على ملفات المصدر وإنشاء/استخدام مجلدي `Work` و`Results` داخل مجلد **كل مرئية** إذا كان ذلك هو النمط المعتمد في ATIAF، دون إنشاء مجلدات مكررة أو تغيير بنية مجلدات أخرى.

**تخطيط مبدئي داخل `Results`** (يعدل حسب شجرة المشروع الفعلية):

- `Geological_Color_Composites/Direct_RGB/`
- `Geological_Color_Composites/Band_Ratio_RGB/`
- مجلد `Preview/` اختياري للصور المعاينة غير التحليلية.

**المخرجات المطلوبة:**

- **GeoTIFF متعدد الحزم** مع CRS وGeotransform وNoData واضح وبيانات Raster مناسبة؛ فصل الناتج التحليلي عن صورة العرض الملونة عندما يكون اختلاف النوع الرقمي مؤثرًا.
- صورة PNG/JPEG للمعاينة **اختيارية** وليست بديلًا عن GeoTIFF؛ إذا لم تتضمن إسنادًا جغرافيًا واضحًا، يجب التصريح بذلك.
- **Metadata** تذكر المدخلات وأسماء/أرقام الحزم، وتاريخ المشهد، مصدر المستشعر، صيغة القنوات، المعادلات، طريقة المعالجة، Stretch/Gamma، إعادة التعيين المكاني، تاريخ التشغيل، وإصدار الأداة والمصدر العلمي للـPreset.
- اسم ملف واضح يتضمن المشهد/المستشعر والطريقة وتركيب RGB، مع أسماء آمنة لكل المنصات.
- خيار `Add output to map`، وخيار معالجة مشهد واحد أو دفعة مشاهد.

**فصل التحليل عن العرض:** لا تُستبدل القيم الأصلية المحسوبة بقيم ألوان 8-bit دون طلب صريح، ولا تُسمَّى نسخة العرض المعالجة «انعكاسية طيفية أصلية».

## 8. شروط الجودة العلمية والحالات الحساسة

1. **ASTER SWIR:** بيانات الحزم SWIR ‏(4–9) المكتسبة منذ **أبريل 2008** غير موثوقة/غير صالحة للاستخدام وفق تنبيه NASA/JPL؛ يجب فحص **تاريخ الالتقاط** لا تاريخ تنزيل المنتج. لا تُفعل تراكيب ASTER المعتمدة على SWIR لتلك المشاهد، وقدم رسالة خطأ/تحذير واضحة [S4].
2. **اختلاف الدقة:** عند دمج Sentinel-2 ‏10/20 متر أو ASTER ‏15/30/90 متر، يجب تحديد grid مرجعية وطريقة إعادة أخذ عينات ملائمة وذكرها في metadata. لا تَعِد بزيادة الدقة الحقيقية بمجرد Upsampling.
3. **محاذاة الحزم:** تحقق من CRS وextent وpixel alignment والترتيب قبل الحساب أو الإخراج؛ أي تحويل يجب توثيقه وعدم تنفيذه بصمت.
4. **النسب:** اعتمد Float للحساب؛ تعامل مع `NoData` والمقامات الصفرية/القريبة من الصفر والقيم غير المنتهية، وتجنب قص النتائج لإجبارها على نطاق غير علمي.
5. **Scale/Offset:** تحقق من مستوى المنتج والانعكاسية وطرق التحويل؛ خصوصًا Landsat Collection 2 Level-2 وSentinel-2 Level-2A.
6. **التحسين اللوني:** يجب أن تكون الإعدادات قابلة للإعادة، خاصة عند معالجة مشاهد متعددة؛ لا تجعل العرض المعتمد على extent الحالي يغيّر تفسير الألوان دون إيضاح.
7. **الحماية:** عدم الكتابة فوق الأصل، والتحقق من المسارات والصلاحيات والمساحة، واستخدام ملفات مرحلية آمنة وتنظيف المخلفات بعد فشل التشغيل.
8. **التفسير:** الألوان ليست مفتاحًا جيولوجيًا مطلقًا؛ يلزم التحقق من الخرائط الجيولوجية والعمل الحقلي/المراجع عند تسمية الوحدات الصخرية.

## 9. مراحل العمل التي يجب أن يتبعها الـAgent

### المرحلة 0 — فحص المشروع (إجباري قبل أي تعديل)

- اقرأ تعليمات التطوير المعتمدة في جذر ATIAF (`AGENTS.md` أو ما يعادله فعليًا)، وهيكل المستودع والأدوات الموجودة.
- راجع **GIS-Development-Skills** والمهارات ذات الصلة قبل اختيار البنية أو واجهة الاستخدام: <https://github.com/ahmadibrahim4geo/GIS-Development-Skills>.
- افحص جزء المعالجة الجيولوجية الحالي، ومسارات العمل، والمحركات، والتعريب، والاختبارات، والمجلدات. لا تفترض وجود ملفات لم تتحقق منها.
- حدد إمكان دمج الوحدة مع الأدوات القائمة دون ازدواج، أو تبرير وحدة مستقلة ذات مدخل واضح.
- قدّم تقرير فحص موجز **قبل كتابة التعديلات**: الموجود، الناقص، المخاطر، خطة الملفات والتبعية والترخيص.

### المرحلة 1 — التصميم العلمي

- ابنِ سجل Presets موحدًا بمصدر موثق لكل تركيبة، وميّز verified/experimental.
- حدد قواعد mapping لكل مستشعر/منتج، والتحقق من Metadata، ومعادلات النسب وأقنعة البيانات.
- صمّم سياسة فصل الـAnalytical Raster عن الـDisplay Rendering.

### المرحلة 2 — تجربة الواجهات

- جهز تجربة الاستخدام في ArcGIS Pro/QGIS بالعربية والإنجليزية؛ قوائم ثابتة وواضحة وبلا خلط لغوي.
- أضف وصفًا مبسطًا للفارق بين Direct RGB وBand Ratio RGB وClassification.
- راجع المعاينة وإدارة presets ومواضع الأخطاء والتنبيهات.

### المرحلة 3 — التنفيذ والاختبارات

- نفّذ أصغر تغييرات قابلة للصيانة ضمن المشروع الأصلي مع إعادة استخدام المهارات والمعايير المعتمدة.
- اختبر مستشعرات ومشاهد حقيقية، وتحقق من المخرجات بحسابات مرجعية مستقلة.
- وثّق حدود كل طريقة، وأمثلة تصويرية مرخصًا باستخدامها أو روابط إليها دون نسخ صور دراسات دون إذن.

### المرحلة 4 — المراجعة والتسليم

- اختبر المنصتين واللغتين والدفعات؛ قدّم مقارنة مخرجات متطابقة الدقة والمدخلات.
- حدّث المساعدة التقنية وREADME إن وُجد، وقدّم قائمة تغييرات واختبارات وشروط التوافق وأية قيود لا تزال موجودة.
- لا تدمج Classification أو PCA أو MNF أو Decorrelation كبدائل صامتة للطريقتين المطلوبتين؛ يمكن اقتراحها لاحقًا كأدوات منفصلة.

## 10. معايير القبول (Acceptance Criteria)

- [ ] يتعرف على Landsat 8/9 وSentinel-2 وASTER المدعوم، ويفحص الحزم/metadata قبل التشغيل.
- [ ] تتاح **Direct RGB** و**Ratio RGB** بصورة مستقلة وقابلة للفهم.
- [ ] يمكن إنتاج صورة تظهر التراكيب الصخرية مع الاحتفاظ بتفاصيل التضاريس، دون تصنيف أو ترميز فئات.
- [ ] ينتج تفاوت في شدة العرض (هادئ/متوازن/قوي) **لنفس** المعالجة؛ ولا يُغيّر بيانات التحليل بغير تصريح.
- [ ] كل Preset موثّق، وتُرفض الحزم المفقودة أو غير الصالحة أو عدم توافق المستشعر.
- [ ] يرفض/يحذر بوضوح من ASTER SWIR غير الصالح بدءًا من أبريل 2008.
- [ ] تُدار المحاذاة وNoData والمقامات الصفرية والـCRS وأحجام البكسل بأمان.
- [ ] تُحفَظ GeoTIFF وMetadata، ولا تتغير البيانات الأصلية.
- [ ] تعمل نسخة **ArcGIS Pro عربي / ArcGIS Pro English**.
- [ ] تعمل نسخة **QGIS عربي / QGIS English**.
- [ ] تعطي المنصتان نتائج حسابية متكافئة عند تثبيت المدخلات والخيارات ونوع البيانات.
- [ ] ينجح تشغيل مشهد واحد ودفعات مشاهد، مع سجلات إخفاق مفهومة.
- [ ] لا توجد تسميات صخرية قطعية مولدة من اللون، ولا Classification تلقائي.

---

# 11. مصادر رسمية وتعليمية وعلمية للـAgent

**قاعدة استخدام المصادر:** يبدأ الوكيل بالمراجع الرسمية في مسألة واجهات البرمجة، ويستعمل الأوراق العلمية لتوثيق **التركيبات والمعادلات**، ويتحقق من سياق الدراسة والمستشعر وتاريخ المشهد قبل النقل. لا يختلق Presets أو يتعامل مع الصور المعروضة بوصفها تصنيفًا لمجرد قوة ألوانها. يُراجع الإصدار الفعلي للتوثيق عند التطوير، لأن الواجهات قد تتغير.

## 11.1 لفهم الـFalse Color والفرق بين لون العرض والتصنيف

**[S1] NASA Earth Observatory — Why Is That Forest Red and That Cloud Blue?**  
<https://earthobservatory.nasa.gov/features/FalseColor>  
*الهدف:* شرح مفهوم False Color، توزيع الحزم على RGB، ولماذا تختلف ألوان الأرض وفق القنوات المستخدمة. مرجع تعليمي ممتاز للشرح داخل واجهة الأداة.

**[S2] USGS — Common Landsat Band RGB Composites**  
<https://www.usgs.gov/media/images/common-landsat-band-rgb-composites>  
*الهدف:* أمثلة مرئية لتراكيب متعددة يمكن الرجوع إليها عند إعداد المعاينات والتوثيق.

**[S3] USGS — What Are the Best Landsat Spectral Bands for Use in My Research?**  
<https://www.usgs.gov/faqs/what-are-best-landsat-spectral-bands-use-my-research>  
*الهدف:* خصائص حزم Landsat والاستخدامات المتعلقة بالمظاهر الأرضية وSWIR والمعادن؛ مرجع لاختيار الحزم والتأكد من المصطلحات.

**[S3b] USGS — Landsat Band Designations**  
<https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites>  
*الهدف:* التحقق من الأرقام العلمية للحزم حسب الأجيال المختلفة وعدم الخلط بينها.

## 11.2 تنبيهات المستشعرات

**[S4] NASA/JPL — ASTER SWIR User Advisory**  
<https://asterweb.jpl.nasa.gov/swir-alert.asp>  
*الهدف:* مرجع إلزامي للتحقق من صلاحية ASTER SWIR وتاريخ أبريل 2008؛ ليس مجرد مصدر اختياري.

**[S4b] Copernicus / ESA — Sentinel-2 User Handbook**  
<https://sentinels.copernicus.eu/documents/247904/685211/Sentinel-2_User_Handbook>  
*الهدف:* الأطوال الموجية، الدقة المكانية والفرق بين الحزم. راجع النسخة الأحدث عند التنفيذ.

**[S4c] Copernicus — Sentinel-2 Spectral Response Functions Update (2026)**  
<https://sentinels.copernicus.eu/-/sentinel-2-spectral-response-functions-update>  
*الهدف:* توثيق تحديثات الاستجابة الطيفية وتجنب افتراض تطابق تام لكل نسخ Sentinel-2 عند تحليل المعادن بصورة دقيقة.

## 11.3 مراجع ArcGIS Pro الرسمية

**[S5] Esri — Composite Bands (Data Management)**  
<https://pro.arcgis.com/en/pro-app/3.6/tool-reference/data-management/composite-bands.htm>  
*الهدف:* إنشاء Raster متعدد الحزم وتحديد ترتيبها وتأثير الحزمة الأولى على المرجع المكاني والدقة.

**[S6] Esri — Imagery Appearance / Band Combination**  
<https://pro.arcgis.com/en/pro-app/3.6/help/data/imagery/raster-display-ribbon.htm>  
*الهدف:* مفهوم تغيير وعرض تركيبات RGB على المرئيات وتخصيص التراكيب حسب المستشعر.

**[S7] Esri — Change the Symbology of Imagery**  
<https://pro.arcgis.com/en/pro-app/3.6/help/data/imagery/symbology-pane.htm>  
*الهدف:* Contrast Stretch، وPercent Clip وGamma، وكيف يختلف تغير العرض عن تغير بيانات البكسل.

**[S8] Esri — List of Raster Functions**  
<https://pro.arcgis.com/en/pro-app/3.5/help/analysis/raster-functions/list-of-raster-functions.htm>  
*الهدف:* معرفة وظائف Band Arithmetic وغيرها ومتطلبات الترخيص لكل وظيفة قبل اتخاذ قرار التصميم.

## 11.4 مراجع QGIS الرسمية

**[S9] QGIS — Raster Properties / Multiband Color**  
<https://docs.qgis.org/3.44/en/docs/user_manual/working_with_raster/raster_properties.html>  
*الهدف:* Render RGB من ثلاث حزم والتحكم بالـMin/Max وContrast Enhancement.

**[S10] QGIS — Raster Calculator (Processing)**  
<https://docs.qgis.org/3.44/en/docs/user_manual/processing_algs/qgis/rasteranalysis.html>  
*الهدف:* Raster algebra لحساب نسب الحزم/المعادلات، والمخرجات الحقيقية أو الافتراضية.

**[S10b] QGIS — GDAL Build Virtual Raster**  
<https://docs.qgis.org/3.44/en/docs/user_manual/processing_algs/gdal/rastermiscellaneous.html>  
*الهدف:* وضع حزم ملفات منفصلة في stacked raster/VRT مع فهم خيارات الدقة والمحاذاة.

**[S10c] QGIS — PyQGIS Using Raster Layers**  
<https://documentation.qgis.org/testing/en/docs/pyqgis_developer_cookbook/raster.html>  
*الهدف:* أسلوب MultiBandColorRenderer وخصائص Raster وقنوات العرض داخل QGIS. استخدم مستند الإصدار المثبت وقت التنفيذ.

**[S14] QGIS — Structuring / Translating Python Plugins**  
<https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/plugins/plugins.html>  
*الهدف:* بنية Plugin وآليات الترجمة `i18n` وملفات الترجمة واختبار العربية والإنجليزية.

## 11.5 دراسات علمية مفيدة — مع صور ومقارنات جيولوجية مصرية

**[S11] Duwi Shear Belt, Central Eastern Desert — Scientific Reports (2024)**  
<https://www.nature.com/articles/s41598-024-66199-3>  
*الأهمية:* مرجع مباشر للأداة؛ يشرح **FCC ‏7-5-3** لـLandsat 8/9 وكذلك **Color Ratio Composites** بصيغ محددة، ويقارن FCC مع PCA/MNF ومع التصنيف في دراسة واحدة. راجع **Figure 3** للدمج المباشر ونتائج CRC في متن الدراسة، وليس الخريطة المصنفة باعتبارها نتيجة RGB.

**[S12] Lithological Mapping in the Central Eastern Desert of Egypt Using ASTER Data — Journal of African Earth Sciences (2010)**  
<https://www.sciencedirect.com/science/article/pii/S1464343X09001071>  
*الأهمية:* دراسة مرجعية حول الفواخير؛ تعرض تركيبة ASTER ‏`((2+4)/3, (5+7)/6, (7+9)/8)` الموزعة على RGB للتمييز بين الصخور الأوفيوليتية والجرانيتية. تحقق من فترة بيانات ASTER وصلاحيتها.

**[S13] Multisource Data Analysis for Gold Potentiality Mapping of Atalla Area — Minerals (2021)**  
<https://www.mdpi.com/2075-163X/11/6/641>  
*الأهمية:* دراسة مصرية مفتوحة تعرض FCC وBand Ratios ومؤشرات التحول المعدني ونتائج Sentinel-2 وASTER. مناسبة لمكتبة المراجع والصور التعليمية، مع التمييز الصارم بين RGB وبين خرائط المعادن المصنفة.

**[S15] Geological Controls of Mineralization in the Egyptian Eastern Desert — Scientific Reports (2024)**  
<https://www.nature.com/articles/s41598-024-66924-y>  
*الأهمية:* صور مرئية توضح ألوانًا طيفية قوية مع الاحتفاظ بشكل المشهد الجغرافي على نطاق الصحراء الشرقية؛ تُراجع طبيعة كل شكل قبل تسميته FCC أو Ratio أو PCA.

**[S16] Application of Magnetic Data and Satellite Spectral Imaging in Fawakheir–Attala — Environmental Earth Sciences (2024)**  
<https://link.springer.com/article/10.1007/s12665-024-11776-y>  
*الأهمية:* أمثلة صور ملونة من الصحراء الشرقية وطرق التحسين الطيفي، للمقارنة البصرية في وثيقة المستخدم.

## 11.6 كيف يستخدم الوكيل هذه المراجع عمليًا؟

1. يراجع **S1–S3** لصياغة شرح مبسط للدمج المباشر واختيار الباندات.
2. يراجع **S11–S13** لبناء Presets **موثقة بمعادلاتها الحرفية**؛ لا يخترع نسبًا ولا يستبدل حزمًا اعتباطيًا.
3. يراجع **S4 وS4b وS4c** للتحقق من صلاحية الحزم والتواريخ والدقة قبل حساب النسب.
4. يراجع **S5–S8** لتكامل ArcGIS Pro ومحددات التراخيص؛ و**S9–S10c وS14** لتكامل QGIS والعربية والإنجليزية.
5. يستخدم أمثلة **S11 وS15 وS16** لتوضيح الفرق البصري بين FCC هادئ، وصورة محسنة شديدة، وخريطة Classification. يُذكر نوع **كل شكل** بدقة من شرح الصورة الأصلي.
6. عند اختلاف مصدر علمي مع آخر: سجّل اختلاف المنطقة، المستشعر، التاريخ، ومستوى التصحيح. لا تعرض لونًا ثابتًا بمعنى صخري عالمي.
7. أرفق قائمة بالمراجع المستخدمة فعليًا في تطوير كل Preset، ولا تكتفِ بإرفاق روابط في README دون ربطها بالخيارات.

---

## 12. شرط التسليم النهائي للـAgent

**لا تعتبر المهمة مكتملة إلا عندما:** تكون الطريقتان واضحتين ومستقلتين، وتعملان مع التراكيب الجيولوجية بالضبط بوصفهما **صور RGB مستمرة لا Classification**، وتعمل كل منهما على ArcGIS Pro وQGIS بالعربية والإنجليزية، وتحافظ الأداة على البيانات والمرجعية المكانية، ويكون لكل Preset مصدر علمي ووصف وتاريخ صلاحية وحدود استخدام، مع اختبارات موثقة لكل واجهة.

**أولوية المستخدم البصرية:** إنتاج مشهد فضائي يُشعِر القارئ أنه يرى تضاريس الأرض الطبيعية، لكن الصخور والوحدات تختلف في الألوان والدرجات؛ **لا تُحوّل هذه النتيجة إلى خريطة تصنيف ذات مساحات مصمتة وحدود فئات واضحة**. ويمكن إتاحة الألوان القوية كخيار عرض مستقل.

---

## ATIAF intake — PLAN-0018 r1 (2026-11-15)

- Status: Active; implementation authorized by the user in this conversation.
- Original title: ATIAF — Geological Color Composites / خطة تطوير موجّهة لوكيل البرمجة.
- Source: `ATIAF_Geological_Color_Composites_Agent_Plan.md` at repository root; unchanged original retained. SHA256: `07A9D78B226DCD82F56B24096D1B7E61DAEE0CE65546833EAC5C8D9709B23BE8`.
- All original requirements above are retained, including manual/custom presets, bounded before/after preview, scientific RGB GeoTIFF versus separate display, both native hosts/languages, real inputs and cross-host equivalence. No classification/PCA/MNF substitution.
- Design: add a seventh independent tool `geological_composites` to existing Pro toolboxes/QGIS provider, with shared `atiaf_core/composites/` calculation/registry/rendering and thin adapters. Preserve existing tool IDs/behavior.
- Reuse metadata discovery and workspace/reporting; exact scientific band IDs and explicit multiband mapping must not be confused with positions. Existing ASTER reader only maps a subset and does not establish complete AST_07 calibration; require explicit verified mapping/calibration for missing exact ASTER bands rather than guess.
- Common options: sensor-first, QA/preflight, compatible same-day mosaic, independent polygon AOI/native metre CRS, opt-in map addition, output folder last. Float analytical channels remain unchanged by display enhancement.
- Test host: measured standalone Python and installed native Pro/QGIS runtimes will be checked; no package installs or live application installation authorized. Unit/numeric, raster readback, native synthetic algorithms/parameters, packaging/source identity and bilingual docs can run when available.
- User confirms no real local scenes are available. Real-product/field visual validation and clean installation remain NOT RUN; do not archive while mandatory original acceptance is unverified.
- Subsequent user update supplies `Testing Data/LC81760392014234LGN00`. Read-only inspection identifies pre-Collection Landsat 8 L1T with exact MTL reflectance coefficients, solar elevation and legacy BQA. This supersedes the earlier availability assumption. Test locally with explicitly labeled TOA conversion and the correct pre-Collection QA decoder; do not call it surface reflectance or apply undocumented atmospheric correction. Preserve the source bundle and save test results separately.
- Evidence: pre-implementation inspection report 0026; later independent numbered implementation reports. Journal request #0049. Existing PLAN-0015 remains partial.

## r1 implementation handoff — 2026-11-15

Implemented the seventh native tool, shared exact-band Direct/Ratio RGB, explicit mapping/calibration, reviewed/gated presets, separate display, bounded previews, preset import/export, QA/TOA, polygon clip and complete-triplet mosaic. Local 1.0.3.dev1 packages built/verified; no publication. Delivery report [0027](../../Reports/0027_geological_color_composites_implementation_and_validation.md) records commands, retained failures and bounded native evidence. Original 13 checklist items plus eight retained requirements are bound in [partial DoneProof](../../Reports/evidence/PLAN-0018/doneproof_r1.json). 162 headless checks pass; native new QGIS 3 / Pro 2 checks pass, QGIS regression 11 pass; Pro old suite has seven initial passes plus one corrected targeted pass. Real QGIS English/Pro Arabic outputs are bitwise equal over all 60,616,171 pixels per channel/method; numerical/TOA evidence is not field accuracy. Preserve the failed helper receipt logs separately from verified artifact readback.

Keep **Active / PARTIAL**: complete automatic ASTER reader/calibration, real Sentinel-2/ASTER and mixed-resolution validation, Fawakheir original-source verification, field interpretation, full installed native journeys/clean installation and comprehensive concurrency/interruption/CRS acceptance remain unverified. Exact next action is report 0027's handoff. Original source above and at root remains unchanged in meaning; no acceptance removed.
