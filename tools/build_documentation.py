"""Build the offline portal and readable EN/AR HTML help using only the standard library."""
from pathlib import Path
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atiaf_core.tool_contract import CATALOG, TITLES
from atiaf_core import __version__


def inline(text):
    value = html.escape(text)
    value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
    value = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)
    def link(match):
        target = html.unescape(match[2])
        if target.lower().startswith(('javascript:', 'data:')):
            return match[1]
        if target.endswith('.md') and '/' not in target:
            target = target[:-3] + '.html'
        return f'<a href="{html.escape(target, quote=True)}">{match[1]}</a>'
    return re.sub(r'\[([^]]+)\]\(([^)]+)\)', link, value)


def render_markdown(text):
    """Render the documented subset: headings, paragraphs, tables, lists, fenced code and links."""
    result, code, table = [], None, False
    for line in text.splitlines():
        if line.startswith('```'):
            if code is None:
                code = []
            else:
                result.append('<pre dir="ltr"><code>' + html.escape('\n'.join(code)) + '</code></pre>')
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        if line.startswith('|'):
            if re.fullmatch(r'[| :\-]+', line):
                continue
            if not table:
                result.append('<div class="table"><table>')
                table = True
            result.append('<tr>' + ''.join('<td>' + inline(c.strip()) + '</td>' for c in line.strip('|').split('|')) + '</tr>')
            continue
        if table:
            result.append('</table></div>')
            table = False
        if not line.strip():
            continue
        match = re.match(r'^(#{1,6}) (.*)', line)
        if match:
            level, label = len(match[1]), match[2]
            anchor = label.split(' — ')[0] if ' — ' in label else re.sub(r'[^a-z0-9_-]', '-', label.lower())
            result.append(f'<h{level} id="{html.escape(anchor)}">{inline(label)}</h{level}>')
        else:
            result.append('<p>' + inline(line) + '</p>')
    if table:
        result.append('</table></div>')
    return '\n'.join(result)


