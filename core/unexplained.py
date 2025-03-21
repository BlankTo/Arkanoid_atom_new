import itertools
from core.property import Speed_x, Speed_y
from core.patch import Patch
from core.events import Event, GlobalEvent, CommandEvent

class Phenomenon:

    def __init__(self, info):
        pass

    def test(self, phenomenon):
        pass

    def __repr__(self):
        pass

    def my_hash(self):
        pass

class SpecificUnexplainedPhenomenon(Phenomenon):

    def __init__(self, info):
        self.unexplained_class = info['unexplained_class']

    def test(self, phenomenon):
        return isinstance(phenomenon, self.unexplained_class)
    
    def __repr__(self):
        return self.unexplained_class.__name__
    
    def __eq__(self, other):
        if isinstance(other, SpecificUnexplainedPhenomenon): return self.unexplained_class == other.unexplained_class
        else: return False

    def my_hash(self):
        return self.unexplained_class.__name__

class NumericalUnexplainedPhenomenon(Phenomenon):

    def __init__(self, info):
        self.prop_name = info['prop_name']
        self.a = info['a']
        self.b = info['b']

    def test(self, phenomenon):
        if not isinstance(phenomenon, PropertyChange): return False
        if self.prop_name != phenomenon.prop_name: return False
        if phenomenon.previous_value is None:
            if self.a == 0: return phenomenon.final_value == self.b
            else: return False
            #else: return (phenomenon.final_value == self.a * 0 + self.b)
        return (phenomenon.final_value == self.a * phenomenon.previous_value + self.b)
    
    def __repr__(self):
        return f'{self.prop_name}(i+1) = {self.a} * {self.prop_name}(i) + {self.b}'
    
    def __eq__(self, other):
        if isinstance(other, NumericalUnexplainedPhenomenon): return (self.prop_name == other.prop_name and self.a == other.a and self.b == other.b)
        else: return False

    def my_hash(self):
        return f'{self.prop_name}{self.a}{self.b}'

class EventPhenomenon(Phenomenon):

    def __init__(self, info):
        self.event_class = info['event_class']

    def test(self, phenomenon):
        if isinstance(phenomenon, EventPhenomenon): return self.event_class == phenomenon.event_class
        if isinstance(phenomenon, type):
            if issubclass(phenomenon, Event): return phenomenon is self.event_class
        return False
    
    def __eq__(self, other):
        if isinstance(other, EventPhenomenon): return self.event_class == other.event_class
        else: return False
    
    def __repr__(self):
        return self.event_class.__name__

    def my_hash(self):
        return self.event_class.__name__

class GlobalEventPhenomenon(Phenomenon):

    def __init__(self, info):
        self.name = info['name']

    def test(self, phenomenon):
        if isinstance(phenomenon, GlobalEventPhenomenon): return self.name == phenomenon.name
        if isinstance(phenomenon, GlobalEvent) or isinstance(phenomenon, CommandEvent): return self.name == phenomenon.name
        if isinstance(phenomenon, str): return phenomenon == self.name
        return False
    
    def __eq__(self, other):
        if isinstance(other, GlobalEventPhenomenon): return self.name == other.name
        else: return False
    
    def __repr__(self):
        return self.name

    def my_hash(self):
        return self.name

class UnexplainedChange:
    pass

class UnexplainedNumericalChange(UnexplainedChange):
    pass

class UnexplainedSpecificChange(UnexplainedChange):
    pass

class PropertyChange(UnexplainedNumericalChange):

    def __init__(self, prop_name, previous_value, final_value):
        self.prop_name = prop_name
        self.previous_value = previous_value
        self.final_value = final_value

    def copy(self):
        return PropertyChange(self.prop_name, self.previous_value, self.final_value)
    
    def __repr__(self): return f'PropertyChange({self.prop_name}: {self.previous_value} -> {self.final_value})'

    def __eq__(self, other):
        if isinstance(other, PropertyChange): return self.prop_name == other.prop_name and self.final_value - self.previous_value == other.final_value - other.previous_value
        else: return False

    def my_hash(self):
        if self.previous_value is None: return ('PropertyChange', self.prop_name, self.final_value)
        return ('PropertyChange', self.prop_name, self.final_value - self.previous_value)

class Appearance(UnexplainedSpecificChange):

    def __init__(self):
        pass

    def copy(self):
        return Appearance()
    
    def __repr__(self): return 'Appearance'

    def __eq__(self, other):
        if isinstance(other, Appearance): return True
        else: return False

    def my_hash(self):
        return ('Appearance', None, None)

