#!/usr/bin/env bash
set -e


# Build the Rust extensions in offline mode
COMMON_FLAGS="--release --offline"

# rust_bitparser
CARGO_FLAGS="--manifest-path rust_bitparser/Cargo.toml $COMMON_FLAGS"
if [ ! -f rust_bitparser/target/release/librust_bitparser.so ]; then
    cargo build $CARGO_FLAGS
fi
cp rust_bitparser/target/release/librust_bitparser.so ami2py/rust_bitparser.so

# rust_amidatabase if available
if [ -f rust_amidatabase/Cargo.toml ]; then
    CARGO_FLAGS="--manifest-path rust_amidatabase/Cargo.toml $COMMON_FLAGS"
    if [ ! -f rust_amidatabase/target/release/librust_amidatabase.so ]; then
        cargo build $CARGO_FLAGS
    fi
    cp rust_amidatabase/target/release/librust_amidatabase.so ami2py/rust_amidatabase.so
fi

# rust_amireader if available
if [ -f rust_amireader/Cargo.toml ]; then
    CARGO_FLAGS="--manifest-path rust_amireader/Cargo.toml $COMMON_FLAGS"
    if [ ! -f rust_amireader/target/release/librust_amireader.so ]; then
        cargo build $CARGO_FLAGS
    fi
    cp rust_amireader/target/release/librust_amireader.so ami2py/rust_amireader.so
fi

pytest "$@"
