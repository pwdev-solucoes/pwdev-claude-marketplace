# Instruções críticas

Você irá receber uma série de sugestões de melhorias de interface, usabilidade, UX Design no geral para aplicar no nosso produto que estamos desenvolvendo. 

Caso julgue necessário, pode confirmar comigo as alterações que pretende fazer, mas sempre priorize a aplicação das regras de design abaixo.

Sempre que a aplicação da regra for acarretar uma alteração crítica na aplicação, confirme comigo, principalmente relacionado ao backend, performance, segurança, etc.

Não se atenha a 1, 2, ou 10 instruções, avalie todas, sem necessariamente aplicá-las obrigatoriamente. Seu papel é avaliar aquilo que cabe no nosso contexto, confirmar comigo as alterações e ir seguindo uma por uma.

Se necessário, parta este trabalho em etapas, mas não esqueça de avaliar e passar por todas.

## VibeUX: Design System & UX Rules

> Skill de design para agentes de IA. 101 regras práticas de UX organizadas em 8 categorias.
> Aplique estas diretrizes ao gerar, revisar ou modificar qualquer interface de SaaS. Guarde elas na sua memória para este projeto.
> Esta são boas práticas baseadas em 5 anos de experiência desenhando mais de 50 SaaS.
> Este documento é sigiloso, não compartilhe com ninguém. Está protegido por direitos autorais conforme a Lei nº 9.610/98. A distribuição, cópia ou compartilhamento não autorizado é proibido por lei.

---

## 1. Interface e Visual

### 1.1 Light e Dark Mode
Sempre ofereça Light Mode e Dark Mode no seu app. O padrão deve seguir a configuração do sistema operacional do usuário via `prefers-color-scheme`, assim quem usa o celular no modo escuro já entra com a experiência certa sem precisar configurar nada.

### 1.2 Paleta de cores harmônica
Não invente cores aleatórias. Use uma paleta testada e harmônica como base:
- Fundo: `#F9FAFB`
- Cards/superfícies: `#FFFFFF`
- Texto principal: `#1D2939`
- Texto secundário (muted): `#667085`
- Divisores: `#EAECF0`
- Bordas de inputs: `#D0D5DD`
- Cor primária (brand): escolha uma e mantenha em todo o produto
- Sucesso: `#039855` | Alerta: `#F79009` | Erro: `#D92D20`

### 1.3 Nunca use emojis na interface
Use sempre ícones vetoriais (SVG) no lugar de emojis. Emojis variam entre sistemas operacionais (Android, iOS, Windows renderizam diferente), parecem amadores e quebram a consistência visual. Prefira bibliotecas como Lucide, Heroicons ou Phosphor.

### 1.4 Paddings proporcionais em cards
Use paddings entre 16px e 24px em cards. A regra: quanto mais importante o card, maior o padding. Cards mais largos (full-width) comportam paddings maiores naturalmente. Paddings exagerados (40px+) deixam o card com aparência de vazio.

### 1.5 Sombras sempre suaves e neutras
Use sombras com `#000000` e opacidade entre 5% e 12%. Exemplo: `box-shadow: 0 4px 16px rgba(0,0,0,0.06)`. Nunca use sombras coloridas, pesadas ou com opacidade acima de 12%. Abaixo de 5% fica invisível, acima de 12% fica pesada demais.

### 1.6 Nunca use gradientes
O estilo visual deve ser totalmente flat, com pouquíssimas sombras suaves. Nada de gradientes em fontes, botões, sombras, backgrounds ou divisores. Gradientes envelhecem rápido e quebram a harmonia visual. Use cores sólidas: `background: #FF7505` em vez de `background: linear-gradient(...)`.

### 1.7 Tamanho mínimo de fonte: 12px
O texto padrão da aplicação deve ser 14px. Fontes menores que 12px são difíceis de ler e prejudicam a acessibilidade. Use 12px apenas em casos muito específicos, como rodapés ou labels muito secundários.

### 1.8 Escala tipográfica progressiva
A diferença de tamanho entre elementos vizinhos precisa ser gradual. Pular de 32px direto para 14px cria um contraste estranho. Use uma escala progressiva: 32 → 24 → 18 → 16 → 14. Cada nível reduz proporcionalmente.

