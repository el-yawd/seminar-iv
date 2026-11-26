# Registro da máquina `vostro-15-3515`

Diário de decisões e ações tomadas nesta máquina. Não faz parte do trabalho
(não é incluído no LaTeX); serve só para rastrear o que foi feito aqui e por quê.

Entradas em ordem cronológica, as mais recentes no fim.

## Máquina

| Item | Valor |
|---|---|
| Hostname | `vostro-15-3515` |
| CPU | AMD Ryzen 7 3700U (4 núcleos / 8 threads) |
| RAM | 13 GB (~9 GB livres em uso normal) |
| GPU | nenhuma |
| SO | Ubuntu 26.04.1 LTS |
| Python do projeto | 3.13 (`.venv`); o sistema não tem 3.12 |

Diferente da máquina do piloto e do bloco G (Intel Core i5-1235U, CachyOS, Python 3.12.16).

---

## 22/11/2026 (noite)

**Situação de partida:** commit `9930a6d` (bloco G concluído, gate negativo, E = 2).
Bloco A com 0 execuções. Apresentação de progresso ao professor em 23/11, 12h.

### Decisões

1. **Usar Python 3.13 em vez de 3.12.** Todas as versões fixadas em
   `requirements-cpu.txt` têm wheel para cp313, e o `venv` do sistema basta, sem
   instalar `uv` ou outro Python. A diferença de versão do Python é verificada
   pelo teste de reprodutibilidade (item 4).
2. **`run.py`: registrar a máquina no JSON.** O campo `env` gravava só `cpu: x86_64`,
   o que não distingue as máquinas. Foram acrescentados `cpu_model` (de
   `/proc/cpuinfo`), `n_cpus`, `host` e `gpu`. O campo `cpu` antigo foi mantido.
3. **`grid.py`: `--shard` passa a dividir por semente.** Antes, `cfgs[i::n]` alternava
   configurações, e FedAvg e FedProx da mesma semente podiam cair em máquinas
   diferentes, o que mistura ruído de hardware na diferença pareada Δ. Agora cada
   fatia recebe sementes inteiras (bloco A com `--shard 0/2` → sementes 0, 2, 4;
   `1/2` → 1, 3).
4. **Teste de reprodutibilidade entre máquinas antes de qualquer execução nova.**
   Reexecutar `fedavg, α = 100, s0, T = 20` do piloto e comparar `acc`, `loss` e
   `pids` com o CSV versionado. Os arquivos originais do piloto são restaurados
   depois com `git checkout`.
   - **Resultado: não é bit a bit idêntico entre máquinas.** Os clientes sorteados
     (`pids`) e a rodada 0 coincidem exatamente, mas a acurácia diverge a partir da
     rodada 3: diferença máxima de 0,13 p.p. (rodada 9: 71,19 % na Intel, 71,32 % aqui)
     e 0,06 p.p. na rodada final (75,36 % × 75,42 %). A perda difere na 4.ª–5.ª casa.
     O P10 local final foi igual (70,8 %). Causa provável: kernels de ponto flutuante
     diferentes entre CPUs (Intel × AMD Zen+) e/ou Python 3.12 × 3.13; não investigado.
   - Consequência: o ruído entre máquinas (~0,1 p.p.) é da mesma ordem dos Δ medidos no
     piloto e no bloco G. **Pares FedAvg × FedProx de uma mesma semente nunca podem
     ser divididos entre máquinas.** O `--shard` por semente (item 3) garante isso.
   - Tempo: 250 s aqui contra 173 s na Intel para a mesma configuração (~1,45×); rodada
     média de 4,6 s contra 3,4 s com α = 100.
   - **Autodeterminismo confirmado:** FedProx μ = 0 rodado aqui reproduz bit a bit o
     FedAvg rodado aqui (α = 100, s0, T = 20; `acc`, `loss` e `pids` idênticos). Os
     pares feitos inteiramente nesta máquina são válidos. Arquivos do piloto
     restaurados com `git checkout -- results/` depois dos dois testes.
