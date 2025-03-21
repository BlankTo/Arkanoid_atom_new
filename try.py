x = 3
y = 5

for i in range(1, y - x + 1):
    print((i, x+i))


exit()

import itertools

d = {
    'x': ['a', 'b'],   # <-- notare: se davvero vuoi solo 4 combinazioni, devi avere 2 valori qui
    'y': ['d'],        #      (altrimenti, con ['a','b','c'] sarebbero 6 combinazioni)
    'z': ['f', 'g']
}

keys = list(d.keys())              # es.: ["x", "y", "z"]
values_lists = [d[k] for k in keys] # es.: [["a", "b"], ["d"], ["f", "g"]]

result = []
for combo in itertools.product(*values_lists):
    # combo è una tupla, es. ("a", "d", "f")
    # uniamo ciascun valore della tupla con la rispettiva chiave
    paired = list(zip(keys, combo))
    result.append(paired)

print(result)



exit()
import itertools

def combine_scenarios(scenarios_by_property):
    """
    scenarios_by_property è un dict con chiavi (es. 'pos_x', 'pos_y', ...)
    e valori: liste di "scenario-dict".
    
    Ogni "scenario-dict" ha la forma:
       {
         frame_id: {
           nome_proprietà: (val_iniz, val_fin)
         },
         ...
       }
    Esempio:
       {
         0: { 'DQ1(pos_x)': (None, 1) }
       }
    
    Ritorna una lista di dict, dove ciascun dict è l'unione coerente
    di uno scenario per ogni proprietà.
    """
    
    # Estraiamo la lista di tutte le (chiave, possibili_scenari)
    prop_names = list(scenarios_by_property.keys())
    scenario_lists = list(scenarios_by_property.values())
    
    # Prodotto cartesiano su tutti i "blocchi" di scenari
    # combo sarà una tupla contenente, per ogni proprietà, uno scenario.
    # Esempio: ( {'pos_x' scenario}, {'pos_y' scenario} )
    all_combinations = []
    for combo in itertools.product(*scenario_lists):
        # combo[i] è uno degli scenari di scenario_lists[i]
        
        # Creiamo il dizionario finale, unendo i vari scenari
        merged_scenario = {}
        for scenario_dict in combo:
            # scenario_dict è tipo:
            #   { 0: {'DQ1(pos_x)': (None, 1)} }  oppure
            #   { 1: {'pos_x': (43, 44)} } e così via
            for frame_key, props_dict in scenario_dict.items():
                if frame_key not in merged_scenario:
                    merged_scenario[frame_key] = {}
                # Uniamo le proprietà
                for prop_name, transition in props_dict.items():
                    # Se dovessi controllare conflitti, lo faresti qui,
                    # ma in questo esempio uniamo e basta
                    merged_scenario[frame_key][prop_name] = transition
        
        all_combinations.append(merged_scenario)
    
    return all_combinations


# Esempio di utilizzo
scenarios_by_property = {
    'pos_x': [
        {0: {'DQ1(pos_x)': (None, 1)}},
        {1: {'pos_x': (43, 44)}}
    ],
    'pos_y': [
        {0: {'DQ1(pos_y)': (None, 1)}},
        {1: {'pos_y': (44, 45)}}
    ],
}

combinations = combine_scenarios(scenarios_by_property)

for i, combo in enumerate(combinations, start=1):
    print(f"Combinazione {i}:")
    for frame_id, changes in combo.items():
        print(f"  Frame {frame_id} => {changes}")
    print()



exit()

s = "DQ1(DQ1(DQ1(x)))"

n_d = s.count('DQ1')

dq1_name = s
while n_d:
    in_prop_name = dq1_name[4:-1]
    print(f'{in_prop_name} modified by val of {dq1_name}')
    dq1_name = in_prop_name
    n_d -= 1

exit()

from itertools import combinations, permutations