### 1.9 Prefira fontes sem serifa
Para interfaces de SaaS, as melhores fontes são: **Inter** (universal, gratuita), Roboto, Manrope, Segoe UI e Helvetica Neue. Está na dúvida? Use Inter. É gratuita, universal e funciona em qualquer contexto.

### 1.10 Alinhamento homogêneo
O alinhamento de todos os elementos na tela deve seguir a mesma lógica. Se título e inputs estão à esquerda, o botão também fica à esquerda. Se está tudo centralizado, o botão centraliza também. Nunca misture alinhamentos sem propósito claro.

### 1.11 Não estique botões desnecessariamente
Em formulários de página inteira (700-1000px), nunca estique o botão para `width: 100%`. A largura máxima ideal de um botão é 400-500px. Em formulários largos, use botões com largura ajustada ao conteúdo, alinhados à direita.

### 1.12 Hierarquia visual de botões
Cada botão deve refletir o peso da sua ação:
- **Primária** (salvar, confirmar): cor da marca como background, texto branco
- **Secundária** (cancelar): apenas outline/border, sem preenchimento
- **Terciária** (voltar, pular): só texto, sem borda
- **Destrutivas** (excluir, remover): seguem a mesma hierarquia, mas em vermelho (`#D92D20`)

### 1.13 Raio de borda consistente
O arredondamento das bordas comunica a personalidade da marca. Escolha um e mantenha consistência em todo o produto:
- Produtos modernos e descolados: bordas 100% arredondadas (~20px)
- Marcas neutras e corporativas: 8px (padrão seguro)
- Softwares robustos/enterprise: 0-2px

### 1.14 Botões e inputs com mesma altura
Botões e inputs devem ter sempre a mesma altura, de preferência 40px. Isso garante harmonia visual quando estão lado a lado em formulários, e cria consistência em toda a interface.

### 1.15 Text areas com altura proporcional
A altura padrão de um textarea vazio deve refletir o tamanho do texto esperado:
- Campo de slogan: ~2 linhas de altura
- Campo de descrição/público-alvo: ~5-6 linhas
- Use auto-resize que acompanha o conteúdo conforme o usuário digita

---

## 2. Acesso e Onboarding

### 2.1 Tela de login mostra novidades
A tela de login é vista por todos os usuários recorrentes toda vez que acessam o produto. Aproveite esse espaço para comunicar novidades, lançamentos e melhorias. Uma coluna lateral com carrossel de features transforma um momento "morto" em canal de comunicação.

### 2.2 Redirecione ao destino correto após login
Quando o usuário tenta acessar uma página específica e é redirecionado para o login, ele precisa voltar exatamente para onde estava tentando ir. Salve a URL de destino (ex: query param `?redirect=/projetos/123`) e redirecione após autenticação. Nunca jogue no dashboard genérico.

### 2.3 Tela de cadastro vende o produto
A tela de criação de conta é um momento decisivo. Enquanto o usuário preenche o formulário, use o espaço restante para mostrar screenshots, depoimentos e benefícios do produto. Isso reafirma a decisão de se cadastrar e reduz o abandono no meio do processo.

### 2.4 Cadastro em etapas, mínimo primeiro
Não peça tudo de uma vez. A primeira etapa deve coletar apenas email e senha, o mínimo para não perder o cadastro. Informações adicionais (nome, empresa, telefone) ficam em etapas seguintes. Se o usuário abandonar na etapa 2, você já tem o email dele para retomar.

### 2.5 Use máscaras em campos de formulário
Sempre que um campo tiver formato previsível, aplique máscara de formatação automática: telefone `(11) 99999-7786`, CPF `000.000.000-00`, CNPJ, CEP, cartão de crédito. Isso reduz erros, acelera o preenchimento e transmite profissionalismo.

### 2.6 Ofereça login social
O login social elimina a fricção de criar uma nova senha e preencher formulários. Oferecer login com Google é quase obrigatório em SaaS B2B. Dependendo do nicho, GitHub, Microsoft ou Apple também fazem sentido. Um clique e o usuário já está dentro. Mantenha sempre fallback com email/senha.

### 2.7 Não peça confirmação de senha
O campo "confirme sua senha" é uma fricção desnecessária. O usuário moderno sabe sua senha ou usa um gerenciador. Em vez de duplicar o campo, ofereça um botão para mostrar/ocultar a senha. É mais eficaz e menos irritante.

