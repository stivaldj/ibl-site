#!/usr/bin/env python3
"""Baixa as fotos oficiais Dynapac do catálogo nacional.

Lê data/dynapac-downloads.json e salva em fotos-dynapac/{categoria}/{slug}/original.{ext}
Cada item traz uma URL principal e alternativas: links da galeria do site às vezes
apontam para arquivos removidos, então tentamos em ordem até uma responder.
Log: .tmp/dynapac-fotos.log
"""
import argparse
import glob
import json
import os
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, '.tmp', 'dynapac-fotos.log')
UA = 'Mozilla/5.0 (Macintosh) IBL-site-build'
os.makedirs(os.path.dirname(LOG), exist_ok=True)
logf = open(LOG, 'w', buffering=1)


def normalizar(url):
    """Escapa espaços e afins no path sem mexer no que já está percent-encoded."""
    partes = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        partes._replace(path=urllib.parse.quote(partes.path, safe="/%"))
    )


def baixar(url, destino):
    req = urllib.request.Request(normalizar(url), headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(destino, 'wb') as f:
        f.write(r.read())


ap = argparse.ArgumentParser()
ap.add_argument('--force', action='store_true', help='rebaixa mesmo o que já existe')
args = ap.parse_args()

items = json.load(open(os.path.join(REPO, 'data', 'dynapac-downloads.json')))
ok = err = pulados = 0
for it in items:
    ja_existe = glob.glob(os.path.join(REPO, 'fotos-dynapac', it['dest'], 'original.*'))
    if ja_existe and not args.force:
        pulados += 1
        continue
    candidatas = [it['url']] + list(it.get('alternativas') or [])
    dest_dir = os.path.join(REPO, 'fotos-dynapac', it['dest'])
    os.makedirs(dest_dir, exist_ok=True)
    ultimo_erro = None
    for n, url in enumerate(candidatas):
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or '.jpg'
        dest = os.path.join(dest_dir, 'original' + ext)
        try:
            baixar(url, dest)
            size = os.path.getsize(dest) // 1024
            nota = '' if n == 0 else f' [alternativa {n}]'
            logf.write(f'OK {it["dest"]} ({size}KB){nota}\n')
            ok += 1
            break
        except Exception as exc:  # noqa: BLE001
            ultimo_erro = exc
            if os.path.exists(dest):
                os.remove(dest)
    else:
        logf.write(f'ERRO {it["dest"]}: {ultimo_erro}\n')
        err += 1
logf.write(f'FIM: {ok} ok, {err} erros, {pulados} já existentes\n')
print(f'{ok} ok, {err} erros, {pulados} já existentes — log em {LOG}')
