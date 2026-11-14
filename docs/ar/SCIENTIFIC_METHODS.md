# المرجع العلمي الشامل للمعادلات الفيزيائية وطرق المعايرة

**إطار التحليل الطيفي والمكاني المتقدم للمرئيات الفضائية (أطياف — ATIAF)**  
*المرجع الهندسي المعتمد للخوارزميات المنفذة، فيزياء المستشعرات، والنماذج الحركية السطحية*

> [!NOTE]
> للاطلاع على الدليل الشامل والمفصل للمستخدم مع شرح تفصيلي للنطاقات الطيفية لكل قمر وجداول تفسير القيم، يرجى مراجعة [دليل المؤشرات الشامل (INDICATORS_CATALOG.md)](INDICATORS_CATALOG.md).

---

## 1. الوحدات الفيزيائية ومعايير المعايرة
تعتمد جميع العمليات الرياضية داخل أطياف على قيم فيزيائية حقيقية ومصححة للسطح:
1. **الانعكاسية السطحية ($\rho$):** أرقام كسرية عائمة ضمن المدى $[0.0, 1.0]$.
   - لاندسات C2 L2: يتم التحويل باستخدام $\rho = \text{DN} \times 0.0000275 - 0.2$.
   - سينتنل-2 L2A: يتم التحويل باستخدام $\rho = \text{DN} / 10000.0$.
   - المنتجات المعايرة مسبقاً لا يتم مضاعفة معاملاتها أبداً.
2. **درجة حرارة السطح ($T$):** أرقام كسرية بوحدة الكلفن ($K$) أو الدرجة المئوية ($^\circ\text{C}$).
   - لاندسات C2 L2 ST: يتم التحويل باستخدام $T_K = \text{DN} \times 0.00341802 + 149.0$ و $T_{^\circ\text{C}} = T_K - 273.15$.
3. **التشتت الراداري المرتد ($\sigma^0$):** يحول للديسبل عبر $\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$.

---

## 2. المعادلات الرياضية المعتمدة حسب حزمة الأدوات

### الأداة 01: المؤشرات الطيفية البصرية
- **NDVI:** $\frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}}}$
- **GNDVI:** $\frac{\rho_{\text{NIR}} - \rho_{\text{Green}}}{\rho_{\text{NIR}} + \rho_{\text{Green}}}$
- **SAVI:** $\frac{(1 + L)(\rho_{\text{NIR}} - \rho_{\text{Red}})}{\rho_{\text{NIR}} + \rho_{\text{Red}} + L} \quad (L = 0.5)$
- **MSAVI:** $\frac{2\rho_{\text{NIR}} + 1 - \sqrt{(2\rho_{\text{NIR}} + 1)^2 - 8(\rho_{\text{NIR}} - \rho_{\text{Red}})}}{2}$
- **OSAVI:** $\frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}} + 0.16}$
- **EVI:** $2.5 \cdot \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + 6.0\rho_{\text{Red}} - 7.5\rho_{\text{Blue}} + 1.0}$
- **NDRE1:** $\frac{\rho_{\text{NIR}} - \rho_{\text{RedEdge1}}}{\rho_{\text{NIR}} + \rho_{\text{RedEdge1}}}$ (سينتنل-2 فقط)
- **VARI:** $\frac{\rho_{\text{Green}} - \rho_{\text{Red}}}{\rho_{\text{Green}} + \rho_{\text{Red}} - \rho_{\text{Blue}}}$
- **GLI:** $\frac{2\rho_{\text{Green}} - \rho_{\text{Red}} - \rho_{\text{Blue}}}{2\rho_{\text{Green}} + \rho_{\text{Red}} + \rho_{\text{Blue}}}$
- **NDWI (ماك فيترز):** $\frac{\rho_{\text{Green}} - \rho_{\text{NIR}}}{\rho_{\text{Green}} + \rho_{\text{NIR}}}$
- **MNDWI (شو):** $\frac{\rho_{\text{Green}} - \rho_{\text{SWIR1}}}{\rho_{\text{Green}} + \rho_{\text{SWIR1}}}$
- **NDMI / NDWI جاو:** $\frac{\rho_{\text{NIR}} - \rho_{\text{SWIR1}}}{\rho_{\text{NIR}} + \rho_{\text{SWIR1}}}$
- **NDBI:** $\frac{\rho_{\text{SWIR1}} - \rho_{\text{NIR}}}{\rho_{\text{SWIR1}} + \rho_{\text{NIR}}}$
- **UI:** $\frac{\rho_{\text{SWIR2}} - \rho_{\text{NIR}}}{\rho_{\text{SWIR2}} + \rho_{\text{NIR}}}$
- **BSI:** $\frac{(\rho_{\text{SWIR1}} + \rho_{\text{Red}}) - (\rho_{\text{NIR}} + \rho_{\text{Blue}})}{(\rho_{\text{SWIR1}} + \rho_{\text{Red}}) + (\rho_{\text{NIR}} + \rho_{\text{Blue}})}$
- **NBR & NBR2:** $\frac{\rho_{\text{NIR}} - \rho_{\text{SWIR2}}}{\rho_{\text{NIR}} + \rho_{\text{SWIR2}}}, \quad \frac{\rho_{\text{SWIR1}} - \rho_{\text{SWIR2}}}{\rho_{\text{SWIR1}} + \rho_{\text{SWIR2}}}$
- **NDSI:** $\frac{\rho_{\text{Green}} - \rho_{\text{SWIR1}}}{\rho_{\text{Green}} + \rho_{\text{SWIR1}}}$
- **تحويلات Tasseled Cap (السطوع TCB، الخضرة TCG، الرطوبة TCW):** مصفوفات تحويل متعامدة مخصصة لكل قمر (لاندسات 8-9، لاندسات 7، لاندسات 4-5، سينتنل-2).