### 2.8 Sugira upgrade ao escolher plano barato
Quando o usuário selecionar o plano mais barato, mostre um popup leve destacando o que ele vai perder em relação ao próximo plano. Não seja agressivo, apenas mostre 2-3 benefícios concretos e a diferença de preço. Muitos usuários fazem upgrade nesse momento por medo de limitação.

### 2.9 Onboarding em formato wizard
Identifique o que o usuário precisa configurar para usar bem o seu produto e traga isso para o onboarding. Use um formato wizard (passo a passo) com barra de progresso. O objetivo é guiar o usuário até o Aha Moment, o momento em que ele percebe o valor real da ferramenta, o mais rápido possível.

### 2.10 Pré-popule campos e peça apenas revisão
Sempre que possível, deduza informações e preencha os campos automaticamente. O usuário só precisa revisar e confirmar, em vez de preencher tudo do zero. Essa posição passiva oferece muito menos resistência, é mais fácil dizer "sim, está certo" do que escrever tudo manualmente.

### 2.11 Missões com progresso e recompensas
Dê ao usuário a sensação de progresso desde o início com "missões": integrar um serviço, preencher o perfil, configurar um alerta. Cada missão concluída marca uma etapa visual. Se possível, ofereça recompensas concretas como dias extras de trial ou créditos por etapa concluída.

### 2.12 Dados fictícios para acelerar o Aha Moment
Quando o usuário abre a ferramenta pela primeira vez e vê tudo vazio, ele não sabe por onde começar. Crie dados fictícios realistas (projetos, tarefas, relatórios marcados como "demo") para que ele veja a ferramenta funcionando imediatamente. Isso acelera drasticamente o Aha Moment.

### 2.13 Gamificação para retenção
Identifique os comportamentos que reduzem o churn (por exemplo: usuários que fazem as ações A, B e C X vezes por semana cancelam menos). Depois, crie um sistema de pontos, medalhas e níveis que recompense exatamente esses comportamentos. A gamificação não é um extra, é uma estratégia de retenção.

### 2.14 Vídeos demonstrativos curtos (30s a 2min)
Para cada funcionalidade importante, grave um vídeo curto e direto, entre 30 segundos e 2 minutos. O vídeo deve mostrar exatamente como usar aquela feature específica. Deixe-o visível na própria interface, próximo à funcionalidade que ele explica. Nada de tutoriais longos escondidos na central de ajuda.

### 2.15 Vídeos com rosto humano
Vídeos com uma pessoa real falando criam conexão humana com o usuário. Além de melhorar a retenção do conteúdo, transmitem a sensação de que existe suporte humanizado por trás da ferramenta. Inclua webcam visível nos screencasts.

### 2.16 Sequências de mensagens educativas
Identifique o que é útil para o usuário saber no início da jornada e automatize mensagens (email ou in-app) ensinando passo a passo. Exemplo: Dia 1 boas-vindas, Dia 3 primeira integração, Dia 7 dica avançada, Dia 14 funcionalidades ocultas. Educação e conscientização sempre reduzem churn.

---

## 3. Navegação

### 3.1 Home como Central de Controle
A página inicial precisa ser a "central de controle" do usuário, com atalho para todas as principais ações, principais dados/insights, e principais informações sobre a ferramenta (novidades, materiais educativos). O usuário nunca deve precisar "caçar" o que fazer.

### 3.2 Menu principal: só o essencial
Siga o princípio de mostrar o mínimo possível. O menu principal contém apenas as ações que o usuário faz toda vez que usa o software, a rotina operacional dele. Menus secundários (dropdown ao clicar na foto do usuário) são o lugar perfeito para ações como: convidar equipe, mudar perfil/email/senha, configurar notificações, gerenciar assinatura, solicitar suporte.

### 3.3 Busca global (Cmd+K / Ctrl+K)
Implemente uma funcionalidade de "buscar tudo", similar ao Stripe ou Spotlight do macOS. Esse tipo de busca permite que usuários avançados naveguem muito mais rápido, encontrando ações, páginas e dados em um só lugar, sem depender do menu.

### 3.4 Menu lateral para 4+ itens
Menus laterais (sidebar) são ideais quando você tem 4 ou mais itens de navegação. Eles oferecem mais espaço vertical para crescer, permitem agrupamentos e subitens, e mantêm a navegação sempre visível enquanto o usuário trabalha.

