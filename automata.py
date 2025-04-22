#7ouzz-coder

def parse_input():
    """
    Lee y procesa la entrada según el formato especificado.
    """
    try:
        # Línea 1: Estados
        states = input().strip().split()
        if not states:
            return "Error encontrado en 1"
        
        # Línea 2: Alfabeto
        alphabet = input().strip().split()
        if not alphabet:
            return "Error encontrado en 2"
        
        # Verificar que no haya caracteres prohibidos
        prohibited = ['#', '"', "'", ',', '.', '_']
        for state in states:
            for char in prohibited:
                if char in state:
                    return "Error encontrado en 1"
        
        for symbol in alphabet:
            if len(symbol) != 1 or not symbol.isalnum():
                return "Error encontrado en 2"
            for char in prohibited:
                if char in symbol:
                    return "Error encontrado en 2"
        
        # Línea 3: Estado inicial
        initial_state = input().strip()
        if initial_state not in states:
            return "Error encontrado en 3"
        
        # Línea 4: Estados finales
        final_states = input().strip().split()
        for state in final_states:
            if state not in states:
                return "Error encontrado en 4"
        
        # Línea 5: Transiciones
        transitions_input = input().strip().split()
        transitions = {}
        
        for t in transitions_input:
            # Verificar formato (estado,símbolo,estado)
            if not (t.startswith('(') and t.endswith(')') and t.count(',') == 2):
                return "Error encontrado en 5"
            
            # Extraer componentes
            parts = t[1:-1].split(',')
            if len(parts) != 3:
                return "Error encontrado en 5"
            
            from_state, symbol, to_state = parts
            
            # Verificar validez de estados y símbolos
            if from_state not in states or to_state not in states:
                return "Error encontrado en 5"
            
            if symbol != '#' and symbol not in alphabet:
                return "Error encontrado en 5"
            
            # Agregar transición al diccionario
            if (from_state, symbol) not in transitions:
                transitions[(from_state, symbol)] = []
            transitions[(from_state, symbol)].append(to_state)
        
        # Línea 6: Palabra a reconocer
        word = input().strip()
        for symbol in word:
            if symbol not in alphabet:
                return "Error encontrado en 6"
        
        return {
            'states': states,
            'alphabet': alphabet,
            'initial_state': initial_state,
            'final_states': set(final_states),
            'transitions': transitions,
            'word': word
        }
    
    except Exception as e:
        # Si ocurre cualquier otro error
        return f"Error inesperado: {str(e)}"

def convert_to_dfa(nfa):
    """
    Convierte un AFND con palabra vacía a un AFD.
    """
    # Calcular el cierre epsilon para cada estado
    epsilon_closure = {}
    for state in nfa['states']:
        epsilon_closure[state] = get_epsilon_closure(state, nfa['transitions'])
    
    # Estado inicial del AFD será el cierre-epsilon del estado inicial del AFND
    dfa_initial = frozenset(epsilon_closure[nfa['initial_state']])
    
    # Inicializar AFD
    dfa = {
        'states': [],
        'alphabet': nfa['alphabet'],
        'transitions': {},
        'initial_state': dfa_initial,
        'final_states': set()
    }
    
    # Cola para los estados no procesados del AFD
    unmarked_states = [dfa_initial]
    dfa['states'].append(dfa_initial)
    
    # Verificar si el estado inicial es final
    if any(state in nfa['final_states'] for state in dfa_initial):
        dfa['final_states'].add(dfa_initial)
    
    # Procesar todos los estados del AFD
    while unmarked_states:
        current_state = unmarked_states.pop(0)
        
        for symbol in nfa['alphabet']:
            next_states = set()
            
            # Para cada estado en el conjunto actual
            for state in current_state:
                # Obtener los siguientes estados para el símbolo actual
                if (state, symbol) in nfa['transitions']:
                    for next_state in nfa['transitions'][(state, symbol)]:
                        # Agregar el cierre-epsilon del siguiente estado
                        next_states.update(epsilon_closure[next_state])
            
            # Convertir a frozenset para usarlo como clave
            next_states_frozenset = frozenset(next_states)
            
            # Agregar transición al AFD
            if next_states:
                dfa['transitions'][(current_state, symbol)] = next_states_frozenset
                
                # Si es un nuevo estado, agregarlo a la lista
                if next_states_frozenset not in dfa['states']:
                    dfa['states'].append(next_states_frozenset)
                    unmarked_states.append(next_states_frozenset)
                    
                    # Verificar si el nuevo estado es final
                    if any(state in nfa['final_states'] for state in next_states_frozenset):
                        dfa['final_states'].add(next_states_frozenset)
    
    return dfa