def generate_partial_biunivocal_assignments(objects, patches):
    n_objects = len(objects)
    n_patches = len(patches)
    all_assignments = []
    
    # Generate all possible assignments including partial assignments
    for k in range(n_objects + 1):  # Allow up to all objects being assigned
        for obj_subset in combinations(objects, k):
            for patch_subset in combinations(patches, k):
                for permuted_patches in permutations(patch_subset):
                    assignment = list(zip(obj_subset, permuted_patches))
                    
                    # Add unassigned objects
                    assigned_objects = {o for o, _ in assignment}
                    unassigned_objects = [(obj, None) for obj in objects if obj not in assigned_objects]
                    
                    # Add unassigned patches
                    assigned_patches = {p for _, p in assignment}
                    unassigned_patches = [(None, patch) for patch in patches if patch not in assigned_patches]
                    
                    # Construct final assignment configuration
                    full_assignment = unassigned_objects + assignment + unassigned_patches
                    all_assignments.append(full_assignment)
    
    return all_assignments

# Example Usage:
objects = ['A', 'B', 'C']
patches = ['X', 'Y']
result = generate_partial_biunivocal_assignments(objects, patches)
for r in sorted(result, key= lambda x: (x[0][0], x[1][0], x[2][0])):
    print(r)



exit()

from itertools import permutations

def generate_assignment_space(objects, patches):
    num_objects, num_patches = len(objects), len(patches)
    max_assignments = min(num_objects, num_patches)  # Non possiamo assegnare più di questo

    assignment_space = []

    # Consideriamo tutti i possibili numeri di oggetti assegnati (da 0 a max_assignments)
    for k in range(max_assignments + 1):
        # Prendiamo tutte le possibili disposizioni di k oggetti nelle k patch
        for permuted_objects in permutations(objects, k):
            # Creiamo una lista con gli oggetti assegnati e le patch vuote
            assigned_patches = list(permuted_objects) + [None] * (num_patches - k)
            patch_assignment = list(zip(patches, assigned_patches))

            # Aggiungiamo anche gli oggetti non assegnati come (None, oggetto)
            unassigned_objects = set(objects) - set(permuted_objects)
            unassigned_pairs = [(None, obj) for obj in unassigned_objects]

            # Aggiungiamo la possibilità completa
            assignment_space.append(patch_assignment + unassigned_pairs)

    return assignment_space

# Esempio di utilizzo
objects = ['A', 'B']
patches = ['X', 'Y', 'Z']

assignments = generate_assignment_space(patches, objects)

# Stampiamo lo spazio generato
for i, assignment in enumerate(assignments):
    print(f"Possibilità {i+1}: {assignment}")




exit()

from itertools import permutations, chain

def generate_assignment_space(objects, patches):
    num_objects, num_patches = len(objects), len(patches)
    max_assignments = min(num_objects, num_patches)  # Non possiamo assegnare più di questo

    assignment_space = []

    # Consideriamo tutti i possibili numeri di oggetti assegnati (da 0 a max_assignments)
    for k in range(max_assignments + 1):
        # Prendiamo tutte le possibili disposizioni di k oggetti nelle k patch
        for permuted_objects in permutations(objects, k):
            # Creiamo una lista con gli oggetti assegnati e le patch vuote
            assignment = list(permuted_objects) + [None] * (num_patches - k)
            # Abbiniamo gli oggetti o None alle patch
            assignment_space.append(list(zip(patches, assignment)))
    
    return assignment_space

# Esempio di utilizzo
objects = ['x', 'y', 'z']
patches = ['b', 'a']

assignments = generate_assignment_space(objects, patches)

# Stampiamo lo spazio generato
for i, assignment in enumerate(assignments):
    print(f"Possibilità {i+1}: {assignment}")


exit()

from itertools import permutations, combinations, product

def generate_assignment_space(objects, patches):
    num_patches = len(patches)
    assignment_space = []

    for k in range(num_patches + 1):  # Da 0 fino al numero di patch
        for selected_objects in combinations(objects, k):  # Scegliamo k oggetti
            for permuted_objects in permutations(selected_objects):  # Permutiamo quegli oggetti
                empty_slots = [None] * (num_patches - k)  # Generiamo slot vuoti
                assignment = list(permuted_objects) + empty_slots
                assignment_space.append(list(zip(patches, assignment)))  # Abbiniamo alle patch
    
    return assignment_space

