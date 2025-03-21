from heuristic.heuristic import Heuristic
from utils import load_patches_per_frame
from utils import debug_patches_per_frame

def main():

    simple_arkanoid_log_file_name = 'arkanoid_log_2025_02_07_16_03_00.pkl'
    complete_arkanoid_long_lose_log_file_name = 'arkanoid_log_2025_02_18_16_14_06.pkl'
    complete_arkanoid_short_lose_log_file_name = 'arkanoid_log_2025_02_18_16_18_28.pkl'
    complete_arkanoid_win_log_file_name = 'arkanoid_log_2025_02_07_15_44_51.pkl'
    complete_arkanoid_win_2_log_file_name = 'arkanoid_log_2025_02_07_10_58_26.pkl'
    complete_arkanoid_win_3_log_file_name = 'arkanoid_log_2025_02_18_16_17_03.pkl'
    
    #patches_per_frame, global_events_per_frame = load_patches_per_frame(None) # last log

    #patches_per_frame = debug_patches_per_frame
    #global_events_per_frame = [[] for _ in range(len(debug_patches_per_frame))]

    #patches_per_frame, global_events_per_frame = load_patches_per_frame(simple_arkanoid_log_file_name)

    #patches_per_frame, global_events_per_frame = load_patches_per_frame(complete_arkanoid_short_lose_log_file_name)
    
    #patches_per_frame, global_events_per_frame = load_patches_per_frame(complete_arkanoid_long_lose_log_file_name)

    patches_per_frame, global_events_per_frame = load_patches_per_frame(complete_arkanoid_win_log_file_name)

    #patches_per_frame, global_events_per_frame = load_patches_per_frame(complete_arkanoid_win_2_log_file_name)

    #patches_per_frame, global_events_per_frame = load_patches_per_frame(complete_arkanoid_win_log_file_name)

    ################################################################################
    ################################################################################
    ################################################################################

    patches_frame_0 = patches_per_frame[0]
    patches_frame_1 = patches_per_frame[1]
    global_events_frame_0 = global_events_per_frame[0]
    global_events_frame_1 = global_events_per_frame[1]
    
    heu = Heuristic()

    heu.heuristic_initialization(patches_frame_0, global_events_frame_0)

    for frame_id in range(1, len(patches_per_frame)):
        new_patches = patches_per_frame[frame_id]
        new_global_events = global_events_per_frame[frame_id]
        
        #heu.frame_by_frame(frame_id, new_patches, new_global_events, debug= True)
        heu.frame_by_frame(frame_id, new_patches, new_global_events)
        print(f'\n==================================\nframe {frame_id} -> n° individuals: {len(heu.population)}')
        for ind_id, ind in heu.population.items():
            print(f'\nind_{ind_id}')
            ball_inside = False
            for obj_id, obj in ind.present_objects.items():
                same_description = True
                description = None
                for p in obj.sequence.values():
                    if description is None: description = p.description
                    if p.description != description:
                        same_description = False
                        break
                if not same_description: print(f'\n(ind_{ind_id}, obj_{obj_id}, present): different descriptions in sequence')
                if any('ball' in p.description for p in obj.sequence.values()):
                #if any('ball' in p.description or 'paddle' in p.description for p in obj.sequence.values()):
                    print(f'(obj_{obj_id}, present): {[(fid, p.description) for fid, p in obj.sequence.items()]}')
                    print(f'(obj_{obj_id}, present) with rules: {[r.my_hash() for r in ind.prototypes[ind.obj_to_proto[obj_id]].rules]}')
                    ball_inside = True
                #print(f'\n\t{[(fid, p.description) for fid, p in obj.sequence.items()]}')
                #print(f'\twith rules: {[r.my_hash() for r in ind.prototypes[ind.obj_to_proto[obj_id]].rules]}')
            for obj_id, obj in ind.not_present_objects.items():
                same_description = True
                description = None
                for p in obj.sequence.values():
                    if description is None: description = p.description
                    if p.description != description:
                        same_description = False
                        break
                if not same_description: print(f'\n(ind_{ind_id}, obj_{obj_id}, not_present): different descriptions in sequence')
                if any('ball' in p.description for p in obj.sequence.values()):
                #if any('ball' in p.description or 'paddle' in p.description for p in obj.sequence.values()):
                    print(f'(obj_{obj_id}, not_present): {[(fid, p.description) for fid, p in obj.sequence.items()]}')
                    print(f'(obj_{obj_id}, not_present) with rules: {[r.my_hash() for r in ind.prototypes[ind.obj_to_proto[obj_id]].rules]}')
                    ball_inside = True
                #print(f'\n\t{[(fid, p.description) for fid, p in obj.sequence.items()]}')
                #print(f'\twith rules: {[r.my_hash() for r in ind.prototypes[ind.obj_to_proto[obj_id]].rules]}')
            if not ball_inside:
                print(f'no ball inside in ind_{ind_id} at frame {frame_id}')
                exit()
        
        if frame_id == 2:

            print(f'\nn° individuals: {len(heu.population)}')
            exit()

    heu.summarize_prototypes()

if __name__ == "__main__":
    main()
