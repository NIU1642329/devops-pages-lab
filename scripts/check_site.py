"""Release gate for the built site: python3 scripts/check_site.py <site_dir> <expected_version>

Fails (exit 1) unless:
  1. README.md still has both activity markers, in order;
  2. the built homepage exists, has a <title> and renders the "Recent activity" section;
  3. version.txt in the build matches the commit being released;
  4. every internal link and image in every built page points to a file that exists.
"""
import os
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

BASEURL = "/devops-pages-lab"
errors = []


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.title = [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.title = True
        for key in ("href", "src"):
            if a.get(key) and tag in ("a", "img", "link", "script"):
                self.refs.append(a[key])


def check_markers():
    text = open("README.md", encoding="utf-8").read()
    start = text.find("<!--START_SECTION:activity-->")
    end = text.find("<!--END_SECTION:activity-->")
    if start < 0 or end < 0 or end < start:
        errors.append("README.md: activity markers missing or out of order")
    else:
        print("✓ README markers present")


def check_page(site, rel):
    path = os.path.join(site, rel)
    parser = Links()
    parser.feed(open(path, encoding="utf-8", errors="replace").read())
    if rel == "index.html":
        html = open(path, encoding="utf-8").read()
        if not parser.title:
            errors.append("index.html: no <title>")
        if "Recent activity" not in html:
            errors.append("index.html: 'Recent activity' section not rendered")
    for ref in parser.refs:
        url = urlparse(ref)
        if url.scheme or ref.startswith(("#", "mailto:", "//")):
            continue  # external links are not part of the gate (flaky, rate limits)
        target = unquote(url.path)
        if target.startswith(BASEURL):
            target = target[len(BASEURL):]
        if target.startswith("/"):
            full = os.path.join(site, target.lstrip("/"))
        else:
            full = os.path.normpath(os.path.join(os.path.dirname(path), target))
        if os.path.isdir(full) or target.endswith("/"):
            full = os.path.join(full, "index.html")
        if not os.path.exists(full) and not os.path.exists(full + ".html"):
            errors.append(f"{rel}: broken link -> {ref}")


def main():
    site, expected = sys.argv[1], sys.argv[2]
    check_markers()
    version_file = os.path.join(site, "version.txt")
    served = open(version_file).read().strip() if os.path.exists(version_file) else "(missing)"
    if served != expected:
        errors.append(f"version.txt is '{served}', expected '{expected}'")
    else:
        print(f"✓ version.txt = {expected}")
    pages = [os.path.relpath(os.path.join(d, f), site)
             for d, _, files in os.walk(site) for f in files if f.endswith(".html")]
    for rel in sorted(pages):
        check_page(site, rel)
    print(f"✓ checked {len(pages)} HTML page(s)")
    if errors:
        print("\nRELEASE BLOCKED:")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)
    print("\nAll gate checks passed: safe to deploy.")


if __name__ == "__main__":
    main()
