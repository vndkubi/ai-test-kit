#!/usr/bin/env python3
"""
04_sql_inventory.py — Static mining of ALL SQL in the codebase.

Covers 3 patterns (works for mixed codebases):
  1. Plain JDBC : string literals / concatenation in .java
  2. JPA        : @NamedQuery / @NamedNativeQuery / createQuery("...")
  3. MyBatis    : XML mapper <select|insert|update|delete>

Usage:
  python3 04_sql_inventory.py [SRC_DIR ...]        # default: src/main
  OUT_DIR=docs/scan python3 04_sql_inventory.py server/src/main bff/src/main

Output:
  docs/scan/SQL_INVENTORY.md      — human-readable, SQL VERBATIM
  docs/scan/sql_inventory.json    — machine-readable (input for 06_heatmap.py)

Key guardrail: SQL is extracted VERBATIM (concat markers preserved),
NEVER normalized — a column renamed during paraphrase corrupts the data contract.
Dynamic SQL (string concat with variables / StringBuilder) is flagged [DYNAMIC-SQL];
we do NOT guess the final SQL — the investigator must read the branching code.
"""
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

SQL_START = re.compile(r'^\s*(SELECT|INSERT|UPDATE|DELETE|MERGE|WITH|CALL)\b', re.I)
STRING_LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')

# ---------------------------------------------------------------- table extraction
def extract_tables(sql: str):
    """Return (tables_read, tables_written) — heuristic; skips aliases/subqueries."""
    s = re.sub(r'\s+', ' ', sql)
    read, written = set(), set()
    ident = r'([A-Za-z_][A-Za-z0-9_$.]*)'
    kind = (re.match(r'\s*(\w+)', s) or [None, ''])[1].upper()

    for m in re.finditer(r'\bFROM\s+' + ident, s, re.I):
        (written if kind == 'DELETE' else read).add(m.group(1).lower())
    for m in re.finditer(r'\bJOIN\s+(?:FETCH\s+)?' + ident, s, re.I):
        read.add(m.group(1).lower())
    for m in re.finditer(r'\bINTO\s+' + ident, s, re.I):
        written.add(m.group(1).lower())
    for m in re.finditer(r'\bUPDATE\s+' + ident, s, re.I):
        written.add(m.group(1).lower())
    for m in re.finditer(r'\bMERGE\s+INTO\s+' + ident, s, re.I):
        written.add(m.group(1).lower())
    keywords = {'select', 'dual', 'values', 'fetch'}

    def plausible(t):
        # Drop JPQL path expressions like c.note / nb.subscriptions (alias prefix ≤2 chars);
        # keep schema-qualified tables like dbo.customer.
        head = t.split('.')[0]
        return '.' not in t or len(head) > 2

    read = {t for t in read if plausible(t)}
    written = {t for t in written if plausible(t)}
    return sorted(read - keywords - written), sorted(written - keywords)


# ---------------------------------------------------------------- java mining
def mine_java(path: Path):
    """Find SQL in string literals; join literals concatenated with '+';
    flag dynamic when variables/method calls sit between literals or inside .append()."""
    entries = []
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return entries
    lines = text.splitlines()

    # Walk "statement blocks": join consecutive literals connected by + (across newlines)
    lits = [(m.start(), m.group(1)) for m in STRING_LIT.finditer(text)]
    used = set()
    for i, (pos, lit) in enumerate(lits):
        if i in used or not SQL_START.match(lit):
            continue
        sql_parts, dynamic = [lit], False
        j = i
        while j + 1 < len(lits):
            between = text[lits[j][0] + len(lits[j][1]) + 2: lits[j + 1][0]]
            if re.fullmatch(r'\s*\+\s*', between):            # "..." + "..."
                sql_parts.append(lits[j + 1][1]); used.add(j + 1); j += 1
            elif re.fullmatch(r'\s*\+\s*[\w.()\[\]]+\s*\+\s*', between):  # "..." + var + "..."
                dynamic = True
                sql_parts.append(' /*+DYNAMIC-PART+*/ ' + lits[j + 1][1]); used.add(j + 1); j += 1
            else:
                break
        line_no = text[:pos].count('\n') + 1
        ctx = lines[line_no - 1].strip() if line_no <= len(lines) else ''
        before = text[max(0, pos - 120):pos]
        if '.append(' in before or 'StringBuilder' in before:
            dynamic = True
        # classify the source
        source = 'jdbc'
        if re.search(r'@Named(Native)?Query', before):
            source = 'jpa-named-query'
        elif re.search(r'@Query', before):
            source = 'spring-data-query'
        elif re.search(r'create(Native)?Query\s*\(\s*$', before.rstrip('" ')):
            source = 'jpa-createquery'
        sql = ' '.join(sql_parts)
        # Plausibility filter: a real statement needs a second SQL keyword.
        # Kills false positives like "Delete book" or "Update notebook index content"
        # (doc strings / swagger @Operation summaries starting with a SQL verb).
        if not re.search(r'\b(FROM|INTO|SET|VALUES|JOIN|WHERE)\b', sql, re.I):
            continue
        tr, tw = extract_tables(sql)
        entries.append(dict(file=str(path), line=line_no, source=source,
                            context=ctx[:160], sql=sql, dynamic=dynamic,
                            tables_read=tr, tables_written=tw))
    return entries