def get_epsilon_closure(state, transitions):
    """
    Calcula el cierre-epsilon de un estado.
    """
    closure = {state}
    stack = [state]
    
    while stack:
        current = stack.pop()
        
        # Buscar transiciones epsilon
        if (current, '#') in transitions:
            for next_state in transitions[(current, '#')]:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
    
    return closure

def is_deterministic(automaton):
    """
    Verifica si el autómata es determinista.
    """
    # Verificar que no haya transiciones con palabra vacía
    for key in automaton['transitions']:
        if key[1] == '#':
            return False
    
    # Verificar que cada par (estado, símbolo) tenga máximo una transición
    for state in automaton['states']:
        for symbol in automaton['alphabet']:
            transitions = automaton['transitions'].get((state, symbol), [])
            if len(transitions) > 1:
                return False
    
    return True

def process_word(automaton, word):
    """
    Procesa una palabra con un autómata y muestra el paso a paso.
    Retorna True si la palabra es aceptada, False en caso contrario.
    """
    # Para autómatas con transiciones epsilon, debemos manejar estados múltiples
    # Primero calculamos el cierre epsilon del estado inicial
    current_states = [automaton['initial_state']]
    
    # Si hay transiciones epsilon desde el estado inicial, las seguimos
    epsilon_states = get_epsilon_closure_states(current_states[0], automaton['transitions'])
    if len(epsilon_states) > 1:  # Si hay más estados en el cierre epsilon
        current_states = epsilon_states
    
    # Mostrar estado inicial
    print(f"_{word} {current_states[0]}")
    
    # Si hay estados adicionales debido a epsilon, mostrarlos
    if len(current_states) > 1:
        print(f"_{word} {''.join(current_states)}")
    
    # Procesar cada símbolo de la palabra
    for i, symbol in enumerate(word):
        next_states = []
        
        # Para cada estado actual, encontrar las transiciones con el símbolo actual
        for state in current_states:
            if (state, symbol) in automaton['transitions']:
                # Agregar los estados de destino
                for next_state in automaton['transitions'][(state, symbol)]:
                    if next_state not in next_states:
                        next_states.append(next_state)
                    
                    # Agregar los estados alcanzables por epsilon desde el nuevo estado
                    for eps_state in get_epsilon_closure_states(next_state, automaton['transitions']):
                        if eps_state not in next_states:
                            next_states.append(eps_state)
        
        # Si no hay transiciones para el símbolo actual, rechazamos
        if not next_states:
            return False
        
        # Actualizar los estados actuales
        current_states = next_states
        
        # Mostrar el paso actual
        print(f"{word[:i+1]}_{word[i+1:]} {''.join(current_states)}")
    
    # Verificar si alguno de los estados finales es de aceptación
    for state in current_states:
        if state in automaton['final_states']:
            return True
    
    return False

def get_epsilon_closure_states(state, transitions):
    """
    Calcula los estados alcanzables a través de transiciones epsilon.
    Retorna una lista con todos los estados incluyendo el estado original.
    """
    closure = [state]
    stack = [state]
    
    while stack:
        current = stack.pop()
        
        # Buscar transiciones epsilon
        if (current, '#') in transitions:
            for next_state in transitions[(current, '#')]:
                if next_state not in closure:
                    closure.append(next_state)
                    stack.append(next_state)
    
    return closure

def main():
    """
    Función principal del programa.
    """
    automaton_data = parse_input()
    
    # Verificar si hubo un error en la entrada
    if isinstance(automaton_data, str):
        print(automaton_data)
        return
    
    # Procesar la palabra
    if process_word(automaton_data, automaton_data['word']):
        print("Aceptado")
    else:
        print("Rechazado")

if __name__ == "__main__":
    main()