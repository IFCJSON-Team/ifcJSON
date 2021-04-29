import json
import copy

import ifcjson

in_file_path = "../Samples/IFC_2x3/Duplex_layer4.json"
out_file_path = "../Samples/IFC_2x3/Duplex_layer5.json"

def remove_empty_attributes(obj):
    """Remove any properties with empty values, where "empty" means returning False"""

    if isinstance(obj, dict):
        delete = []
        for item in list(obj):
            if not obj[item]:
                delete.append(item)
            else:
                remove_empty_attributes(obj[item])
        for item in delete:
            del obj[item]
    elif isinstance(obj, tuple):
        for item in obj:
            remove_empty_attributes(item)
    elif isinstance(obj, list):
        for item in obj:
            remove_empty_attributes(item)

def check_object_by_ref(data, globalId):
    for obj in data:
        if obj["globalId"] == globalId:
            return True
    return False

def remove_orphan_attributes(data, obj):
    """Check every "ref" property against the list of present objects.
    If object doesn't exist the property is also removed"""

    if isinstance(obj, dict):
        for key in obj:
            if isinstance(obj[key], dict):
                remove_orphan_attributes(data, obj[key])
            elif isinstance(obj[key], list):
                for item in obj[key]:
                    if isinstance(item, dict):
                        if "ref" in item:
                            if not check_object_by_ref(data, item['ref']):
                                obj[key].remove(item)
                        else:
                            remove_orphan_attributes(data, obj[key])
            elif isinstance(obj[key], tuple):
                delete = []
                for item in obj[key]:
                    if isinstance(item, dict):
                        if "ref" in item:
                            if not check_object_by_ref(data, item['ref']):
                                delete.append(item)
                        else:
                            remove_orphan_attributes(data, obj[key])
                if delete:
                    items = list(obj[key])
                    for entity in delete:
                        items.remove(entity)
                    obj[key] = tuple(items)
    elif isinstance(obj, list):
        for item in obj:
            remove_orphan_attributes(data, item)
    elif isinstance(obj, tuple):
        for item in obj:
            remove_orphan_attributes(data, item)

def remove_complex_geometry(data):
    """Removes all IfcShapeRepresentation types other then OBJ
    TODO: cleanup orphaned entities"""
    
    delete = []
    for entity in data:
        if "type" in entity:
            if entity["type"] == "IfcShapeRepresentation":
                if entity["representationType"] != "OBJ":
                    delete.append(entity)
    for entity in delete:
        data.remove(entity)

with open(in_file_path, encoding='utf-8') as in_file:
    model = json.load(in_file)
    data = model["data"]

    remove_complex_geometry(data)
    remove_orphan_attributes(data, data)
    # remove_empty_attributes(data)

    with open(out_file_path, 'w') as outfile:
        json.dump(model, outfile, indent=2)