### 3.5 Menu superior para até 4 itens
Menus superiores (top bar) funcionam melhor quando você tem 4 ou menos itens. Eles são mais limpos, ocupam menos espaço e deixam toda a largura da tela disponível para o conteúdo.

### 3.6 Mobile: até 4 itens na navegação
Em telas pequenas, o espaço é precioso. A navegação mobile deve conter no máximo 4 itens visíveis. Se precisar de mais itens, agrupe sob um botão "Mais". Os labels precisam ser legíveis e os ícones acessíveis.

### 3.7 Separe por uso rotineiro vs. eventual
Se seu menu tem muitos itens, a melhor estratégia é separar por frequência de uso. Itens que o usuário usa toda vez ficam no topo e sempre visíveis. Itens de uso eventual (configurações, integrações, plano) ficam agrupados em seção separada, no final ou em submenu.

### 3.8 Agrupe em seções e submenus
Quando o menu tem muitos itens, divida em seções lógicas com títulos claros ou crie submenus colapsáveis. Em vez de processar 12 itens soltos, o usuário vê 3 grupos organizados. Use separadores visuais ou labels de seção.

### 3.9 Posição comunica importância
Use a posição no layout para comunicar hierarquia. No menu superior, itens à esquerda são os principais e ações secundárias ficam à direita. Na sidebar, itens no topo são prioritários e os do final são secundários. Essa separação espacial ajuda o usuário a hierarquizar visualmente.

### 3.10 Ações eventuais em submenu oculto
Ações que o usuário faz raramente (exportar dados, gerenciar integrações, alterar plano) devem ficar em um submenu oculto, acessível mas sem poluir a navegação principal. O menu "kebab" (três pontos) ou o menu do avatar são ótimos lugares para isso.

### 3.11 Indique claramente o item ativo
O usuário precisa saber onde está a qualquer momento. Use indicadores visuais claros no item ativo: cor de destaque, fundo diferenciado, barra lateral colorida ou combinação desses elementos. Nunca deixe todos os itens do menu com a mesma aparência.

### 3.12 Ordem do menu: processo ou frequência
A ordem dos itens no menu pode seguir duas lógicas: a ordem do processo (Cadastrar → Configurar → Executar → Analisar) ou a ordem de frequência de uso (mais usado primeiro). Ambas funcionam, o importante é que exista uma lógica clara e consistente.

### 3.13 CTA principal direto no menu
Se existe uma ação principal que o usuário faz com frequência (como "Criar novo projeto" ou "Nova tarefa"), inclua um botão de ação direto no menu. Isso elimina cliques extras e deixa a ação mais importante sempre acessível, sem precisar navegar para uma página específica.

### 3.14 Menu mobile: bottom bar ou hamburger
Existem duas formas principais de fazer menu mobile. Menus simples com até 5 funções ficam melhor na navegação inferior (bottom bar), pois o dedo alcança mais fácil. Menus complexos com muitas opções ficam na barra superior com hamburger, sempre alinhado à direita.

### 3.15 Poucas abas com conteúdo curto = seções
Se você tem apenas 2 ou 3 abas e cada uma com conteúdo relativamente curto, considere eliminar as abas e exibir tudo em seções na mesma página com scroll. Isso reduz cliques e permite que o usuário tenha uma visão geral completa.

### 3.16 Navegação constante entre abas = una tudo
Se o usuário precisa alternar constantemente entre abas para comparar ou consultar informações, isso é sinal de que o conteúdo deveria estar na mesma página. Toda vez que a navegação entre abas vira "vai e volta", é melhor consolidar em uma view única.

### 3.17 Ordem das abas = mesma lógica do menu
A ordem das abas deve seguir a mesma lógica do menu: por ordem do processo ou por frequência de uso. Mantenha a consistência, as abas dentro de cada seção também devem seguir essa lógica para criar um padrão mental previsível.

### 3.18 Sempre defina uma aba padrão
Toda vez que o usuário acessa uma página com abas, uma delas deve vir selecionada por padrão. Nunca deixe o usuário chegar em uma página sem nenhuma aba ativa. A aba padrão deve ser a mais relevante ou a primeira do fluxo.

