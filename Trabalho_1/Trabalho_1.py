# Python 3
import time
import json
import copy
import heapq

class Node:
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h

    def get_f_score(self): return self.g + self.h
    
    def __lt__(self, other): return self.get_f_score() < other.get_f_score()

# --- Funções Auxiliares ---
def find_pos(state, value):
    """Finds the position (row, col) of a value in the 3x3 state."""
    for r in range(3):
        for c in range(3):
            if state[r][c] == value: return r, c
    return None

def reconstruct_solution_path(final_node):
    """Reconstructs the solution path from the final node to the initial node."""
    if not final_node: 
        return []
    path = []
    current_node = final_node
    while current_node.parent is not None:
        path.append(current_node.action)
        current_node = current_node.parent
    path.reverse()
    return path

def get_all_successors(node):
    """Generates all valid successor nodes from the current node."""
    successors = []
    state = node.state
    empty_pos = find_pos(state, 0)

    if empty_pos is None: 
        return []
    
    empty_row, empty_col = empty_pos
    possible_moves = [(-1, 0, 'UP'), (1, 0, 'DOWN'), (0, -1, 'LEFT'), (0, 1, 'RIGHT')]
    new_g_score = node.g + 1
    
    for dr, dc, move_name in possible_moves:
        new_row, new_col = empty_row + dr, empty_col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_state = copy.deepcopy(state)
            peca_a_mover = new_state[new_row][new_col]
            new_state[empty_row][empty_col] = peca_a_mover
            new_state[new_row][new_col] = 0
            detailed_action = {
                "move_direction": move_name, "moved_tile": peca_a_mover,
                "empty_tile_from": [empty_row, empty_col], "empty_tile_to": [new_row, new_col]
            }
            successors.append(Node(state=new_state, parent=node, action=detailed_action, g=new_g_score))
    return successors

# --- Funções de Heurística ---
def h_uniform_cost(state, goal_state):
    """Calculates the uniform cost heuristic for the 8-puzzle."""
    return 0

def h_non_admissible(state, goal_state): 
    """Calculates a non-admissible heuristic for the 8-puzzle."""
    return h_manhattan_distance(state, goal_state) * 3

def h_misplaced_tiles(state, goal_state):
    """Calculates the number of misplaced tiles heuristic for the 8-puzzle."""
    misplaced = 0
    for r in range(3):
        for c in range(3):
            if state[r][c] != goal_state[r][c] and state[r][c] != 0:
                misplaced += 1
    return misplaced

def h_manhattan_distance(state, goal_state):
    """Calculates the Manhattan distance heuristic for the 8-puzzle."""
    dist = 0
    for r in range(3):
        for c in range(3):
            value = state[r][c]
            if value != 0:
                goal_r, goal_c = find_pos(goal_state, value)
                if goal_r is not None:
                    dist += abs(r - goal_r) + abs(c - goal_c)
    return dist

# --- Algoritmo A* com Visualização Opcional ---
def a_star_search(initial_state, goal_state, heuristic_func, visualize_steps=False):
    """Performs the A* search algorithm to solve the 8-puzzle."""
    initial_h = heuristic_func(initial_state, goal_state)
    initial_node = Node(state=initial_state, g=0, h=initial_h)
    open_list_heap = [initial_node]
    closed_dict = {}
    open_dict = {tuple(map(tuple, initial_state)): initial_node}  # Track nodes in open list
    iteration_counter = 0

    while open_list_heap:
        if visualize_steps:
            print(f"\n" + "="*15 + f" ITERAÇÃO {iteration_counter} " + "="*15)
            print(f"VISITADOS ({len(closed_dict)}):")
            if not closed_dict: print("  - {}")
            else:
                # --- MUDANÇA 1: Loop de impressão dos VISITADOS ---
                # Agora itera sobre o dicionário que armazena Nodes completos
                for state_tuple, node in closed_dict.items():
                    print(f"  - (g={node.g}, h={node.h}, cost={node.get_f_score()}) Estado: {[list(row) for row in state_tuple]}")
            
            print(f"ABERTOS ({len(open_list_heap)}):")
            if not open_list_heap: print("  - {}")
            else:
                for node in sorted(open_list_heap):
                    print(f"  - (g={node.g}, h={node.h}, cost={node.get_f_score()}) Estado: {node.state}")

        current_node = heapq.heappop(open_list_heap)
        current_state_tuple = tuple(map(tuple, current_node.state))
        
        # Remove from open list tracking
        if current_state_tuple in open_dict:
            del open_dict[current_state_tuple]
            
        if current_state_tuple in closed_dict: continue

        # --- MUDANÇA 2: Armazena o Node inteiro nos VISITADOS ---
        closed_dict[current_state_tuple] = current_node
        
        if visualize_steps:
            print(f"\n--> Expandindo: {current_node.state} com custo g={current_node.g}")

        # Check if we reached the goal
        if current_state_tuple == tuple(map(tuple, goal_state)):
            if visualize_steps: print("\n" + "*"*10 + " SOLUÇÃO ENCONTRADA! " + "*"*10)
            return {"solution_path": reconstruct_solution_path(current_node), "nodes_visited": len(closed_dict)}

        for successor_node in get_all_successors(current_node):
            successor_state_tuple = tuple(map(tuple, successor_node.state))
            if successor_state_tuple not in closed_dict:
                successor_node.h = heuristic_func(successor_node.state, goal_state)
                
                # Check if this state is already in open list with better g-score
                if successor_state_tuple in open_dict:
                    existing_node = open_dict[successor_state_tuple]
                    if successor_node.g < existing_node.g:
                        # Remove the existing node (will be ignored when popped due to closed list check)
                        open_dict[successor_state_tuple] = successor_node
                        heapq.heappush(open_list_heap, successor_node)
                else:
                    open_dict[successor_state_tuple] = successor_node
                    heapq.heappush(open_list_heap, successor_node)
        iteration_counter += 1
    return None

# --- Bloco Principal para Execução ---
if __name__ == "__main__":
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
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

    print("\n" + "-"*30)
    visualize_input = input("Deseja visualizar o passo a passo da busca? (s/n): ").lower()
    show_visualization = True if visualize_input == 's' else False
    print("-" * 30)

    print(f"\nIniciando busca com {heuristic_name}...")
    start_time = time.time()
    result = a_star_search(initial_state, goal_state, heuristic_func, visualize_steps=show_visualization)
    execution_time = time.time() - start_time

    if result:
        print("\n" + "="*15 + " RESUMO FINAL " + "="*15)
        path = result['solution_path']
        print(f"Solução encontrada com {len(path)} movimentos.")
        print(f"Total de nós expandidos (visitados): {result['nodes_visited']}")
        print(f"Tempo de execução: {execution_time:.4f} segundos")
        # Fix filename generation to avoid invalid characters for Windows
        safe_name = heuristic_name.replace(' ', '_').replace('*', 'estrela').lower()
        output_filename = f"solucao_{safe_name}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(path, f, indent=4, ensure_ascii=False)
        print(f"Caminho detalhado salvo em '{output_filename}'")
    else:
        print("Não foi possível encontrar uma solução.")