class Disappearance(UnexplainedSpecificChange):

    def __init__(self):
        pass

    def copy(self):
        return Disappearance()

    def __eq__(self, other):
        if isinstance(other, Disappearance): return True
        else: return False

    def my_hash(self):
        return ('Disappearance', None, None)
    
    def __repr__(self): return 'Disappearance'

class Duplication(UnexplainedSpecificChange):

    def __init__(self, from_obj):
        self.from_obj = from_obj

    def copy(self):
        return Duplication(self.from_obj)
    
    def __repr__(self): return f'Duplication(from {self.from_obj})'

    def __eq__(self, other):
        if isinstance(other, Duplication): return self.from_obj == other.from_obj

    def my_hash(self):
        return ('Duplication', self.from_obj.id, None) # this is wrong and just a placeholder

# change the dict keys to string
# define Property as mother class and Property_0 and Property_1
# Property_0's compute just return the new patch's property associated with the string of reference (starting with only Property_0 and in future expanding to Property_1)
# Property_1's compute compute the actual value change between the last two frames
# Property_0's effect return the same value
# Property_1's effect return the change and in which property
# then modify the function to test possible combinations Property_1's changes that could explain the diff and return all possible list of unexplaineds
def check_for_speed(obj, patch, frame_id):

    ##
    #return False, None, None
    ##

    last_patch = obj.sequence[frame_id - 1]
    current_properties = {fid: {k: v for k, v in prop.items()} for fid, prop in obj.properties.items()}
    current_properties[frame_id - 1][Speed_x] = Speed_x.compute(last_patch, patch)
    current_properties[frame_id - 1][Speed_y] = Speed_y.compute(last_patch, patch)

    dummy_object = obj.create_dummy([obj.frames_id[-1]], {obj.frames_id[-1]: last_patch}, current_properties, obj.rules)

    all_ok = True
    for prop_name, value in patch.properties.items():
        if dummy_object.prediction[prop_name] != value:
            all_ok = False
            break

    if not all_ok: return False, None, None

    unexplained_dict = {}

    current_properties[frame_id] = dummy_object.prediction

    q1_unexplained = []
    if Speed_x in obj.properties[frame_id - 1].keys():
        if obj.properties[frame_id - 1][Speed_x] != current_properties[frame_id][Speed_x]:
            q1_unexplained.append(PropertyChange(Speed_x, obj.properties[frame_id - 1][Speed_x], current_properties[frame_id][Speed_x]))
    elif current_properties[frame_id][Speed_x] != 0:
        q1_unexplained.append(PropertyChange(Speed_x, 0, current_properties[frame_id][Speed_x]))
    if Speed_y in obj.properties[frame_id - 1].keys():
        if obj.properties[frame_id - 1][Speed_y] != current_properties[frame_id][Speed_y]:
            q1_unexplained.append(PropertyChange(Speed_y, obj.properties[frame_id - 1][Speed_y], current_properties[frame_id][Speed_y]))
    elif current_properties[frame_id][Speed_y] != 0:
        q1_unexplained.append(PropertyChange(Speed_y, 0, current_properties[frame_id][Speed_y]))

    if not q1_unexplained: return False, None, None

    if frame_id - 1 in unexplained_dict.keys(): unexplained_dict[frame_id - 1].extend(q1_unexplained)
    else: unexplained_dict[frame_id - 1] = q1_unexplained

    ##
    return True, unexplained_dict, current_properties
    ##

def check_for_property0_changes(obj, patch, frame_id):

    unexplained = []
    current_properties = {fid: {k: v for k, v in prop.items()} for fid, prop in obj.properties.items()}
    current_properties[frame_id] = obj.prediction

    for prop_name, value in patch.properties.items():
        if current_properties[frame_id][prop_name] != value:
            unexplained.append(PropertyChange(prop_name, obj.properties[frame_id - 1][prop_name], value))
            current_properties[frame_id][prop_name] = value

    if unexplained: return True, {frame_id: unexplained}, current_properties
    else: return False, {}, current_properties


def check_disappearance(frame_id):
    return {frame_id: [Disappearance()]}