5. **Regra permanente (o teste entre máquinas deu negativo):** esta máquina roda
   apenas sementes inteiras, e os resultados dela não são pareados com execuções da
   outra máquina.
6. **Micro-experimento de custo (H4) não roda aqui.** A Metodologia o especifica no
   i5-1235U.
7. **Bloco A lançado durante a madrugada** (22/11, 23h49), com
   `systemd-inhibit --what=sleep:idle` + `setsid nohup`, sem `--shard`: as 100
   configurações em ordem de semente, de modo que a semente 0 (20 execuções) sai
   primeiro. Estimativa: semente 0 em ~4,5 h; ~30 execuções até 07h30. Log em
   `~/blocoA.log`. Retomável: execuções interrompidas são refeitas na próxima chamada.
   Se outra máquina entrar depois, ela deve pegar sementes que esta ainda não começou.

### Pendências para 23/11 de manhã (antes das 12h)

- [ ] Conferir quantas execuções do bloco A concluíram (`ls experimentos/results/*_T100.json`).
- [ ] Gerar a tabela da semente 0 (FedAvg × 3 μ × 5 α).
- [ ] Atualizar `tab:status` em `5-Desenvolvimento.tex` e registrar a troca de máquina e o resultado do teste entre máquinas.
- [ ] Compilar o PDF (sem LaTeX nesta máquina: outra máquina, Overleaf ou `apt`).
- [ ] Opcional: notebook do Kaggle e tempo de uma execução na T4.

## 23/11/2026 (manhã)

**Situação às 07h45:** bloco A rodou a noite toda sem falhas. 33 de 100 execuções
concluídas: semente 0 completa (20) e semente 1 com 13 (α = 0,05; 0,1; 0,5 completos;
α = 1 em andamento). Tempo médio de 14,3 min por execução (T = 100), um pouco acima
da estimativa. Projeção: semente 1 completa por volta das 09h30; bloco A inteiro
por volta da meia-noite de 23→24/11, se a máquina continuar ligada.

**Leitura preliminar (exploratória; n = 1 a 2 sementes, sem teste estatístico):**
- μ ∈ {0,01; 0,1}: |Δacc| ≤ 0,1 p.p. em todos os α ≥ 0,1, nas duas sementes.
- μ = 1: piora de 0,6 a 1,0 p.p. com α ≥ 0,5; com α = 0,05 melhora (+1,06 e +0,50
  p.p.) e reduz a instabilidade, mas na semente 0 o P10 cai 3,6 p.p.
- R_τ: o FedProx não reduz as rodadas até o alvo; com μ = 1 e α alto, aumenta.
- FedAvg (semente 0): 84,7 % com α = 100 → 72,3 % com α = 0,05; P10 de 81,6 → 44,1 %.

**Decisões (23/11, manhã):**
- Apresentação adiada para as 17h. O slide 3 vai mostrar a **média das sementes 0 e 1**,
  e não só a semente 0. Aguardando a semente 1 terminar (~09h30).
- `tab:status` será atualizada com os números finais da semente 1.
- **`experimentos/analysis.py` criado.** Consolida um bloco em métricas por execução
  (acc das últimas 5 rodadas, instabilidade das últimas 20 com ddof = 1, P10 e DP
  locais, R_τ com censura) e Δ pareado por semente. Só pareia execuções feitas no mesmo
  `host`. τ = 90 % da acurácia média do FedAvg com α = 100 nas sementes disponíveis.
  Wilcoxon, Holm e TOST ficam para os blocos C e D. Os números dos slides saem dele
  (`results/blocoA_resumo.json`).
- **`grid.py`: blocos `C` (40) e `D` (100) do plano original** acrescentados (sementes
  5–14, T = 100, E = 2, `--mu-star`). Antes só existiam os `D2`/`cifar` da reformulação
  descartada.