# Esempio di utilizzo
objects = ['A', 'B']
patches = ['X', 'Y', 'Z']

assignments = generate_assignment_space(objects, patches)

# Stampiamo lo spazio generato
for i, assignment in enumerate(assignments):
    print(f"Possibilità {i+1}: {assignment}")



exit()

from itertools import permutations, combinations, product

def generate_assignment_space(objects, patches):
    num_patches = len(patches)
    assignment_space = []

    # Generiamo tutte le disposizioni parziali
    for k in range(num_patches + 1):  # Possiamo assegnare da 0 a num_patches oggetti
        for selected_objects in combinations(objects, k):  # Selezioniamo k oggetti senza ripetizione
            for permuted_objects in permutations(selected_objects):  # Permutiamo gli oggetti selezionati
                for empty_slots in product([None], repeat=num_patches - k):  # Slot vuoti per le patch non assegnate
                    # Creiamo una lista di assegnazioni con gli oggetti e gli slot vuoti
                    assignment = list(permuted_objects) + list(empty_slots)
                    assignment_space.append(list(zip(patches, assignment)))  # Abbiniamo alle patch
    
    return assignment_space

# Esempio di utilizzo
objects = ['A', 'B', 'C']  # Lista di oggetti
patches = ['X', 'Y']  # Lista di patch

assignments = generate_assignment_space(objects, patches)

# Stampiamo lo spazio generato
for i, assignment in enumerate(assignments):
    print(f"Possibilità {i+1}: {assignment}")


exit()

from itertools import permutations

A = [1, 2, 3]
B = ['a', 'b']

for perm in permutations(A, len(B)):  # Permutazioni di lunghezza len(B)
    print(list(zip(perm, B)))  # Abbina ogni permutazione agli elementi di B


exit()

from collections import defaultdict
from itertools import product

def group_instances(data):
    shape_groups = defaultdict(list)
    
    # Raggruppa per shape
    for key, (shape, protos) in data.items():
        shape_groups[shape].append((key, set(protos)))
    
    instance_map = {}
    instance_counter = 0
    
    for shape, items in shape_groups.items():
        # Trova tutte le combinazioni possibili di proto
        proto_sets = [proto_set for _, proto_set in items]
        grouped = []
        
        while proto_sets:
            base = proto_sets.pop(0)
            group = [base]
            remaining = []
            
            for proto in proto_sets:
                if base & proto:  # Se c'è intersezione
                    group.append(proto)
                    base &= proto  # Intersezione comune
                else:
                    remaining.append(proto)
            
            grouped.append((group, base))
            proto_sets = remaining
        
        # Assegna istanze
        for group, common_proto in grouped:
            instance_label = f"instance_{instance_counter}"
            instance_counter += 1
            for key, proto_set in items:
                if proto_set in group:
                    instance_map[key] = (list(common_proto), instance_label)
    
    return instance_map

def generate_explanations(instance_mapping):

    instance_to_protos = defaultdict(set)
    for _, (possible_protos, instance_label) in instance_mapping.items():
        instance_to_protos[instance_label].update(possible_protos)
    
    instance_label_list = list(instance_to_protos.keys())
    proto_choices = [list(instance_to_protos[il]) for il in instance_label_list]
    
    explanations = []
    for choice in product(*proto_choices):

        combination = {}
        for obj_id, (_, instance_label) in instance_mapping.items():
            combination[obj_id] = (choice[instance_label_list.index(instance_label)], instance_label)
            
        explanations.append(combination)
    
    return explanations


# Dati di input
data = {
    0: ("shape_a", ["proto_b"]),
    1: ("shape_a", ["proto_a", "proto_b"]),
    2: ("shape_b", ["proto_a"]),
    3: ("shape_b", ["proto_a"]),
    4: ("shape_b", ["proto_a"]),
    5: ("shape_b", ["proto_a"]),
    6: ("shape_c", ["proto_c"]),
    7: ("shape_d", ["proto_d"]),
    8: ("shape_e", ["proto_a"]),
    9: ("shape_a", ["proto_a", "proto_b"]),
    10: ("shape_a", ["proto_a", "proto_b"]),
    11: ("shape_a", ["proto_a", "proto_b"]),
    12: ("shape_a", ["proto_a", "proto_b"]),
    13: ("shape_a", ["proto_a", "proto_b"]),
    15: ("shape_a", ["proto_e", "proto_f"]),
    16: ("shape_b", ["proto_e", "proto_f"]),
    17: ("shape_b", ["proto_e", "proto_f", "proto_g"]),
}

