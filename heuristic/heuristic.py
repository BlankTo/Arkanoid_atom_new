from core.individual import Individual
from core.object import Object
from core.prototype import Prototype
from utils.various import ID_generator

SURVIVAL_TIME = 2

class Heuristic():


    def __init__(self):

        self.ind_id_generator = ID_generator()

        self.population = None


    def heuristic_initialization(self, patches_frame_0, global_events_frame_0, debug= False):

        if debug: print(' - initialization start - ')

        obj_id_generator = ID_generator()
        reference_id_generator = ID_generator()

        # initialization with one object per patch in the first frame

        present_objects = {obj_id_generator(): Object(reference_id= reference_id_generator(), frames_id= [0], sequence= {0: patch}, properties= {0: patch.properties}, global_events= {0: global_events_frame_0}) for patch in patches_frame_0} # dict obj_id: obj
        not_present_objects = {} # dict obj_id: obj

        prop_hash_to_prop = {}
        for obj_id, obj in present_objects.items():
            prop_hash = tuple([prop_name for prop_name in obj.properties[0].keys()])
            if prop_hash in prop_hash_to_prop.keys(): prop_hash_to_prop[prop_hash][1].append(obj_id)
            else: prop_hash_to_prop[prop_hash] = ([prop_name for prop_name in obj.properties[0].keys()], [obj_id])

        obj_to_proto = {}
        proto_to_objs = {}
        prototypes = {}
        for (prop_name_list, obj_id_list) in prop_hash_to_prop.values():
            proto_id = len(prototypes)
            proto_signature = ''
            for prop_name in sorted(prop_name_list): proto_signature += f'_{prop_name}_F'
            proto_signature += '' # no rules
            proto_signature += '_sameshape_F'
            prototypes[proto_id] = Prototype(
                property_variance_dict= {prop_name: False for prop_name in prop_name_list},
                rules= [],
                same_shape= False,
                signature= proto_signature
                )
            for obj_id in obj_id_list:
                obj_to_proto[obj_id] = proto_id
            proto_to_objs[proto_id] = obj_id_list[:]
        
        self.population = {self.ind_id_generator(): Individual(present_objects, not_present_objects, prototypes, obj_to_proto, proto_to_objs, run_id= 0, last_frame_id= 0, survival_left= SURVIVAL_TIME)}

        if debug:
            print(' - prediction phase end - ')
            print(f'\nn° individuals: {len(self.population)}')
            print('\nPopulation:')
            for ind_id, ind in self.population.items():
                print(f'\n\tind_{ind_id}:')
                for obj_id, obj in (ind.present_objects | ind.not_present_objects).items():
                    print(f'\n\t\tobj_{obj_id}:')
                    print(obj)
                for proto_id, proto in ind.prototypes.items():
                    print(f'\n\t\tproto_{proto_id}:')
                    print(proto)

    def heuristic_initialization_from_prototypes(patches_frame_0, patches_frame_1, global_events_frame_0, global_events_frame_1, prototypes):

        pass


    def cleaning_phase(self):

        inds_to_remove = []
        seen_signatures = []
        for ind_id, ind in self.population.items():

            #consistent, ind_signature = ind.check_consistency()
            #if (not consistent) or ind_signature in seen_signatures: inds_to_remove.append(ind_id)

            ind_signature = ind.get_signature()

            if ind_signature in seen_signatures: inds_to_remove.append(ind_id)
            else: seen_signatures.append(ind_signature) 
        
        for ind_id in inds_to_remove: self.population.pop(ind_id)


    def pruning_phase(self):

        best_score = max(ind.score for ind in self.population.values())

        inds_to_remove = []
        for ind_id, ind in self.population.items():
            if ind.score < best_score:
                ind.survival_left -= 1
                if ind.survival_left < 0: inds_to_remove.append(ind_id)
        
        for ind_id in inds_to_remove: self.population.pop(ind_id)


    def frame_by_frame(self, frame_id, new_patches, new_global_events, debug= False):

        for ind in self.population.values():
            ind.reset_unassigned(new_patches)
            ind.add_global_events(new_global_events, frame_id)

        # Prediction Phase

        if debug: print(' - starting prediction phase - ')

        new_inds = []
        for ind in self.population.values(): new_inds.extend(ind.prediction_phase(frame_id))

        self.population |= {self.ind_id_generator(): new_ind for new_ind in new_inds}

        if debug:
            print('\n==========================\n - prediction phase end - ')
            print(f'\nn° individuals: {len(self.population)}')
            print('\nPopulation:')
            for ind_id, ind in self.population.items():
                print(f'\n\tind_{ind_id}:')
                for obj_id, obj in (ind.present_objects | ind.not_present_objects).items():
                    print(f'\n\t\tobj_{obj_id}:')
                    print(obj)
                for proto_id, proto in ind.prototypes.items():
                    print(f'\n\t\tproto_{proto_id}:')
                    print(proto)


        # Pairing Phase

        new_inds = []
        for ind in self.population.values(): new_inds.extend(ind.pairing_phase(frame_id))
        
        self.population |= {self.ind_id_generator(): new_ind for new_ind in new_inds}

        if debug:
            print('\n==========================\n - pairing phase end - ')
            print(f'\nn° individuals: {len(self.population)}')
            print('\nPopulation:')
            for ind_id, ind in self.population.items():
                print(f'\n\tind_{ind_id}:')
                for obj_id, obj in (ind.present_objects | ind.not_present_objects).items():
                    if obj.sequence[0].description == 'ball':
                        print(f'\n\t\tobj_{obj_id}:')
                        print(obj)
                #for proto_id, proto in ind.prototypes.items():
                #    print(f'\n\t\tproto_{proto_id}:')
                #    print(proto)
        
        # Remaining Phase

        new_inds = []
        for ind in self.population.values(): new_inds.extend(ind.remaining_phase(frame_id))
        
        self.population |= {self.ind_id_generator(): new_ind for new_ind in new_inds}

        # Prototype Phase

        new_inds = []
        for ind in self.population.values(): new_inds.extend(ind.prototype_phase(frame_id))
        
        self.population |= {self.ind_id_generator(): new_ind for new_ind in new_inds}

        # Cleaning Phase

        self.cleaning_phase()

        # Pruning Phase

        self.pruning_phase()

    def summarize_prototypes(self):

        #TODO

        print('def summarize_prototypes(self):')
        exit(0)