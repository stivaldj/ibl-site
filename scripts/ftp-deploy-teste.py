#!/usr/bin/env python3
"""Deploy do pacote de TESTE via FTP (roda no macOS, fora da VM).

Extrai ibl-site-TESTE-20260810.zip e espelha tudo no FTP
siteadmin@teste.iblmaquinas.com.br. Log em .tmp/ftp-deploy.log.
"""
import os, sys, tempfile, zipfile, posixpath
from ftplib import FTP, error_perm

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP = os.path.join(REPO, 'ibl-site-TESTE-20260810.zip')
LOG = os.path.join(REPO, '.tmp', 'ftp-deploy.log')
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

os.makedirs(os.path.dirname(LOG), exist_ok=True)
logf = open(LOG, 'w', buffering=1)
def log(msg):
    logf.write(msg + '\n')

try:
    tmp = tempfile.mkdtemp(prefix='ibl-teste-')
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(tmp)
    total = sum(len(fs) for _, _, fs in os.walk(tmp))
    log(f'extraído: {total} arquivos em {tmp}')

    ftp = FTP()
    ftp.connect(HOST, 21, timeout=30)
    ftp.login(USER, PASS)
    log(f'login OK — raiz: {ftp.pwd()}')
    root_list = ftp.nlst()
    log(f'raiz contém: {root_list[:10]}')

    # Se a raiz do FTP for o home (com public_html), entrar nele
    base = ''
    if 'public_html' in root_list:
        base = 'public_html'
        log('usando public_html/ como docroot')

    made = set()
    def ensure_dir(remote_dir):
        if not remote_dir or remote_dir in made:
            return
        parent = posixpath.dirname(remote_dir)
        ensure_dir(parent)
        try:
            ftp.mkd(remote_dir)
        except error_perm:
            pass  # já existe
        made.add(remote_dir)

    sent = 0
    errors = []
    for dirpath, _, files in os.walk(tmp):
        rel = os.path.relpath(dirpath, tmp)
        remote_dir = base if rel == '.' else posixpath.join(base, rel.replace(os.sep, '/')) if base else rel.replace(os.sep, '/')
        if rel != '.':
            ensure_dir(remote_dir)
        for name in files:
            local = os.path.join(dirpath, name)
            remote = posixpath.join(remote_dir, name) if remote_dir and remote_dir != '.' else name
            try:
                with open(local, 'rb') as fh:
                    ftp.storbinary(f'STOR {remote}', fh)
                sent += 1
                if sent % 20 == 0:
                    log(f'{sent}/{total} enviados...')
            except Exception as exc:
                errors.append(f'{remote}: {exc}')
                log(f'ERRO {remote}: {exc}')

    log(f'CONCLUÍDO: {sent}/{total} enviados, {len(errors)} erros')
    if errors:
        log('Primeiros erros: ' + '; '.join(errors[:5]))
    ftp.quit()
    log('FIM_OK' if not errors else 'FIM_COM_ERROS')
except Exception as exc:
    log(f'FALHA_GERAL: {type(exc).__name__}: {exc}')
    sys.exit(1)
