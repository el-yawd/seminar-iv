# Experimentos: FedAvg × FedProx sob heterogeneidade

Simulação com Flower + PyTorch: 100 clientes, 10 por rodada, sementes pareadas (na mesma
semente, todos os algoritmos têm a mesma partição, a mesma inicialização e os mesmos clientes
sorteados). O desenho está no capítulo de Metodologia (`elemtextuais/4-Metodologia.tex`);
o andamento, no de Desenvolvimento (`elemtextuais/5-Desenvolvimento.tex`).

## Situação dos blocos

| Bloco | O que é | Execuções | Situação | Máquina |
|---|---|---:|---|---|
| piloto | F-MNIST, semente 0, T = 20, sanidade μ = 0 | 10 | concluído | i5-1235U |
| G | gate da reformulação α × E (negativo, E = 2 mantido) | 18 | concluído | i5-1235U |
| A (F-MNIST) | (FedAvg + μ ∈ {0,01; 0,1; 1}) × 5 α × sementes 0–4 | 100 | concluído | `vostro-15-3515` |
| B (F-MNIST) | FedAvgM, FedAdam × 5 α × sementes 0–2 (SCAFFOLD não integrado) | 30 (+15 FedAvg) | a executar | máquina do Diego, em `results/blocoB/` |
| C (F-MNIST) | (FedAvg, FedProx μ*) × patológica/quantidade × sementes 5–14 | 40 | em execução desde 25/11 | `vostro-15-3515` |
| D (F-MNIST) | (FedAvg, FedProx μ*) × 5 α × sementes 5–14 | 100 | a executar | a definir (sementes inteiras por máquina) |
| A–D (CIFAR-10) | os mesmos blocos com `--dataset cifar10` | 270 | a executar | Kaggle (T4) |
| microbench | custo do termo proximal, CPU de 1 *thread*, 30 repetições (H4) | — | `microbench.py` ainda não existe | i5-1235U |

**μ\* do F-MNIST = 0.01** (regra da Metodologia: o μ com maior acurácia média do FedProx
no bloco A). Foi 78,99 %, contra 78,96 % com μ = 0,1 e 78,35 % com μ = 1: empate prático com 0,1,
mas a regra foi aplicada como definida. Ver `results/blocoA_resumo.json` (`mu_star`, `mu_mean_acc`).

Os blocos `A2`, `D2` e `cifar` do `grid.py` são da reformulação descartada (`docs/plano-reformulacao.md`)
e não devem ser usados.

## Regra obrigatória: sementes inteiras por máquina

Os resultados **não são bit a bit iguais entre máquinas**: até 0,13 p.p. na mesma configuração
(Intel i5-1235U com Python 3.12 × AMD Ryzen 7 3700U com Python 3.13). Isso é da ordem das
diferenças que se quer medir. Na mesma máquina, a execução é determinística (FedProx com μ = 0
reproduz o FedAvg bit a bit). Portanto:

- todas as execuções de uma mesma semente (FedAvg e as variantes que serão comparadas com ele)
  rodam na **mesma máquina**;
- para dividir um bloco entre máquinas, use `--shard i/n`, que divide **por semente**;
- cada JSON registra a máquina (`env.host`, `env.cpu_model`), e o `analysis.py` só pareia
  execuções do mesmo `host`.

Consequência para o bloco B: ele é comparado ao FedAvg das sementes 0–2, e o do bloco A rodou na
`vostro-15-3515`. Como o B roda em outra máquina, ela refaz também esse FedAvg (15 execuções),
numa pasta separada para não sobrescrever o do bloco A:

```bash
../.venv/bin/python grid.py --block B --out results/blocoB   # 45 execuções: FedAvg, FedAvgM, FedAdam
```

Na pasta padrão (`results/`), o mesmo comando pula o FedAvg, que já existe, e roda só as 30 do B.
Os blocos C e D usam sementes novas (5–14) e podem rodar em qualquer máquina, desde que cada
semente fique inteira em uma só.

## Ambiente

Python 3.12 ou 3.13.

```bash
python3 -m venv .venv
.venv/bin/pip install -r experimentos/requirements-cpu.txt --extra-index-url https://download.pytorch.org/whl/cpu
# GPU (Kaggle/Colab): pip install -r experimentos/requirements-gpu.txt
```

O dataset é baixado na primeira execução para `experimentos/data/` (fora do Git). Antes de
rodar um bloco numa máquina nova, vale repetir o teste de sanidade, que precisa dar resultado
bit a bit igual entre as duas execuções:

```bash
cd experimentos
../.venv/bin/python run.py --alpha 100 --strategy fedavg --seed 0 --rounds 20 --force
../.venv/bin/python run.py --alpha 100 --strategy fedprox --mu 0 --seed 0 --rounds 20 --force
# compare as colunas acc, loss e pids dos dois CSV em results/; depois: git checkout -- results/
```

## Como rodar

```bash
cd experimentos
../.venv/bin/python grid.py --block A                          # retomável: pula o que já tem JSON
../.venv/bin/python grid.py --block D --mu-star 0.01         # blocos C e D usam o mu*
../.venv/bin/python grid.py --block D --mu-star 0.01 --shard 0/2   # sementes 5, 7, 9, 11, 13
../.venv/bin/python grid.py --block A --dataset cifar10        # CIFAR-10
../.venv/bin/python run.py --help                              # uma execução isolada
```

Execuções longas: rode desacoplado do terminal e sem suspender a máquina, por exemplo
`setsid nohup systemd-inhibit --what=sleep:idle ../.venv/bin/python grid.py --block D --mu-star 0.01 >> ~/blocoD.log 2>&1 &`.
Uma execução interrompida não grava o JSON e é refeita na próxima chamada.

Tempo por execução (F-MNIST, T = 100, E = 2): ~14 min no Ryzen 7 3700U; o i5-1235U é ~1,45×
mais rápido. Tempo na T4 ainda não medido: `kaggle.ipynb` faz a sanidade na GPU e mede uma
execução.

## Resultados e análise

Cada execução grava, em `results/`, `<chave>.csv` (uma linha por rodada: acurácia, perda,
tempos, bytes, clientes sorteados) e `<chave>.json` (argumentos, métricas finais, acurácia local
por cliente, ambiente). A chave tem a forma
`fmnist_dirichlet_a0.1_fedprox_mu0.1_E2_s3_T100`.

```bash
../.venv/bin/python analysis.py                      # bloco A do F-MNIST → results/blocoA_resumo.json
../.venv/bin/python analysis.py --dataset cifar10 --name blocoA_cifar10
```

O `analysis.py` calcula as métricas da Metodologia (acurácia das últimas 5 rodadas,
instabilidade, P10 e DP locais, R_τ com censura), as diferenças pareadas com IC por *bootstrap*,
o μ*, a avaliação descritiva de H2 e a regra de ampliar T. A opção `--results` lê outra pasta
(por exemplo, `results/blocoB`). **Falta implementar:** a leitura dos
blocos B, C e D (partições patológica e de quantidade) e os testes confirmatórios (Wilcoxon com
Holm sobre os 5 α, TOST com δ = 1 p.p.), além das figuras.

Os demais scripts: `gate.py` (avaliação do bloco G), `analysis_piloto.py` e `fill_tables.py`
(piloto), `partition_stats.py` e `min_size_check.py` (verificação das partições).
