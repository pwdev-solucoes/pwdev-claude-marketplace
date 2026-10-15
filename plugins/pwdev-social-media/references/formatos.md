# Formatos, tipografia e contraste

Regras de leitura consultadas pelas skills de montagem. Dimensões e zonas seguras: `pwdev-media formatos`.

> **Aviso de validade.** Dimensões são estáveis; **zonas seguras mudam** a cada atualização de
> app. Elas ficam no catálogo de formatos do `pwdev-media`, com data de verificação.

---

## Dimensões

| Plataforma | Formato | Pixels | Proporção |
|---|---|---|---|
| **Instagram** | feed retrato | 1080 × 1350 | 4:5 |
| | feed quadrado | 1080 × 1080 | 1:1 |
| | stories / reels | 1080 × 1920 | 9:16 |
| | carrossel | 1080 × 1350 ou 1080 × 1080 | 4:5 ou 1:1 |
| **LinkedIn** | feed nativo retrato | 1080 × 1350 | 4:5 |
| | imagem de link | 1200 × 627 | 1.91:1 |
| | carrossel (documento PDF) | 1080 × 1350 | 4:5 |
| **Facebook** | feed nativo | 1080 × 1350 | 4:5 |
| | imagem de link | 1200 × 630 | 1.91:1 |
| | stories | 1080 × 1920 | 9:16 |
| **YouTube** | miniatura | 1280 × 720 | 16:9 |
| | shorts | 1080 × 1920 | 9:16 |
| **TikTok** | vídeo / foto | 1080 × 1920 | 9:16 |
| **Pinterest** | pin padrão | 1000 × 1500 | 2:3 |

**Regra:** produza sempre em 4:5 quando o feed permitir. Ocupa mais altura de
tela que 1:1 e é o formato de maior superfície no feed sem cair em corte.

---

## Áreas seguras

As margens por formato vivem **num lugar só**: o catálogo de formatos do `pwdev-media`.

```bash
pwdev-media formatos listar
pwdev-media formatos mostrar reels-9x16
pwdev-media formatos conferir feed-4x5 --caixa x,y,largura,altura
```

O que vale lembrar além dos números:

- **Vertical 9:16:** o app cobre topo (perfil, som), base (legenda, CTA, progresso) e lateral direita
  (curtir, comentar). Erro mais comum: chamada no rodapé, onde a legenda do app cobre.
- **Feed 4:5 e 1:1:** pouca sobreposição de UI, mas margem estreita comprime visualmente.

### Miniatura do YouTube
Texto legível em **168 × 94 px** — o tamanho real no celular. Se não lê nesse
tamanho, não funciona. Teste reduzindo, sempre.

### Carrossel
Reserve **80 px na borda externa** de cada slide: o gesto de swipe e o indicador
de página ocupam essa faixa.

---

## Tipografia mínima

Valores para leitura em celular, sobre 1080 px de largura:

| Elemento | Mínimo | Recomendado |
|---|---|---|
| Título de capa | 72 px | 96-120 px |
| Cabeçalho de slide | 48 px | 56-72 px |
| Corpo | 32 px | 36-44 px |
| Legenda / fonte | 24 px | 28 px |

**Abaixo de 24 px é inacessível em celular.** Não use, nem para crédito de fonte.

Limite por slide de carrossel: **título até 8 palavras, corpo até 30 palavras.**
Passou disso, vira dois slides.

---

## Contraste

WCAG 2.1 AA é o piso, não a meta — compressão de rede social degrada bordas
e reduz o contraste percebido.

| Elemento | Mínimo WCAG | Alvo para social |
|---|---|---|
| Texto normal (< 24 px) | 4.5:1 | **7:1** |
| Texto grande (≥ 24 px ou 19 px bold) | 3:1 | **4.5:1** |
| Elemento gráfico essencial | 3:1 | 4.5:1 |

**Texto sobre foto:** nunca confie no contraste direto. Use sobreposição sólida,
gradiente ou caixa atrás do texto. Meça o contraste contra a **região mais clara**
da foto sob o texto, não contra a média.

---

## Contagem de slides

| Plataforma | Mínimo | Ideal | Máximo |
|---|---|---|---|
| Instagram | 5 | 8-10 | 20 |
| LinkedIn (documento) | 5 | 7-12 | 300 (irrelevante na prática) |
| Facebook | 3 | 5-8 | 10 |

Abaixo de 5 slides não justifica o formato — vira post único.

---

## Setor público

Peças de serviço ao cidadão têm exigência adicional:

- Contraste alvo **7:1 em todo texto**, não só no pequeno
- Texto essencial **nunca** apenas dentro da imagem — repetir na legenda
- Sem texto sobre foto de pessoa em situação de vulnerabilidade
- Fonte do dado visível na peça, com data
- Identidade visual do órgão conforme manual da instituição
- Descrição alternativa obrigatória — ver `social-alt-text`
