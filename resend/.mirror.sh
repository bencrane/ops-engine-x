#!/usr/bin/env bash
# Mirror all Resend docs (.md pages) listed in llms.txt into resend/docs/.
# Preserves URL path structure so /docs/api-reference/emails/send-email.md
# lands at resend/docs/api-reference/emails/send-email.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
INDEX="$ROOT/docs/llms.txt"
BASE="https://resend.com/docs/"
DEST="$ROOT/docs"
UA="Mozilla/5.0 (resend-docs-mirror)"

if [[ ! -f "$INDEX" ]]; then
  echo "missing $INDEX" >&2
  exit 1
fi

URL_LIST="$(grep -oE 'https://resend\.com/docs/[^)]+\.md' "$INDEX" | sort -u)"
COUNT="$(printf '%s\n' "$URL_LIST" | wc -l | tr -d ' ')"
echo "found $COUNT markdown URLs"

fetch_one() {
  local url="$1"
  local rel="${url#${BASE}}"
  local out="$DEST/$rel"
  mkdir -p "$(dirname "$out")"
  if curl -sS -f --retry 3 --retry-delay 1 -A "$UA" "$url" -o "$out"; then
    printf 'ok  %s\n' "$rel"
  else
    printf 'ERR %s\n' "$rel" >&2
    return 1
  fi
}

export -f fetch_one
export BASE DEST UA

# 8-way parallel fetch
printf '%s\n' "$URL_LIST" | xargs -n1 -P8 -I{} bash -c 'fetch_one "$@"' _ {}

echo "done"
