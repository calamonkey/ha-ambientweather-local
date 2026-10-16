#!/usr/bin/env bash
# Fail if tracked files contain LAN IPs, real-looking MACs, or any string listed in
# scripts/private_strings.txt (git-ignored, one per line: your MAC, station keys, ...).
set -u
fail=0
if git grep -nE '192\.168\.[0-9]+\.[0-9]+|10\.[0-9]+\.[0-9]+\.[0-9]+' -- . ':!scripts/check_private.sh'; then fail=1; fi
if git grep -nEi '([0-9a-f]{2}:){5}[0-9a-f]{2}' -- . ':!tests' ':!scripts/check_private.sh'; then fail=1; fi
if [ -f scripts/private_strings.txt ]; then
  while IFS= read -r s; do [ -n "$s" ] && git grep -nF -- "$s" && fail=1; done < scripts/private_strings.txt
fi
exit $fail
