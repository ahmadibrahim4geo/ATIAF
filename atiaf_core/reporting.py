"""Separate UTF-8 English/Arabic run reports, with escaped scientific provenance."""
from pathlib import Path
from html import escape
import json


def localized_reports(run_dir, manifest, parameters):
    labels = {
        'en': ['Scientific run record', 'Saved outputs', 'Parameters', 'Source scene and exact band assets',
               'Calculation definitions and references', 'Source calibration comes from the product profile or explicit expert mapping. It is not claimed to have been read from a metadata key unless recorded as such.',
               'Requested CRS and grid policy are recorded below. Native GUI, real-product and clean-install acceptance remain separate evidence.', 'Products'],
        'ar': ['سجل التشغيل العلمي', 'النواتج المحفوظة', 'المعاملات', 'المرئية المصدر وأصول الباندات الدقيقة',
               'تعريفات الحساب والمراجع', 'معايرة المصدر من تعريف المنتج أو تعيين الخبير الصريح؛ لا تُنسب إلى حقل ميتاداتا ما لم يكن ذلك مسجلًا بالفعل.',
               'المسقط المطلوب وسياسة الشبكة مسجلان أدناه. قبول الواجهة والمنتج الحقيقي والتثبيت النظيف أدلة منفصلة.', 'المنتجات']}
    def code(value):
        return '<pre dir="ltr">' + escape(json.dumps(value, ensure_ascii=False, indent=2, default=str)) + '</pre>'
    for lang, text in labels.items():
        direction = 'rtl' if lang == 'ar' else 'ltr'
        products = manifest.get('output_products', [])
        interpretation_html = ''
        for definition in manifest.get('scientific_definitions', []):
            interpretation = definition.get('interpretation', {})
            text_values = interpretation.get(lang, {})
            interpretation_html += '<h3><bdi>' + escape(definition['id']) + '</bdi></h3>'
            for key in ('meaning', 'units', 'range', 'caution'):
                interpretation_html += '<p>' + escape(text_values.get(key, '')) + '</p>'
            if interpretation.get('educational_examples'):
                interpretation_html += '<p>' + escape(interpretation['educational_examples'][lang]) + '</p>'
        for product in products:
            effective = product.get('classification')
            if not effective:
                continue
            heading = 'Local classes — not an international standard' if lang == 'en' else 'فئات محلية — ليست معيارًا دوليًا'
            interpretation_html += '<h3>' + heading + '</h3><table>'
            bounds = [0] + effective['effective_breaks'] + [1]
            for i, name in enumerate(effective['labels'][lang]):
                interval = f'[{bounds[i]}, {bounds[i+1]}' + (']' if i == 3 else ')')
                interpretation_html += '<tr><td>' + str(i+1) + '</td><td dir="ltr">' + interval + '</td><td>' + escape(name) + '</td></tr>'
            interpretation_html += '</table>' + code(effective)
        rows = ''.join('<tr><td>' + escape(str(p.get('index_id') or p.get('product_name') or p.get('acronym', ''))) +
                       '</td><td><bdi>' + escape(str(p.get('clipped_path') or p.get('full_path', ''))) + '</bdi></td></tr>' for p in products)
        page = f'''<!doctype html><html lang="{lang}" dir="{direction}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ATIAF — {text[0]}</title><style>body{{max-width:1000px;margin:24px auto;padding:24px;color:#062d46;background:#f5f9fc;font:16px/1.8 "Segoe UI",Tahoma,sans-serif}}pre{{background:white;border:1px solid #d8e5ed;padding:16px;overflow:auto;font-size:13px}}td{{padding:12px;border:1px solid #d8e5ed;overflow-wrap:anywhere}}table{{width:100%;border-collapse:collapse}}a{{color:#075f9c}}</style><h1>{text[0]}</h1><p><a href="report.en.html">English</a> · <a href="report.ar.html">العربية</a> · <a href="Processing_Manifest.json">JSON</a></p><p><bdi>{escape(manifest['run_id'])}</bdi></p><h2>{text[1]}: {len(products)}</h2><table>{rows}</table><p>{text[6]}</p><h2>{text[2]}</h2>{code(parameters)}<h2>{text[3]}</h2>{code(manifest.get('source_scene', {}))}<p>{text[5]}</p><h2>{text[4]}</h2>{code(manifest.get('scientific_definitions', []))}<h2>{text[7]}</h2>{code(products)}</html>'''
        page = page.replace('</html>', '<h2>' + ('Output interpretation' if lang == 'en' else 'تفسير النتائج') + '</h2>' + interpretation_html + '</html>')
        (Path(run_dir)/f'report.{lang}.html').write_text(page, 'utf-8')