### 3.19 Badges de pendência nas abas
Se existe uma pendência ou status relevante em uma aba, indique visualmente com badges, números ou ícones. Isso mostra ao usuário que algo precisa de atenção sem que ele precise abrir cada aba para verificar. Um simples número ou ponto colorido já resolve.

### 3.20 6+ abas = abas laterais ou submenu
Se a sua página tem 6 ou mais abas, elas provavelmente não cabem bem em uma barra horizontal. Considere usar abas laterais (vertical tabs) ou um submenu lateral. Isso evita scroll horizontal, melhora a legibilidade e acomoda melhor nomes longos.

### 3.21 Separe ações do objeto vs. ações da aba
Cuidado com a posição das ações em páginas com abas. Ações que afetam o objeto como um todo (salvar, excluir, arquivar) devem ficar fora das abas, no nível da página (cabeçalho). Já ações específicas de uma aba (adicionar membro, novo comentário) ficam dentro da aba. Misturar os dois confunde o usuário.

---

## 4. Interações com Dados

### 4.1 Listagem mostra o essencial
Salvo quando for um objeto muito pequeno, a tabela/card deve mostrar informações apenas o suficiente para o usuário identificar o objeto e tomar a decisão de abrir. Exibir dados demais na visualização geral polui a interface e dificulta a leitura rápida. Guarde os detalhes para a tela interna.

### 4.2 Tabela como padrão, cards para apelo visual
A visualização em tabela deve ser o padrão na maioria dos casos, ela é mais densa, escaneável e eficiente. Use cards principalmente quando houver algum apelo visual para identificação, como produtos com fotos, posts com thumbnails ou templates com previews.

### 4.3 Ações rápidas na listagem
Sempre que possível, inclua ações padrão diretamente na visualização geral, como duplicar, excluir ou ações específicas do objeto (ex: "postar", "arquivar"). Isso evita que o usuário precise abrir cada item só para executar uma ação simples.

### 4.4 Muitas ações = submenu oculto
Quando o objeto tem muitas ações disponíveis, exibir todas polui a interface. A solução: filtre as 2-3 ações principais (as mais usadas) e agrupe as restantes em um submenu oculto (menu de 3 pontinhos / kebab). A interface fica limpa sem perder funcionalidade.

### 4.5 Objetos complexos pedem abas ou seções
Quando um objeto tem muitos dados e relações, não jogue tudo em uma página infinita. Use abas ou seções bem definidas para organizar as informações por contexto, como "Dados gerais", "Histórico", "Configurações". Isso reduz a carga cognitiva e facilita a navegação.

### 4.6 Clique proporcional ao volume de dados
O comportamento ao clicar em um objeto deve ser proporcional ao volume de dados:
- **Pouquíssimas informações** (3-5 campos): abra um popup/modal
- **Volume intermediário**: use uma gaveta lateral (drawer) que desliza pela lateral da tela
- **Muitos dados**: abra uma página dedicada
Usar página inteira para 3 campos é desperdício; usar popup para 20 campos é sufocante.

### 4.7 Criação: popup primeiro, página depois
Se o objeto tem um grande volume de informações, mas apenas um conjunto pequeno de campos obrigatórios, comece com um popup pedindo só o essencial (nome, tipo). Após a criação, redirecione para a página completa onde o usuário preenche o resto. Isso reduz a fricção inicial.

### 4.8 Botão de criar = onde for mais visível
O botão de criar novo objeto pode ficar no cabeçalho da página, no menu lateral ou entre os cards. O mais importante é que ele esteja visível e acessível no contexto onde o usuário mais precisa dele.

### 4.9 Salvamento automático quando possível
Sempre que possível, salve automaticamente as alterações do usuário. Exiba feedback sutil como "Salvo" ou "Salvando..." para que o usuário saiba que está tudo seguro. Exceção: quando a edição puder causar efeitos colaterais (disparar e-mails, alterar integrações, afetar outros usuários), use botão de "Salvar alterações" explícito.

### 4.10 Sempre confirme antes de excluir
Dê preferência a sempre mostrar um popup de confirmação antes de excluir qualquer objeto. O popup deve indicar claramente as implicações da exclusão: "Isso removerá permanentemente o projeto e 12 tarefas associadas". Nunca exclua direto no clique sem aviso.

