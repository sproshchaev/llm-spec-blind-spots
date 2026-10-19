"""Проверяет, что каждая цитата «...» в таблицах scores/*.md дословно есть в файле ответа.

Цитата должна быть подстрокой одной строки файла из runs/, указанного в заголовке раздела
«## <файл>». Код выхода 1, если хотя бы одна цитата не найдена.
"""
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def check(path):
    total = missing = 0
    lines = None
    run = None
    for row in open(path, encoding='utf-8').read().splitlines():
        m = re.match(r'## (\S+\.(?:txt|md))', row)
        if m:
            run = m.group(1)
            lines = open(os.path.join(BASE, 'runs', run), encoding='utf-8').read().splitlines()
            continue
        if row.startswith('## '):
            run = None
        if not run or not row.startswith('|') or row.startswith('|---') or row.startswith('| №'):
            continue
        for quote in re.findall(r'«([^»]+)»', row):
            total += 1
            if not any(quote in line for line in lines):
                missing += 1
                print(f'MISS {run}: {quote}')
    return total, missing


def main():
    bad = 0
    for name in sorted(os.listdir(os.path.join(BASE, 'scores'))):
        total, missing = check(os.path.join(BASE, 'scores', name))
        print(f'scores/{name}: цитат {total}, не найдено {missing}')
        bad += missing
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
