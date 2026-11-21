# Plano de reformulação: heterogeneidade × trabalho local

Plano de implementação para reformular a pergunta de pesquisa após o piloto de 18/11/2026.

> **Situação em 21/11/2026: gate negativo, plano original mantido (E = 2).** Ver a seção 5.1.
> As seções 2, 3, 6 e 7 deixam de valer; os blocos `A2`, `D2` e `cifar` do
> `grid.py` ficam no código, mas não serão executados.

Prazo final da entrega: 15/12/2026. Situação de partida: commit `3e0d3ce`.

---

## 1. Por que reformular

### 1.1 O que o piloto mostrou

No piloto (Fashion-MNIST, semente 0, T = 20, E = 2), o FedProx com μ ∈ {0,01; 0,1} ficou a no
máximo 0,1 p.p. do FedAvg **tanto com α = 0,1 quanto com α = 100**. Só μ = 1 mudou algo.

A explicação mais provável é o pouco trabalho local da configuração fixa: com E = 2, lotes de 32
e η = 0,01, o cliente mediano dá cerca de 20 passos de SGD por rodada com α = 0,1 e 30 com
α = 100. O modelo local se afasta pouco de w^t, e o termo proximal, proporcional a
‖w − w^t‖², quase não atua.

### 1.2 Consequência para a pesquisa

O *client drift* que o FedProx corrige depende de **dois** fatores:

1. **Heterogeneidade** (α): quanto os objetivos locais divergem.
2. **Trabalho local** (épocas E × passos por época): quanto cada cliente caminha em direção ao
   próprio ótimo antes de agregar.

O plano atual varia só o primeiro e fixa o segundo em um valor baixo (E = 2). Assim, o resultado
mais provável seria "FedProx ≈ FedAvg em todos os α", que é válido, mas estreito e dependente
de uma escolha arbitrária de E.

Os estudos da literatura que se contradizem usam valores de E diferentes, e a maioria não os
controla. **Variar α e E em conjunto pode explicar a contradição, em vez de acrescentar mais
um ponto a ela.** Esse é o ganho de valor científico.

### 1.3 Por que não testar mais algoritmos

Incluir FedNova, FedDyn, MOON etc. transformaria o trabalho em um NIID-Bench menor: mais
implementação, mais GPU e um resultado do tipo "ranking", que é justamente o que a literatura
já tem e não consegue conciliar. Os algoritmos de referência (bloco B) saem do escopo principal.

### 1.4 Novidade, com honestidade

Li et al. (2020) já avaliaram o FedProx com até 20 épocas, e o FedNova (Wang et al., 2020) trata
a inconsistência causada por números diferentes de passos locais. A ideia de que "trabalho local
importa" não é nova. O que este trabalho acrescenta é:

- um **mapa sistemático α × E × μ**, com sementes pareadas;
- **testes de equivalência** (TOST) para afirmar onde o FedProx *não* faz diferença;
- efeito medido **na cauda** (pior decil de clientes), e não só na média;
- **custo total até o alvo** (C_τ) em função de E, relevante para dispositivos de borda.

---

## 2. Nova pergunta e hipóteses

**QP1 (nova).** Como a heterogeneidade dos dados (α) e o trabalho local por rodada (E) determinam,
em conjunto, quando o FedProx supera, empata ou perde para o FedAvg, na acurácia média e nos
clientes mais mal atendidos?

**QP2 (mantida, ampliada).** O custo local adicional do termo proximal é compensado pela redução
de rodadas até a acurácia-alvo, e como esse balanço muda com E?

