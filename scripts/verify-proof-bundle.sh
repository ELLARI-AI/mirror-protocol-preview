#!/usr/bin/env bash
set -euo pipefail

mode="${1:-}"
proof_dir="${2:-docs/proof}"
manifest="$proof_dir/bundle_manifest.json"

validate_manifest() {
  if [[ ! -f "$manifest" ]]; then
    echo "::error::Missing manifest: $manifest" >&2
    return 1
  fi

  if ! jq -e '
    type == "object"
    and (.title | type == "string" and length > 0)
    and (.version | type == "string" and length > 0)
    and (.files | type == "array" and length > 0 and all(.[]; type == "string" and length > 0))
    and (.issuer | type == "string" and length > 0)
    and (.license | type == "string" and length > 0)
  ' "$manifest" >/dev/null; then
    echo "::error::Invalid proof manifest schema: $manifest" >&2
    return 1
  fi
}

check_referenced_files() {
  validate_manifest
  while IFS= read -r file; do
    if [[ ! -f "$proof_dir/$file" ]]; then
      echo "::error::Missing referenced proof file: $file" >&2
      return 1
    fi
  done < <(jq -r '.files[]' "$manifest")
}

compute_hashes() {
  check_referenced_files
  while IFS= read -r file; do
    sha256sum "$proof_dir/$file"
  done < <(jq -r '.files[]' "$manifest")
}

case "$mode" in
  validate) validate_manifest ;;
  files) check_referenced_files ;;
  hashes) compute_hashes ;;
  *)
    echo "Usage: $0 {validate|files|hashes} [proof-directory]" >&2
    exit 2
    ;;
esac