- **`experimentos/kaggle.ipynb` criado:** sanidade μ = 0 ≡ FedAvg na GPU e tempo de uma
  execução do bloco A (T = 100). Move os resultados versionados para `results_repo/`
  antes, para que o zip de saída só tenha o que foi gerado no Kaggle. Clona o
  repositório público: precisa das mudanças locais no GitHub para usar o código novo.
- **Commit `5d73bd5`** (só código: `run.py`, `grid.py`, `analysis.py`, `kaggle.ipynb`).
  A máquina não tem identidade Git configurada; o commit foi assinado como Augusto Lázaro
  via `git -c` (sem alterar a configuração). Registro, slides e resultados do bloco A
  ficaram fora do commit. Sem push.
- Instalação do LaTeX autorizada; requer `sudo` com senha, então o comando precisa ser
  rodado pelo usuário.
- **LaTeX instalado pelo usuário** (`apt`: texlive-latex-extra, -lang-portuguese,
  -science, -fonts-extra, latexmk). `latexmk main.tex` compila sem erros: 22 páginas,
  sem referências ou citações indefinidas, sem avisos do BibTeX. Dois *overfull hbox*
  pequenos, já existentes: tabela larga de `3-TrabalhosRelacionado.tex` (linha 62,
  9,8 pt) e `tab:sanidade` em `5-Desenvolvimento.tex` (linha 222, 8,2 pt).
- **Avisos de margem corrigidos:** coluna "Resultado principal" de `tab:comparacao`
  de 3,0 para 2,6 cm; cabeçalhos de `tab:sanidade` em duas linhas. Recompilado sem
  *overfull*; as duas tabelas foram conferidas visualmente (páginas 9 e 17).
- O usuário vai se ausentar. Ficou autorizado seguir sozinho quando a semente 1
  terminar: `analysis.py`, slide 3 com a média das sementes 0–1, PDF dos slides,
  `tab:status` e recompilação do artigo.
- **09h36: semente 1 concluída** (40/100, nenhuma falha; 14,6 min por execução em
  média). `analysis.py` gerou `results/blocoA_resumo.json`. Médias das sementes 0–1,
  Δacc em p.p. (μ = 0,01 / 0,1 / 1): α = 0,05: +0,02 / +0,31 / +0,78;
  α = 0,1: −0,01 / +0,05 / −0,29; α = 0,5: −0,01 / −0,07 / −0,90;
  α = 1: −0,01 / −0,11 / −0,92; α = 100: 0,00 / −0,07 / −0,70.
  R_τ: o FedProx nunca atinge τ antes do FedAvg; com μ = 1, atinge depois em 9 de 10 pares.
- **Slides (`docs/atv06/slides.html` → `docs/ATV06-segundo-acompanhamento.pdf`)**,
  ainda com 5 slides:
  - Slide 3: novo "Resultado 1 · Bloco A, sementes 0–1 (exploratório)" com a tabela
    acima. O bloco G foi resumido em dois itens, e a reprodutibilidade passou para a
    tabela de dificuldades. As linhas de tempo da máquina e o quadro "Estágio atual"
    foram atualizados (40/100).
  - Slide 2: linha do tempo até 23/11, com o bloco A em 40/100.
  - Slide 4: sementes restantes, `analysis.py` com as métricas já implementadas e
    o cronograma com "A: 40/100".
  - PDF anterior guardado no *scratchpad* da sessão (não versionado).
- **Artigo (`5-Desenvolvimento.tex`):**
  - `tab:status` (data 23/11): nova linha da segunda máquina; blocos A/B "atrasado;
    A com 40/100".
  - `tab:cenarios`: situação de C1 e C2.
  - `tab:ajustes`: nova linha sobre a divisão entre máquinas.
  - Parágrafo de situação e próximos passos atualizados.
  - Recompilado sem avisos (22 páginas).
