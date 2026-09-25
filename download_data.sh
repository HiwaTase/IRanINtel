#!/usr/bin/env bash
set -euo pipefail
url='https://github.com/HiwaTase/IRanINtel/releases/download/v1/result.json'
expected='a049f1dbeceee1b8d0332583182e8962a7dd37d07814da29fcb8339ae5cf8a96'
output="${1:-result.json}"
curl -L --fail --retry 3 --output "$output" "$url"
actual="$(sha256sum "$output" | cut -d ' ' -f 1)"
if [[ "$actual" != "$expected" ]]; then
  echo "Checksum mismatch for $output" >&2
  exit 1
fi
echo "Downloaded and verified $output"
