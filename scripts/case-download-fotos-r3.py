#!/usr/bin/env python3
"""Baixa fotos oficiais CASE round 3 (roda no macOS, com rede).

Lê data/case-downloads-r3.json e salva em fotos-case-r3/{dest}/{name}.img
Log: .tmp/case-fotos-r3.log
"""
import json
import os
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, '.tmp', 'case-fotos-r3.log')
os.makedirs(os.path.dirname(LOG), exist_ok=True)
logf = open(LOG, 'w', buffering=1)

items = json.load(open(os.path.join(REPO, 'data', 'case-downloads-r3.json')))
ok = err = 0
for it in items:
    dest_dir = os.path.join(REPO, 'fotos-case-r3', it['dest'])
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, it['name'] + '.img')
    try:
        req = urllib.request.Request(it['url'], headers={'User-Agent': 'Mozilla/5.0 (Macintosh) IBL-site-build'})
        with urllib.request.urlopen(req, timeout=45) as r, open(dest, 'wb') as f:
            f.write(r.read())
        size = os.path.getsize(dest) // 1024
        logf.write('OK %s/%s (%dKB)\n' % (it['dest'], it['name'], size))
        ok += 1
    except Exception as exc:
        logf.write('ERRO %s/%s: %s\n' % (it['dest'], it['name'], exc))
        err += 1
logf.write('FIM: %d ok, %d erros\n' % (ok, err))