- Observação, sem mudança: as tabelas 16 e 17 (`tab:ajustes`, `tab:status`) caem nas
  páginas das referências. Isso já acontecia no commit `9930a6d`. Correção possível:
  `\clearpage` antes da bibliografia, a decidir com o usuário.

## 23/11/2026 (tarde)

- Usuário pediu para mostrar **três sementes** na apresentação e seguir automaticamente
  quando a semente 2 terminasse.
- **13h50: semente 2 concluída** (60/100, nenhuma falha). A semente 2 levou 4h15
  (12,8 min por execução); média geral de 14,0 min. A semente 3 começou em seguida.
  Previsão para o bloco inteiro: ~23h de 23/11.
- `analysis.py` com as sementes 0–2 (τ = 76,16 %). Δacc médio em p.p.
  (μ = 0,01 / 0,1 / 1): α = 0,05: +0,02 / +0,16 / +0,13; α = 0,1: 0,00 / +0,02 / −0,48;
  α = 0,5: 0,00 / −0,09 / −0,93; α = 1: −0,01 / −0,09 / −0,86; α = 100: −0,01 / −0,08 / −0,69.
  - **Mudança de leitura:** com α = 0,05, μ = 1 deu −1,17 p.p. na semente 2 (antes:
    +1,06 e +0,50). O ganho das sementes 0–1 não se manteve; o sinal varia por semente.
    Instabilidade 4,89 → 3,97 p.p.; P10 −1,4 p.p.
  - μ = 1 piora com α ≥ 0,5 nas 3 sementes (−0,62 a −1,03 p.p.).
  - R_τ: o FedProx nunca atinge τ antes do FedAvg. Com μ = 1, atinge depois em 14 de 14
    pares em que τ é atingido; com α = 0,05 e semente 2, ninguém atinge τ (censurada).
- Slides atualizados (slide 3 com as médias de 3 sementes e o texto novo sobre α = 0,05;
  slides 2 e 4 com 60/100) e PDF regenerado; conferido visualmente.
- Artigo: `tab:cenarios` (C1, C2), `tab:status` (60/100), parágrafo de situação (60/100,
  ~14 min) e próximos passos (sementes 3 e 4). Recompilado sem avisos (22 páginas).
- Nada commitado.
- **Parada às 17h (máquina será desligada).** Pedido do usuário: nenhuma execução nova
  depois das 17h; a que estiver rodando pode ir até 17h30, nunca além. Vigia
  `parada17h.sh` (no *scratchpad* da sessão), lançado às 13h58 com `setsid nohup`:
  às 17h00 encerra o `grid.py` (PID 41038), sem iniciar execuções novas, e deixa a
  corrente terminar (~13 min, então acaba por volta das 17h15). Às 17h30, se ainda
  houver processo da sessão do bloco A (run.py + Ray), envia SIGTERM e depois SIGKILL.
  Log em `~/parada17h.log`. Uma execução interrompida não grava o JSON e é refeita
  na próxima chamada de `grid.py --block A`. Previsão: ~73/100 às 17h, com a semente 3
  incompleta.
- **17h00–17h02: parada.** O vigia encerrou o `grid.py` às 17h00; a execução corrente
  (α = 1, FedProx μ = 0,01, semente 3) terminou às 17h02 e gravou o resultado. Nada foi
  morto à força. **Bloco A: 74/100**, sementes 0–2 completas e 14 de 20 da semente 3.
  Faltam 26: α = 1 com μ = 0,1 e μ = 1, e α = 100 inteiro, na semente 3, mais a semente 4
  inteira. Para retomar nesta máquina: `cd experimentos && ../.venv/bin/python grid.py
  --block A` (pula as 74 prontas). A semente 3 precisa terminar nesta máquina, porque os
  pares não podem ser divididos entre máquinas.
