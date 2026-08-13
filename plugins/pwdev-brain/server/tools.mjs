// tools.mjs — as 6 tools somente-leitura do pwdev-brain e a cadeia de
// resolução do brain. Toda falha vira ToolError (mensagem instrutiva),
// nunca crash do servidor.

import { readFileSync, realpathSync, readdirSync, existsSync } from 'node:fs';
import { join, resolve, sep } from 'node:path';
import {
  parseFrontmatter, walkConcepts, readConcept, parseLog, countByStatus, isDir,
} from './okf.mjs';

export const SERVER_VERSION = '1.1.0';
const MAX_BODY_BYTES = 48 * 1024;
const TEXT_EXTENSIONS = ['.md', '.markdown', '.txt', '.csv', '.json', '.yaml', '.yml'];

export class ToolError extends Error {}

// --- Resolução do brain ----------------------------------------------------
// (1) brain_path da chamada → (2) env PWDEV_BRAIN_PATH → (3) linha
// "Brain: /caminho" em .claude/pwdev-brain-context.md (cwd, depois
// CLAUDE_PROJECT_DIR). O servidor nunca falha no boot: sem brain, a tool
// responde com instrução.

function contextBrain(dir) {
  try {
    const text = readFileSync(join(dir, '.claude', 'pwdev-brain-context.md'), 'utf8');
    const m = text.match(/^Brain:\s*(\S.*)$/m);
    return m ? m[1].trim() : null;
  } catch {
    return null;
  }
}

export function resolveBrain(args) {
  let path = null;
  let via = null;
  if (args && typeof args.brain_path === 'string' && args.brain_path.trim() !== '') {
    path = args.brain_path.trim(); via = 'param';
  } else if (process.env.PWDEV_BRAIN_PATH && process.env.PWDEV_BRAIN_PATH.trim() !== '') {
    path = process.env.PWDEV_BRAIN_PATH.trim(); via = 'env';
  } else {
    for (const dir of [process.cwd(), process.env.CLAUDE_PROJECT_DIR].filter(Boolean)) {
      const p = contextBrain(dir);
      if (p) { path = p; via = 'context'; break; }
    }
  }
  if (!path) {
    throw new ToolError(
      'Brain não configurado. Rode /pwdev-brain:init no projeto, ou defina a env var ' +
      'PWDEV_BRAIN_PATH, ou passe o parâmetro brain_path na chamada.'
    );
  }
  path = resolve(path.replace(/^~(?=\/|$)/, process.env.HOME || '~'));
  if (!isDir(path) || !existsSync(join(path, 'wiki', 'index.md'))) {
    throw new ToolError(
      `Brain inválido em ${path}: wiki/index.md não encontrado. Rode /pwdev-brain:init.`
    );
  }
  return { path, via };
}

// --- Guardas de leitura ----------------------------------------------------

function safeResolve(brainPath, relPath) {
  if (typeof relPath !== 'string' || relPath.trim() === '') {
    throw new ToolError('path é obrigatório (relativo ao brain, ex.: wiki/conceito.md).');
  }
  const clean = relPath.trim().replace(/^\/+/, '');
  if (!(clean === 'AGENTS.md' || clean.startsWith('wiki/') || clean.startsWith('raw/'))) {
    throw new ToolError('path deve apontar para wiki/, raw/ ou AGENTS.md.');
  }
  if (clean.startsWith('wiki/output/')) {
    throw new ToolError('wiki/output/ não é servido pelo MCP — artefatos ficam fora do bundle.');
  }
  const brainReal = realpathSync(brainPath);
  let targetReal;
  try {
    targetReal = realpathSync(join(brainPath, clean));
  } catch {
    throw new ToolError(`Arquivo não encontrado: ${clean}`);
  }
  if (targetReal !== brainReal && !targetReal.startsWith(brainReal + sep)) {
    throw new ToolError('path resolve para fora do brain — leitura negada.');
  }
  const ext = clean.slice(clean.lastIndexOf('.')).toLowerCase();
  if (!TEXT_EXTENSIONS.includes(ext)) {
    throw new ToolError(`Extensão não suportada (${ext}) — só arquivos de texto: ${TEXT_EXTENSIONS.join(', ')}.`);
  }
  return targetReal;
}

function truncate(text) {
  const buf = Buffer.from(text, 'utf8');
  if (buf.byteLength <= MAX_BODY_BYTES) return { text, truncated: false };
  return { text: buf.subarray(0, MAX_BODY_BYTES).toString('utf8'), truncated: true };
}

const normalize = (s) => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

// --- Tools -----------------------------------------------------------------

