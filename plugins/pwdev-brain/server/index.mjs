#!/usr/bin/env node
// index.mjs — servidor MCP stdio do pwdev-brain (somente leitura, zero
// dependências). JSON-RPC 2.0 newline-delimited: initialize →
// notifications/initialized → tools/list / tools/call / ping.
// Debug apenas em stderr; stdout é exclusivo do protocolo.

import { createInterface } from 'node:readline';
import { TOOLS, ToolError, SERVER_VERSION } from './tools.mjs';

const DEFAULT_PROTOCOL = '2025-06-18';

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + '\n');
}

function reply(id, result) {
  send({ jsonrpc: '2.0', id, result });
}

function replyError(id, code, message) {
  send({ jsonrpc: '2.0', id, error: { code, message } });
}

function handleRequest(req) {
  const { id, method, params } = req;
  const isNotification = id === undefined || id === null;

  switch (method) {
    case 'initialize':
      reply(id, {
        protocolVersion: (params && params.protocolVersion) || DEFAULT_PROTOCOL,
        capabilities: { tools: {} },
        serverInfo: { name: 'pwdev-brain', version: SERVER_VERSION },
      });
      return;

    case 'ping':
      reply(id, {});
      return;

    case 'tools/list':
      reply(id, {
        tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })),
      });
      return;

    case 'tools/call': {
      const name = params && params.name;
      const args = (params && params.arguments) || {};
      const tool = TOOLS.find((t) => t.name === name);
      if (!tool) {
        replyError(id, -32602, `Tool desconhecida: ${name}`);
        return;
      }
      try {
        const result = tool.handler(args);
        reply(id, { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] });
      } catch (err) {
        const message = err instanceof ToolError ? err.message : `Erro interno: ${err.message}`;
        if (!(err instanceof ToolError)) console.error('[pwdev-brain]', err);
        reply(id, { content: [{ type: 'text', text: message }], isError: true });
      }
      return;
    }

    default:
      if (method && method.startsWith('notifications/')) return; // ignorar
      if (!isNotification) replyError(id, -32601, `Método não suportado: ${method}`);
  }
}

const rl = createInterface({ input: process.stdin, terminal: false });

rl.on('line', (line) => {
  const trimmed = line.trim();
  if (trimmed === '') return;
  let req;
  try {
    req = JSON.parse(trimmed);
  } catch {
    replyError(null, -32700, 'Parse error');
    return;
  }
  try {
    handleRequest(req);
  } catch (err) {
    console.error('[pwdev-brain]', err);
    if (req && req.id !== undefined && req.id !== null) {
      replyError(req.id, -32603, `Erro interno: ${err.message}`);
    }
  }
});

rl.on('close', () => process.exit(0));
