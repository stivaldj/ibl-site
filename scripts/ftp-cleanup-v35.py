#!/usr/bin/env python3
"""Limpeza no servidor de staging pós-v3.5 (roda no macOS, com rede).

Remove do teste.iblmaquinas.com.br:
- páginas das escavadeiras excluídas (acima da CX350C)
- assets das escavadeiras excluídas
- recortes -nobg.webp substituídos por -card.webp

Log: .tmp/ftp-cleanup.log
"""
import ftplib
import os

HOST = "ftp.iblmaquinas.com.br"
USER = "siteadmin@teste.iblmaquinas.com.br"
PASS = "CCLABPHB7C07"

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, ".tmp", "ftp-cleanup.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)
logf = open(LOG, "w", buffering=1)

DIRS_RECURSIVOS = [
    "case/escavadeiras-hidraulicas/cx370c-me",
    "case/escavadeiras-hidraulicas/cx490c",
    "case/escavadeiras-hidraulicas/cx500c",
    "case/escavadeiras-hidraulicas/cx800b",
    "case-assets/escavadeiras-hidraulicas/cx370c-me",
    "case-assets/escavadeiras-hidraulicas/cx490c",
    "case-assets/escavadeiras-hidraulicas/cx500c",
    "case-assets/escavadeiras-hidraulicas/cx800b",
]

ARQUIVOS = [
    "case-assets/pas-carregadeiras/621e/621e-nobg.webp",
    "case-assets/pas-carregadeiras/721e/721e-nobg.webp",
    "case-assets/pas-carregadeiras/821e/821e-nobg.webp",
    "case-assets/minicarregadeiras/sr150b/sr150b-nobg.webp",
    "case-assets/minicarregadeiras/sr175b/sr175b-nobg.webp",
    "case-assets/minicarregadeiras/sr200b/sr200b-nobg.webp",
    "case-assets/minicarregadeiras/sv185b/sv185b-nobg.webp",
]


def rmtree(ftp, path):
    """Remove diretório recursivamente; ignora se não existir."""
    try:
        entries = list(ftp.mlsd(path))
    except ftplib.error_perm as exc:
        logf.write(f"SKIP dir {path}: {exc}\n")
        return
    for name, facts in entries:
        if name in (".", ".."):
            continue
        child = f"{path}/{name}"
        if facts.get("type") == "dir":
            rmtree(ftp, child)
        else:
            try:
                ftp.delete(child)
                logf.write(f"DEL {child}\n")
            except ftplib.error_perm as exc:
                logf.write(f"ERRO del {child}: {exc}\n")
    try:
        ftp.rmd(path)
        logf.write(f"RMD {path}\n")
    except ftplib.error_perm as exc:
        logf.write(f"ERRO rmd {path}: {exc}\n")


def main():
    ftp = ftplib.FTP(HOST, timeout=40)
    ftp.login(USER, PASS)
    logf.write(f"conectado: {ftp.pwd()}\n")
    for d in DIRS_RECURSIVOS:
        rmtree(ftp, d)
    for f in ARQUIVOS:
        try:
            ftp.delete(f)
            logf.write(f"DEL {f}\n")
        except ftplib.error_perm as exc:
            logf.write(f"SKIP {f}: {exc}\n")
    ftp.quit()
    logf.write("FIM_OK\n")


try:
    main()
except Exception as exc:  # noqa: BLE001
    logf.write(f"FALHA: {exc}\n")
    raise
