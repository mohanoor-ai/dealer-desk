#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
command -v docker >/dev/null 2>&1 || { echo 'Install and start Docker with Compose first.'; exit 1; }
docker info >/dev/null
if [ ! -f .env ]; then
  umask 077
  generated_password=$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')
  printf 'POSTGRES_PASSWORD=%s\nDEALER_PORT=8090\n' "$generated_password" > .env
fi
docker compose up --build -d --wait --wait-timeout 180
docker compose exec app python -m scripts.create_user manager --role manager --if-empty
app_port=$(sed -n 's/^DEALER_PORT=//p' .env | tail -n 1)
printf 'Open http://127.0.0.1:%s - local to this computer. Stop with: docker compose stop\n' "${app_port:-8090}"
