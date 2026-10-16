#!/usr/bin/env bash
# Publica o pacote (ibl-site-deploy-*.zip) num domínio da hospedagem pela API
# do cPanel, por HTTPS. Não usa FTP.
#
# Uso:  scripts/deploy-cpanel.sh <usuario-cpanel> <dominio>
# Ex.:  scripts/deploy-cpanel.sh iblmaq teste.iblmaquinas.com.br
#
# Precisa de um token de API: cPanel → Segurança → "Gerenciar tokens de API"
# → Criar. O token é pedido na hora, não aparece na tela nem fica salvo.
# Revogue o token no cPanel quando terminar.
#
# O que faz: descobre a pasta do domínio, mostra, pede confirmação, envia o
# zip, extrai por cima (sobrescreve; não apaga nada) e apaga o zip do servidor.
set -euo pipefail

USUARIO=${1:?"uso: scripts/deploy-cpanel.sh <usuario-cpanel> <dominio>"}
DOMINIO=${2:?"uso: scripts/deploy-cpanel.sh <usuario-cpanel> <dominio>"}
HOST=${CPANEL_HOST:-iblmaquinas.com.br}
cd "$(dirname "$0")/.."

ZIP=$(ls -t ibl-site-deploy-*.zip 2>/dev/null | head -1 || true)
[[ -n $ZIP ]] || { echo "Nenhum pacote. Rode antes: npm run package:deploy"; exit 1; }
command -v python3 >/dev/null || { echo "python3 não encontrado"; exit 1; }

read -rsp "Token de API do cPanel (usuário $USUARIO): " TOKEN; echo
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
umask 077
printf 'header = "Authorization: cpanel %s:%s"\n' "$USUARIO" "$TOKEN" > "$TMP/auth.cfg"
unset TOKEN
api() { curl --silent --show-error --fail-with-body --max-time 600 -K "$TMP/auth.cfg" "$@"; }

echo "Procurando a pasta de $DOMINIO..."
PASTA=$(api "https://$HOST:2083/execute/DomainInfo/domains_data" --data-urlencode "format=list" | python3 -c '
import json, sys
d = json.load(sys.stdin)
if not d.get("status"):
    sys.exit("API recusou: " + "; ".join(d.get("errors") or ["sem detalhe"]))
alvo = sys.argv[1]
for item in d.get("data") or []:
    if item.get("domain") == alvo:
        print(item["documentroot"]); sys.exit()
sys.exit("Domínio " + alvo + " não está nesta conta cPanel. Domínios: " + ", ".join(i.get("domain","?") for i in d.get("data") or []))
' "$DOMINIO")

[[ -n $PASTA ]] || { echo "Não achei a pasta de $DOMINIO"; exit 1; }
echo "Pasta do site: $PASTA"
echo "Conteúdo hoje:"
api "https://$HOST:2083/execute/Fileman/list_files" --data-urlencode "dir=$PASTA" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print("\n".join("  "+f["file"] for f in d.get("data") or []))'
echo
read -rp "Enviar $ZIP e extrair em $PASTA por cima? [s/N] " OK
[[ $OK == [sS] ]] || { echo "Cancelado. Nada foi enviado."; exit 1; }

echo "Enviando $ZIP ($(du -h "$ZIP" | cut -f1))..."
api "https://$HOST:2083/execute/Fileman/upload_files" -F "dir=$PASTA" -F "file-1=@$ZIP" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0) if d.get("status") else sys.exit("Upload falhou: " + "; ".join(d.get("errors") or ["?"]))'

echo "Extraindo no servidor..."
api "https://$HOST:2083/json-api/cpanel" \
  --data-urlencode "cpanel_jsonapi_apiversion=2" --data-urlencode "cpanel_jsonapi_module=Fileman" \
  --data-urlencode "cpanel_jsonapi_func=fileop" --data-urlencode "op=extract" \
  --data-urlencode "sourcefiles=$PASTA/$ZIP" --data-urlencode "destfiles=$PASTA" \
  | python3 -c '
import json,sys; d=json.load(sys.stdin); r=d.get("cpanelresult",{})
if r.get("error") or not r.get("data"): sys.exit("Extração falhou: " + str(r.get("error") or d)[:300])
out=r["data"][0].get("output","") if isinstance(r["data"],list) else ""
print("  " + out.strip().splitlines()[-1] if out.strip() else "  ok")'

echo "Apagando o zip do servidor (contém a chave do Bitrix)..."
api "https://$HOST:2083/execute/Fileman/fileop" --data-urlencode "op=unlink" --data-urlencode "sourcefiles=$PASTA/$ZIP" >/dev/null || echo "  (não apagou o zip; remova $PASTA/$ZIP no Gerenciador de Arquivos)"

echo "Pronto. Confira: https://$DOMINIO/"
