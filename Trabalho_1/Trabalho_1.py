# Python 3
import time
import json
import heapq
from typing import List, Tuple, Dict, Any, Optional

GOAL_STATE_LIST = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
GOAL_STATE_TUPLE = tuple(map(tuple, GOAL_STATE_LIST))
# calc pos do estado final p busca O(1) na heurística de D Manhattan
GOAL_POSITIONS = {tile: (r, c) for r, row in enumerate(GOAL_STATE_LIST) for c, tile in enumerate(row)}


class Node:
    def __init__(self, state: Tuple[Tuple[int, ...], ...], parent: Optional['Node'] = None, action: Optional[Dict[str, Any]] = None, g: int = 0, h: int = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h

    def get_f_score(self) -> int:
        return self.g + self.h

    def __lt__(self, other: 'Node') -> bool:
        return self.get_f_score() < other.get_f_score()

# --- Funções Auxiliares ---
def find_pos(state: Tuple[Tuple[int, ...], ...], value: int) -> Optional[Tuple[int, int]]:
    for r, row in enumerate(state):
        for c, tile in enumerate(row):
            if tile == value:
                return r, c
    return None

def reconstruct_solution_path(final_node: Node) -> List[Dict[str, Any]]:
    """Reconstrói o caminho da solução a partir do nó final."""
    path = []
    current_node = final_node
    while current_node.parent is not None:
        path.append(current_node.action)
        current_node = current_node.parent
    path.reverse()
    return path

def get_all_successors(node: Node) -> List[Node]:
    """Gera todos os nós sucessores válidos a partir do nó atual."""
    successors = []
    empty_pos = find_pos(node.state, 0)
    if empty_pos is None:
        return []

    empty_row, empty_col = empty_pos
    possible_moves = [(-1, 0, 'UP'), (1, 0, 'DOWN'), (0, -1, 'LEFT'), (0, 1, 'RIGHT')]
    new_g_score = node.g + 1

    for dr, dc, move_name in possible_moves:
        new_row, new_col = empty_row + dr, empty_col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            # converte tupla p lista p poder modificar
            new_state_list = [list(row) for row in node.state]
            moved_tile = new_state_list[new_row][new_col]
            
            new_state_list[empty_row][empty_col] = moved_tile
            new_state_list[new_row][new_col] = 0
            
            # converte p tupla p ser imutável
            new_state_tuple = tuple(map(tuple, new_state_list))
            
            detailed_action = {
                "move_direction": move_name, "moved_tile": moved_tile,
                "empty_tile_from": [empty_row, empty_col], "empty_tile_to": [new_row, new_col]
            }
            successors.append(Node(state=new_state_tuple, parent=node, action=detailed_action, g=new_g_score))
    return successors

# --- Funções de Heurística ---
def h_uniform_cost(state: Tuple[Tuple[int, ...], ...]) -> int:
    """Heurística p busca de Custo Uniforme (sempre 0)."""
    return 0

def h_non_admissible(state: Tuple[Tuple[int, ...], ...]) -> int:
    """Heurística não admissível (superestima o custo)."""
    return h_manhattan_distance(state) * 3

def h_misplaced_tiles(state: Tuple[Tuple[int, ...], ...]) -> int:
    """Heurística admissível simples: conta as peças fora do lugar."""
    misplaced = 0
    for r in range(3):
        for c in range(3):
            if state[r][c] != GOAL_STATE_TUPLE[r][c] and state[r][c] != 0:
                misplaced += 1
    return misplaced

def h_manhattan_distance(state: Tuple[Tuple[int, ...], ...]) -> int:
    """Heurística admissível Distância de Manhattan."""
    dist = 0
    for r in range(3):
        for c in range(3):
            value = state[r][c]
            if value != 0:
                # busca O(1) no mapa existenet
                goal_r, goal_c = GOAL_POSITIONS[value]
                dist += abs(r - goal_r) + abs(c - goal_c)
    return dist

# --- Algoritmo A* ---
def a_star_search(initial_state_list: List[List[int]], heuristic_func) -> Optional[Dict[str, Any]]:
    """Executa o algoritmo de busca A* para resolver o 8-Puzzle."""
    initial_state = tuple(map(tuple, initial_state_list))
    initial_h = heuristic_func(initial_state)
    initial_node = Node(state=initial_state, g=0, h=initial_h)

    open_list_heap = [initial_node] # fila de prioridade da fronteira de escolha
    open_dict = {initial_state: initial_node} # acesso rápido aos nos na fronteira
    closed_dict = {} # nós visitados
    
    max_frontier_size = 1

    while open_list_heap:
        current_node = heapq.heappop(open_list_heap)
        
        if current_node.state in open_dict:
            del open_dict[current_node.state]

        if current_node.state in closed_dict:
            continue
        
        closed_dict[current_node.state] = current_node
        
        # alcançou o estado final?
        if current_node.state == GOAL_STATE_TUPLE:
            return {
                "solution_path": reconstruct_solution_path(current_node),
                "nodes_visited": len(closed_dict),
                "max_frontier_size": max_frontier_size,
                "final_frontier": open_list_heap,
                "visited_nodes": closed_dict
            }

        for successor_node in get_all_successors(current_node):
            if successor_node.state in closed_dict:
                continue

            successor_node.h = heuristic_func(successor_node.state)

            if successor_node.state in open_dict:
                existing_node = open_dict[successor_node.state]
                # se o novo caminho for melhor (menor g), atualiza
                if successor_node.g < existing_node.g:
                    existing_node.g = successor_node.g
                    existing_node.parent = successor_node.parent
                    existing_node.action = successor_node.action
                    heapq.heapify(open_list_heap) # reordena a heap
            else:
                # adiciona o novo nó à fronteira
                heapq.heappush(open_list_heap, successor_node)
                open_dict[successor_node.state] = successor_node

        max_frontier_size = max(max_frontier_size, len(open_list_heap))

    return None # se não encontrar solução

# --- Bloco Principal para Execução ---
if __name__ == "__main__":
    initial_states = {
        "facil": [[1, 2, 3], [4, 5, 6], [0, 7, 8]],
        "medio": [[1, 3, 0], [4, 2, 5], [7, 8, 6]],
        "dificil": [[8, 6, 7], [2, 5, 4], [3, 0, 1]]
    }
    heuristics = {
        "1": ("Custo Uniforme", h_uniform_cost),
        "2": ("A* Nao Admissivel", h_non_admissible),
        "3": ("A* Pecas Fora do Lugar", h_misplaced_tiles),
        "4": ("A* Distancia de Manhattan", h_manhattan_distance)
    }

    print("Escolha o tabuleiro inicial:")
    for key in initial_states:
        print(f"- {key}")
    board_choice = input("Digite sua escolha: ").lower()
    initial_state = initial_states.get(board_choice, initial_states["medio"])

    print("\nEscolha a heurística:")
    for key, (name, _) in heuristics.items():
        print(f"{key}: {name}")
    heuristic_choice = input("Digite sua escolha (1-4): ")
    heuristic_name, heuristic_func = heuristics.get(heuristic_choice, heuristics["4"])

    print(f"\nIniciando busca com {heuristic_name}...")
    start_time = time.time()
    result = a_star_search(initial_state, heuristic_func)
    execution_time = time.time() - start_time

    if result:
        print("\n" + "="*15 + " RESUMO FINAL " + "="*15)
        path = result['solution_path']
        
        # Requisito a) - total de nós visitados
        print(f"Total de nos expandidos (visitados): {result['nodes_visited']}")

        # Requisito b) - tamanho do caminho
        print(f"Solucao encontrada com {len(path)} movimentos.")
        
        # Requisito c) - tempo de execucao
        print(f"Tempo de execucao: {execution_time:.4f} segundos")
        
        # Requisito d) - maior tamanho da fronteira
        print(f"Maior tamanho da fronteira: {result['max_frontier_size']}")

        # Requisito e) - salvar fronteira e visitados em um arquivo .json
        final_frontier_serializable = [
            {"state": node.state, "g": node.g, "h": node.h, "f": node.get_f_score()}
            for node in result['final_frontier']
        ]
        
        visited_nodes_serializable = {
            str(state_tuple): {"state": state_tuple, "g": node.g, "h": node.h, "f": node.get_f_score()}
            for state_tuple, node in result['visited_nodes'].items()
        }

        output_data = {
            "board_choice": board_choice,
            "heuristic_used": heuristic_name,
            "execution_time_seconds": round(execution_time, 4),
            "path_length": len(path),
            "nodes_visited": result['nodes_visited'],
            "max_frontier_size": result['max_frontier_size'],
            "solution_path": result['solution_path'],
            "final_frontier": final_frontier_serializable,
            "visited_nodes": visited_nodes_serializable
        }
        
        safe_name = heuristic_name.replace(' ', '_').replace('*', 'estrela').lower()
        output_filename = f"resultado_{board_choice}_{safe_name}.json"
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(f"Dados completos da busca salvos em '{output_filename}'")
        
    else:
        print("Nao foi possivel encontrar uma solucao.")