"""Пересчитывает сводную таблицу из оценок и сверяет её с summary.md.

Из scores/*.md берётся оценка каждого пункта в каждом прогоне. Прогоны группируются
по имени файла без номера (A1, A2, A3 -> группа A одной модели). Для каждой группы
считаются «спросила / решила молча / пропустила» по пунктам и итог, а также строгий итог:
«спросила» без примечаний «слабо», «косвенно», «частично». Код выхода 1 при расхождении.
"""
import os
import re
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
GRADES = ['спросила', 'решила молча', 'пропустила']
WEAK = ('слабо', 'косвенно', 'частично')


def load_scores():
    counts = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    strict = defaultdict(int)
    for name in sorted(os.listdir(os.path.join(BASE, 'scores'))):
        group = None
        for row in open(os.path.join(BASE, 'scores', name), encoding='utf-8').read().splitlines():
            m = re.match(r'## ([a-z]+)_([AB])\d\.(?:txt|md)', row)
            if m:
                group = (m.group(1), m.group(2))
                continue
            if row.startswith('## '):
                group = None
            cells = [c.strip() for c in row.strip().strip('|').split('|')]
            if not group or len(cells) < 5 or not cells[0].isdigit():
                continue
            item, grade, note = int(cells[0]), cells[2], cells[4]
            counts[group][item][GRADES.index(grade)] += 1
            if grade == GRADES[0] and not note.lower().startswith(WEAK):
                strict[group] += 1
    return counts, strict


def load_summary():
    header, rows = None, {}
    for row in open(os.path.join(BASE, 'summary.md'), encoding='utf-8').read().splitlines():
        cells = [c.strip() for c in row.strip().strip('|').split('|')]
        if cells[:2] == ['№', 'пункт']:
            header = cells[2:]
        elif header and len(cells) == len(header) + 2:
            key = cells[0] if cells[0].isdigit() else cells[1]
            rows[key] = cells[2:]
    return header, rows


def column_of(group, header):
    model, prompt = group
    for i, title in enumerate(header):
        t = title.lower()
        if model in t and t.endswith(' ' + prompt.lower()):
            return i
    raise SystemExit(f'нет колонки для {model} {prompt}')


def main():
    counts, strict = load_scores()
    header, rows = load_summary()
    bad = 0

    def compare(label, key, col, expected):
        nonlocal bad
        actual = rows[key][col]
        ok = actual == expected or actual.startswith(expected + ' ')
        if not ok:
            bad += 1
            print(f'РАСХОЖДЕНИЕ {label}, строка «{key}»: в summary.md {actual}, по оценкам {expected}')

    for group in sorted(counts):
        col = column_of(group, header)
        label = header[col]
        total = [0, 0, 0]
        for item in range(1, 15):
            c = counts[group][item]
            total = [a + b for a, b in zip(total, c)]
            compare(label, str(item), col, ' / '.join(map(str, c)))
        compare(label, 'итого из 42', col, ' / '.join(map(str, total)))
        strict_key = next(k for k in rows if k.startswith('«спросила» строго'))
        compare(label, strict_key, col, str(strict[group]))
        print(f'{label}: итого {" / ".join(map(str, total))}, строго {strict[group]}')

    print('сводка совпадает с оценками' if not bad else f'расхождений: {bad}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
