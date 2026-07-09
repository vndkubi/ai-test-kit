#!/usr/bin/env python3
"""
06_heatmap.py — Join the 3 scan outputs into the Entity × Flow matrix (the decisive artifact).

  entrypoint class --(jdeps reachable set)--> DAO class --(sql_inventory)--> tables

Input (from docs/scan/):
  ENTRYPOINTS.md       (01_entrypoints.sh)
  deps.txt             (03_deps.sh)         — if missing, degrade: only SQL in the entrypoint class itself
  sql_inventory.json   (04_sql_inventory.py)

Output:
  docs/scan/HEATMAP.md
    - Table 1: which tables each flow touches (read/write) — many written tables = complex/risky flow
    - Table 2: table centrality — tables touched by the most flows = core entities
      → highest fixture priority (build once, reuse forever)

Usage: python3 06_heatmap.py   (env OUT_DIR=docs/scan)
"""
import json
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

OUT_DIR = Path(os.environ.get('OUT_DIR', 'docs/scan'))

def path_to_fqcn(p: str):
    """src/main/java/com/x/Y.java -> com.x.Y (heuristic per Maven convention).
    Greedy prefix so the LAST /java/ (or /src/) segment wins — otherwise
    backend/src/main/java/... would yield main.java.com... and break the join."""
    p = p.replace('\\', '/')
    m = re.match(r'.*/(?:java|src)/((?:[a-z_][\w]*/)+[A-Z]\w*)\.java$', p)
    return m.group(1).replace('/', '.') if m else None

def main():
    # ---- entrypoints: group by class, keep a label (@Path value / annotation)
    ep_file = OUT_DIR / 'ENTRYPOINTS.md'
    if not ep_file.exists():
        raise SystemExit('Missing ENTRYPOINTS.md — run 01_entrypoints.sh first')
    flows = {}  # fqcn -> label
    for line in ep_file.read_text(encoding='utf-8', errors='replace').splitlines():
        m = re.match(r'([^\s:]+\.java):(\d+):(.*)', line.strip())
        if not m:
            continue
        fqcn = path_to_fqcn(m.group(1))
        if not fqcn:
            continue
        label = flows.get(fqcn, '')
        pm = re.search(r'@(?:Path|RequestMapping|GetMapping|PostMapping|PutMapping|'
                       r'DeleteMapping|PatchMapping)\(\s*(?:value\s*=\s*)?"([^"]+)"', m.group(3))
        if pm and pm.group(1) not in label:
            label = (label + ' ' + pm.group(1)).strip()
        flows[fqcn] = label

    # ---- dependency edges
    edges = defaultdict(set)
    deps_file = OUT_DIR / 'deps.txt'
    if deps_file.exists():
        for line in deps_file.read_text(encoding='utf-8', errors='replace').splitlines():
            m = re.match(r'\s*([\w.$]+)\s*->\s*([\w.$]+)', line)
            if m:
                a, b = m.group(1).split('$')[0], m.group(2).split('$')[0]
                if a != b:
                    edges[a].add(b)
    else:
        print('WARN: deps.txt missing — heatmap degrades: only SQL inside entrypoint classes themselves')

    # ---- sql inventory: fqcn -> (read, write)
    inv_file = OUT_DIR / 'sql_inventory.json'
    if not inv_file.exists():
        raise SystemExit('Missing sql_inventory.json — run 04_sql_inventory.py first')
    sql_by_class, unmapped = defaultdict(lambda: (set(), set())), []
    for e in json.loads(inv_file.read_text(encoding='utf-8')):
        fq = path_to_fqcn(e['file'])
        if fq:
            r, w = sql_by_class[fq]
            r.update(e['tables_read']); w.update(e['tables_written'])
        else:
            unmapped.append(e)  # MyBatis XML etc. — listed separately

    # ---- BFS reachability per flow
    def reach(start):
        seen, stack = {start}, [start]
        while stack:
            for nxt in edges.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt); stack.append(nxt)
        return seen

    flow_tables = {}
    for f in flows:
        r_all, w_all = set(), set()
        for c in reach(f):
            r, w = sql_by_class.get(c, (set(), set()))
            r_all |= r; w_all |= w
        flow_tables[f] = (r_all, w_all)

    table_flows = defaultdict(set)
    for f, (r, w) in flow_tables.items():
        for t in r | w:
            table_flows[t].add(f)

    # ---- render
    md = [f'# HEATMAP — Entity × Flow (generated {date.today()})', '',
          '> Table 2 decides fixture build order: tables touched by many flows = core entities.', '',
          '## 1. Flow → tables',
          '',
          '| Flow (entrypoint class) | Label | Read | Write |',
          '|---|---|---|---|']
    for f in sorted(flows, key=lambda x: -len(flow_tables[x][1])):
        r, w = flow_tables[f]
        md.append(f'| `{f}` | {flows[f] or "—"} | {", ".join(sorted(r)) or "—"} '
                  f'| **{", ".join(sorted(w)) or "—"}** |')
    md += ['', '## 2. Table centrality (fixture priority)', '',
           '| Table | #Flows | Flows |', '|---|---|---|']
    for t in sorted(table_flows, key=lambda x: -len(table_flows[x])):
        fs = sorted(table_flows[t])
        shown = ', '.join(f'`{x.rsplit(".", 1)[-1]}`' for x in fs[:6])
        more = f' +{len(fs)-6}' if len(fs) > 6 else ''
        md.append(f'| **{t}** | {len(fs)} | {shown}{more} |')
    if unmapped:
        md += ['', '## 3. SQL not mappable to a class (MyBatis XML, etc.)', '',
               '| File | Context | Read | Write |', '|---|---|---|---|']
        for e in unmapped:
            md.append(f'| `{e["file"]}` | {e["context"]} | {", ".join(e["tables_read"]) or "—"} '
                      f'| {", ".join(e["tables_written"]) or "—"} |')
    (OUT_DIR / 'HEATMAP.md').write_text('\n'.join(md), encoding='utf-8')
    print(f'OK: {OUT_DIR}/HEATMAP.md ({len(flows)} flows × {len(table_flows)} tables)')


if __name__ == '__main__':
    main()