- Encerramento do dia, autorizado pelo usuário: `analysis.py` rodado de novo
  (`blocoA_resumo.json` com 74 execuções; τ = 76,16 % segue das sementes 0–2, porque a
  semente 3 ainda não tem α = 100). Artigo atualizado para 74/100 (`tab:cenarios`,
  `tab:status`, parágrafo de situação, próximos passos) e recompilado sem avisos.
  Slides mantidos como apresentados (sementes 0–2, 60/100). Commits e push de todo o
  trabalho do dia: resultados, artigo, slides e este registro.
- **Push.** A primeira tentativa falhou: a conta `augustolr06` não tinha escrita em
  `el-yawd/seminar-iv`. Depois que o Diego deu a permissão, o push de `main` foi feito
  (`9930a6d..d9a4e72`, 4 commits). Esta entrada fica para o próximo commit.

## 24/11, noite: conclusão do bloco A e passagem para outra máquina

- **20h11: bloco A retomado** (`setsid nohup systemd-inhibit ... grid.py --block A >> ~/blocoA.log`,
  PID 15925), sem limite de horário: o usuário deixa a máquina ligada o tempo necessário.
  Faltavam 26 execuções (~14 min cada); previsão de término por volta das 2h30 de 25/11.
- **`analysis.py`** passa a tomar as decisões da Metodologia que dependem do bloco A:
  μ* (o μ com maior acurácia média do FedProx, só com (α, semente) que têm os três μ, para
  nenhum μ ganhar por ter mais execuções prontas), H2 descritivo (posto médio dos μ em cada α
  e IC de Δ com μ = 1 e α = 100) e a regra de censura (T = 200 se menos da metade das
  execuções com α ≤ 0,1 atingir τ). Também passa a filtrar por sementes (`--seeds`, padrão
  0-4) e estratégias: os blocos A e D têm o mesmo padrão de nome de arquivo, e sem o filtro
  o bloco D entraria no resumo do A. Prévia com 74 execuções: μ* = 0,01, só 0,016 p.p. acima
  de μ = 0,1 (empate prático).
- **`experimentos/README.md`** (novo): situação dos blocos, regra de sementes inteiras por
  máquina, ambiente, teste de sanidade, comandos e o que falta implementar. É o ponto de
  partida para continuar em outra máquina.
- Encadear o bloco B depois do A foi bloqueado pelo sistema de permissões (não tinha sido
  pedido); ficou como pergunta ao usuário.
- **Decisão do usuário e do Diego: o bloco B roda na máquina do Diego e o C nesta.** Como o
  B é comparado ao FedAvg das sementes 0–2, que rodou aqui, a outra máquina refaz esse FedAvg.
  Para isso: `run.py` e `grid.py` ganham `--out` (pasta dos resultados; padrão `results`),
  `analysis.py` ganha `--results`, e o bloco B do `grid.py` passa a incluir o FedAvg, que é
  pulado quando já existe na pasta de saída. Na máquina do Diego:
  `grid.py --block B --out results/blocoB` (45 execuções). O padrão não muda nada aqui.
  O `run.py` foi trocado com o bloco A rodando: testado antes numa cópia (o caminho de
  `[skip]` e uma pasta alternativa), depois trocado de uma vez com `mv`. As execuções
  seguintes do A só ganham o campo `out` em `args` no JSON.
- Partições do bloco C verificadas para as sementes 5–14: a patológica dá 600 amostras e
  2 classes por cliente; a de quantidade dá de 5 a 5051 amostras e de 4 a 10 classes por
  cliente. Todas as amostras são usadas uma vez e nenhum cliente fica sem teste local.
- **Bloco C encadeado** (`encadeia_C.sh` no *scratchpad*, `setsid nohup`): espera o PID 15925
  sair; se houver 100 execuções do A e nenhuma falha, roda o `analysis.py` (saída em
  `~/blocoA_analise.txt`), lê o `mu_star` de `blocoA_resumo.json` e inicia
  `grid.py --block C --mu-star <mu*>` com `systemd-inhibit` (log em `~/blocoC.log`). Se o A
  ficar incompleto, o C não é iniciado. O bloco D ainda não foi atribuído a nenhuma máquina.