---

### الأداة 02: درجة حرارة السطح والانبعاثية (LST & LSE)
- **نموذج سوبرينو (Sobrino et al. 2004) للانبعاثية بالاعتماد على عتبات NDVI:**
  $$P_v = \left( \frac{\text{NDVI} - 0.2}{0.5 - 0.2} \right)^2$$
  $$\varepsilon = \begin{cases}
  0.985 & \text{إذا كان } \text{NDVI} < 0.0 \\
  0.970 & \text{إذا كان } 0.0 \le \text{NDVI} < 0.2 \\
  0.004 \cdot P_v + 0.986 & \text{إذا كان } 0.2 \le \text{NDVI} \le 0.5 \\
  0.990 & \text{إذا كان } \text{NDVI} > 0.5
  \end{cases}$$

---

### الأداة 03: مؤشر تباين الحقل الحراري الحضري (UTFVI)
$$\text{UTFVI} = \frac{\text{LST} - \mu_{\text{LST}}}{\mu_{\text{LST}}}$$
يصنف إلى 6 مستويات للراحة البيئية من ممتاز ($<0$) وحتى الأسوأ للغاية ($>0.020$).
وتحدد البؤر الحرارية الشديدة عبر:
$$z = \frac{\text{LST} - \mu_{\text{LST}}}{\sigma_{\text{LST}}} \ge 2.0$$

---

### الأداة 04: الجفاف البيئي ومؤشر TVDI والبيدو السطح
- **البيدو السطح (Liang 2001):**
  $$\alpha = 0.356\rho_{\text{Blue}} + 0.130\rho_{\text{Red}} + 0.373\rho_{\text{NIR}} + 0.085\rho_{\text{SWIR1}} + 0.072\rho_{\text{SWIR2}} - 0.0018$$
- **مؤشر جفاف الغطاء النباتي الحراري (TVDI):**
  $$\text{TVDI} = \frac{\text{LST} - \text{LST}_{\text{min}}}{\text{LST}_{\text{max}} - \text{LST}_{\text{min}}}$$

---

### الأداة 05: التحليل الجيولوجي والنسب المعدنية
- **أكاسيد الحديد:** $\rho_{\text{Red}} / \rho_{\text{Blue}}$
- **الحديد ثلاثي التكافؤ:** $\rho_{\text{Red}} / \rho_{\text{Green}}$
- **الحديد ثنائي التكافؤ:** $\rho_{\text{SWIR1}} / \rho_{\text{NIR}}$
- **تحورات الطين والهيدروكسيل:** $\rho_{\text{SWIR1}} / \rho_{\text{SWIR2}}$
- **الجوسان واللاتريت:** $\rho_{\text{SWIR1}} / \rho_{\text{Red}}$
- **الكوارتز الحراري (QI):** $(\text{TIR}_{11} \cdot \text{TIR}_{11}) / (\text{TIR}_{10} \cdot \text{TIR}_{12})$
- **الكربونات الحراري (CI):** $\text{TIR}_{13} / \text{TIR}_{14}$
- **الصخور المافية الحراري (MI):** $\text{TIR}_{12} / \text{TIR}_{13}$

---

### الأداة 06: التحليل الزمني وتغير الغطاء الأرضي
- **فارق نسبة الحريق (dNBR) وفق المعيار القياسي الأمريكي USGS FIREMON:**
  $$\text{dNBR} = \text{NBR}_{\text{قبل الحريق}} - \text{NBR}_{\text{بعد الحريق}}$$
- **التغير الزمني للمؤشرات (dNDVI / dLST):** $\Delta M = M_{T_2} - M_{T_1}$
- **نسبة التغير المئوية:** $\text{RelChange} = \frac{M_{T_2} - M_{T_1}}{|M_{T_1}| + 10^{-6}} \times 100\%$

---

### الأنماط المتقدمة: رادار الفتحة الاصطناعية والاستشعار فائق الطيفية
- **رادار Sentinel-1:** معايرة $\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$، ونسبة $VH/VV$، ومؤشر RVI، ومرشح لي (Lee Filter).
- **الاستشعار فائق الطيفية (EnMAP / PRISMA):** مخطط الزاوية الطيفية SAM ($\theta = \arccos \frac{\mathbf{v} \cdot \mathbf{r}}{\|\mathbf{v}\| \|\mathbf{r}\|}$)، وعمق قيعان الامتصاص التشخيصية للمعادن.
