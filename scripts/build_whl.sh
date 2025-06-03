#!/usr/bin/env bash
# Fail fast and show progress
set -euo pipefail
echo "Starting wheel build" >&2

# Optional argument to force a clean bootstrap
CLEAN_BOOTSTRAP=0
while [ $# -gt 0 ]; do
    case "$1" in
        -c|--clean)
            CLEAN_BOOTSTRAP=1
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
    shift
done
# Provide more detailed output for troubleshooting

# Determine repository root
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo $ROOT_DIR
BOOT_DIR="$ROOT_DIR/.bootstrap"
echo "Root directory: $ROOT_DIR" >&2
echo "Bootstrap directory: $BOOT_DIR" >&2
mkdir -p "$BOOT_DIR"

PYDIR="$BOOT_DIR/python"
VENV_DIR="$BOOT_DIR/venv"

if [ "$CLEAN_BOOTSTRAP" -eq 1 ]; then
    echo "Performing clean bootstrap" >&2
    rm -rf "$PYDIR" "$VENV_DIR"
fi

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


echo "Bootstrapping Python" >&2
PYVER="3.11.6"

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
        if [ ! -x "$PYDIR/python.exe" ]; then
            mkdir -p "$PYDIR"
            echo "Fetching Python interpreter from F2011B/python311" >&2
            if command -v git >/dev/null 2>&1; then
                git clone --depth 1 https://github.com/F2011B/python311 "$PYDIR"
            else
                echo "git not found, cannot bootstrap python" >&2
                exit 1
            fi
        fi
        PY="$PYDIR/python.exe"
        export PATH="$PYDIR:$PATH"
        ;;
    *)
        if [ ! -x "$PYDIR/install/bin/python3" ]; then
            mkdir -p "$PYDIR"
            fetch "https://www.python.org/ftp/python/$PYVER/Python-$PYVER.tgz" "$BOOT_DIR/python.tgz"
            tar -xzf "$BOOT_DIR/python.tgz" -C "$PYDIR" --strip-components=1
            pushd "$PYDIR" >/dev/null
            echo "Configuring Python $PYVER" >&2
            ./configure --prefix="$PYDIR/install" >/dev/null
            echo "Compiling Python" >&2
            make -j"$(nproc)" >/dev/null
            make install >/dev/null
            popd >/dev/null
        fi
        PY="$PYDIR/install/bin/python3"
        export PATH="$PYDIR/install/bin:$PATH"
        ;;
esac


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
if [ ! -x "$PY" ]; then
    echo "Warning: Python executable not found at $PY" >&2
else
    echo "Using Python executable $(command -v "$PY" || echo "$PY")" >&2
fi

# Create and activate virtual environment
echo "Creating virtual environment in $VENV_DIR" >&2
"$PY" -m venv "$VENV_DIR"
echo "Created ${VENV_DIR}"
# Some python installations (e.g. those created with `pyvenv`) do not
# include the usual activation scripts.  If they are missing, retry
# using `virtualenv` which always provides them.
if [ ! -f "$VENV_DIR/bin/activate" ] && [ ! -f "$VENV_DIR/Scripts/activate" ]; then
    echo "Virtualenv missing activate script, recreating using virtualenv" >&2
    "$PY" -m pip install --upgrade virtualenv >/dev/null
    rm -rf "$VENV_DIR"
    "$PY" -m virtualenv "$VENV_DIR" >/dev/null
fi
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Windows virtualenv layout
    echo "Activating Windows virtualenv" >&2
    source "$VENV_DIR/Scripts/activate"
else
    # POSIX virtualenv layout
    echo "Activating POSIX virtualenv" >&2
    source "$VENV_DIR/bin/activate"
fi
echo "Virtual environment activated" >&2
echo "Installing Python build dependencies" >&2
$VENV_DIR/Scripts/python.exe  -m pip install --upgrade pip build wheel >/dev/null

# ----------------------------------------------------------------------
# Ensure Rust
echo "Checking for Rust toolchain" >&2
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
        echo "Copying $SRC_LIB to $DEST_LIB" >&2
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
echo "Built CLI binary at $CLI_BIN" >&2

# Build wheel
export AMI_CLI_BIN="$CLI_BIN"
cd "$ROOT_DIR"
echo "Building wheel" >&2
python -m build --wheel

echo "Wheel built in $ROOT_DIR/dist" >&2

