#!/usr/bin/env python3
"""Limpeza staging pos-v3.6: remove recortes -nobg substituidos por -card. Log: .tmp/ftp-cleanup36.log"""
import ftplib, os
def _ftp_credencial():
    """Lê FTP_HOST, FTP_USER e FTP_PASS do ambiente ou de .env.ftp.local na raiz do repo (fora do git). Nunca escreva a senha no código."""
    cred = {}
    arq = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.ftp.local')
    if os.path.exists(arq):
        for linha in open(arq, encoding='utf-8'):
            if '=' in linha and not linha.lstrip().startswith('#'):
                k, v = linha.strip().split('=', 1); cred[k.strip()] = v.strip()
    cred.update({k: os.environ[k] for k in ('FTP_HOST', 'FTP_USER', 'FTP_PASS') if os.environ.get(k)})
    falta = [k for k in ('FTP_HOST', 'FTP_USER', 'FTP_PASS') if not cred.get(k)]
    if falta:
        raise SystemExit('Falta ' + ', '.join(falta) + ': defina no ambiente ou em .env.ftp.local (fora do git).')
    return cred['FTP_HOST'], cred['FTP_USER'], cred['FTP_PASS']


HOST, USER, PASS = _ftp_credencial()
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, ".tmp", "ftp-cleanup36.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)
logf = open(LOG, "w", buffering=1)
ARQUIVOS = ['case-assets/escavadeiras-hidraulicas/cx130c/cx130c-nobg.webp', 'case-assets/escavadeiras-hidraulicas/cx220c-s2/cx220c-s2-nobg.webp', 'case-assets/escavadeiras-hidraulicas/cx350c/cx350c-nobg.webp', 'case-assets/fotos-processed/885b-motoniveladora-nobg.webp', 'case-assets/fotos-processed/cx220c-lateral-nobg.webp', 'case-assets/fotos-processed/cx220c-v1-nobg.webp', 'case-assets/fotos-processed/cx22d-nobg.webp', 'case-assets/fotos-processed/trator-2050m-nobg.webp', 'case-assets/fotos-processed/unknown-dji-nobg.webp', 'case-assets/fotos-processed/unknown-ds8336-nobg.webp', 'case-assets/fotos-processed/unknown-ds8800-nobg.webp', 'case-assets/fotos-processed/w20f-studio-nobg.webp', 'case-assets/fotos-processed/w20g-front-nobg.webp', 'case-assets/minicarregadeiras/sr250b/sr250b-nobg.webp', 'case-assets/miniescavadeiras/cx22d/cx22d-nobg.webp', 'case-assets/miniescavadeiras/cx35d/cx35d-nobg.webp', 'case-assets/motoniveladoras/845b-series-2/845b-series-2-nobg.webp', 'case-assets/motoniveladoras/865b-series-2/865b-nobg.webp', 'case-assets/motoniveladoras/865b-series-2/865b-series-2-nobg.webp', 'case-assets/motoniveladoras/885b-series-2/885b-series-2-nobg.webp', 'case-assets/pas-carregadeiras/w20g/w20g-nobg.webp', 'case-assets/retroescavadeiras/575sv/575sv-nobg.webp', 'case-assets/tratores-de-esteiras/1150l/1150l-nobg.webp', 'case-assets/tratores-de-esteiras/1650l/1650l-nobg.webp', 'case-assets/tratores-de-esteiras/2050m/2050m-nobg.webp', 'case-assets/tratores-de-esteiras/750m/750m-nobg.webp', 'case-assets/tratores-de-esteiras/850m/850m-nobg.webp']
ftp = ftplib.FTP(HOST, timeout=40)
ftp.login(USER, PASS)
ok = 0
for f in ARQUIVOS:
    try:
        ftp.delete(f); ok += 1; logf.write("DEL %s\n" % f)
    except ftplib.error_perm as exc:
        logf.write("SKIP %s: %s\n" % (f, exc))
ftp.quit()
logf.write("FIM_OK %d/%d\n" % (ok, len(ARQUIVOS)))
