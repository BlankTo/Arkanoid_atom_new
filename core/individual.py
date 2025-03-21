import itertools
from core.object import Object
from core.prototype import Prototype
from core.rule import new_infer_rules
from core.unexplained import Appearance, check_disappearance, check_not_present, check_present
from utils.various import ID_generator
from itertools import combinations, permutations

def generate_partial_biunivocal_assignments(objects, patches):
    n_objects = len(objects)
    all_assignments = []
    
    # Generate all possible assignments including partial assignments
    for k in range(1, n_objects + 1):  # Allow up to all objects being assigned
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

class Individual:

    def __init__(self, present_objects, not_present_objects, prototypes, obj_to_proto, proto_to_objs, run_id, last_frame_id, survival_left, unassigned_present_objects= [], unassigned_not_present_objects= [], unassigned_patches= [], latest_patches= {}, score= 0):

        self.reference_id_generator = ID_generator(max(obj.reference_id for obj in (present_objects | not_present_objects).values() if obj.reference_id is not None))
        self.obj_id_generator = ID_generator(max(obj_id for obj_id in (present_objects | not_present_objects).keys()))
        self.proto_id_generator = ID_generator(max(proto_id for proto_id in prototypes.keys()))

        self.present_objects = {obj_id: obj.copy() for obj_id, obj in present_objects.items()} # dict obj_id: obj
        self.not_present_objects = {obj_id: obj.copy() for obj_id, obj in not_present_objects.items()} # dict obj_id: obj

        self.prototypes = {proto_id: proto.copy() for proto_id, proto in prototypes.items()}
        self.obj_to_proto = obj_to_proto.copy()
        self.proto_to_objs = {proto_id: obj_id_list[:] for proto_id, obj_id_list in proto_to_objs.items()}

        self.latest_patches = {pid: patch for pid, patch in latest_patches.items()}
        self.unassigned_present_objects = unassigned_present_objects[:]
        self.unassigned_not_present_objects = unassigned_not_present_objects[:]
        self.unassigned_patches = unassigned_patches[:]

        self.run_id = run_id

        self.last_frame_id = last_frame_id

        self.survival_left = survival_left

        self.score = score


    def copy(self):
        return Individual(self.present_objects, self.not_present_objects, self.prototypes, self.obj_to_proto, self.proto_to_objs, self.run_id, self.last_frame_id, self.survival_left, self.unassigned_present_objects, self.unassigned_not_present_objects, self.unassigned_patches, self.latest_patches, self.score)


    def reset_unassigned(self, new_patches):
        patch_id_generator = ID_generator()
        self.latest_patches = {patch_id_generator(): patch for patch in new_patches}
        self.unassigned_present_objects = [obj_id for obj_id in self.present_objects.keys()]
        self.unassigned_not_present_objects = [obj_id for obj_id in self.not_present_objects.keys()]
        self.unassigned_patches = [patch_id for patch_id in self.latest_patches.keys()]


    def add_global_events(self, new_global_events, frame_id):
        for obj in (self.present_objects | self.not_present_objects).values(): obj.add_global_events(new_global_events, frame_id)


    def manual_association(self, obj_id, patch_id, frame_id, new_properties, new_unexplained= {}, not_present= False):

        if not_present: current_object = self.not_present_objects[obj_id]
        else:current_object = self.present_objects[obj_id]

        current_object.update(
            frame_id,
            patch= self.latest_patches[patch_id],
            new_properties= new_properties,
            other_patches= [p for p_id, p in self.latest_patches.items() if p_id != patch_id],
            new_unexplained= new_unexplained,
            )
        
        if not_present: self.unassigned_not_present_objects.remove(obj_id)
        else: self.unassigned_present_objects.remove(obj_id)
        self.unassigned_patches.remove(patch_id)


    def prediction_phase(self, frame_id):

        patch_assignment = {}

        tmp_unassigned_present_objects = self.unassigned_present_objects[:]
        for obj_id in tmp_unassigned_present_objects:
            obj = self.present_objects[obj_id]

            prediction, _ = obj.predict(frame_id - 1, self.prototypes[self.obj_to_proto[obj_id]].rules)

            for patch_id in self.unassigned_patches:
                patch = self.latest_patches[patch_id]

                all_ok = True
                for prop_name, value in patch.properties.items():

                    if prediction[prop_name] != value:
                        all_ok = False
                
                if all_ok: # if an object prediction correctly identifies a patch, then that patch is assigned to the object and marked as assigned for the individuals with that object
                    if patch_id in patch_assignment.keys(): patch_assignment[patch_id].append((obj_id, prediction))
                    else: patch_assignment[patch_id] = [(obj_id, prediction)]


        overlapping_predictions = {}
        for patch_id, possible_assignments in patch_assignment.items():

            if len(possible_assignments) == 0: continue # patch is not assigned
            
            if len(possible_assignments) == 1: # patch is assigned to the only object that predict it

                current_obj = self.present_objects[possible_assignments[0][0]]

                prediction_score = 1 # base for correct prediction

                new_properties = {fid: {k: v for k, v in props.items()} for fid, props in current_obj.properties.items()}
                new_properties[frame_id] = possible_assignments[0][1]

                for prop_name, val in new_properties[frame_id].items():
                    if prop_name in new_properties[frame_id - 1]:
                        if new_properties[frame_id - 1][prop_name] != val: prediction_score += 1 # correctly predicted a variation
                    else: prediction_score += 1 # correctly predicted a new prop

                self.score += prediction_score

                current_obj.update(
                    frame_id,
                    patch= self.latest_patches[patch_id],
                    new_properties= new_properties,
                    other_patches= [p for p_id, p in self.latest_patches.items() if p_id != patch_id],
                    new_unexplained= {},
                    )
                
                self.unassigned_present_objects.remove(possible_assignments[0][0])
                self.unassigned_patches.remove(patch_id)
            
            else: # multiple objects predict the same patch -> splitting

                overlapping_predictions[patch_id] = possible_assignments

        new_inds = []
        if len(overlapping_predictions) == 1:

            patch_id, possible_assignments = next(iter(overlapping_predictions.items()))

            for obj_id, prediction in possible_assignments:

                new_ind = self.copy()

                current_obj = self.present_objects[obj_id]

                new_properties = {fid: {k: v for k, v in props.items()} for fid, props in current_obj.properties.items()}
                new_properties[frame_id] = prediction

                new_ind.manual_association(obj_id, patch_id, frame_id, new_properties)

                new_inds.append(new_ind)

        elif len(overlapping_predictions) > 1:

            #TODO overlapping e prediction_score per overlapping

            print('elif len(overlapping_predictions) > 1')
            exit(0)

        return new_inds

    
    def pairing_phase(self, frame_id):

        possible_assignments = generate_partial_biunivocal_assignments(self.unassigned_present_objects, self.unassigned_patches)

        new_inds = []
        for pa in possible_assignments:

            pa_combinations = {}

            for obj_id, patch_id in pa:
                if (obj_id is not None) and (patch_id is not None):

                    pa_combinations[(obj_id, patch_id)] = []

                    possibilities_with_properties = check_present(self.present_objects[obj_id], self.latest_patches[patch_id], frame_id)
                    for pwp in possibilities_with_properties:
                        pa_combinations[(obj_id, patch_id)].append(pwp)
            
            pa_keys = list(pa_combinations.keys())
            pwp_list = [pa_combinations[pa_key] for pa_key in pa_keys]

            pa_pwp = []
            for comb in itertools.product(*pwp_list):
                paired = list(zip(pa_keys, comb))
                pa_pwp.append(paired)

            for possibility in pa_pwp:

                new_ind = self.copy()

                pairing_score = 0

                for (obj_id, patch_id), (unexplained_dict, new_properties) in possibility:

                    new_ind.manual_association(obj_id, patch_id, frame_id, new_properties, unexplained_dict)

                    for unexpl_list in unexplained_dict.values():
                        pairing_score -= len(unexpl_list)

                new_ind.score += pairing_score

                new_inds.append(new_ind)

        return new_inds
    
    def new_objects_for_unassigned_patches(self, frame_id):

        for patch_id in self.unassigned_patches:
            patch = self.latest_patches[patch_id]

            new_obj_id = self.obj_id_generator()
            new_obj = Object(None, [frame_id], {frame_id: patch}, {frame_id: patch.properties}, {}, {frame_id: [Appearance()]}, {frame_id: next(iter(self.present_objects.values())).global_events[frame_id]})

            all_props = set()
            for fid in new_obj.frames_id:
                all_props.update(new_obj.properties[fid].keys())

            #TODO improve it, this is tmp

            chosen_proto_id = None
            for proto_id, proto in self.prototypes.items():

                same_props = True
                for prop_name in proto.property_variance_dict.keys():
                    if prop_name not in all_props:
                        same_props = False
                        break

                if same_props:
                    if len(proto.rules) == 0:
                        chosen_proto_id = proto_id
                        break

            if chosen_proto_id is None:
                
                chosen_proto_id = self.proto_id_generator()
                proto_signature = ''
                for prop_name in sorted(all_props): proto_signature += f'_{prop_name}_F'
                proto_signature += '' # no rules
                proto_signature += '_sameshape_F'
                self.prototypes[chosen_proto_id] = Prototype(
                    property_variance_dict= {prop_name: False for prop_name in all_props},
                    rules= [],
                    same_shape= False,
                    signature= proto_signature
                )
            
            self.obj_to_proto[new_obj_id] = chosen_proto_id
            if chosen_proto_id in self.proto_to_objs.keys(): self.proto_to_objs[chosen_proto_id].append(new_obj_id)
            else: self.proto_to_objs[chosen_proto_id] = [new_obj_id]
                
            self.present_objects[new_obj_id] = new_obj

            self.score -= 1

    def remaining_phase(self, frame_id):

        remaining_score = 0

        tmp_unassigned_present_objects = self.unassigned_present_objects[:]
        for obj_id in tmp_unassigned_present_objects:

            unexplained_dict = check_disappearance(frame_id)
            disappearing_obj = self.present_objects.pop(obj_id)
            disappearing_obj.add_unexplained(unexplained_dict)
            self.not_present_objects[obj_id] = disappearing_obj
            self.unassigned_present_objects.remove(obj_id)

            for unexpl_list in unexplained_dict.values():
                        remaining_score -= len(unexpl_list)
        
        possible_reappearings = generate_partial_biunivocal_assignments(self.unassigned_not_present_objects, self.unassigned_patches)

        new_inds = []
        for pr in possible_reappearings:

            pr_combinations = {}

            for obj_id, patch_id in pr:
                if (obj_id is not None) and (patch_id is not None):

                    pr_combinations[(obj_id, patch_id)] = []

                    possibilities_with_properties = check_not_present(self.not_present_objects[obj_id], self.latest_patches[patch_id], frame_id)
                    for pwp in possibilities_with_properties:
                        pr_combinations[(obj_id, patch_id)].append(pwp)
            
            pr_keys = list(pr_combinations.keys())
            pwp_list = [pr_combinations[pr_key] for pr_key in pr_keys]

            pr_pwp = []
            for comb in itertools.product(*pwp_list):
                paired = list(zip(pr_keys, comb))
                pr_pwp.append(paired)

            for possibility in pr_pwp:

                new_ind = self.copy()

                new_remaining_score = remaining_score

                for (obj_id, patch_id), (unexplained_dict, new_properties) in possibility:
                    new_ind.manual_association(obj_id, patch_id, frame_id, new_properties, unexplained_dict, not_present= True)

                    for unexpl_list in unexplained_dict.values():
                        new_remaining_score -= len(unexpl_list)

                new_ind.score += new_remaining_score

                new_inds.append(new_ind)

        self.score += remaining_score

        for ind in new_inds + [self]:
            ind.new_objects_for_unassigned_patches(frame_id)

        return new_inds
    
    def prototype_phase(self, frame_id):

        for obj_id, obj in self.present_objects.items():

            obj_rule_score = new_infer_rules(obj, frame_id)

            new_rule_hashes = []
            for rule, _ in obj_rule_score:
                rule_hash = rule.my_hash()
                if rule_hash not in new_rule_hashes: new_rule_hashes.append(rule_hash)
            new_rule_hashes = sorted(new_rule_hashes)

            current_proto_id = self.obj_to_proto[obj_id]
            current_proto = self.prototypes[current_proto_id]

            proto_rule_hashes = []
            for rule in current_proto.rules:
                rule_hash = rule.my_hash()
                if rule_hash not in proto_rule_hashes: proto_rule_hashes.append(rule_hash)
            proto_rule_hashes = sorted(proto_rule_hashes)

            if len(new_rule_hashes) == len(proto_rule_hashes):
                same_rules = True
                for nr, pr in zip(new_rule_hashes, proto_rule_hashes):
                    if nr != pr: same_rules = False
                    break
            else: same_rules = False

            
            all_props = set()
            for fid in obj.frames_id:
                all_props.update(obj.properties[fid].keys())
            
            prop_variance = {}
            for prop_class in all_props:
                variance = False
                for i_fid in range(len(obj.frames_id) - 1):
                    if prop_class not in obj.properties[obj.frames_id[i_fid]]:
                        if prop_class in obj.properties[obj.frames_id[i_fid + 1]]:
                            if obj.properties[obj.frames_id[i_fid + 1]][prop_class] != 0:
                                variance = True
                                break
                    elif prop_class in obj.properties[obj.frames_id[i_fid + 1]]:
                        if obj.properties[obj.frames_id[i_fid]][prop_class] != obj.properties[obj.frames_id[i_fid + 1]][prop_class]:
                            variance = True
                            break
                prop_variance[prop_class] = variance

            same_variance = True
            for prop_name, new_variance in prop_variance.items():
                if prop_name not in current_proto.property_variance_dict:
                    same_variance = False
                    break
                elif new_variance != current_proto.property_variance_dict[prop_name]:
                    same_variance = False
                    break

            if same_rules and same_variance: continue

            proto_signature = ''
            for prop_name, variance in sorted(prop_variance.items(), key= lambda x: x[0]): proto_signature += f'_{prop_name}_{"T" if variance else "F"}'
            for rule_hash in new_rule_hashes: proto_signature += f'_{rule_hash}'
            proto_signature += '_sameshape_F'

            objs_assigned_to_proto = self.proto_to_objs[current_proto_id]

            if len(objs_assigned_to_proto) == 1:

                current_proto.rules = [rule for rule, _ in obj_rule_score]
                current_proto.property_variance_dict = prop_variance
                current_proto.signature = proto_signature

            else:
                
                new_proto_id = self.proto_id_generator()
                self.prototypes[new_proto_id] = Prototype(
                    property_variance_dict= {prop_name: variance for prop_name, variance in prop_variance.items()},
                    rules= [rule for rule, _ in obj_rule_score],
                    same_shape= False,
                    signature= proto_signature
                )
                self.obj_to_proto[obj_id] = new_proto_id
                self.proto_to_objs[current_proto_id].remove(obj_id)
                self.proto_to_objs[new_proto_id] = [obj_id]

        return []


    def prototype_phase_real(self, frame_id):

        #TODO aggiornamento o separazione prototipi

        pass


    def get_signature(self):

        #TODO improve signature, now it's tmp

        obj_signatures = []
        for obj in (self.present_objects | self.not_present_objects).values():
            obj_signatures.append(obj.get_signature())
        obj_signatures = sorted(obj_signatures)

        proto_signatures = sorted(proto.signature for proto in self.prototypes.values())

        ind_signature = ''
        for obj_signature in obj_signatures: ind_signature += f'_{obj_signature}'
        for proto_signature in proto_signatures: ind_signature += f'_{proto_signature}'

        return ind_signature