function toolInfo(args) {
  const { path, via } = resolveBrain(args);
  const indexText = readFileSync(join(path, 'wiki', 'index.md'), 'utf8');
  const { frontmatter } = parseFrontmatter(indexText);
  const concepts = walkConcepts(path);
  let rawFiles = 0;
  try { rawFiles = readdirSync(join(path, 'raw')).filter((f) => !f.startsWith('.')).length; } catch {}
  let outputDirs = 0;
  try {
    outputDirs = readdirSync(join(path, 'wiki', 'output'), { withFileTypes: true })
      .filter((e) => e.isDirectory()).length;
  } catch {}
  return {
    brain_path: path,
    resolved_via: via,
    okf_version: frontmatter ? frontmatter.okf_version ?? null : null,
    counts: {
      concepts: concepts.length,
      by_status: countByStatus(concepts, path),
      raw_files: rawFiles,
      output_dirs: outputDirs,
    },
    server_version: SERVER_VERSION,
    read_only: true,
  };
}

function toolIndex(args) {
  const { path } = resolveBrain(args);
  const { text, truncated } = truncate(readFileSync(join(path, 'wiki', 'index.md'), 'utf8'));
  return { path: 'wiki/index.md', content: text, truncated };
}

function conceptMeta(brainPath, relPath) {
  const { frontmatter } = readConcept(brainPath, relPath);
  const fm = frontmatter || {};
  return {
    path: relPath,
    title: typeof fm.title === 'string' ? fm.title : null,
    type: typeof fm.type === 'string' ? fm.type : null,
    status: typeof fm.status === 'string' ? fm.status : 'stable',
    tags: Array.isArray(fm.tags) ? fm.tags : [],
    description: typeof fm.description === 'string' ? fm.description : null,
    stale_after: fm.stale_after ?? null,
  };
}

function applyFilters(metas, args) {
  let out = metas;
  if (args.type) out = out.filter((c) => c.type && normalize(c.type) === normalize(args.type));
  if (args.status) out = out.filter((c) => c.status === args.status);
  if (args.tag) out = out.filter((c) => c.tags.some((t) => normalize(t) === normalize(args.tag)));
  return out;
}

function paginate(items, args, defLimit, maxLimit) {
  const limit = Math.min(Math.max(1, args.limit ?? defLimit), maxLimit);
  const offset = Math.max(0, args.offset ?? 0);
  const page = items.slice(offset, offset + limit);
  return { page, total: items.length, truncated: offset + page.length < items.length };
}

function toolList(args) {
  const { path } = resolveBrain(args);
  const metas = walkConcepts(path).map((p) => {
    try { return conceptMeta(path, p); } catch { return { path: p, title: null, type: null, status: 'stable', tags: [], description: null, stale_after: null }; }
  });
  const filtered = applyFilters(metas, args);
  const { page, total, truncated } = paginate(filtered, args, 50, 200);
  return { concepts: page, total, truncated };
}

function snippetsFor(body, terms) {
  const nBody = normalize(body);
  const found = [];
  for (const term of terms) {
    let idx = 0;
    while (found.length < 3) {
      const pos = nBody.indexOf(term, idx);
      if (pos === -1) break;
      const start = Math.max(0, pos - 80);
      const end = Math.min(body.length, pos + term.length + 120);
      found.push((start > 0 ? '…' : '') + body.slice(start, end).replace(/\s+/g, ' ').trim() + (end < body.length ? '…' : ''));
      idx = pos + term.length;
    }
    if (found.length >= 3) break;
  }
  return found;
}

function toolSearch(args) {
  if (!args.query || String(args.query).trim() === '') {
    throw new ToolError('query é obrigatória.');
  }
  const { path } = resolveBrain(args);
  const terms = normalize(args.query).split(/\s+/).filter(Boolean);
  const matches = [];
  for (const rel of walkConcepts(path)) {
    let meta;
    let body = '';
    try {
      const parsed = readConcept(path, rel);
      body = parsed.body;
      meta = conceptMeta(path, rel);
    } catch {
      continue;
    }
    const hay = {
      title: normalize(meta.title || ''),
      tags: normalize(meta.tags.join(' ')),
      description: normalize(meta.description || ''),
      body: normalize(body),
    };
    let score = 0;
    for (const t of terms) {
      if (hay.title.includes(t)) score += 10;
      if (hay.tags.includes(t)) score += 5;
      if (hay.description.includes(t)) score += 3;
      if (hay.body.includes(t)) score += 1;
    }
    if (score > 0) {
      matches.push({ ...meta, score, snippets: snippetsFor(body, terms) });
    }
  }
  const filtered = applyFilters(matches, args).sort((a, b) => b.score - a.score || a.path.localeCompare(b.path));
  const { page, total, truncated } = paginate(filtered, args, 10, 50);
  return { matches: page, total, truncated };
}