# ---------------------------------------------------------------- mybatis mining
MYBATIS_STMT = re.compile(
    r'<(select|insert|update|delete)\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</\1>',
    re.I | re.S)

def mine_mybatis(path: Path):
    entries = []
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return entries
    if '<mapper' not in text:
        return entries
    ns = (re.search(r'<mapper[^>]*namespace="([^"]+)"', text) or [None, '?'])[1]
    for m in MYBATIS_STMT.finditer(text):
        kind, stmt_id, body = m.group(1), m.group(2), m.group(3)
        line_no = text[:m.start()].count('\n') + 1
        dynamic = bool(re.search(r'<(if|choose|foreach|where|set|trim)\b|\$\{', body))
        sql = re.sub(r'<[^>]+>', ' ', body)  # strip tags for table extraction; verbatim keeps raw body
        tr, tw = extract_tables(sql)
        entries.append(dict(file=str(path), line=line_no, source='mybatis',
                            context=f'{ns}.{stmt_id}', sql=body.strip(),
                            dynamic=dynamic, tables_read=tr, tables_written=tw))
    return entries


# ---------------------------------------------------------------- main
def main():
    src_dirs = [Path(p) for p in (sys.argv[1:] or ['src/main'])]
    out_dir = Path(os.environ.get('OUT_DIR', 'docs/scan'))
    out_dir.mkdir(parents=True, exist_ok=True)
    max_md = int(os.environ.get('MAX_MD_SQL', '2000'))

    entries = []
    for src in src_dirs:
        for p in sorted(src.rglob('*.java')):
            entries += mine_java(p)
        for p in sorted(src.rglob('*.xml')):
            entries += mine_mybatis(p)

    (out_dir / 'sql_inventory.json').write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding='utf-8')

    n_dyn = sum(1 for e in entries if e['dynamic'])
    md = [f'# SQL INVENTORY (generated {date.today()})', '',
          f'> {len(entries)} SQL statements, of which **{n_dyn} dynamic** '
          f'([DYNAMIC-SQL] = read the branching code, do NOT guess the final SQL).', '',
          '> Given (SELECTed tables) = data to seed. Then (INSERT/UPDATE/DELETE tables) = assertions.', '']
    by_file = {}
    for e in entries:
        by_file.setdefault(e['file'], []).append(e)
    for f, es in sorted(by_file.items()):
        md.append(f'## `{f}`')
        md.append('')
        for e in es:
            tag = ' **[DYNAMIC-SQL]**' if e['dynamic'] else ''
            md.append(f'### line {e["line"]} — {e["source"]}{tag}')
            md.append(f'- context: `{e["context"]}`')
            md.append(f'- read: {", ".join(e["tables_read"]) or "—"} | '
                      f'write: {", ".join(e["tables_written"]) or "—"}')
            md.append('')
            md.append('```sql')
            md.append(e['sql'][:max_md] + ('\n-- ...(truncated)' if len(e['sql']) > max_md else ''))
            md.append('```')
            md.append('')
    (out_dir / 'SQL_INVENTORY.md').write_text('\n'.join(md), encoding='utf-8')
    print(f'OK: {out_dir}/SQL_INVENTORY.md + sql_inventory.json '
          f'({len(entries)} statements, {n_dyn} dynamic)')


if __name__ == '__main__':
    main()
