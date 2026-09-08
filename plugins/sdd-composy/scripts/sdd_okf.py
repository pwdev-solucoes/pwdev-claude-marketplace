#!/usr/bin/env python3
"""Small dependency-free OKF v0.2 validator for SDD project bundles."""
from __future__ import annotations
import argparse, datetime as dt, json, re, ast
from pathlib import Path

_LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")

def parse_frontmatter(text):
    if not text.startswith('---\n') and not text.startswith('---\r\n'):
        return None, text
    m = re.match(r'^---\r?\n([\s\S]*?)\r?\n---\r?\n?', text)
    if not m: return None, text
    raw = m.group(1); lines = raw.splitlines()
    def scalar(v):
        v=v.strip()
        if not v: return None
        if v.startswith(('|','>')): raise ValueError('unsupported block scalar')
        if v[0:1] in ('"', "'"):
            try: return json.loads(v) if v[0]=='"' else v[1:-1].replace("''", "'")
            except Exception as e: raise ValueError('invalid quoted scalar') from e
        if v.startswith('[') or v.startswith('{'):
            converted=[]; quote=None; i=0
            while i < len(v):
                ch=v[i]
                if ch in "'\"":
                    if quote is None: quote=ch
                    elif quote == ch and (i == 0 or v[i-1] != '\\'): quote=None
                    converted.append(ch); i += 1; continue
                if quote is None:
                    m=re.match(r'(true|false|null)\b', v[i:], re.I)
                    if m:
                        converted.append({'true':'True','false':'False','null':'None'}[m.group(1).lower()]); i += len(m.group(1)); continue
                converted.append(ch); i += 1
            normalized=''.join(converted)
            def quote_bare(match):
                word=match.group(1); end=normalized[match.end():]
                if word in ('True','False','None') or re.match(r'\s*:', end): return word
                return repr(word)
            parts=[]; start=0; quote=None; i=0
            while i < len(normalized):
                if normalized[i] in "'\"":
                    q=normalized[i]
                    if quote is None: quote=q
                    elif quote == q and (i == 0 or normalized[i-1] != '\\'): quote=None
                if quote is None and (i == 0 or normalized[i-1] in ',[{ '):
                    m=re.match(r'[A-Za-z_][\w.-]*', normalized[i:])
                    if m:
                        parts.append(normalized[start:i]); parts.append(quote_bare(re.match(r'([A-Za-z_][\w.-]*)', m.group(0)))); i += len(m.group(0)); start=i; continue
                i += 1
            normalized=''.join(parts)+normalized[start:]
            try: return ast.literal_eval(normalized)
            except Exception as e: raise ValueError('invalid inline value') from e
        if v.lower() in ('true','false'): return v.lower()=='true'
        if v.lower() in ('null','~'): return None
        return v
    def split_key(s):
        quote=None
        for i,ch in enumerate(s):
            if ch in "'\"": quote = None if quote==ch else (ch if quote is None else quote)
            elif ch==':' and quote is None: return s[:i].strip(), s[i+1:].strip()
        return None,None
    def block(pos, indent):
        container = [] if lines[pos].lstrip().startswith('- ') else {}
        while pos < len(lines):
            line=lines[pos];
            if not line.strip() or line.lstrip().startswith('#'): pos+=1; continue
            n=len(line)-len(line.lstrip())
            if n<indent: break
            if n>indent: raise ValueError('invalid indentation')
            s=line.strip()
            if isinstance(container,list):
                if not s.startswith('- '): break
                rest=s[2:].strip(); pos+=1
                if not rest: item,pos=block(pos, indent+2)
                else:
                    k,v=split_key(rest)
                    if k is None: item=scalar(rest)
                    else:
                        item={k: scalar(v) if v else None}
                        if not v and pos<len(lines) and len(lines[pos])-len(lines[pos].lstrip())>indent: item[k],pos=block(pos,indent+2)
                        if pos<len(lines) and len(lines[pos])-len(lines[pos].lstrip())>indent:
                            more,pos=block(pos,indent+2); item.update(more)
                container.append(item)
            else:
                k,v=split_key(s)
                if k is None or not k: raise ValueError(f'unsupported frontmatter line: {s}')
                pos+=1
                if v in ('|','>'):
                    raise ValueError('unsupported block scalar')
                elif v: container[k]=scalar(v)
                elif pos<len(lines) and (lines[pos].strip() and len(lines[pos])-len(lines[pos].lstrip())>indent): container[k],pos=block(pos,len(lines[pos])-len(lines[pos].lstrip()))
                else: container[k]={}
        return container,pos
    if not lines: return {}, text[m.end():]
    out,_=block(0,len(lines[0])-len(lines[0].lstrip()))
    return out, text[m.end():]

