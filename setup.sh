#!/usr/bin/env bash
# One-time setup on macOS. Safe to re-run.
#   ./setup.sh            core tools + Python env + `explainer` command
#   ./setup.sh --latex    also install LaTeX (~5 GB, asks for your password)
set -euo pipefail
cd "$(dirname "$0")"

command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
echo "› system packages"
brew install ffmpeg cairo pango pkg-config uv >/dev/null

echo "› python environment (.venv, Python 3.12)"
[ -d .venv ] || uv venv --python 3.12 .venv
uv pip install --python .venv -e . >/dev/null
# pydub (a manim dependency) prints SyntaxWarnings until its bytecode is cached
.venv/bin/python -W ignore -m compileall -q .venv/lib/python3.*/site-packages/pydub || true

if [[ "${1:-}" == "--latex" ]]; then
  echo "› LaTeX (MacTeX, no GUI apps)"
  brew install --cask mactex-no-gui
  echo "  open a new terminal afterwards so 'latex' is on PATH"
fi

[ -f .env ] || { cp .env.example .env; chmod 600 .env; echo "› created .env: paste your API keys into it"; }

echo
.venv/bin/explainer doctor || true
echo
echo "Activate with:  source .venv/bin/activate     then try:  explainer build birthday_paradox"