- **Falha e conclusão do bloco A.** Uma execução falhou na rodada 40 (α = 0,1, μ = 0,01,
  semente 4, por volta das 22h33): o link do cabo de rede (`enp2s0`) caiu e só voltou à
  0h13, e o Ray, que usa o IP da rede (10.0.1.7) para falar com os próprios atores, perdeu
  os 10 clientes da rodada ("Network is unreachable"). O `grid.py` registrou a falha e
  seguiu. À 1h37, com 99 execuções e 1 falha, o encadeamento cumpriu a checagem e **não**
  iniciou o C. A execução foi refeita (`encadeia_C2.sh`: `grid.py --block A`, que só
  roda a que falta, e depois as mesmas checagens) e terminou à 1h56. **Bloco A: 100/100.**
  O CSV parcial foi sobrescrito, porque o `RoundWriter` abre o arquivo com `"w"`.
- **Decisões (`blocoA_resumo.json`, 100 execuções, τ = 76,20 %):**
  - **μ\* = 0,01**: 78,994 %, contra 78,961 % com μ = 0,1 e 78,355 % com μ = 1. A margem é
    de 0,03 p.p., mas a regra foi aplicada como fixada. Como μ = 0,01 teve |Δ| ≤ 0,02 p.p.
    em todo α, os blocos C e D comparam o FedAvg com um FedProx sem efeito mensurável no
    bloco A, e H1 passa a depender sobretudo do TOST.
  - **H2, em parte**: o IC de Δ com μ = 1 e α = 100 é [−0,79; −0,66] p.p. (abaixo de zero).
    O melhor posto médio fica em {0,01; 0,1} em 4 de 5 α. Com α = 0,05, μ = 1 tem posto 1,8,
    contra 2,0 e 2,2, mas as médias dos três μ diferem em no máximo 0,18 p.p.
  - **T = 100 mantido**: 80 % das execuções com α ≤ 0,1 atingem τ (3/5 sementes com
    α = 0,05; 5/5 com α = 0,1).
- **Bloco C iniciado à 1h56 de 25/11** com `--mu-star 0.01` (PID do `grid.py` 154365; log em
  `~/blocoC.log`). São 40 execuções, previsão de término por volta das 11h30.
- Artigo: nova Seção 5.8 (bloco A, com `tab:blocoA`, as médias de 5 sementes e as três
  decisões). Também atualizados `tab:cenarios` (C1–C3), o parágrafo de situação, `tab:status`
  (25/11) e os próximos passos. Recompilado: 23 páginas, sem *overfull*. README com o μ\*.
- **Bloco C, primeira passada (1h56–6h06): 19/40, com 21 falhas.**
  - **20 falhas eram um bug na partição patológica.** Todas falharam na rodada 1 com
    `IndexError: arrays used as indices must be of integer (or boolean) type`. Na patológica,
    todos os clientes têm o mesmo tamanho (600 amostras, 480 de treino), e
    `np.array(tr, dtype=object)` no `run.py` vira uma matriz 2-D de objetos. A linha que o
    cliente lê tem dtype `object` e não serve de índice. Na Dirichlet e na de quantidade, os
    tamanhos diferem e isso não acontece.
  - **Correção:** `client.py` converte os índices para `int64`. Testado com 3 rodadas da
    patológica (roda) e de uma configuração do bloco A (α = 0,1, μ = 0,01, semente 4), que deu
    acurácia e perda iguais bit a bit às 3 primeiras rodadas do CSV gravado, ou seja, os
    resultados existentes não mudam. A verificação das partições feita ontem só conferiu os
    índices, e não a passagem pelo `np.savez`, por isso o bug não apareceu antes.
  - **1 falha foi de rede.** A execução da quantidade com μ = 0,01 e semente 10 caiu na
    rodada 50: o cabo caiu de novo às 4h22 (link down/up três vezes em 1 min). Tentei fazer o
    Ray usar só 127.0.0.1 (`init_args._node_ip_address`), mas o Ray troca o endereço local
    pelo IP da rede de propósito (`resolve_ip_for_localhost`). Desfeito.
  - **Mitigação:** `blocoC_retoma.sh` (*scratchpad*) chama `grid.py --block C --mu-star 0.01`
    até 3 vezes, enquanto faltar alguma das 40. Relançado às 6h09 com 21 execuções a fazer.
