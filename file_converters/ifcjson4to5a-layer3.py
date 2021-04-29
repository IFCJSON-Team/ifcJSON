import json
import copy
import itertools

import ifcjson

in_file_path = "../Samples/IFC_2x3/Duplex_layer2.json"
out_file_path = "../Samples/IFC_2x3/Duplex_layer3.json"

# Attributes that are not part of ifcJSON5a
INVALIDATTRIBUTES = {
    'ownerHistory',
    'representationContexts',
    'contextOfItems',
    'objectPlacement',
    'representationMaps',
    'ofProductRepresentation'
}

def remove_invalid_attributes(obj):
    if isinstance(obj, dict):
        for item in list(obj):
            if item in INVALIDATTRIBUTES:
                del obj[item]
            else:
                remove_invalid_attributes(obj[item])
    elif isinstance(obj, tuple):
        for item in obj:
            remove_invalid_attributes(item)
    elif isinstance(obj, list):
        for item in obj:
            remove_invalid_attributes(item)

def remove_empty_attributes(obj):
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


def count_references(obj, id_dict):
    if isinstance(obj, dict):
        map(lambda x: count_references(obj[x], id_dict), obj.keys())
        for item in obj.items():
            count_references(item, id_dict)
        if "ref" in obj:
            if obj["ref"] in id_dict:
                id_dict[obj["ref"]] += 1
    elif isinstance(obj, (list, set, tuple)):
        [count_references(item, id_dict) for item in obj]

def create_id_dict(model, id_list):
    id_dict = dict.fromkeys(id_list, 0)
    count_references(model, id_dict)
    return id_dict

def get_objects_by_type(data, type_list):
    id_list = []
    for entity in list(data):
        if all(k in entity for k in ("type","globalId")):
            if entity["type"] in type_list:
                id_list.append(entity["globalId"])
    return id_list

def remove_entities_by_id(entities, id_list):
    filtered_entities = []
    for entity in list(entities):
        if all(k in entity for k in ("type","globalId")):
            if entity["globalId"] not in id_list:
                filtered_entities.append(entity)
    return filtered_entities

def get_global_ids(obj):
    id_list = []
    if isinstance(obj, dict):
        id_list = list(itertools.chain(
            *map(lambda x: get_global_ids(obj[x]), obj)))
        if "globalId" in obj:
            id_list.append(obj["globalId"])
    elif isinstance(obj, (list, set, tuple)):
        id_list = list(itertools.chain(*map(lambda x: get_global_ids(x), obj)))
    return id_list

def entity_in_list(entity, entity_type_list):
    if isinstance(entity, dict):
        if "type" in entity:
            if entity["type"] in entity_type_list:
                return True
    return False


def remove_entities_by_type(data, obj, entity_type_list):
    """Recursively remove items from obj that match entities in entity_type_list"""

    if isinstance(obj, dict):
        for item in list(obj):
            if isinstance(obj[item], list):
                delete = False
                for entity in obj[item]:
                    if entity_in_list(entity, entity_type_list):
                        delete = True
                if delete:
                    del obj[item]
            elif entity_in_list(obj[item], entity_type_list):
                del obj[item]
            else:
                remove_entities_by_type(data, obj[item], entity_type_list)
    elif isinstance(obj, list):
        delete_items = []
        for item in obj:
            if entity_in_list(item, entity_type_list):
                delete_items.append(item)
            else:
                remove_entities_by_type(data, item, entity_type_list)
        for item in delete_items:
            obj.remove(item)


with open(in_file_path, encoding='utf-8') as in_file:
    model = json.load(in_file)
    data = model["data"]

    invalid_entities = [
        "IfcOwnerHistory",
        "IfcGeometricRepresentationContext",
        "IfcGeometricRepresentationSubContext",
        "IfcLocalPlacement"
        ]
    # entity_id_list = get_objects_by_type(data, invalid_entities)
    # remove_invalid_attributes(data)
    remove_entities_by_type(data, data, invalid_entities)
    # model["data"] = remove_entities_by_id(data, entity_id_list)

    # remove_empty_attributes(data)

    id_list = get_global_ids(model)
    id_dict = create_id_dict(model, id_list)
    count = sum(i == 0 for i in id_dict.values())
    print(f"Out model contains {str(count)} orphaned objects")

    with open(out_file_path, 'w') as outfile:
        json.dump(model, outfile, indent=2)