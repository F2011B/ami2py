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

# rust python wrappers (single crate)
CARGO_FLAGS="--manifest-path rust/rust_ami_py/Cargo.toml $COMMON_FLAGS --target-dir rust/rust_ami_py/target"

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

# build wrappers if library not already built
RUST_LIB_DIR="rust/rust_ami_py/target/release"
if [ ! -f "$RUST_LIB_DIR/${LIB_PREFIX}rust_ami_py${LIB_SUFFIX}" ]; then
    cargo build $CARGO_FLAGS
fi

for mod in rust_bitparser rust_amidatabase rust_amireader; do
    RUST_LIB="$RUST_LIB_DIR/${LIB_PREFIX}rust_ami_py${LIB_SUFFIX}"
    DEST_LIB="ami2py/${mod}${DEST_EXT}"
    cp "$RUST_LIB" "$DEST_LIB"
done

# Build ami_cli if available
if [ -f rust/ami_cli/Cargo.toml ]; then
    cargo build --manifest-path rust/ami_cli/Cargo.toml $COMMON_FLAGS || true
fi

python -m pytest "$@"