# Esegui raggruppamento
result = group_instances(data)

# Stampa il risultato
for k, v in sorted(result.items()):
    print(k, ":", v)

# Genera le combinazioni per istanza
combinations = generate_explanations(result)

if not combinations:
    print('no combinations')

# Stampa il risultato
for i, comb in enumerate(combinations):
    print(f"Combination {i}:")
    for k, v in sorted(comb.items()):
        print(f"  {k}: {v}")
    print()







exit()

from core.property import Pos_x, Pos_y, Shape_x, Shape_y

def check_general_contact(hitbox_A, hitbox_B):

    ax, ay, aw, ah = hitbox_A
    bx, by, bw, bh = hitbox_B

    ax -= 1
    ay -= 1
    aw += 2
    ah += 2

    x_overlap = (bx <= ax + aw) and (ax <= bx + bw)
    y_overlap = (by <= ay + ah) and (ay <= by + bh)

    return x_overlap and y_overlap

def check_contact_left(frame_id, obj, other):

    if frame_id- 1 in obj.frames_id:
        previous_obj_patch = obj.patches[frame_id - 1]
    else:
        previous_obj_patch = None

    if frame_id in obj.frames_id:
        current_obj_patch = obj.patches[frame_id]
    else:
        current_obj_patch = None

    if frame_id- 1 in other.frames_id:
        previous_other_patch = other.patches[frame_id - 1]
    else:
        previous_other_patch = None

    if frame_id in other.frames_id:
        current_other_patch = other.patches[frame_id]
    else:
        current_other_patch = None

    if current_obj_patch:
        current_obj_hitbox = (current_obj_patch.properties[Pos_x], current_obj_patch.properties[Pos_y], current_obj_patch.properties[Shape_x], current_obj_patch.properties[Shape_y])
    elif previous_obj_patch:
        current_obj_hitbox = (current_obj_patch.properties[Pos_x], current_obj_patch.properties[Pos_y], current_obj_patch.properties[Shape_x], current_obj_patch.properties[Shape_y])
    else: return False

    if current_other_patch:
        current_other_hitbox = (current_other_patch.properties[Pos_x], current_other_patch.properties[Pos_y], current_other_patch.properties[Shape_x], current_other_patch.properties[Shape_y])
    elif previous_other_patch:
        current_other_hitbox = (current_other_patch.properties[Pos_x], current_other_patch.properties[Pos_y], current_other_patch.properties[Shape_x], current_other_patch.properties[Shape_y])
    else: return False

    if check_general_contact(current_obj_hitbox, current_other_hitbox):
        print('contact')

    # check direction left with speeds after computing them

    exit()

# Example Usage
hitbox_A = (0, 0, 1, 1)  # Cube A occupies cell (0, 0)
hitbox_B = (1, 1, 1, 1)  # Cube B occupies cell (1, 1)

class Patch:
    def __init__(self, pos_x, pos_y, shape_x, shape_y):
        self.properties = {
            Pos_x: pos_x,
            Pos_y: pos_y,
            Shape_x: shape_x,
            Shape_y: shape_y,
        }

class Object:
    def __init__(self, previous_patch, current_patch):
        self.patches = [previous_patch, current_patch]
        self.frames_id = [0, 1]

prev_obj_patch = Patch(0, 0, 1, 1)
curr_obj_patch = Patch(1, 1, 1, 1)
obj = Object(prev_obj_patch, curr_obj_patch)

prev_other_patch = Patch(1, 3, 1, 1)
curr_other_patch = Patch(1, 3, 1, 1)
other = Object(prev_other_patch, curr_other_patch)

print("contact left?", check_contact_left(1, obj, other))





#####


