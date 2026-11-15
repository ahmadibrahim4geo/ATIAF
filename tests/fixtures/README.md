# tests/fixtures
`create_synthetic_fixtures.py` creates small synthetic metadata and deliberately invalid raster placeholders for filename/product parser tests. `test_product_recognition.py` generates them in an isolated temporary directory on each run, including on a clean checkout. No satellite imagery is downloaded or redistributed. These stubs must not be used as evidence of real raster processing or scientific accuracy; raster workflow tests generate separate valid synthetic rasters.

ينشئ المساعد بيانات وصفية وملفات شكلية اصطناعية لاختبار اكتشاف المنتجات في مجلد مؤقت مستقل، دون تنزيل مرئيات أو الاعتماد على ملفات محلية غير منشورة. هذه الملفات ليست مرئيات صالحة ولا دليلًا على الدقة العلمية؛ اختبارات معالجة الراستر تنشئ عينات صالحة منفصلة.