- **Bloco C concluído às 11h14 de 25/11: 40/40.** A segunda tentativa começou às 10h59 com
  39/40. Faltava a execução patológica com FedProx e semente 9, que caiu na rodada 78 por
  outra queda do cabo (link down às 7h46 e várias vezes entre 8h07 e 8h24). Todas as 40 têm
  100 rodadas com 10 clientes e `host` = `vostro-15-3515`.
- **Verificação das execuções feitas durante as quedas de rede** (pedido do usuário): uma
  execução que termina recebeu todos os clientes em todas as rodadas, porque o `aggregate_fit`
  aborta se houver qualquer falha. Os 123 CSVs completos têm 10 clientes por rodada. Refeitas
  3 rodadas de duas execuções do A que rodaram com o cabo desconectado (α = 0,1, μ = 0,1, e
  α = 1, FedAvg, semente 4): acurácia, perda e clientes iguais bit a bit. Primeiro a
  comparação acusou diferença, mas era o NaN da coluna `pids` na rodada 0 (NaN ≠ NaN); com
  `DataFrame.equals`, iguais.
- **Prévia descritiva do bloco C** (não está no artigo; o `analysis.py` ainda não lê o C):
  - patológica: FedAvg 72,34 %, FedProx 72,34 %, Δ médio 0,00 p.p., de −0,03 a +0,04
    (4 de 10 sementes positivas);
  - quantidade: FedAvg 86,62 %, FedProx 86,59 %, Δ médio −0,03 p.p., de −0,06 a 0,00
    (0 de 10 positivas).
  - Com μ* = 0,01, como esperado pelo bloco A, o FedProx fica praticamente igual ao FedAvg
    nos dois tipos de heterogeneidade.
- Artigo (C3, `tab:status`, situação, próximos passos) e README atualizados: C concluído,
  análise pendente.
- **Bloco B recebido do Diego** (`893db42`, 8h17 de 25/11): 30 execuções em `results/`, mas
  sem o FedAvg das sementes 0–2 refeito na máquina dele e sem `env.host` nos JSON, o que
  indica código anterior a 23/11. O meu commit do bloco C foi rebaseado sobre o dele
  (`--autostash`, para preservar as remoções do usuário, que continuam fora dos commits) e
  enviado (`99de7c5`). A comparação do B com o FedAvg entre máquinas ficou como pergunta
  para o Diego.
- **Bloco D iniciado às 17h41 de 25/11 nesta máquina**, a pedido do usuário:
  `blocoD.sh` (*scratchpad*) chama `grid.py --block D --mu-star 0.01` até 3 vezes. São 100
  execuções nas sementes 5–14, com log em `~/blocoD.log` e previsão de ~22 h, até por volta
  das 16h de 26/11.
- **Bloco B, opção 2** (decisão do usuário e do Diego): o Diego refaz na máquina dele o FedAvg
  das sementes 0–2 (15 execuções) com `--out results/blocoB`. Para adiantar, as 30 execuções
  dele foram movidas aqui para `results/blocoB/` (`git mv`), e o `grid.py --block B --out
  results/blocoB` pula essas 30. O código de 18/11 que ele usou difere do atual só nos
  metadados (`host`, `cpu_model`), no `--out` e no índice `int64` da patológica, sem efeito no
  cálculo da Dirichlet, então as 30 continuam válidas. O pareamento do B deve ser feito por
  pasta, porque as 30 não têm `env.host`.
