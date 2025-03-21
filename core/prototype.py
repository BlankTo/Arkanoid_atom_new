

class Prototype:

    def __init__(self, property_variance_dict, rules, same_shape, signature):

        self.property_variance_dict = {prop_name: variance for prop_name, variance in property_variance_dict.items()}

        self.rules = rules[:]

        self.same_shape = same_shape

        self.signature = signature

    def copy(self):
        return Prototype(self.property_variance_dict, self.rules, self.same_shape, self.signature)

    def test(self, obj, debug= False):

        score = 0

        for prop_name in obj.properties[obj.frames_id[-1]].keys():
            variance = False
            for i_fid in range(len(obj.frames_id) - 1):
                if prop_name in obj.properties[obj.frames_id[i_fid]].keys():
                    if obj.properties[obj.frames_id[i_fid]][prop_name] != obj.properties[obj.frames_id[i_fid + 1]][prop_name]:
                        variance = True
                        break
                elif prop_name in obj.properties[obj.frames_id[i_fid + 1]].keys():
                    variance = True
                    break
            if prop_name in self.property_variance_dict.keys():
                if self.property_variance_dict[prop_name] != variance:
                    if variance:
                        return False, -100
                    else:
                        score -= 1
                elif variance:
                    score += 1
            else:
                return False, -100
            
        #

        if debug and 'paddle' in obj.sequence[0].description: debug_in= True
        else: debug_in= False

        if debug_in:
            print('================================================================================================================================')
            print(f'{obj.sequence[0].description}')
            print('properties:')
            for frame_id, props in obj.properties.items():
                print(f'\tframe_{frame_id}')
                for prop_name, value in props.items():
                    print(f'\t\t{prop_name}: {value}')
            print(f'against prototype {self.property_variance_dict}')
            print('================================================================================================================================')

        for cf in obj.frames_id:
            if debug_in: print(f'\n-----\ncf: {cf}')
            for rule in self.rules:
                if debug_in: print(f'\n=================\nchecking rule: {rule.my_hash()}')
                triggered, effects, cause_offset = rule.trigger(obj, cf, debug= debug_in)
                if debug_in: print(f'triggered: {triggered} - effects: {effects} - cause_offset: {cause_offset}')
                if triggered:
                    ef = cf + cause_offset
                    if ef <= obj.frames_id[-1]:
                        if debug_in:
                            print(f'\n-----\nef: {ef}')
                            print(f'unexplaineds: {obj.unexplained}')
                        if ef in obj.unexplained.keys():
                            if debug_in: print(f'result: {all(any(effect.test(unexpl) for unexpl in obj.unexplained[ef]) for effect in effects)} -')
                            if all(any(effect.test(unexpl) for unexpl in obj.unexplained[ef]) for effect in effects):
                                score += 10
                            else:
                                if debug_in: print('result: False --')
                                return False, -100
                        else:
                            if debug_in: print('result: False ---')
                            return False, -100
                    else:
                        print('no data yet - end of frames_id')
        
        return True, score