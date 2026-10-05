#!/usr/bin/env python3
import argparse, json, re, sys, time
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen

UA = "CloudStreamBuilder-AutoPilot/1.0"

def fetch(url, timeout=15):
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(req, timeout=timeout) as r:
        data = r.read()
        ctype = r.headers.get("content-type", "")
        return r.geturl(), data[:2_000_000], ctype

def clean_url(base, href):
    if not href:
        return None
    u = urldefrag(urljoin(base, href.strip()))[0]
    p = urlparse(u)
    if p.scheme not in ("http", "https"):
        return None
    return u

def text_from_html(s):
    s = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def scan(start, depth):
    host = urlparse(start).netloc
    q = deque([(start, 0)])
    seen = set()
    pages = []
    links = set()
    paths = set()
    categories = []
    media_candidates = []
    api_candidates = []

    while q:
        url, d = q.popleft()
        if url in seen or d > depth:
            continue
        seen.add(url)
        try:
            final, raw, ctype = fetch(url)
            html = raw.decode("utf-8", "ignore")
        except Exception as e:
            pages.append({"url": url, "depth": d, "error": str(e)})
            continue

        title_m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
        title = text_from_html(title_m.group(1)) if title_m else ""
        text = text_from_html(html)

        for m in re.finditer(r'(?i)(?:href|src|action)\s*=\s*["\']([^"\']+)["\']', html):
            u = clean_url(final, m.group(1))
            if not u:
                continue
            links.add(u)
            p = urlparse(u)
            if p.netloc == host:
                paths.add(p.path or "/")
                low = (p.path or "").lower()
                if any(x in low for x in ("/kategori", "/category", "/genre", "/kanal", "/channel", "/dizi", "/film")):
                    categories.append(u)
                if any(x in low for x in ("/api/", "/ajax", "/search", "/graphql", ".json")):
                    api_candidates.append(u)
                if d < depth:
                    q.append((u, d + 1))

        for m in re.finditer(r'(?i)(https?://[^"\'\s<>]+)', html):
            u = urldefrag(m.group(1))[0]
            if any(x in u.lower() for x in (".m3u8", ".mp4", ".mpd")):
                media_candidates.append(u)

        pages.append({
            "url": final,
            "depth": d,
            "title": title,
            "text_sample": text[:1200],
            "links_found": len(links)
        })

    return {
        "schema": "cloudstream-builder-scan/v1",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "start_url": start,
        "host": host,
        "depth": depth,
        "pages": pages,
        "discovered_paths": sorted(paths),
        "category_candidates": sorted(set(categories)),
        "api_candidates": sorted(set(api_candidates)),
        "media_candidates": sorted(set(media_candidates)),
        "stats": {
            "pages": len(pages),
            "links": len(links),
            "paths": len(paths),
            "category_candidates": len(set(categories)),
            "api_candidates": len(set(api_candidates)),
            "media_candidates": len(set(media_candidates))
        }
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--kind", default="movie")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    if not re.match(r"^https?://", a.url):
        raise SystemExit("URL http:// veya https:// ile başlamalı.")
    result = scan(a.url, max(0, min(a.depth, 4)))
    result["kind"] = a.kind
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result["stats"], ensure_ascii=False))

if __name__ == "__main__":
    main()