function toolGet(args) {
  const { path } = resolveBrain(args);
  const abs = safeResolve(path, args.path);
  const text = readFileSync(abs, 'utf8');
  const rel = args.path.trim().replace(/^\/+/, '');
  if (rel.endsWith('.md')) {
    const { frontmatter, partial, body } = parseFrontmatter(text);
    const t = truncate(body);
    const out = { path: rel, frontmatter, body: t.text, truncated: t.truncated };
    if (partial) out.frontmatter_partial = true;
    return out;
  }
  const t = truncate(text);
  return { path: rel, frontmatter: null, body: t.text, truncated: t.truncated };
}

function toolLog(args) {
  const { path } = resolveBrain(args);
  const limit = Math.min(Math.max(1, args.limit ?? 10), 50);
  const text = readFileSync(join(path, 'wiki', 'log.md'), 'utf8');
  return parseLog(text, limit);
}

// --- Registro --------------------------------------------------------------

const brainPathProp = {
  brain_path: {
    type: 'string',
    description: 'Caminho absoluto do brain (opcional — sobrepõe env var e contexto do projeto)',
  },
};

export const TOOLS = [
  {
    name: 'brain_info',
    description: 'Diagnóstico do segundo cérebro: caminho resolvido, versão OKF, contagens de conceitos por status, fontes em raw/ e artefatos em output/. Somente leitura.',
    inputSchema: { type: 'object', properties: { ...brainPathProp }, additionalProperties: false },
    handler: toolInfo,
  },
  {
    name: 'brain_index',
    description: 'Retorna o índice raiz da wiki (wiki/index.md) — ponto de entrada para descoberta dos conceitos.',
    inputSchema: { type: 'object', properties: { ...brainPathProp }, additionalProperties: false },
    handler: toolIndex,
  },
  {
    name: 'brain_list',
    description: 'Lista os documentos de conceito da wiki com metadados do frontmatter (title, type, status, tags, description). Filtros opcionais e paginação.',
    inputSchema: {
      type: 'object',
      properties: {
        ...brainPathProp,
        type: { type: 'string', description: 'Filtra por type do frontmatter (ex.: Concept, Entity, Synthesis)' },
        status: { type: 'string', enum: ['draft', 'stable', 'deprecated'], description: 'Filtra por status (ausente no frontmatter conta como stable)' },
        tag: { type: 'string', description: 'Filtra por tag' },
        limit: { type: 'integer', minimum: 1, maximum: 200, description: 'Máximo de itens (default 50)' },
        offset: { type: 'integer', minimum: 0, description: 'Deslocamento para paginação' },
      },
      additionalProperties: false,
    },
    handler: toolList,
  },
  {
    name: 'brain_search',
    description: 'Busca conceitos na wiki por termo (case- e acento-insensível) em título, tags, descrição e corpo; retorna matches ranqueados com snippets. Não busca em raw/ nem em wiki/output/.',
    inputSchema: {
      type: 'object',
      properties: {
        ...brainPathProp,
        query: { type: 'string', description: 'Termos de busca' },
        tag: { type: 'string', description: 'Filtra por tag' },
        status: { type: 'string', enum: ['draft', 'stable', 'deprecated'], description: 'Filtra por status' },
        limit: { type: 'integer', minimum: 1, maximum: 50, description: 'Máximo de matches (default 10)' },
        offset: { type: 'integer', minimum: 0, description: 'Deslocamento para paginação' },
      },
      required: ['query'],
      additionalProperties: false,
    },
    handler: toolSearch,
  },
  {
    name: 'brain_get',
    description: 'Lê um arquivo do brain por caminho relativo (wiki/… ou raw/…): frontmatter parseado + corpo. wiki/output/ e binários são negados. Somente leitura.',
    inputSchema: {
      type: 'object',
      properties: {
        ...brainPathProp,
        path: { type: 'string', description: 'Caminho relativo ao brain, ex.: wiki/conceitos/x.md ou raw/fonte.md' },
      },
      required: ['path'],
      additionalProperties: false,
    },
    handler: toolGet,
  },
  {
    name: 'brain_log',
    description: 'Últimas entradas do histórico da wiki (wiki/log.md), da mais recente para a mais antiga.',
    inputSchema: {
      type: 'object',
      properties: {
        ...brainPathProp,
        limit: { type: 'integer', minimum: 1, maximum: 50, description: 'Máximo de entradas (default 10)' },
      },
      additionalProperties: false,
    },
    handler: toolLog,
  },
];
