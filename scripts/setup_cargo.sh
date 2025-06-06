#!/usr/bin/env bash
set -euo pipefail

# Repository-Root ermitteln
root_dir="$(cd "$(dirname "$0")/.." && pwd)"
proj_dir="$root_dir/rust/rust_ami_py"

cd "$proj_dir"

# Alte Vendor-Kopie + Config entfernen, falls vorhanden
rm -rf vendor
rm -f .cargo/config.toml

# Lockfile sicherstellen
cargo generate-lockfile

# Abhängigkeiten spiegeln und neue Config erzeugen
mkdir -p .cargo
cargo vendor --locked vendor > .cargo/config.toml

echo "✔ Alle Crates wurden nach rust/rust_ami_py/vendor gespiegelt."
echo "  Offline-Build:  cargo build --offline"
