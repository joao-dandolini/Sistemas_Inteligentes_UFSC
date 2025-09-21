# 8-Puzzle Solver com Algoritmo A*

Este projeto implementa um solucionador para o problema do 8-puzzle utilizando o algoritmo de busca A* com diferentes heurísticas. Desenvolvido como trabalho acadêmico para a disciplina de Sistemas Inteligentes da UFSC.

## 📋 Descrição do Problema

O 8-puzzle é um quebra-cabeça deslizante que consiste em um tabuleiro 3x3 com 8 peças numeradas (1-8) e um espaço vazio. O objetivo é reorganizar as peças para alcançar a configuração final:

```
1 2 3
4 5 6
7 8 _
```

## 🚀 Funcionalidades

- **4 Algoritmos de Busca Implementados:**
  1. **Custo Uniforme** - Busca sem heurística (h=0)
  2. **A* Não Admissível** - Heurística que superestima o custo
  3. **A* Peças Fora do Lugar** - Conta o número de peças mal posicionadas
  4. **A* Distância de Manhattan** - Soma das distâncias Manhattan de todas as peças

- **Três Níveis de Dificuldade:**
  - **Fácil:** `[[1, 2, 3], [4, 5, 6], [0, 7, 8]]`
  - **Médio:** `[[1, 3, 0], [4, 2, 5], [7, 8, 6]]`
  - **Difícil:** `[[8, 6, 7], [2, 5, 4], [3, 0, 1]]`

- **Visualização Opcional:** Acompanhe o algoritmo passo a passo
- **Análise Completa:** Métricas detalhadas de desempenho
- **Exportação JSON:** Dados completos da execução

## 📊 Saídas do Programa

### Console
- Sequência de movimentos da solução
- Total de nós expandidos (visitados)
- Tamanho do caminho (número de movimentos)
- Tempo de execução em segundos
- Maior tamanho da fronteira durante a busca

### Arquivo JSON
Arquivo detalhado contendo:
- **`caminho_solucao`**: Sequência completa de movimentos
- **`fronteira_no_final`**: Estados na lista de abertos no término
- **`nos_visitados`**: Todos os nós expandidos com custos g, h, f

## 🛠️ Como Executar

### Pré-requisitos
- Python 3.7 ou superior
- Bibliotecas padrão: `time`, `json`, `copy`, `heapq`

### Execução
```bash
python Trabalho_1.py
```

### Uso Interativo
1. Escolha o nível de dificuldade (facil/medio/dificil)
2. Selecione a heurística (1-4)
3. Opte por visualizar o passo a passo (s/n)
4. Aguarde a execução e análise dos resultados

## 📁 Estrutura de Arquivos

```
Trabalho1/
├── README.md
├── Trabalho_1/
│   ├── Trabalho_1.py                    # Código principal
│   └── resultado_busca_*.json           # Arquivos de saída gerados
└── Ligue_4/                            # Outros projetos
    ├── ligue_4.py
    └── ligue_4_eu.py
```

## 🧮 Algoritmos e Heurísticas

### 1. Custo Uniforme
```python
def h_uniform_cost(state, goal_state):
    return 0
```
Busca cega que garante a solução ótima, mas explora muitos nós.

### 2. A* Não Admissível
```python
def h_non_admissible(state, goal_state):
    return h_manhattan_distance(state, goal_state) * 3
```
Heurística que superestima o custo, resultando em busca mais rápida mas sem garantia de otimalidade.

### 3. A* Peças Fora do Lugar
```python
def h_misplaced_tiles(state, goal_state):
    # Conta peças fora da posição correta
```
Heurística admissível simples que conta o número de peças mal posicionadas.

### 4. A* Distância de Manhattan
```python
def h_manhattan_distance(state, goal_state):
    # Soma das distâncias Manhattan de todas as peças
```
Heurística admissível mais precisa, oferece o melhor equilíbrio entre otimalidade e eficiência.

## 📈 Exemplo de Saída

```
=============== RESUMO FINAL ===============
Total de nos expandidos (visitados): 3
Solucao encontrada com 2 movimentos.
Tempo de execucao: 0.0015 segundos
Maior tamanho da fronteira: 2
Dados completos da busca salvos em 'resultado_busca_facil_aestrela_distancia_de_manhattan.json'
```

## 🔍 Análise de Desempenho

O projeto permite comparar diferentes heurísticas em termos de:
- **Nós expandidos**: Eficiência computacional
- **Tamanho da fronteira**: Uso de memória
- **Tempo de execução**: Velocidade
- **Qualidade da solução**: Otimalidade do caminho encontrado

## 👥 Desenvolvimento

- **Disciplina:** Sistemas Inteligentes - UFSC
- **Implementação:** Algoritmo A* com múltiplas heurísticas
- **Linguagem:** Python 3
- **Estruturas:** Classes, heaps, dicionários para otimização

## 📝 Observações Técnicas

- Utiliza `copy.deepcopy()` para garantir integridade dos estados
- Implementa lista de abertos com `heapq` para eficiência
- Evita duplicatas na fronteira com verificação de g-score
- Gera nomes de arquivos seguros para compatibilidade Windows
- Serialização JSON customizada para objetos complexos

---

*Trabalho desenvolvido para demonstrar a aplicação prática de algoritmos de busca informada em problemas de otimização combinatória.*