| Hip. | Enunciado | Teste |
|---|---|---|
| H1 (interação) | O ganho Δ do FedProx(μ*) sobre o FedAvg cresce com E quando α é baixo. Com E = 2, Δ é equivalente a zero (±1 p.p.) em todos os α. | Wilcoxon pareado + Holm nas células (α, E); TOST com δ = 1 p.p. |
| H2 (μ) | O μ que maximiza o ganho cresce com E. μ = 1 prejudica a acurácia quase IID (α = 100) em qualquer E. | Descritivo (bloco A'): μ* por E com IC 95% (bootstrap) |
| H3 (cauda) | Com α = 0,1, o ganho do FedProx no P10 da acurácia local é maior que o ganho na acurácia global. | Wilcoxon pareado sobre (ΔP10 − Δacc) |
| H4 (custo) | O tempo por época do FedProx é < 1,10 × o do FedAvg. Com E alto e α baixo, o FedProx atinge τ em menos rodadas, e C_τ é menor. | Mann-Whitney (n = 30); razão das medianas; C_τ em pares não censurados |

A antiga H3 (tipo de heterogeneidade) vira extensão: as partições patológica e de quantidade já
estão implementadas e só são executadas se sobrar orçamento (seção 7).

---

## 3. Desenho experimental

### 3.1 Fatores

| Fator | Antes | Depois |
|---|---|---|
| E (épocas locais) | fixo em 2 | **{2; 5; 10}** |
| α (Dirichlet) | {0,05; 0,1; 0,5; 1; 100} | **{0,1; 1; 100}** (três regimes bem separados no piloto) |
| μ | {0,01; 0,1; 1} | igual |
| Algoritmos | FedAvg, FedProx, FedAvgM, FedAdam, SCAFFOLD | **FedAvg, FedProx** |
| T (rodadas) | 100 | **100 para E = 2; 50 para E ≥ 5** |
| Datasets | F-MNIST e CIFAR-10 completos | **F-MNIST completo; CIFAR-10 só confirmatório** |

E = 1 não entra porque, se E = 2 já não produz efeito, E = 1 não acrescenta informação.

T = 50 para E ≥ 5 é aceitável porque mais trabalho local converge em menos rodadas, e as
comparações de acurácia são sempre *dentro* da mesma célula (α, E). Entre valores de E, a
comparação usa R_τ e C_τ, que não dependem de T, desde que o alvo seja atingido.

### 3.2 Blocos

| Bloco | Composição | Execuções | Finalidade |
|---|---|---:|---|
| **G** (gate) | (FedAvg, FedProx μ = 0,1) × α = 0,1 × E ∈ {2; 5; 10} × sementes 0–2, T = 50 | 18 | Decide se a reformulação vale a pena (seção 5) |
| **A'** (exploratório) | (FedAvg + 3 μ) × 3 α × 3 E × sementes 0–2 | 108 | Mapa α × E × μ; escolha de μ* |
| **D'** (confirmatório) | (FedAvg, FedProx μ*) × α ∈ {0,1; 100} × E ∈ {2; 10} × sementes 5–14 | 80 | Testes de H1 e H3 com n = 10 |
| **CIFAR** (condicional) | (FedAvg, FedProx μ*) × α = 0,1 × E ∈ {2; 10} × sementes 5–14 | 40 | Validade externa da célula principal |
| **C4** (custo) | μ ∈ {0; 0,1} × 2 modelos × 30 repetições, 1 thread | – | H4 |

As 18 execuções do bloco G reaproveitam as sementes 0–2. As execuções de G com α = 0,1 e
μ = 0,1 coincidem com células do bloco A' e são reaproveitadas automaticamente pela chave única
(com T = 50; para E = 2 em A', roda-se com T = 100 à parte).

### 3.3 Orçamento estimado (CPU local, a partir dos tempos do piloto)

Modelo de custo por rodada, ajustado no piloto: t_rodada ≈ c + E × t_época,máx, com c ≈ 2,2 s e
t_época,máx ≈ 1,7 s para α = 0,1, e c ≈ 1,5 s e t_época,máx ≈ 1,0 s para α = 100. Há ainda cerca
de 90 s fixos por execução.

| (α, E) | s/rodada | T | min/execução |
|---|---:|---:|---:|
| 0,1, E = 2 | 5,6 | 100 | ~11 |
| 0,1, E = 10 | ~19 | 50 | ~17 |
| 100, E = 2 | 3,4 | 100 | ~7 |
| 100, E = 10 | ~11 | 50 | ~11 |

| Bloco | Execuções | Horas de CPU (estimativa) |
|---|---:|---:|
| G | 18 | ~3 |
| A' | 108 | ~19 |
| D' | 80 | ~15 |
| CIFAR | 40 | a medir |
| **Total F-MNIST** | 206 | **~37** |

É viável em cerca de duas semanas se o laptop rodar à noite e o Kaggle rodar em paralelo. Se a
T4 for de 3 a 5 vezes mais rápida, o orçamento cabe com folga. **Medir isso é o primeiro passo.**

---

## 4. Implementação: mudanças no código

Ordem sugerida. Todas as mudanças são pequenas; a estrutura do protótipo não muda.

### 4.1 Correções obrigatórias (antes de qualquer execução nova)

1. **`run.py` → `key_of`: incluir E na chave.** Hoje a chave não tem `epochs`, então execuções com
   E diferentes **sobrescreveriam umas às outras** (ou seriam puladas como "já feitas").
   - Adicionar `_E{a.epochs}` à chave.
   - Migrar os 10 resultados do piloto (renomear `*_s0_T20.*` → `*_E2_s0_T20.*`) e atualizar
     `k()` em `analysis_piloto.py`.
2. **Determinismo na GPU.** O texto da Metodologia diz que `cudnn.benchmark = False` e
   `CUBLAS_WORKSPACE_CONFIG` estão definidos, mas o código não os define. Com
   `torch.use_deterministic_algorithms(True)` em CUDA, a falta de `CUBLAS_WORKSPACE_CONFIG`
   gera erro. Em `client.py`, antes de importar o torch:
   `os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")` e
   `torch.backends.cudnn.benchmark = False`.
3. **`run.py`: GPU no Ray.** `num_gpus` está fixo em 0,0. Usar `0.1` quando
   `torch.cuda.is_available()` e o servidor também na GPU para a avaliação.
4. **Dependências.** `requirements.txt` fixa `torch==2.15.0+cpu`, que não serve no Kaggle.
   - Separar `requirements-cpu.txt` e `requirements-gpu.txt`, ou fixar só a versão e instalar
     pelo índice certo em cada ambiente.
   - Adicionar `scipy`, que ainda não está instalado e é necessário para os testes.

### 4.2 Novas funcionalidades

5. **`grid.py`: novos blocos** `G`, `A2`, `D2`, `cifar`, com a regra `rounds = 100 if E <= 2 else 50`.
   Opção `--shard i/n` para dividir um bloco entre máquinas (por exemplo, `--shard 0/2` no laptop
   e `--shard 1/2` no Kaggle). As chaves já evitam duplicação.
6. **Redução do custo fixo, opcional mas barata.** Cada ator do Ray recarrega e normaliza o dataset
   na primeira rodada (26 a 32 s por execução). **Implementado:** o treino normalizado fica em
   cache `.npy`, aberto com `mmap_mode="r"`. Medido: a rodada 1 caiu de 27,8 s para 23,3 s, com
   resultados idênticos. O restante é a inicialização dos atores do Ray, que não depende dos
   dados. Ganho de ~20 min no total; reaproveitar a sessão do Ray entre configurações ficaria
   para depois.
7. **`kaggle.ipynb`.** Clonar o repositório, instalar as dependências de GPU, rodar
   `grid.py --block X --shard i/n` e compactar `results/` como saída do notebook. Os resultados
   voltam ao repositório por download e commit.
8. **`analysis.py`** (substitui `analysis_piloto.py` para os blocos):
   - consolida os CSV/JSON em um DataFrame (chave → fatores);
   - calcula as métricas: acc final (média das últimas 5 rodadas), instabilidade (DP das últimas
     20), R_τ com censura, P10 e DP local, C_τ = C · R_τ · E · t̄_e;
   - calcula os testes: Δ pareado por semente, IC 95% por *bootstrap*, Wilcoxon bilateral + Holm
     sobre as células, TOST (IC 90% dentro de ±δ) e o teste de H3 sobre (ΔP10 − Δacc);
   - gera as figuras: (i) mapa de calor de Δ em α × E para cada μ (figura principal);
     (ii) curvas por célula; (iii) Δacc × ΔP10; (iv) C_τ por E.
9. **`microbench.py`** (C4): 1 thread (`torch.set_num_threads(1)`), cliente de tamanho mediano,
   30 repetições de 1 época para μ ∈ {0; 0,1} nos dois modelos, com `perf_counter` e
   `resource.getrusage(...).ru_maxrss`; grava um CSV. É independente de E, porque mede o tempo
   por época.

### 4.3 Verificações antes de lançar a grade

- Repetir o **teste de sanidade na GPU** (FedAvg × FedProx μ = 0, α = 0,1, T = 20) no Kaggle. Se
  não for idêntico, os blocos pareados rodam só em CPU ou adota-se uma tolerância documentada.
- **Medir o tempo** de uma execução com α = 0,1, E = 10 e T = 50 na T4, e recalcular o orçamento
  da seção 3.3.

---

## 5. Ponto de decisão (gate) após o bloco G

O bloco G (cerca de 3 h de CPU) decide se a reformulação entra no trabalho.

**Critério para reformular:** com α = 0,1, a média de Δacc (FedProx μ = 0,1 − FedAvg) em
E = 10 supera a de E = 2 em pelo menos 1 p.p. em 2 das 3 sementes, **ou** ΔP10 em E = 10 supera
o de E = 2 em pelo menos 3 p.p. em 2 das 3 sementes.

- **Se o critério for atendido:** segue este plano (seções 3, 4 e 6).
- **Se não for:** mantém o plano original (bloco A com E = 2) e registra o resultado de G como
  evidência de que, *nesta configuração*, o trabalho local não altera o efeito do FedProx. É um
  parágrafo de discussão e uma limitação, sem retrabalho.

Os dois caminhos usam o mesmo código; só muda a lista de blocos.

### 5.1 Resultado (21/11/2026)

Bloco G concluído no laptop (18 execuções, ~2,2 h de CPU somadas; nenhuma falha). Avaliação com
`experimentos/gate.py`; resumo em `experimentos/results/gate_resumo.json`.

| Semente | Δacc(E10) − Δacc(E2) | ΔP10(E10) − ΔP10(E2) | Voto |
|---|---:|---:|---|
| 0 | −0,40 p.p. | +1,73 p.p. | não |
| 1 | −0,51 p.p. | −2,82 p.p. | não |
| 2 | −0,28 p.p. | −0,34 p.p. | não |

Médias das 3 sementes:

| E | Acc FedAvg | Acc FedProx | Δacc | P10 FedAvg | P10 FedProx | ΔP10 | Tempo/execução |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 69,0 | 69,1 | +0,12 | 31,3 | 30,5 | −0,80 | 4,8 min |
| 5 | 73,5 | 73,5 | −0,03 | 42,3 | 42,2 | −0,16 | 6,1 min |
| 10 | 77,1 | 76,9 | −0,27 | 48,6 | 47,4 | −1,28 | 11,0 min |

**Decisão: manter o plano original.** Δacc fica em [−0,45; +0,44] p.p. nas 9 células e é
levemente negativo em E = 10 nas 3 sementes. Mais trabalho local melhora os dois algoritmos por
igual (~+8 p.p. de acurácia e ~+17 p.p. de P10 de E = 2 para E = 10); com η = 0,01 o *drift* não
cresce o bastante para o termo proximal com μ = 0,1 atuar. Registrado em `5-Desenvolvimento.tex`
(seção "Verificação do efeito do trabalho local", `tab:gate`, linha nova em `tab:ajustes`) como
limitação de validade externa.

---

## 6. Mudanças nos documentos

O enunciado da atividade aceita "ajustes em relação ao planejamento original" quando
justificados. Aqui a justificativa é o piloto, e a mudança deve ser apresentada assim.

| Arquivo | Mudança |
|---|---|
| `1-Introducao.tex` | Problema: acrescentar o trabalho local como segunda dimensão do *drift*. Objetivo geral e OE3/OE4: incluir E; o OE3 passa a cobrir Dirichlet (tipos de desvio como extensão). Contribuição (i): mapa α × E × μ. |
| `4-Metodologia.tex` | QP1, H1–H4 (seção 2 deste plano); `tab:fatores`, `tab:blocos`, `tab:hipoteses`, orçamento; ameaças à validade: T diferente por E. Corrigir a frase sobre `CUBLAS_WORKSPACE_CONFIG` assim que o código a implementar (item 4.1.2). |
| `5-Desenvolvimento.tex` | Nova subseção "Reformulação após o piloto", com a evidência da seção 1.1 e o resultado do bloco G. Atualizar `tab:ajustes` e `tab:status`. |
| `6-Resultados.tex` | Trocar a tabela por α por uma tabela α × E; figura principal: mapa de calor de Δ. |
| `abstract.tex` | Uma frase sobre a nova pergunta. |
| `2-Referencial.tex` / `3-TrabalhosRelacionado.tex` | Citar FedNova (`wang2020fednova`, já no `.bib`) e destacar quais estudos do levantamento fixam ou variam E. Isso reforça a lacuna. |

---

## 7. Cronograma revisado

| Período | Atividade | Saída |
|---|---|---|
| 19–20 nov | Correções 4.1 (chave com E, GPU, dependências); bloco G no laptop (~3 h); notebook do Kaggle; sanidade e tempo na T4 | Resultado do gate; orçamento confirmado |
| 21 nov | **Decisão do gate** (seção 5) | Plano definitivo |
| 21–24 nov | Atualizar Introdução e Metodologia; iniciar A' dividido entre laptop e Kaggle; `analysis.py` (métricas) | A' em andamento |
| 25 nov–1 dez | Concluir A'; escolher μ*; iniciar D'; `microbench.py` e C4 | μ*; C4 concluído |
| 2–8 dez | Concluir D'; CIFAR (se houver orçamento); `analysis.py` (testes e figuras) | Tabelas e figuras finais |
| 9–15 dez | Resultados, conclusões, revisão e entrega | Trabalho final |

Folga: se A' atrasar, D' pode começar com μ* provisório (μ = 0,1) e ser confirmado depois, já que
só a escolha de μ* depende de A'.

---

## 8. Riscos e mitigação

| Risco | Probabilidade | Mitigação |
|---|---|---|
| T4 não é muito mais rápida que a CPU (o custo do Ray não depende do dispositivo) | média | Item 4.2.6 (mmap); dividir os blocos entre máquinas; cortar o CIFAR antes de cortar D' |
| Gate negativo | média | Plano original intacto (seção 5) |
| Não determinismo na GPU | baixa a média | Rodar pares em CPU ou documentar a tolerância |
| Cota do Kaggle (≈ 30 h/semana; sessões de até 12 h) | média | Execução retomável; *shards* pequenos |
| E = 10 com α = 0,1 diverge ou fica instável com η = 0,01 | baixa | Seria um resultado em si (instabilidade); reportar, sem mudar η |
| Pouco tempo para a escrita | média | Escrever Metodologia e Desenvolvimento enquanto A' roda; `analysis.py` gera as tabelas LaTeX diretamente |
| Sobreposição com Li et al. (2020) e FedNova | certa | Posicionar explicitamente a contribuição (seção 1.4) |

---

## 9. Próximos passos imediatos

1. [x] `run.py`: chave com `_E{epochs}`; resultados do piloto migrados (`*_E2_s0_T20.*`).
2. [x] `client.py` e `run.py`: `CUBLAS_WORKSPACE_CONFIG`, `cudnn.benchmark = False` e `num_gpus` condicional (ainda não testado em GPU).
3. [x] `requirements-cpu.txt` e `requirements-gpu.txt`, com `scipy`.
4. [x] `grid.py`: blocos `G` (18), `A2` (108), `D2` (80), `cifar` (40); regra de T; `--shard i/n`; `--mu-star`.
5. [x] Bloco G concluído no laptop (interrompido em 18/11, retomado e concluído em 21/11); avaliado com `experimentos/gate.py`.
6. [ ] `kaggle.ipynb`; sanidade na GPU; tempo de uma execução do bloco A (E = 2, T = 100) na T4.
7. [x] Decisão do gate (negativa: manter o plano original) e atualização dos documentos.
