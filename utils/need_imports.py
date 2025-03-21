import os
import pickle

from core.patch import Patch
from core.property import Pos_x, Pos_y, Shape_x, Shape_y

from core.events import GlobalEvent, CommandEvent

############

DESCRIPTIONS_TO_EXCLUDE = ['environment']

# future update: a method to extract patches with properties from images instead of convert_properties 

def convert_properties(elem_props):

    #properties = {prop_name: val for prop_name, val in elem_props.items()}

    properties = {
        'pos_x': elem_props['pos_x'],
        'pos_y': elem_props['pos_y'],
        'shape_x': elem_props['pos_x'] - elem_props['hitbox_tl_x'],
        'shape_y': elem_props['pos_y'] - elem_props['hitbox_tl_y'],
    }

    #properties = {
    #    Pos_x: elem_props['pos_x'],
    #    Pos_y: elem_props['pos_y'],
    #    Shape_x: elem_props['pos_x'] - elem_props['hitbox_tl_x'],
    #    Shape_y: elem_props['pos_y'] - elem_props['hitbox_tl_y'],
    #}

    return properties
    
def load_patches_per_frame(log_file_name= None, ):

    if log_file_name is None: # use last saved
        log_files_name = os.listdir('logs/arkanoid_logs')
        if not log_files_name: raise Exception('no saved logs')
        log_file_name = sorted(log_files_name, reverse= True)[0]

    log_file_path = f'logs/arkanoid_logs/{log_file_name}'
    with open(log_file_path, 'rb') as log_file:
        log = pickle.load(log_file)
    print(f'{log_file_path} loaded')

    patches_per_frame = []
    global_events_per_frame = []
    for frame in log:

        patches, global_events = convert_single_frame(frame['elements'], frame['events'], frame['commands'])
        patches_per_frame.append(patches)
        global_events_per_frame.append(global_events)

    return patches_per_frame, global_events_per_frame

def convert_single_frame(elements, event_log, command_log):

    patches = []
    for description, elem_props in elements.items():
        if description in DESCRIPTIONS_TO_EXCLUDE or elem_props['existence'] == False: continue
        
        patches.append(Patch(description, convert_properties(elem_props)))

    global_events = [CommandEvent(com) for com in command_log]
    global_events.extend([GlobalEvent(ev['description']) for ev in event_log])

    return patches, global_events

