#!/usr/bin/env bash
# Обе проверки эксперимента: цитаты в оценках и сводная таблица.
set -euo pipefail
cd "$(dirname "$0")"

python3 verify_quotes.py
echo
python3 check_summary.py
