#!/usr/bin/env python3
"""Baixa fotos oficiais Dynapac (roda no macOS, com rede).

Lê data/dynapac-downloads.json e salva em fotos-dynapac/{categoria}/{slug}/original.{ext}
Log: .tmp/dynapac-fotos.log
"""
import json, os, urllib.request, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, '.tmp', 'dynapac-fotos.log')
os.makedirs(os.path.dirname(LOG), exist_ok=True)
logf = open(LOG, 'w', buffering=1)

items = json.load(open(os.path.join(REPO, 'data', 'dynapac-downloads.json')))
ok = err = 0
for it in items:
    url = it['url']
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or '.jpg'
    dest_dir = os.path.join(REPO, 'fotos-dynapac', it['dest'])
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, 'original' + ext)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh) IBL-site-build'})
        with urllib.request.urlopen(req, timeout=40) as r, open(dest, 'wb') as f:
            f.write(r.read())
        size = os.path.getsize(dest) // 1024
        logf.write(f'OK {it["dest"]} ({size}KB)\n')
        ok += 1
    except Exception as exc:
        logf.write(f'ERRO {it["dest"]}: {exc}\n')
        err += 1
logf.write(f'FIM: {ok} ok, {err} erros\n')