def main():
    folder = ROOT/'documentation'
    template = (folder/'site_template.html').read_text('utf-8')
    portal = template.replace('__CALCULATIONS__', json.dumps(CATALOG, ensure_ascii=False).replace('</', '<\\/'))
    portal = portal.replace('__VERSION__', __version__)
    portal = portal.replace('__TITLES__', json.dumps(TITLES, ensure_ascii=False).replace('</', '<\\/'))
    (folder/'index.html').write_text(portal, 'utf-8')
    root_portal = re.sub(r'(href|src)="(assets/|ar/|en/|project/)', r'\1="documentation/\2', portal)
    root_portal = root_portal.replace('href="../', 'href="').replace("a.href=lang+", "a.href='documentation/'+lang+")
    (ROOT/'index.html').write_text(root_portal, 'utf-8')
    for language in ('en', 'ar'):
        cards = ['# ' + ('Calculation catalog' if language == 'en' else 'دليل الحسابات'),
                 ('Local implementation definitions; conditional availability is not real-product validation. '
                  'See current project state and workflow eligibility. No external catalog imported.' if language == 'en' else
                  'تعريفات التنفيذ المحلية؛ الإتاحة المشروطة ليست تحققًا بمرئية حقيقية. راجع حالة المشروع وشروط الأداة. لم يُستورد كتالوج خارجي.')]
        for tool, rows in CATALOG.items():
            cards.extend([f'\n## {tool} — {TITLES[tool][language == "ar"]}', '[Usage](QUICK_START.md)' if language == 'en' else '[طريقة الاستخدام](QUICK_START.md)'])
            for row in rows:
                cards.extend([f'\n### {row["id"]} — {row[language]}', f'`{row.get("formula", row["id"])}`'])
                if row.get('roles'):
                    cards.append(('Band roles: ' if language == 'en' else 'أدوار الباندات: ') + ', '.join(row['roles']))
                if row.get('citation'):
                    cards.append(('Reference: ' if language == 'en' else 'المرجع: ') + row['citation'])
                if row.get('source_url'):
                    cards.append(('[Method source](' if language == 'en' else '[مصدر الطريقة](') + row['source_url'] + ')')
                interpretation = row['interpretation']
                text = interpretation[language]
                captions = (['Meaning', 'Units', 'Range', 'Limitations', 'Classification'] if language == 'en' else
                            ['المعنى', 'الوحدات', 'المدى', 'حدود التفسير', 'التصنيف'])
                for caption, key in zip(captions, ('meaning', 'units', 'range', 'caution')):
                    cards.append('**' + caption + ':** ' + text[key])
                cards.append('**' + captions[4] + ':** ' + ('No verified universal classification standard; optional local schemes must be justified and recorded.' if language == 'en' else
                    'لم يثبت معيار تصنيف عالمي منطبق؛ أي فئات محلية اختيارية تحتاج مبررًا وتسجيلًا.'))
                if interpretation.get('educational_examples'):
                    cards.append(interpretation['educational_examples'][language])
                for url in interpretation['reference_urls']:
                    cards.append('[Source](' + url + ')' if language == 'en' else '[المصدر](' + url + ')')
                if row['id'] == 'NDVI' and tool == 'spectral_indices':
                    from atiaf_core.classification import DEFAULT_BREAKS, NAMES
                    cards.append('**' + ('Optional LOCAL illustrative classes, NOT an international standard. Negative/out-of-range/QA values are excluded; continuous NDVI is preserved.' if language == 'en' else
                        'فئات محلية استرشادية اختيارية وليست معيارًا دوليًا. تُستبعد القيم السالبة وخارج المدى وغير الصالحة، وتُحفظ قيم NDVI الأصلية.') + '**')
                    cards.append('| ' + ('Code | Interval | Meaning |' if language == 'en' else 'الرمز | المجال | المعنى |'))
                    cards.append('|---|---|---|')
                    bounds = [0] + DEFAULT_BREAKS + [1]
                    for i in range(4):
                        interval = f'[{bounds[i]}, {bounds[i+1]}' + (']' if i == 3 else ')')
                        cards.append(f'| {i+1} | {interval} | {NAMES[language][i]} |')
                    cards.append('Change the three internal boundaries only with a documented local basis. Classification is not plant-health diagnosis.' if language == 'en' else
                        'تُعدل الحدود الداخلية الثلاثة مع أساس محلي موثق فقط. التصنيف ليس تشخيصًا لصحة النبات.')
        (folder/language/'INDICATORS_CATALOG.md').write_text('\n\n'.join(cards) + '\n', 'utf-8')
        for source in (folder/language).glob('*.md'):
            body = render_markdown(source.read_text('utf-8'))
            home = 'Documentation home' if language == 'en' else 'الرئيسية'
            direction = 'rtl' if language == 'ar' else 'ltr'
            page = f'''<!doctype html><html lang="{language}" dir="{direction}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ATIAF — {source.stem}</title><style>body{{max-width:980px;margin:auto;padding:28px;color:#062d46;background:#f5f9fc;font:17px/1.85 "Segoe UI",Tahoma,sans-serif}}a{{color:#075f9c}}header{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #d8e5ed;padding-bottom:18px}}header img{{width:150px;height:auto}}pre,.table{{overflow-x:auto}}pre,code{{background:#e7f0f6;padding:3px 6px;border-radius:4px;unicode-bidi:isolate}}pre{{padding:18px}}table{{border-collapse:collapse;background:white;width:100%}}td{{padding:12px;border:1px solid #d8e5ed}}h2{{margin-top:40px}}h1{{line-height:1.5}}</style><header><img src="../assets/atiaf-logo.png" alt="ATIAF"><a href="../index.html">{home}</a></header><main>{body}</main></html>'''
            source.with_suffix('.html').write_text(page, 'utf-8')
    print('Built root/documentation portals and EN/AR HTML help; no network used.')


if __name__ == '__main__':
    main()
