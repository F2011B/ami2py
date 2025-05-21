#!/bin/sh

set -e

# we expect to be run from the repository root
cd "$(dirname "$0")/rust_bitparser"

# im Projektverzeichnis
cargo generate-lockfile          # erstellt/aktualisiert Cargo.lock
cargo vendor --locked vendor/    # spiegelt alle Abhängigkeiten nach ./vendor