def check_present(obj, patch, frame_id):
    
    current_properties = dict(obj.properties[frame_id - 1])
    
    possible_variations_per_property = {}

    for prop_name, p1 in patch.properties.items():
        dq1_name = f'DQ1({prop_name})'
        
        p0 = current_properties[prop_name]
        diff = p1 - p0
        
        if diff == 0:

            if dq1_name in current_properties:
                dq1_p0 = current_properties[dq1_name]
                
                if dq1_p0 == 0: continue
                else:
                    
                    possible_variations_per_property[prop_name] = [
                        {frame_id - 1: {dq1_name: (dq1_p0, 0)}},
                        #{frame_id: {prop_name: -dq1_p0}}
                    ]
            else: continue
        
        else:

            if dq1_name in current_properties:
                dq1_p0 = current_properties[dq1_name]
                
                if dq1_p0 == diff: continue

                else:

                    possible_variations_per_property[prop_name] = [
                        {frame_id - 1: {dq1_name: (dq1_p0, diff)}},
                        {frame_id - 1: {dq1_name: (dq1_p0, 0)}, frame_id: {prop_name: (p0, p1)}},
                        {frame_id: {prop_name: (p0, p1 - p0 + diff)}}
                    ]
            
            else:
                
                possible_variations_per_property[prop_name] = [
                    {frame_id - 1: {dq1_name: (None, diff)}},
                    {frame_id: {prop_name: (p0, p1)}}
                ]

    scenario_lists = list(possible_variations_per_property.values())
    
    possibilities = []
    for comb in itertools.product(*scenario_lists):

        merged_scenario = {}
        for scenario_dict in comb:

            for frame_key, props_dict in scenario_dict.items():

                if frame_key not in merged_scenario: merged_scenario[frame_key] = {}
                for prop_name, transition in props_dict.items():
                    merged_scenario[frame_key][prop_name] = transition
        
        possibilities.append(merged_scenario)

    possibilities_with_properties = []
    for possibility in possibilities:
        unexplained_dict = {}
        new_properties = {fid: {k: v for k, v in props.items()} for fid, props in obj.properties.items()}
        new_properties[frame_id] = {k: v for k, v in patch.properties.items()}
        for fid, props_change in possibility.items():
            unexplained_dict[fid] = []
            for prop_name, val in props_change.items():
                new_properties[fid][prop_name] = val[1]
                unexplained_dict[fid].append(PropertyChange(prop_name, val[0], val[1]))
        possibilities_with_properties.append((unexplained_dict, new_properties))

#    print('\n\nprevious properties:')
#    for prop_name, val in current_properties.items():
#        print(f'{prop_name}: {val}')
#
#    print('\n\npatch properties:')
#    for prop_name, val in patch.properties.items():
#        print(f'{prop_name}: {val}')
#
#    for possibility_id, (unexpl_dict, new_props) in enumerate(possibilities_with_properties):
#        print(f'\n-----possibility {possibility_id}:\n')
#        print('\n\tunexplaineds:\n')
#        for fid, unexpl_list in unexpl_dict.items():
#            print(f'\t\tframe_{fid}: {unexpl_list}')
#        print('\n\tnew_properties:\n')
#        for fid, props in new_props.items():
#            print(f'\t\tframe_{fid}:\n')
#            for prop_name, val in props.items():
#                print(f'\t\t\t{prop_name}: {val}')
 
    return possibilities_with_properties

def check_not_present(obj, patch, frame_id):

    last_frame_id = obj.frames_id[-1]
    time_diff = frame_id - last_frame_id

    last_properties = dict(obj.properties[last_frame_id])
    
    possible_variations_per_property = {}

    for prop_name, p1 in patch.properties.items():

        dq1_name = f'DQ1({prop_name})'
        
        p0 = last_properties[prop_name]
        diff = p1 - p0
        
        if diff == 0:

            if dq1_name in last_properties:
                dq1_p0 = last_properties[dq1_name]
                
                if dq1_p0 == 0: continue
                else:
                    
                    possible_variations_per_property[prop_name] = [
                        {last_frame_id: {dq1_name: (dq1_p0, 0)}},
                        #{frame_id: {prop_name: -dq1_p0 * time_diff}},
                    ]
            else: continue
        
        else:

            if dq1_name in last_properties:
                dq1_p0 = last_properties[dq1_name]
                
                if dq1_p0 == diff: continue

                else:

                    possible_variations_per_property[prop_name] = [
                        {last_frame_id: {dq1_name: (dq1_p0, diff / time_diff)}},
                        {last_frame_id: {dq1_name: (dq1_p0, 0)}, frame_id: {prop_name: (p0, p1)}},
                        {frame_id: {prop_name: (p0, p1 - p0 + diff)}}
                    ]
            
            else:
                
                possible_variations_per_property[prop_name] = [
                    {last_frame_id: {dq1_name: (None, diff / time_diff)}},
                    {frame_id: {prop_name: (p0, p1)}}
                ]

    scenario_lists = list(possible_variations_per_property.values())
    
    possibilities = []
    for comb in itertools.product(*scenario_lists):

        merged_scenario = {}
        for scenario_dict in comb:

            for frame_key, props_dict in scenario_dict.items():

                if frame_key not in merged_scenario: merged_scenario[frame_key] = {}
                for prop_name, transition in props_dict.items():
                    merged_scenario[frame_key][prop_name] = transition
        
        possibilities.append(merged_scenario)

    possibilities_with_properties = []
    for possibility in possibilities:
        unexplained_dict = {}
        new_properties = {fid: {k: v for k, v in props.items()} for fid, props in obj.properties.items()}
        new_properties[frame_id] = {k: v for k, v in patch.properties.items()}
        for fid, props_change in possibility.items():
            unexplained_dict[fid] = []
            for prop_name, val in props_change.items():
                new_properties[fid][prop_name] = val[1]
                unexplained_dict[fid].append(PropertyChange(prop_name, val[0], val[1]))
        possibilities_with_properties.append((unexplained_dict, new_properties))