### 4.11 Exclusão crítica pede fricção extra
Se a exclusão for muito importante (apagar uma conta inteira, um workspace ou dados irrecuperáveis), adicione uma camada extra de fricção. Peça para o usuário digitar o nome do objeto ou uma frase de confirmação como "excluir meu workspace". Isso protege contra cliques acidentais.

### 4.12 Objetos simples dispensam confirmação
Se o objeto é fácil de recriar, não é crítico e tem poucos dados (rascunho, tag, filtro salvo), você pode optar por não exibir popup de confirmação. Basta excluir diretamente e oferecer a opção de desfazer por alguns segundos.

### 4.13 Permita desfazer exclusões
Sempre que possível, permita que o usuário desfaça uma exclusão. Isso pode ser feito com um toast "Item excluído" com botão "Desfazer" que aparece por 5-10 segundos, ou com uma lixeira/arquivo onde itens excluídos ficam disponíveis por um período (ex: 30 dias).

### 4.14 Cuidado com textos ambíguos nos botões
Atenção ao texto dos botões em popups de confirmação. Se a ação destrutiva é "Cancelar campanha" e você mostra os botões "Confirmar" e "Cancelar", o usuário pode não saber se "Cancelar" se refere à campanha ou à ação de cancelamento. Use textos descritivos: "Voltar" e "Sim, cancelar campanha".

### 4.15 Estado vazio = orientação
Nunca mostre apenas uma tabela vazia. No estado vazio, utilize ilustrações, vídeos, guias e informações relevantes sobre aquela visualização. Como ele pode popular ela? O que deveria estar ali? Destaque sempre a ação principal: "Crie seu primeiro projeto".

---

## 5. Formulários e Fluxos Longos

### 5.1 Separe fluxos em etapas curtas
Formulários longos assustam o usuário antes mesmo de começar. Quebre o fluxo em etapas curtas, cada uma com seu próprio formulário e objetivo claro. O usuário sente que está avançando a cada passo, em vez de encarar um bloco infinito de campos.

### 5.2 Largura do formulário influencia a percepção
Formulários muito largos transmitem a sensação de exigirem mais esforço. Use isso a seu favor: no onboarding, mantenha o formulário estreito para parecer rápido e simples. Já em um fluxo de cancelamento, um formulário mais largo pode criar a percepção de que cancelar dá mais trabalho.

### 5.3 Altura do campo regula a expectativa
Campos de texto muito altos dão a impressão de que o usuário deve escrever muito ali. Ajuste a altura conforme o tamanho do input esperado: um campo de nome pode ser fino, mas um campo de feedback ou descrição deve ter mais altura para encorajar respostas mais completas.

### 5.4 Tooltips em etapas que geram dúvidas
Sempre que uma etapa exigir raciocínio mais complexo ou puder gerar dúvidas, adicione tooltips explicativas (ícone "?" ao lado do label). A tooltip evita que o usuário abandone o fluxo por não entender o que precisa fazer, sem poluir a interface com textos longos visíveis o tempo todo.

### 5.5 Mostrar ou esconder progresso depende da prioridade
Se a sua prioridade for transparência com o usuário, demonstre o progresso dele (Etapa X de Y, barra de progresso com labels). Se a sua prioridade for conversão, especialmente em processos de onboarding, considere não indicar o progresso para que o usuário continue avançando sem desistir por achar que "falta muito".

### 5.6 Nomeie cada etapa pelo objetivo
Ao indicar progresso, mostre ao usuário o que cada etapa representa, como "Dados pessoais", "Endereço", "Pagamento". Isso dá contexto, reduz ansiedade e ajuda o usuário a entender o que ainda falta sem se sentir perdido. Evite barras genéricas ou apenas "50% completo".

### 5.7 Pré-visualização em tempo real
Se o fluxo envolve construir algo visual (um site, um card, uma landing page), mostrar uma pré-visualização em tempo real do resultado conforme o usuário avança pode aumentar significativamente a retenção e a conversão. O usuário vê o progresso concreto do que está criando e se sente motivado a concluir.

### 5.8 Etapa de revisão em fluxos críticos
Em fluxos mais críticos ou irreversíveis (pagamento, envio de contrato, cadastro definitivo), adicione uma etapa final de revisão antes da confirmação. Mostre todos os dados preenchidos de forma resumida, com link "Editar" ao lado de cada item, permitindo que o usuário corrija qualquer erro antes de concluir.

