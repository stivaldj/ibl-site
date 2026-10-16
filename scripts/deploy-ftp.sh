#!/usr/bin/env bash
# Envia o pacote de deploy (ibl-site-deploy-*.zip) para a hospedagem por FTPS.
#
# Uso:   scripts/deploy-ftp.sh <usuario-ftp> [servidor]
# Ex.:   scripts/deploy-ftp.sh siteadmin@teste.iblmaquinas.com.br
#
# A senha é pedida na hora, fica só na memória deste script e some ao terminar.
# O servidor padrão é o nome da HostGator, que é o que o certificado TLS cobre.
# Só envia e sobrescreve; nunca apaga nada no servidor.
set -euo pipefail

USUARIO=${1:?"uso: scripts/deploy-ftp.sh <usuario-ftp> [servidor]"}
SERVIDOR=${2:-br302-ip05.hostgator.com.br}
# O nome acima é o que o certificado cobre, mas no DNS público ele aponta para
# outra máquina. A conexão vai para o IP de ftp.iblmaquinas.com.br e o TLS
# continua conferindo o certificado pelo nome.
IP=$(dig +short ftp.iblmaquinas.com.br | tail -1)
[[ -n $IP ]] || { echo "Não resolvi ftp.iblmaquinas.com.br"; exit 1; }
cd "$(dirname "$0")/.."

ZIP=$(ls -t ibl-site-deploy-*.zip 2>/dev/null | head -1 || true)
[[ -n $ZIP ]] || { echo "Nenhum pacote. Rode antes: npm run package:deploy"; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir "$TMP/site"
unzip -q "$ZIP" -d "$TMP/site"
TOTAL=$(find "$TMP/site" -type f | wc -l | tr -d ' ')

read -rsp "Senha FTP de $USUARIO: " SENHA; echo
umask 077
printf 'machine %s login %s password %s\n' "$SERVIDOR" "$USUARIO" "$SENHA" > "$TMP/netrc"
unset SENHA

# --disable-epsv: servidor da HostGator trava no modo estendido (a listagem
# ficava parada para sempre); PASV clássico funciona. Tempo limite para
# nunca mais pendurar sem aviso.
CURL=(curl --silent --show-error --ssl-reqd --netrc-file "$TMP/netrc" --ftp-create-dirs
      --ftp-pasv --disable-epsv --connect-timeout 20
      --connect-to "$SERVIDOR:21:$IP:21"
      --tls-max 1.2)
# --tls-max 1.2: o Pure-FTPd da HostGator exige reaproveitar a sessão TLS no
# canal de dados; com TLS 1.3 o curl do macOS não reaproveita e cada envio
# volta 451.

echo
echo "Pasta remota agora:"
if ! "${CURL[@]}" --max-time 60 --list-only "ftp://$SERVIDOR/" > "$TMP/pasta.txt"; then
  echo "Não consegui listar a pasta remota (senha errada ou conexão bloqueada). Nada foi enviado."
  exit 1
fi
sed 's/^/  /' "$TMP/pasta.txt"
echo
read -rp "Esta é a pasta do site certo? Enviar $TOTAL arquivos de $ZIP por cima? [s/N] " OK
[[ $OK == [sS] ]] || { echo "Cancelado. Nada foi enviado."; exit 1; }

# Um único curl para todos os arquivos: reaproveita a conexão
( cd "$TMP/site" && find . -type f | sed 's|^\./||' ) | while IFS= read -r arq; do
  printf 'upload-file = "%s/site/%s"\nurl = "ftp://%s/%s"\n' "$TMP" "$arq" "$SERVIDOR" "$arq"
done > "$TMP/lista.cfg"

# Ensaio com um arquivo pequeno antes dos outros: se o servidor recusar,
# mostra só as respostas dele (linhas "<"), nunca o que enviamos (a senha)
echo "Testando o envio com robots.txt..."
if ! "${CURL[@]}" -v -T "$TMP/site/robots.txt" "ftp://$SERVIDOR/robots.txt" -o /dev/null 2> "$TMP/ensaio.log"; then
  echo "O servidor recusou o envio. Respostas dele:"
  grep '^< [45]' "$TMP/ensaio.log" | sed 's/^< /  /' | tail -5
  echo "Nada foi enviado."
  exit 1
fi

echo "Enviando $TOTAL arquivos (leva alguns minutos)..."
"${CURL[@]}" --fail-early -K "$TMP/lista.cfg" -o /dev/null
echo "Pronto: $TOTAL arquivos enviados."
