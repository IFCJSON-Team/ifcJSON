import json
import copy

import ifcjson

in_file_path = "../Samples/IFC_2x3/Duplex_layer5.json"
out_file_path = "../Samples/IFC_2x3/Duplex_layer6.json"

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

def remove_orphan_attributes(data, obj):
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
            
def get_object_by_id(data, globalId):
    for obj in data:
        if obj["globalId"] == globalId:
            return copy.deepcopy(obj)

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
    
def is_not_ref(obj, globalId):
    if isinstance(obj, dict):
        if "ref" in obj:
            if obj["ref"] == globalId:
                return False
    return True

def not_contains_ref(obj, globalid):
    """ Search in given dict or list if a reference to given id is present"""

    if isinstance(obj, dict):
        return is_not_ref(obj, globalid)

    elif isinstance(obj,list):
        return all([is_not_ref(x, globalid) for x in obj])
    return False

def get_relationship_target(obj, globalid):
    if isinstance(obj, dict):
        if "type" in obj:
            if obj["type"] in SIMPLIFIED_RELATIONSHIPS:
                entity_type = obj["type"]
                target = False
                for rel in SIMPLIFIED_RELATIONSHIPS[entity_type]:
                    if rel in obj:
                        if not_contains_ref(obj[rel], globalid):
                            return obj[rel]
            
# def flatten_propertysets(data, obj):
#     if isinstance(obj, dict):
#         for item in list(obj):
#             # print(item)
#             if item == "isDefinedBy":
#                 if "type" in obj[item]:
#                     if obj[item]["type"] == "IfcPropertySet":
#                         if "ref" in obj[item]:
#                             propertyset = get_object_by_id(data, obj[item]["ref"])
#                             if propertyset:
#                                 if "hasProperties" in propertyset:
#                                     has_properties = propertyset["hasProperties"]
#                                     if isinstance(has_properties, tuple):
#                                         for property in has_properties:
#                                             if isinstance(property, dict):
#                                                 if "name" in property:
#                                                     if "nominalValue" in property:
#                                                         nominalValue = property["nominalValue"]
#                                                         if "value" in nominalValue:
#                                                             if not property["name"] in obj:
#                                                                 obj[property["name"]] = nominalValue["value"]
#                 del obj[item]
#             else:
#                 flatten_propertysets(data, obj[item])
#     elif isinstance(obj, list):
#         for item in obj:
#             flatten_propertysets(data, item)

def flatten_propertysets(data, obj, pset_id_list, obj_globalid):
    if isinstance(obj, dict):
        if "globalId" in obj:
            obj_globalid = obj["globalId"]
        for item in list(obj):
            if isinstance(obj[item], list):
                delete_items = []
                i = 0
                while i < len(obj[item]):
                # for rel in obj[item]:
                    rel = obj[item][i]
                    if isinstance(rel, dict):
                        if "ref" in rel:
                            globalid = rel["ref"]
                            if globalid in pset_id_list:
                                # try:
                                propertyset = get_object_by_id(data, globalid)
                                if propertyset:
                                    if "hasProperties" in propertyset:
                                        # print(type(propertyset["hasProperties"]))
                                        has_properties = propertyset["hasProperties"]
                                        if isinstance(has_properties, list):
                                            for property in has_properties:
                                                if isinstance(property, dict):
                                                    if "name" in property:
                                                        if "nominalValue" in property:
                                                            nominalValue = property["nominalValue"]
                                                            property_name = toLowerCamelcase(property["name"])
                                                            if "value" in nominalValue:
                                                                if globalid == "675cc425-c907-4434-a4ee-3caf31e36025":
                                                                    print(property_name)
                                                                if not property_name in obj:
                                                                    obj[property_name] = nominalValue["value"]
                                                            #     else:
                                                            #         print(f"propertyname '{property_name}' already exists")
                                                            # else:
                                                            #     print(f"nominalValue for '{property_name}' has no value")
                                                        else:
                                                            print("property has no nominalValue")
                                                            print(property)
                                                            print(type(property))
                                                            raise BaseException("end")
                                                    else:
                                                        print("property has no name")
                                                        print(property)
                                                        print(type(property))
                                                        raise BaseException("end")
                                                else:
                                                    print("property is no dict")
                                                    print(property)
                                                    print(type(property))
                                                    raise BaseException("end")
                                        else:
                                            print("hasProperties is no list")
                                            print(has_properties)
                                            print(type(has_properties))
                                            raise BaseException("end")
                                    # else:
                                    #     print("Has no hasProperties, must be removed")
                  
                                    # print(obj[item][i])
                                    # print(rel)
                                    # obj[item].remove(rel)
                                else:
                                    print(f"propertyset entity {globalid} not found")
                                    # items.append(rel)
                            
                            # else:
                                # print("Is no propertyset")
                                delete_items.append(rel)
                                # except Exception as e:
                                #     print("Exception")
                                #     print(e)
                                #     items.append("what?")
                    i += 1
                # if items:
                    # print("add items")
                # obj[item] = delete_items
                
                for delete_item in delete_items:
                    obj[item].remove(delete_item)
                # if not items:
                #     del obj[item]
                # else:
                #     print("wtf?")
            else:
                flatten_propertysets(data, obj[item], pset_id_list, obj_globalid)
    elif isinstance(obj, list):
        for item in obj:
            flatten_propertysets(data, item, pset_id_list, obj_globalid)

def toLowerCamelcase(string):
    """Convert string from upper to lower camelCase"""

    return string[0].lower() + string[1:]

with open(in_file_path, encoding='utf-8') as in_file:
    model = json.load(in_file)
    data = model["data"]

    pset_id_list = get_objects_by_type(data, ["IfcPropertySet"])
    # with open("psets.json", 'w') as outfile:
    #     json.dump(pset_id_list, outfile, indent=2)
    flatten_propertysets(data, data, pset_id_list, "")
    # flatten_propertysets(data, data)
    model["data"] = remove_entities_by_id(data, pset_id_list)
    
    # remove_orph
    remove_empty_attributes(data)

    with open(out_file_path, 'w') as outfile:
        json.dump(model, outfile, indent=2)