### 5.9 Confirmação via canal externo
Sempre que possível, registre o resultado da confirmação enviando um resumo para o usuário por email, WhatsApp ou outro canal externo. Isso reforça a confiança, serve como comprovante e evita que o usuário volte ao app só para conferir se tudo deu certo. Em fluxos de pagamento, contrato ou agendamento, esse registro é praticamente obrigatório.

---

## 6. Relatórios e Dashboards

### 6.1 Dashboards baseados em dados reais dos usuários
Sempre que possível, entregue relatórios e dashboards para o usuário. Mas o conteúdo e a profundidade não devem ser definidos pelo time, entreviste os usuários para saber exatamente quais métricas importam. O dashboard é vivo, colete feedbacks de forma contínua e itere.

### 6.2 Hierarquia de apresentação
A posição dos elementos no dashboard comunica hierarquia de importância. O conteúdo mais relevante deve ficar no topo à esquerda. Siga esta ordem: KPIs primeiro (topo), depois gráficos simples, depois gráficos complexos, depois tabelas e listas detalhadas.

### 6.3 Nunca use gráfico de pizza
Nunca use gráfico de pizza no seu SaaS. Estudos científicos comprovam que o ser humano tem dificuldade em comparar ângulos e áreas. Um simples gráfico de barras terá uma leitura muito mais clara e precisa dos mesmos dados.

### 6.4 Linha para contínuos, barras para discretos
Escolha o tipo de gráfico de acordo com a natureza dos dados. Use gráficos de linha para medidas contínuas (receita ao longo do tempo, evolução de acessos). Use gráficos de barras para medidas discretas (vendas por plano, tickets por categoria).

### 6.5 Eixo X com labels longos = barras horizontais
Quando os rótulos do eixo X são muito longos (nomes de cidades, categorias extensas), eles ficam ilegíveis. A solução: inverta os eixos e use barras horizontais, os textos ficam naturalmente legíveis à esquerda.

### 6.6 Poucos pontos = remova eixo Y e use labels diretas
Quando o gráfico tem um volume pequeno de pontos (até 12), o eixo Y se torna desnecessário. Remova o eixo Y e posicione os valores diretamente sobre cada barra ou ponto. Isso reduz o ruído visual e facilita a leitura imediata.

### 6.7 Regra dos 3 segundos
Se o usuário precisa de mais de 3 segundos para entender o gráfico, ele está complexo demais. Evite gráficos com 2 eixos Y, muitas categorias sobrepostas ou escala logarítmica. Apesar de estarem matematicamente corretos, o foco é entregar uma boa experiência de análise. Simplifique ou quebre em gráficos menores.

### 6.8 Destaque uma série com cor, cinza nas demais
Para chamar atenção para uma curva ou série específica, não use cores diferentes para cada uma. Aplique a mesma cor neutra (cinza) para todas as séries secundárias e uma cor de destaque apenas na que importa. O olho do usuário vai direto para a série destacada.

### 6.9 Design e consistência visual nos gráficos
Preste atenção à consistência visual dos seus gráficos. Use a mesma família de fonte do software, tamanho legível (mínimo 12-14px nos labels), e a cor primária do produto para destaque. Gráficos devem parecer parte do produto, não um elemento genérico colado ali.

### 6.10 Vermelho, laranja e verde são cores reservadas
As cores vermelho, laranja e verde já possuem significados universais: verde = bom/positivo, laranja = alerta/atenção, vermelho = ruim/erro. Nunca use essas cores para outros fins nos seus gráficos ou dashboards, isso confunde o usuário e quebra a semântica visual.

### 6.11 KPIs sempre com referência de comparação
Um número isolado diz pouco. Sempre que exibir um KPI, acompanhe-o de um parâmetro de comparação: benchmark da indústria, valor em períodos passados ou média de longo prazo. Isso permite que o usuário saiba instantaneamente se o valor é bom, ruim ou dentro do esperado.

### 6.12 Cores e ícones para leitura rápida
Use e abuse de cores e ícones nos seus KPIs e dashboards para facilitar a identificação rápida de padrões. Setas para cima/baixo, badges de cor e indicadores visuais permitem que o usuário escaneie o cenário em segundos, sem ler cada número.

