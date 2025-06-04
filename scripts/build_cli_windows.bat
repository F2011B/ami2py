@echo off
setlocal
REM Build ami_cli.exe in release mode
cd /d "%~dp0.."
if not exist ami_cli\Cargo.toml (
    echo ami_cli project not found.
    exit /b 1
)
cargo build --manifest-path ami_cli\Cargo.toml --release
if exist ami_cli\target\release\ami_cli.exe (
    echo Built ami_cli.exe at ami_cli\target\release\ami_cli.exe
) else (
    echo Failed to build ami_cli.exe
    exit /b 1
)
endlocal
