"""Local link checks with explicit immutable-report path migrations."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = {
    ('Reports/0009_advanced_modalities_and_gating.md', '../docs/en/ADVANCED_MODALITIES.md'): 'documentation/en/ADVANCED_MODALITIES.md',
    ('Reports/0009_advanced_modalities_and_gating.md', '../docs/ar/ADVANCED_MODALITIES.md'): 'documentation/ar/ADVANCED_MODALITIES.md',
    ('Reports/0022_professional_presentation_and_publication_preparation.md', '../Development_Plans/Active/PLAN-0016_professional_presentation_and_github_publication.md'): 'Development_Plans/Completed/PLAN-0016_professional_presentation_and_github_publication.md',
}


class LocalHTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for key, value in attrs if key in ('href', 'src') and value)


def broken_links():
    broken = []
    for source in ROOT.rglob('*'):
        if not source.is_file() or any(p in source.relative_to(ROOT).parts for p in ('.agent_resources', '.git', 'dist', 'build', '__pycache__')):
            continue
        if source.suffix not in ('.md', '.html') or source.name == 'site_template.html':
            continue
        parser = LocalHTMLLinks()
        content = source.read_text('utf-8')
        parser.feed(content)
        targets = parser.targets
        if source.suffix == '.md':
            targets += re.findall(r'\]\(([^)]+)\)', content)
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target_path = unquote(parsed.path)
            key = (source.relative_to(ROOT).as_posix(), target)
            resolved = ROOT/HISTORICAL[key] if key in HISTORICAL else source.parent/target_path
            if not resolved.exists():
                broken.append(f'{source.relative_to(ROOT)} -> {target}')
    return broken
