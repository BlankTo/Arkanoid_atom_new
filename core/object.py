from core.unexplained import NumericalUnexplainedPhenomenon
from utils import equal_collections
from core.events import event_pool

class Object:

    def __init__(self, reference_id, frames_id, sequence, properties= {}, unexplained= {}, events= {}, global_events= {}):
        
        self.reference_id = reference_id

        self.frames_id = frames_id[:]

        self.sequence = {fid: p for fid, p in sequence.items()}

        self.properties = {fid: {k: v for k, v in prop.items()} for fid, prop in properties.items()}

        self.unexplained = {fid: [ex.copy() for ex in v_list] for fid, v_list in unexplained.items()}

        self.events = {fid: [ev for ev in v_list] for fid, v_list in events.items()}

        self.global_events = {fid: [ev.copy() for ev in v_list] for fid, v_list in global_events.items()}

        #self.causes = causes
        #self.effects = effects
        #
        #if cause_effect_last_check < frames_id[-1]:
        #   
        #    #TODO gestire strutture dati per regole qui e in aggiornamenti update, unexplaineds e global events
        #
        #    pass


    def copy(self):
        return Object(self.reference_id, self.frames_id, self.sequence, self.properties, self.unexplained, self.events, self.global_events)


    def add_unexplained(self, unexplained_dict):
        for frame_id, unexplained in unexplained_dict.items():
            if frame_id in self.unexplained.keys(): self.unexplained[frame_id].extend([ex.copy() for ex in unexplained])
            else: self.unexplained[frame_id] = [ex.copy() for ex in unexplained]

    def add_global_events(self, new_global_events, frame_id):
        if frame_id in self.global_events.keys(): self.global_events[frame_id].extend(new_global_events)
        else: self.global_events[frame_id] = new_global_events[:]
    
    def create_dummy(self, frames_id, sequence, properties):
        return Object(-1, frames_id, sequence, properties, {}, {}, {})

    def predict(self, current_frame_id, rules):

        new_properties = {prop_name: value for prop_name, value in self.properties[current_frame_id].items()}

        predicted_events = []
        for rule in rules:
            triggered, effects, _ = rule.trigger(self, current_frame_id - rule.cause_offset)
            if triggered:
                for effect in effects:
                    if isinstance(effect, NumericalUnexplainedPhenomenon):
                        prop_name = effect.prop_name
                        if prop_name in new_properties: new_properties[prop_name] = effect.a * new_properties[prop_name] + effect.b
                        elif effect.a == 0: new_properties[prop_name] = effect.b
                        else:
                            print('to be corrected')
                            exit()
                    else:
                        predicted_events.append(effect)

        new_new_properties = {prop_name: value for prop_name, value in new_properties.items()}

        for prop_name in new_properties.keys():

            n_d = prop_name.count('DQ1')

            dq1_name = prop_name
            while n_d:
                in_prop_name = dq1_name[4:-1]
                new_new_properties[in_prop_name] += new_properties[dq1_name]
                dq1_name = in_prop_name
                n_d -= 1

        return new_new_properties, predicted_events
    

    def update(self, frame_id, patch, new_properties, other_patches, new_unexplained):

        self.frames_id.append(frame_id)
        self.sequence[frame_id] = patch 
        self.properties = {fid: {k: v for k, v in props.items()} for fid, props in new_properties.items()}

        previous_patch = self.sequence[frame_id - 1] if (frame_id - 1) in self.sequence.keys() else None

        new_events = []
        for event in event_pool:
            if event.check(previous_patch, patch, other_patches):
                new_events.append(event)
        self.events[frame_id] = new_events
        
        for frame_id, unexplained in new_unexplained.items():
            if frame_id in self.unexplained.keys(): self.unexplained[frame_id].extend([ex.copy() for ex in unexplained])
            else: self.unexplained[frame_id] = [ex.copy() for ex in unexplained]

    def get_signature(self):

        #TODO improve

        obj_signature = ''
        for fid, props in self.properties.items():
            obj_signature += f'_f{fid}'
            for prop_name, val in sorted(props.items(), key= lambda x: x[0]):
                obj_signature += f'_{prop_name}:{val}'
        for fid, unexpl_list in sorted(self.unexplained.items(), key= lambda x: x[0]):
            obj_signature += f'_f{fid}'
            for unexpl_hash in sorted(unexpl.__repr__() for unexpl in unexpl_list):
                obj_signature += f'_{unexpl_hash}'

        return obj_signature


    def __eq__(self, other):
        
        if isinstance(other, Object):
            if set(self.frames_id) != set(other.frames_id): return False
            if not equal_collections(self.sequence, other.sequence): return False
            if not equal_collections(self.unexplained, other.unexplained): return False
            return True

    def __repr__(self):
        ss = f'['
        for frame_id, patch in self.sequence.items():
            ss += f'{frame_id}: {patch.description}, '
        ss += f']\nreference_id: {self.reference_id}'
        ss += '\nlast properties: {'
        for prop_name, val in self.properties[self.frames_id[-1]].items():
            ss += f'({prop_name}: {val})'
        ss += '}\nunexplaineds: {'
        for frame_id, unexpl in self.unexplained.items():
            ss += f'{frame_id}: {unexpl} |'
        ss += '}\nevents: {'
        for frame_id, ev in self.events.items():
            ss += f'{frame_id}: {ev} |'
        ss += '}\nglobal events: {'
        for frame_id, ev in self.global_events.items():
            ss += f'{frame_id}: {ev} |'
        ss += '}'
        return ss