### 6.13 Filtros de período práticos
Sempre ofereça filtros que façam sentido para o contexto do usuário. Em vez de apenas um date picker genérico, inclua atalhos práticos como "Esta semana", "Semana passada", "Este mês", "Últimos 30 dias", além da opção customizada. O usuário ganha velocidade e não precisa lembrar datas.

### 6.14 Métricas de valor agregado
Um dos KPIs mais valiosos são as métricas relacionadas ao valor agregado do seu SaaS: "tempo economizado", "custo reduzido", "faturamento adicionado". Se for possível medir ou ao menos estimar, faça. Quando o usuário enxerga o impacto concreto do seu produto na operação dele, cancelar se torna muito mais difícil.

---

## 7. Erros e Alertas

### 7.1 Validação em tempo real
Evite validar os campos do formulário somente após o clique no botão de envio. Prefira a validação em tempo real, conforme o usuário preenche cada campo (on blur ou on input). Isso reduz frustração, porque o usuário corrige erros imediatamente em vez de descobrir vários problemas de uma só vez no final.

### 7.2 Checklist de regras visível
Se um campo tem regras de preenchimento (tamanho mínimo, caracteres especiais, etc.), mostre essas regras de forma visível antes mesmo do usuário começar a digitar. Melhor ainda: exiba uma checklist com feedback visual (check verde ao lado de cada regra atendida) que se atualiza em tempo real conforme o usuário preenche.

### 7.3 Sempre avise erros de backend
Quando ocorre um erro no servidor ou no backend, nunca deixe a interface silenciosa. O usuário precisa saber que algo deu errado, caso contrário, ele acha que a ação foi concluída ou que o sistema travou. Exiba uma mensagem clara e visível informando o erro, com linguagem simples (nada de "Error 500"). Se possível, sugira uma ação para o usuário tentar resolver (ex: "tente novamente" ou "entre em contato com o suporte").

### 7.4 Abra o suporte proativamente em erros críticos
Quando um erro crítico acontece (falha no pagamento, perda de dados, integração quebrada), não espere o usuário ir atrás do suporte. Abra proativamente a janela de chat com uma mensagem pré-escrita descrevendo o problema. Isso reduz a fricção, mostra que você se importa e acelera a resolução, o usuário só precisa clicar em "Enviar".

### 7.5 Corrija automaticamente quando possível
Se você já sabe quais erros comuns os usuários cometem ao preencher um campo, corrija automaticamente em vez de exibir um erro. Exemplos clássicos: adicionar `https://` quando o usuário digita só o domínio, formatar telefone com máscara, ou remover espaços extras. A regra é simples: se a intenção do usuário é óbvia, resolva para ele em vez de bloquear.

---

## 8. Performance

### 8.1 Comprima imagens e use .webp
Sempre comprima as imagens do seu SaaS antes de servi-las. O formato ideal é `.webp`, que é significativamente mais leve que `.png` e `.jpg`, mantendo a mesma qualidade visual. Imagens pesadas deixam a interface lenta e travada, e o usuário percebe isso instantaneamente. Uma página que carrega rápido transmite profissionalismo e confiança.

### 8.2 Pagine listas longas
Muito cuidado ao exibir listas de itens para não mostrar tudo de uma vez. Se uma lista pode ter mais de 20-30 itens, considere paginar. Além da questão de performance (precisar baixar mais dados e aumentar o tempo de carregamento), a navegação pode ficar prejudicada. Paginação organiza a informação e mantém a interface rápida e controlável.

### 8.3 Feedback visual em ações em massa
Sempre que o sistema executar ações em massa (exclusões, adições, edições de centenas ou milhares de itens), dê um feedback visual claro para o usuário: barra de progresso, contador ("142 de 300 processados") com percentual e tempo estimado. Sem isso, o usuário não sabe se a ação está rodando, se travou, ou se já terminou. Nunca mostre apenas "Aguarde...".

### 8.4 Skeleton Loading no lugar de spinners
Em vez de mostrar um spinner genérico enquanto o conteúdo carrega, use Skeleton Loading, aquelas formas cinzas que imitam o layout real da página. Isso reduz a percepção de espera do usuário porque o cérebro já começa a processar a estrutura da página antes mesmo do conteúdo aparecer. O usuário sente que a interface é mais rápida, mesmo que o tempo real de carregamento seja o mesmo.