- **Bloco D: 3 falhas por falta de memória** entre 17h41 e ~18h10
  (`ray.exceptions.OutOfMemoryError`; o Ray mata atores acima de 95 % da RAM). Cada execução
  ocupa ~6 GB (8 atores de ~670 MB, mais o processo principal) dos 13 GiB da máquina, e havia
  outros programas abertos. As três (semente 5: α = 0,05 com os dois algoritmos e α = 0,1 com
  o FedAvg) não gravaram JSON e serão refeitas na 2ª tentativa do `blocoD.sh`. Desde ~18h10,
  sem falhas.
- **Bloco D: 4ª falha por falta de memória** por volta das 11h de 26/11 (FedAvg, α = 1,
  semente 13, rodada 35), com ~1 GB livre por causa de VS Code, navegador, Slack e Claude
  Desktop abertos. O usuário fechou os programas (a memória disponível voltou a ~5,9 GB) e
  não houve outras falhas. O processo que esperava o fim do bloco foi encerrado pelo Claude
  Code nessa hora, também por falta de memória, e foi reiniciado a pedido do usuário; o
  `blocoD.sh` não foi afetado.

## 26/11 — bloco D concluído (100/100); integração dos commits do Diego

- **Bloco D concluído às 14h47 de 26/11**: 96 execuções na 1ª tentativa e as 4 que
  falharam por memória na 2ª (13h52–14h47). As 100 foram conferidas: todas com JSON e CSV,
  100 rodadas, 10 clientes por rodada e `env.host = vostro-15-3515`. Média de 12,4 min por
  execução.
- **Prévia descritiva** (FedProx μ = 0,01 − FedAvg na mesma semente, sementes 5–14; IC por
  *bootstrap*; ainda não é o teste confirmatório de H1):

  | α | FedAvg (%) | FedProx (%) | Δ (p.p.) | IC 95 % | Δ P10 (p.p.) | sementes com Δ > 0 |
  |---|---:|---:|---:|---|---:|---:|
  | 0,05 | 70,07 | 70,09 | +0,02 | [−0,01; +0,06] | +0,60 | 7/10 |
  | 0,1 | 73,00 | 72,99 | −0,01 | [−0,03; +0,02] | −0,15 | 5/10 |
  | 0,5 | 81,31 | 81,31 | 0,00 | [−0,01; +0,02] | +0,09 | 4/10 |
  | 1 | 83,15 | 83,14 | −0,01 | [−0,02; +0,01] | −0,11 | 3/10 |
  | 100 | 84,34 | 84,33 | −0,01 | [−0,03; 0,00] | −0,16 | 4/10 |

  Como no bloco A, com μ* = 0,01 o FedProx fica a menos de 0,1 p.p. do FedAvg em todos os α,
  muito dentro da margem de equivalência de 1 p.p.
- **Commits do Diego integrados** (`83d9008`, `e2a4d88`, `faf512c`, de 25/11 à noite):
  FedAvg das sementes 0–2 refeito no i5 em `results/blocoB/`, `analysis_bc.py` (blocos B e
  C), seção Proposta e segunda versão do Desenvolvimento. Como ele reescreveu o
  Desenvolvimento, a minha edição local do status do D foi descartada e refeita sobre a
  versão dele (avanço rápido, sem conflito).
- Artigo atualizado: resumo da seção, C1, tempo do bloco D, linha "Memória no bloco D" dos
  ajustes (quatro falhas; bloco completo), OE4, `tab:status` (26/11; "D concluído, análise
  pendente") e próximos passos. Compila com 29 páginas, sem *overfull*. README: D concluído.