#    print('\n\nprevious properties:')
#    for prop_name, val in last_properties.items():
#        print(f'{prop_name}: {val}')
#
#    print('\n\npatch properties:')
#    for prop_name, val in patch.properties.items():
#        print(f'{prop_name}: {val}')
#
#    for possibility_id, (unexpl_dict, new_props) in enumerate(possibilities_with_properties):
#        print(f'\n-----possibility {possibility_id}:\n')
#        print('\n\tunexplaineds:\n')
#        for fid, unexpl_list in unexpl_dict.items():
#            print(f'\t\tframe_{fid}: {unexpl_list}')
#        print('\n\tnew_properties:\n')
#        for fid, props in new_props.items():
#            print(f'\t\tframe_{fid}:\n')
#            for prop_name, val in props.items():
#                print(f'\t\t\t{prop_name}: {val}')
 
    return possibilities_with_properties

# same for this one
def check_multiple_holes_simple(obj, patch, frame_id):

    starting_frame_id = obj.frames_id[-1]
    dummy_object = obj.create_dummy([obj.frames_id[-1]], {obj.frames_id[-1]: obj.sequence[obj.frames_id[-1]]}, obj.properties, obj.rules)

    for i in range(starting_frame_id + 1, frame_id):

        dummy_object.update(i, Patch('dummy', dummy_object.prediction), dummy_object.prediction, [])

    all_ok = True
    for prop_name, value in patch.properties.items():
        if dummy_object.prediction[prop_name] != value:
            all_ok = False
            break

    if all_ok: return True, {frame_id: [Appearance(frame_id)]}, dummy_object.prediction
    else: return False, None, None

# same for this one
def check_multiple_holes_speed(obj, patch, frame_id):

    dummy_object = obj.create_dummy([obj.frames_id[-1]], {obj.frames_id[-1]: obj.sequence[obj.frames_id[-1]]}, obj.properties, obj.rules)

    starting_frame_id = obj.frames_id[-1]
    last_patch = obj.sequence[obj.frames_id[-1]]
    last_properties = {k: v for k, v in obj.properties[obj.frames_id[-1]].items()}
    last_properties[Speed_x] = Speed_x.compute(last_patch, patch) / (frame_id - starting_frame_id)
    last_properties[Speed_y] = Speed_y.compute(last_patch, patch) / (frame_id - starting_frame_id)

    for i in range(starting_frame_id + 1, frame_id):

        dummy_object.update(i, Patch('dummy', dummy_object.prediction), dummy_object.prediction, [])

    all_ok = True
    for prop_name, value in patch.properties.items():
        if dummy_object.prediction[prop_name] != value:
            all_ok = False
            break

    if all_ok: return True, {starting_frame_id: [PropertyChange(Speed_x, obj.properties[obj.frames_id[-1]][Speed_x], dummy_object.prediction[Speed_x]), PropertyChange(Speed_y, obj.properties[obj.frames_id[-1]][Speed_y], dummy_object.prediction[Speed_y])], frame_id: Appearance()}, dummy_object.prediction
    else: return False, None, None


# same
def check_blink(obj, patch, frame_id):

    last_properties = {k: v for k, v in obj.properties[obj.frames_id[-1]].items()}

    for prop_name, value in patch.properties.items():
        last_properties[prop_name] = value

    return True, {frame_id: [Disappearance(), Appearance()]}, last_properties

# same
def check_duplication(obj, patch, frame_id):

    last_properties = {k: v for k, v in obj.properties[obj.frames_id[-1]].items()}

    for prop_name, value in patch.properties.items():
        last_properties[prop_name] = value

    return True, {frame_id: [Duplication(obj)]}, last_properties