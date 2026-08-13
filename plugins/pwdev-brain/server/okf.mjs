// okf.mjs — leitura do bundle OKF: frontmatter (subset YAML), walk da wiki,
// parse do log. Zero dependências. Nunca lança em conteúdo malformado: o que
// não couber no subset vira string bruta com a flag `partial`.

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

// --- Subset YAML -----------------------------------------------------------
// Cobre o frontmatter OKF: escalares (com/sem aspas), arrays inline [a, b],
// listas em bloco (- item | - chave: valor com continuação), 1 nível de mapa
// aninhado (generated:, usage_window:). Fora disso: string bruta + partial.

function parseScalar(raw) {
  const s = raw.trim();
  if (s === '') return '';
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    return s.slice(1, -1);
  }
  if (s === 'true') return true;
  if (s === 'false') return false;
  if (s === 'null' || s === '~') return null;
  if (/^-?\d+$/.test(s)) return parseInt(s, 10);
  if (/^-?\d+\.\d+$/.test(s)) return parseFloat(s);
  return s;
}

function parseInlineArray(raw) {
  const inner = raw.trim().slice(1, -1).trim();
  if (inner === '') return [];
  return inner.split(',').map((x) => parseScalar(x));
}

function indentOf(line) {
  return line.length - line.trimStart().length;
}

// Parseia um bloco de linhas com a mesma indentação base como um mapa.
// Retorna { value, partial }.
function parseBlock(lines, start, baseIndent) {
  const map = {};
  let partial = false;
  let i = start;

  while (i < lines.length) {
    const line = lines[i];
    if (line.trim() === '' || line.trim().startsWith('#')) { i++; continue; }
    const ind = indentOf(line);
    if (ind < baseIndent) break;
    if (ind > baseIndent) { partial = true; i++; continue; } // indentação inesperada

    const m = line.trim().match(/^([A-Za-z0-9_.-]+):(.*)$/);
    if (!m) { partial = true; i++; continue; }
    const key = m[1];
    const rest = m[2].trim();

    if (rest !== '') {
      if (rest.startsWith('[') && rest.endsWith(']')) {
        map[key] = parseInlineArray(rest);
      } else if (rest.startsWith('>') || rest.startsWith('|')) {
        // bloco escalar multi-linha: junta as linhas mais indentadas
        const parts = [];
        i++;
        while (i < lines.length && (lines[i].trim() === '' || indentOf(lines[i]) > baseIndent)) {
          parts.push(lines[i].trim());
          i++;
        }
        map[key] = parts.join(' ').trim();
        continue;
      } else {
        map[key] = parseScalar(rest);
      }
      i++;
      continue;
    }

    // valor vazio: lista em bloco ou mapa aninhado nas próximas linhas
    let j = i + 1;
    while (j < lines.length && lines[j].trim() === '') j++;
    if (j >= lines.length || indentOf(lines[j]) <= baseIndent) {
      map[key] = null;
      i++;
      continue;
    }
    const childIndent = indentOf(lines[j]);
    if (lines[j].trim().startsWith('- ') || lines[j].trim() === '-') {
      const { items, next, partial: p } = parseListItems(lines, j, childIndent);
      map[key] = items;
      partial = partial || p;
      i = next;
    } else {
      const child = parseBlock(lines, j, childIndent);
      map[key] = child.value;
      partial = partial || child.partial;
      i = child.next;
    }
  }

  return { value: map, partial, next: i };
}

function parseListItems(lines, start, baseIndent) {
  const items = [];
  let partial = false;
  let i = start;

  while (i < lines.length) {
    const line = lines[i];
    if (line.trim() === '' || line.trim().startsWith('#')) { i++; continue; }
    const ind = indentOf(line);
    if (ind < baseIndent) break;
    if (ind > baseIndent || !line.trim().startsWith('-')) { partial = true; i++; continue; }

    const rest = line.trim().replace(/^-\s*/, '');
    const m = rest.match(/^([A-Za-z0-9_.-]+):(.*)$/);
    if (m) {
      // item-mapa: "- id: x" com chaves de continuação mais indentadas
      const item = {};
      if (m[2].trim() !== '') item[m[1]] = parseScalar(m[2]);
      else item[m[1]] = null;
      let j = i + 1;
      while (j < lines.length) {
        const l = lines[j];
        if (l.trim() === '') { j++; continue; }
        const ind2 = indentOf(l);
        if (ind2 <= baseIndent) break;
        const mm = l.trim().match(/^([A-Za-z0-9_.-]+):(.*)$/);
        if (!mm) { partial = true; j++; continue; }
        const v = mm[2].trim();
        item[mm[1]] = v.startsWith('[') && v.endsWith(']') ? parseInlineArray(v) : parseScalar(v);
        j++;
      }
      items.push(item);
      i = j;
    } else {
      items.push(parseScalar(rest));
      i++;
    }
  }

  return { items, partial, next: i };
}

export function parseFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { frontmatter: null, partial: false, body: text };
  const body = text.slice(m[0].length);
  try {
    const lines = m[1].split(/\r?\n/);
    const { value, partial } = parseBlock(lines, 0, 0);
    return { frontmatter: value, partial, body };
  } catch {
    return { frontmatter: null, partial: true, body };
  }
}

// --- Walk da wiki ----------------------------------------------------------
// Retorna paths relativos ao brain (wiki/...), excluindo os reservados
// index.md e log.md da raiz da wiki e todo o conteúdo de wiki/output/.

export function walkConcepts(brainPath) {
  const out = [];
  const wikiRoot = join(brainPath, 'wiki');
  const walk = (dir, rel) => {
    let entries;
    try { entries = readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.name.startsWith('.')) continue;
      const abs = join(dir, e.name);
      const relPath = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) {
        if (relPath === 'output') continue;
        walk(abs, relPath);
      } else if (e.name.endsWith('.md')) {
        if (rel === '' && (e.name === 'index.md' || e.name === 'log.md')) continue;
        out.push(`wiki/${relPath}`);
      }
    }
  };
  walk(wikiRoot, '');
  return out.sort();
}

export function readConcept(brainPath, relPath) {
  const text = readFileSync(join(brainPath, relPath), 'utf8');
  return { ...parseFrontmatter(text), raw: text };
}

// --- Log -------------------------------------------------------------------
// wiki/log.md agrupado por "## YYYY-MM-DD" em ordem desc; cada bullet é uma
// entrada.

export function parseLog(text, limit) {
  const entries = [];
  let date = null;
  for (const line of text.split(/\r?\n/)) {
    const h = line.match(/^##\s+(\d{4}-\d{2}-\d{2})\s*$/);
    if (h) { date = h[1]; continue; }
    const b = line.match(/^-\s+(.*)$/);
    if (b && date) entries.push({ date, text: b[1] });
  }
  return { entries: entries.slice(0, limit), total: entries.length };
}

// --- Utilidades ------------------------------------------------------------

export function countByStatus(concepts, brainPath) {
  const by = { draft: 0, stable: 0, deprecated: 0 };
  for (const p of concepts) {
    try {
      const { frontmatter } = readConcept(brainPath, p);
      const s = frontmatter && typeof frontmatter.status === 'string' ? frontmatter.status : 'stable';
      if (s in by) by[s] += 1; else by.stable += 1;
    } catch {
      by.stable += 1;
    }
  }
  return by;
}

export function isDir(p) {
  try { return statSync(p).isDirectory(); } catch { return false; }
}
