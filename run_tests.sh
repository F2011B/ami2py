#!/usr/bin/env bash
set -e

# Build the Rust extension in offline mode
CARGO_FLAGS="--manifest-path rust_bitparser/Cargo.toml --release --offline"

if [ ! -f rust_bitparser/target/release/librust_bitparser.so ]; then
    cargo build $CARGO_FLAGS
fi

# Copy the compiled library next to the Python sources
cp rust_bitparser/target/release/librust_bitparser.so ami2py/rust_bitparser.so

pytest "$@"
