#!/bin/bash
set -euo pipefail
cd "$(dirname "${0}")"
rm -Rf test_programs/workdir
poetry run pytest -vv tests/
