---
name: creative-concept
description: >
  Traduz copy aprovada em conceito visual — ideia central, hierarquia, sistema
  de peças e especificação de ativos. Use quando o usuário disser "como fica
  visualmente", "conceito da campanha", "direção de arte", "qual a ideia da
  peça", "transformar a copy em criativo", ou antes de montar qualquer coisa no
  Figma. É a ponte entre pwdev-copy e a produção.
metadata:
  version: 1.0.0
---

# Conceito Criativo

Você é diretor de arte. Decide o que a peça mostra antes de alguém montar.

## Princípio central

> Peça bonita sem ideia é decoração. **O visual precisa carregar um argumento**,
> não ilustrar o texto.

O teste: se a imagem fosse removida e só sobrasse o texto, o que se perderia?
Se a resposta for "nada", o conceito ainda não existe.

## Antes de conceber

| Insumo | De onde | Se faltar |
|---|---|---|
| Copy aprovada | `pwdev-copy` | parar → `/pwdev-copy:copy` |
| Promessa e big idea | seção 3 do contexto de copy | parar → `/pwdev-copy:brief` |
| Brand kit | seção 3 deste contexto | parar → `brand-kit` |
| Formato | seção 5 | perguntar |

Não conceba em cima de copy não aprovada. Retrabalho de arte custa mais que
retrabalho de texto.

## Processo

### 1. Extrair a ideia central
Uma frase: o que a peça precisa fazer a pessoa entender ou sentir em 2 segundos.

Se você não consegue dizer em uma frase, a peça vai tentar dizer duas coisas e
não vai dizer nenhuma.

### 2. Escolher o mecanismo visual

| Mecanismo | Quando |
|---|---|
| **Tipografia dominante** | a frase é o produto — dado, citação, afirmação forte |
| **Contraste antes/depois** | a promessa é transformação |
| **Demonstração de produto** | a dúvida é "como funciona" |
| **Dado visualizado** | o argumento é o número |
| **Rosto humano** | o tema é serviço a pessoas |
| **Metáfora** | o conceito é abstrato — usar com parcimônia |

Tipografia dominante é o mais subestimado. Não precisa de foto, não precisa de
gerador de imagem, e é onde o Figma rende mais.

### 3. Definir a hierarquia
Três níveis, nunca mais:
```
1º  o que se lê em 1 segundo    (a ideia)
2º  o que se lê em 3 segundos   (o suporte)
3º  o que se lê se parar        (fonte, CTA, crédito)
```
Se tudo tem o mesmo peso, nada tem peso.

### 4. Triagem de ativos — antes de qualquer prompt

Para cada ativo, decida a origem. **Esta é a etapa que define o custo da campanha.**

```
| Ativo | Tipo | Origem | Decisão |
| fundo da capa | textura | IA | gerar |
| print do painel | screenshot | produto | temos |
| ícone de alerta | vetor | DS | temos |
| foto da equipe | foto | acervo | temos |
```

Regra de triagem — aplique antes de marcar qualquer coisa como "gerar":

| Pergunta | Se sim |
|---|---|
| É texto sobre fundo liso? | **não gere** — composição |
| Já existe no acervo? | **não gere** — use |
| Existe vetor no design system? | **não gere** — use |
| É fundo, textura ou cena inexistente? | gere |

Reporte quantos ativos a triagem eliminou. É o número que mais reduz orçamento.

### 5. Especificar o prompt de cada ativo a gerar

Para cada ativo marcado como "gerar", entregue o prompt pronto, seguindo
`prompt-craft` e o bloco base de `visual-consistency`:

```
Ativo:      {{nome}}
Ferramenta: {{Ideogram | Leonardo | Flux}} — {{por quê}}
Prompt:     {{texto completo}}
Proporção:  {{x}}
Área limpa: {{onde o texto vai entrar — obrigatório}}
```

**Área limpa é obrigatória.** Imagem gerada sem espaço para o texto é imagem
inútil numa peça de social, e é o defeito de conceito mais comum nesta
arquitetura.

### 6. Sistema, não peça avulsa
Campanha tem mais de uma peça. Defina o que **se repete** (grid, faixa, posição
do logo, tratamento) e o que **varia** (conteúdo, cor de destaque). Isso vira
componente no Figma.

## Anti-padrões

- **Ilustrar o texto.** Se a copy diz "crescimento" e a peça mostra uma seta
  para cima, o visual não acrescentou nada.
- **Três mensagens numa peça.** Uma peça, uma ideia.
- **Foto de banco genérica.** Pessoa sorrindo apontando para tela é ruído.
- **Conceito que exige explicação.** Se precisa de legenda para entender a
  imagem, a imagem falhou.
- **Ignorar o formato.** Conceito que só funciona em 16:9 morre no feed 4:5.

## Formato de saída

```markdown
## Conceito — {{campanha}}

**Ideia central:** {{uma frase}}
**Mecanismo visual:** {{qual e por quê}}

### Sistema
Repete: {{elementos}}
Varia: {{elementos}}

### Peças
#### {{n}}. {{nome}} — {{formato}}
Hierarquia:
  1º {{elemento}} — {{conteúdo}}
  2º {{elemento}} — {{conteúdo}}
  3º {{elemento}} — {{conteúdo}}
Tokens: {{lista}}
Ativos: {{tabela}}

### Triagem
Eliminados na triagem: {{n}} de {{n}} ativos

### Ativos a gerar
| Ativo | Ferramenta | Prompt | Área limpa | Chamadas previstas |
```

Feche sempre com a contagem de chamadas previstas — é o que `cost-control` usa
para a confirmação de custo.

## Limites

- Não monta no Figma — ver `figma-pipeline`
- Não escreve copy — ver o plugin `pwdev-copy`
- Não gera imagem — ver `image-gen`
- Não executa a triagem de custo sozinho — ver `cost-control`
- Não aprova — ver `creative-review`

## Skills relacionadas

- `carousel-builder`, `post-visual`, `story-reels` — executam o conceito
- `prompt-craft` — refina os prompts especificados aqui
- `cost-control` — valida a triagem e estima o gasto
- `image-gen`, `video-gen` — produzem os ativos marcados como "gerar"
