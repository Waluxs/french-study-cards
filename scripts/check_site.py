"""Dependency-free predeployment checks. Exit nonzero to block publication."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'public'
manifest = json.loads((SITE / 'release-manifest.json').read_text(encoding='utf-8'))
pages = {}
checks = 0


def check(condition, message):
    global checks
    if not condition:
        raise AssertionError(message)
    checks += 1


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.cards = set()
        self.questions = set()
        self.duplicates = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                self.duplicates.append(a['id'])
            self.ids.add(a['id'])
        if a.get('data-card-id'):
            self.cards.add(a['data-card-id'])
        if a.get('data-question-id'):
            self.questions.add(a['data-question-id'])
        for field in ('href', 'src', 'data-lazy-src'):
            if a.get(field):
                self.links.append((field, a[field]))


for name, data in {**manifest['pages'], **manifest['assets']}.items():
    path = (SITE / name).resolve()
    check(path.is_relative_to(SITE.resolve()), f'Out-of-root resource: {name}')
    check(path.is_file() and not path.is_symlink(), f'Missing or symlink resource: {name}')
    raw = path.read_bytes()
    check(len(raw) == data['bytes'], f'Size mismatch: {name}')
    check(hashlib.sha256(raw).hexdigest() == data['sha256'], f'Hash mismatch: {name}')

check((SITE / '.nojekyll').exists(), 'Missing .nojekyll')
check((SITE / 'index.html').exists(), 'Missing index')
check(len(manifest['pages']) == 3, 'Expected three main pages')

for name in [*manifest['pages'], 'index.html']:
    text = (SITE / name).read_text(encoding='utf-8')
    pages[name] = Page(text)
    check(not pages[name].duplicates, f'Duplicate HTML ids: {name}: {pages[name].duplicates}')
    check('name="viewport"' in text, f'Missing mobile viewport: {name}')
    check(not re.search(r'(?:file:///|D:\\zheng\\|C:\\Users\\)', text), f'Local path leaked in {name}')
    check(not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)', text), f'Credential-like value in {name}')
    for index, script in enumerate(re.findall(r'<script\b[^>]*>(.*?)</script>', text, flags=re.S | re.I)):
        if not script.strip():
            continue
        check(shutil.which('node') is not None, 'Node required for JavaScript syntax checks')
        result = subprocess.run(['node', '--check'], input=script, encoding='utf-8', capture_output=True)
        check(result.returncode == 0, f'JS syntax failed {name} script {index}: {result.stderr}')

for name, parsed in pages.items():
    for field, value in parsed.links:
        url = urlsplit(value)
        if url.scheme or url.netloc:
            check(url.scheme not in ('file', 'javascript'), f'Unsafe link {name}: {value}')
            continue
        if not url.path and not url.fragment:
            continue
        target_name = unquote(url.path) or name
        path = (SITE / target_name).resolve()
        check(path.is_relative_to(SITE.resolve()), f'Out-of-root local link {name}: {value}')
        check(path.exists(), f'Broken local link {name}: {value}')
        if target_name in pages and url.fragment:
            check(unquote(url.fragment) in pages[target_name].ids, f'Broken anchor {name}: {value}')

vocab = pages['近期词块样包-01.html'].cards
recall = pages['只看法语.html'].cards
questions = pages['原题回顾.html'].questions
check(len(vocab) >= 120, f'Unexpected vocabulary card loss: {len(vocab)}')
check(vocab == recall, 'Vocabulary and recall card ids diverged')
check(len(questions) >= 208, f'Unexpected question loss: {len(questions)}')

# Only the explicit deploy allowlist may enter the public artifact.
allowed = set(manifest['pages']) | set(manifest['assets']) | {'index.html', '.nojekyll', 'robots.txt', 'release-manifest.json'}
actual = {str(p.relative_to(SITE)).replace('\\', '/') for p in SITE.rglob('*') if p.is_file()}
check(actual == allowed, f'Unexpected public files: {sorted(actual - allowed)}; missing: {sorted(allowed - actual)}')
print(json.dumps({'passed': checks, 'cards': len(vocab), 'questions': len(questions),
                  'assets': len(manifest['assets']), 'deployment_performed': False}, ensure_ascii=False))
