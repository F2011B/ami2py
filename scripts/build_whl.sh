#!/usr/bin/env bash
set -euo pipefail
echo "Starting wheel build" >&2

# Determine repository root
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BOOT_DIR="$ROOT_DIR/.bootstrap"
echo "Root directory: $ROOT_DIR" >&2
echo "Bootstrap directory: $BOOT_DIR" >&2
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
elif command -v python >/dev/null 2>&1; then
    PY=$(command -v python)
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
echo "Using Python at $PY" >&2

# On Windows, command -v may return a path without the required extension.
# Add '.exe' or '.bat' if those files exist so the executable can be invoked
if [ ! -f "$PY" ]; then
    if [ -f "${PY}.exe" ]; then
        PY="${PY}.exe"
    elif [ -f "${PY}.bat" ]; then
        PY="${PY}.bat"
    fi
fi

# Create and activate virtual environment
VENV_DIR="$BOOT_DIR/venv"
echo "Creating virtual environment in $VENV_DIR" >&2
"$PY" -m venv "$VENV_DIR"
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Windows virtualenv layout
    echo "Activating Windows virtualenv" >&2
    source "$VENV_DIR/Scripts/activate"
else
    # POSIX virtualenv layout
    echo "Activating POSIX virtualenv" >&2
    source "$VENV_DIR/bin/activate"
fi
pip install --upgrade pip build wheel >/dev/null

# ----------------------------------------------------------------------
# Ensure Rust
if ! command -v cargo >/dev/null 2>&1; then
    echo "Rust not found, bootstrapping locally" >&2
    RVER="1.75.0"
    RDIR="$BOOT_DIR/rust"
    mkdir -p "$RDIR"
    fetch "https://static.rust-lang.org/dist/rust-$RVER-x86_64-unknown-linux-gnu.tar.gz" "$BOOT_DIR/rust.tar.gz"
    tar -xzf "$BOOT_DIR/rust.tar.gz" -C "$RDIR" --strip-components=1
    export PATH="$RDIR/bin:$PATH"
else
    echo "Using system Rust" >&2
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
        echo "Building $CRATE" >&2
        cargo build --manifest-path "$ROOT_DIR/$CRATE/Cargo.toml" $COMMON_FLAGS
        SRC_LIB="$ROOT_DIR/$CRATE/target/release/${LIB_PREFIX}${CRATE}${LIB_SUFFIX}"
        DEST_LIB="$ROOT_DIR/ami2py/${CRATE}${DEST_EXT}"
        if [ -f "$SRC_LIB" ]; then
            cp "$SRC_LIB" "$DEST_LIB"
        else
            echo "Expected library not found: $SRC_LIB" >&2
            exit 1
        fi
    fi
done

# Build CLI binary
echo "Building ami_cli" >&2
cargo build --manifest-path "$ROOT_DIR/ami_cli/Cargo.toml" $COMMON_FLAGS
CLI_BIN="$ROOT_DIR/ami_cli/target/release/ami_cli${BIN_EXT}"
if [ ! -f "$CLI_BIN" ]; then
    echo "CLI binary not found: $CLI_BIN" >&2
    exit 1
fi

# Build wheel
export AMI_CLI_BIN="$CLI_BIN"
cd "$ROOT_DIR"
echo "Building wheel" >&2
python -m build --wheel

echo "Wheel built in $ROOT_DIR/dist" >&2