def validate_frontmatter(meta, actor=None, require_generated=False):
    errors=[]
    if not isinstance(meta, dict): return ['missing or unparsable frontmatter']
    if not isinstance(meta.get('type'), str) or not meta['type'].strip(): errors.append('required type')
    for section in ('generated','verified'):
        value=meta.get(section)
        if section=='generated' and require_generated and not isinstance(value,dict): errors.append('generated required')
        if isinstance(value,dict): values=[value]
        elif isinstance(value,list): values=value
        elif value is None: values=[]
        else: errors.append(f'{section} must be mapping or list'); values=[]
        for item in values:
            if not isinstance(item,dict): errors.append(f'{section} entry must be mapping'); continue
            if 'by' in item and (not isinstance(item['by'],str) or not item['by'].strip()): errors.append(f'{section}.by invalid')
            if 'at' in item and (not isinstance(item['at'],str) or not _ISO.match(item['at'])): errors.append(f'{section}.at must be ISO timestamp')
            if actor and item.get('by') and item['by'] != actor: errors.append(f'{section} actor mismatch: {item["by"]}')
    if isinstance(meta.get('sources'),list):
        for i, src in enumerate(meta['sources']):
            if not isinstance(src,dict) or not isinstance(src.get('resource'),str) or not src['resource'].strip(): errors.append(f'sources[{i}].resource required')
    elif 'sources' in meta: errors.append('sources must be a list')
    return errors

def lint(root, actor=None):
    root=Path(root); errors=[]; warnings=[]
    for path in sorted(root.rglob('*.md')):
        rel=path.relative_to(root).as_posix()
        if rel == 'index.md':
            try: meta,body=parse_frontmatter(path.read_text(encoding='utf-8'))
            except ValueError as exc: errors.append(f'{rel}: {exc}'); meta,body=None,''
            if not meta or meta.get('okf_version') != '0.2': errors.append(f'{rel}: reserved index requires okf_version 0.2')
            errors += [f'{rel}: {e}' for e in validate_frontmatter(meta, actor)]
            docs=body
        elif rel == 'log.md':
            continue
        else:
            try: meta,body=parse_frontmatter(path.read_text(encoding='utf-8'))
            except ValueError as exc: errors.append(f'{rel}: {exc}'); meta,body=None,''
            errors += [f'{rel}: {e}' for e in validate_frontmatter(meta, actor)]
            docs=body
        for target in _LINK.findall(docs):
            target=target.split('#',1)[0].strip('<>')
            if target and not target.startswith(('#','/','mailto:')) and '://' not in target and not (path.parent/target).resolve().exists(): warnings.append(f'{rel}: broken link {target}')
    return {'ok': not errors, 'errors': errors, 'warnings': warnings}

def generate_index(root):
    root=Path(root); entries=[]
    for path in sorted(root.rglob('*.md')):
        if path.name in ('index.md','log.md') or 'output' in path.relative_to(root).parts: continue
        try: meta,_=parse_frontmatter(path.read_text(encoding='utf-8'))
        except ValueError as exc: raise ValueError(f'{path.name}: {exc}') from exc
        title=str((meta or {}).get('title', path.stem)).replace('[','\\[').replace(']','\\]')
        desc=str((meta or {}).get('description','')).replace('\n',' ').replace('\r',' ')
        entries.append(f'- [{title}]({path.relative_to(root).as_posix()})' + (f' - {desc}' if desc else ''))
    return '---\ntype: Index\nokf_version: "0.2"\n---\n\n# Project documents\n\n'+'\n'.join(entries)+'\n'

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    for cmd in ('lint','index'):
        q=sub.add_parser(cmd); q.add_argument('root'); q.add_argument('--actor')
    a=p.parse_args()
    if a.cmd=='lint':
        result=lint(a.root,a.actor); print(json.dumps(result,ensure_ascii=False)); raise SystemExit(0 if result['ok'] else 1)
    try: print(generate_index(a.root),end='')
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False)); raise SystemExit(2)
if __name__=='__main__': main()
