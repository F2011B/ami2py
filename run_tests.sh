#!/usr/bin/env bash
set -e


# Build the Rust extensions
if [ -n "${CIRCLECI:-}" ] || [ -n "${GITHUB_ACTIONS:-}" ]; then
    # CI environments have network access, disable any offline config
    export CARGO_NET_OFFLINE=false
    COMMON_FLAGS="--release"
else
    # Default to offline mode for local environments to support Codex
    COMMON_FLAGS="--release --offline"
fi

# rust_bitparser
CARGO_FLAGS="--manifest-path rust_bitparser/Cargo.toml $COMMON_FLAGS"

# Determine platform specific library names
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
        LIB_PREFIX=""
        LIB_SUFFIX=".dll"
        DEST_EXT=".pyd"
        ;;
    Darwin*)
        LIB_PREFIX="lib"
        LIB_SUFFIX=".dylib"
        DEST_EXT=".so"
        ;;
    *)
        LIB_PREFIX="lib"
        LIB_SUFFIX=".so"
        DEST_EXT=".so"
        ;;
esac

RUST_LIB="rust_bitparser/target/release/${LIB_PREFIX}rust_bitparser${LIB_SUFFIX}"
DEST_LIB="ami2py/rust_bitparser${DEST_EXT}"

if [ ! -f "$RUST_LIB" ]; then
    cargo build $CARGO_FLAGS
fi
cp "$RUST_LIB" "$DEST_LIB"

# rust_amidatabase if available
if [ -f rust_amidatabase/Cargo.toml ]; then
    CARGO_FLAGS="--manifest-path rust_amidatabase/Cargo.toml $COMMON_FLAGS"
    RUST_LIB="rust_amidatabase/target/release/${LIB_PREFIX}rust_amidatabase${LIB_SUFFIX}"
    DEST_LIB="ami2py/rust_amidatabase${DEST_EXT}"
    if [ ! -f "$RUST_LIB" ]; then
        cargo build $CARGO_FLAGS
    fi
    cp "$RUST_LIB" "$DEST_LIB"
fi

# rust_amireader if available
if [ -f rust_amireader/Cargo.toml ]; then
    CARGO_FLAGS="--manifest-path rust_amireader/Cargo.toml $COMMON_FLAGS"
    RUST_LIB="rust_amireader/target/release/${LIB_PREFIX}rust_amireader${LIB_SUFFIX}"
    DEST_LIB="ami2py/rust_amireader${DEST_EXT}"
    if [ ! -f "$RUST_LIB" ]; then
        cargo build $CARGO_FLAGS
    fi
    cp "$RUST_LIB" "$DEST_LIB"
fi

python -m pytest "$@"
