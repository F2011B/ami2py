#!/usr/bin/env bash
set -euo pipefail

# Determine repository root
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BOOT_DIR="$ROOT_DIR/.bootstrap"
mkdir -p "$BOOT_DIR"

# Helper to download a file if it does not already exist
fetch() {
    local url="$1" dest="$2"
    if [ ! -f "$dest" ]; then
        echo "Downloading $url" >&2
        curl -L "$url" -o "$dest"
    fi
}

# ----------------------------------------------------------------------
# Ensure Python
if command -v python3 >/dev/null 2>&1; then
    PY=$(command -v python3)
else
    PYVER="3.11.6"
    PYDIR="$BOOT_DIR/python"
    mkdir -p "$PYDIR"
    fetch "https://www.python.org/ftp/python/$PYVER/Python-$PYVER.tgz" "$BOOT_DIR/python.tgz"
    tar -xzf "$BOOT_DIR/python.tgz" -C "$PYDIR" --strip-components=1
    pushd "$PYDIR" >/dev/null
    ./configure --prefix="$PYDIR/install" >/dev/null
    make -j"$(nproc)" >/dev/null
    make install >/dev/null
    popd >/dev/null
    PY="$PYDIR/install/bin/python3"
    export PATH="$PYDIR/install/bin:$PATH"
fi

# Create and activate virtual environment
"$PY" -m venv "$BOOT_DIR/venv"
source "$BOOT_DIR/venv/bin/activate"
pip install --upgrade pip build wheel >/dev/null

# ----------------------------------------------------------------------
# Ensure Rust
if ! command -v cargo >/dev/null 2>&1; then
    RVER="1.75.0"
    RDIR="$BOOT_DIR/rust"
    mkdir -p "$RDIR"
    fetch "https://static.rust-lang.org/dist/rust-$RVER-x86_64-unknown-linux-gnu.tar.gz" "$BOOT_DIR/rust.tar.gz"
    tar -xzf "$BOOT_DIR/rust.tar.gz" -C "$RDIR" --strip-components=1
    export PATH="$RDIR/bin:$PATH"
fi

# Determine platform specifics
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
        LIB_PREFIX=""
        LIB_SUFFIX=".dll"
        DEST_EXT=".pyd"
        BIN_EXT=".exe"
        ;;
    Darwin*)
        LIB_PREFIX="lib"
        LIB_SUFFIX=".dylib"
        DEST_EXT=".so"
        BIN_EXT=""
        ;;
    *)
        LIB_PREFIX="lib"
        LIB_SUFFIX=".so"
        DEST_EXT=".so"
        BIN_EXT=""
        ;;
esac

COMMON_FLAGS="--release --offline"

# Build Rust libraries and copy them into the package
for CRATE in rust_bitparser rust_amidatabase rust_amireader; do
    if [ -f "$ROOT_DIR/$CRATE/Cargo.toml" ]; then
        cargo build --manifest-path "$ROOT_DIR/$CRATE/Cargo.toml" $COMMON_FLAGS
        cp "$ROOT_DIR/$CRATE/target/release/${LIB_PREFIX}${CRATE}${LIB_SUFFIX}" \
           "$ROOT_DIR/ami2py/${CRATE}${DEST_EXT}"
    fi
done

# Build CLI binary
cargo build --manifest-path "$ROOT_DIR/ami_cli/Cargo.toml" $COMMON_FLAGS
CLI_BIN="$ROOT_DIR/ami_cli/target/release/ami_cli${BIN_EXT}"

# Build wheel
export AMI_CLI_BIN="$CLI_BIN"
cd "$ROOT_DIR"
python -m build --wheel

echo "Wheel built in $ROOT_DIR/dist" >&2

