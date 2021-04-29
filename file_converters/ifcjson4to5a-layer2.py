import json
import copy
import itertools

import ifcjson

in_file_path = "../Samples/IFC_2x3/Duplex_layer1.json"
out_file_path = "../Samples/IFC_2x3/Duplex_layer2.json"

# Attributes for which the intermediate relationship object is removed
SIMPLIFICATIONS = {
    # IfcRelAggregates
    'isDecomposedBy':       ['relatedObjects'],
    'decomposes':           ['relatingObject'],
    # IfcRelContainedInSpatialStructure
    'containsElements':     ['relatedElements'],
    'containedInStructure': ['relatingStructure'],
    # IfcRelDefinesByProperties
    'isDefinedBy':          ['relatingPropertyDefinition', 'relatingType'],
    'definesOccurrence':    ['relatedObjects'],
    # IfcRelAssociatesMaterial
    'hasAssociations':      ['relatingMaterial'],
    # IfcRelFillsElement
    'hasFillings':          ['relatedBuildingElement'],
    'fillsVoids':           ['relatingOpeningElement'],
    # IfcRelVoidsElement
    'hasOpenings':          ['relatedOpeningElement'],
    'voidsElements':        ['relatingBuildingElement'],
    # IfcRelDefinesByType
    'objectTypeOf':         ['relatedObjects'],
    'isTypedBy':            ['relatingType'],
    'types':                ['relatedObjects'],
    # IfcRelConnectsPathElements (!) This skips all IfcRelConnectsPathElements properties
    'connectedTo':          ['relatedElement'],
    'connectedFrom':        ['relatingElement'],
    # IfcRelSpaceBoundary (!) This skips all spaceboundary properties like for example geometry
    'boundedBy':            ['relatedBuildingElement'],
    'providesBoundaries':   ['relatingSpace']
}


# Testen!!!
# beide mogelijke relatie velden controleren, maar niet allemaal!


SIMPLIFIED_RELATIONSHIPS = {
    # 'IfcRelationship':                    [],
    # 'IfcRelAssigns':                      ['relatedObjects'],
    'IfcRelDecomposes':                     ['relatedObjects', 'relatingObject'],
    'IfcRelAggregates':                     ['relatedObjects', 'relatingObject'],
    'IfcRelNests':                          ['relatedObjects', 'relatingObject'],
    # 'IfcRelAssociates':                   ['relatedObjects'],
    'IfcRelAssociatesClassification':       ['relatedObjects', 'relatingClassification'],
    'IfcRelAssociatesDocument':             ['relatedObjects', 'relatingDocument'],
    'IfcRelAssociatesLibrary':              ['relatedObjects', 'relatingLibrary'],
    'IfcRelAssociatesMaterial':             ['relatedObjects', 'relatingMaterial'],
    # 'IfcRelDefines':                      ['relatedObjects'],
    'IfcRelDefinesByProperties':            ['relatedObjects', 'relatingPropertyDefinition'],
    'IfcRelDefinesByType':                  ['relatedObjects', 'relatingType'],
    'IfcRelVoidsElement':                   ['relatingBuildingElement', 'relatedOpeningElement'],
    # 'IfcRelConnects':                     [],
    'IfcRelConnectsElements':               ['relatingElement', 'relatedElement'],
    'IfcRelConnectsWithRealizingElements':  ['relatingElement', 'relatedElement'],
    'IfcRelConnectsPathElements':           ['relatingElement', 'relatedElement'],
    'IfcRelConnectsPortToElement':          ['relatingPort', 'relatedElement'],
    'IfcRelConnectsPorts':                  ['relatingPort', 'relatedPort'],
    'IfcRelConnectsStructuralActivity':     ['relatingElement', 'relatedStructuralActivity'],
    'IfcRelConnectsStructuralMember':       ['relatingStructuralMember', 'relatedStructuralConnection'],
    'IfcRelContainedInSpatialStructure':    ['relatedElements', 'relatingStructure'],
    'IfcRelCoversBldgElements':             ['relatingBuildingElement', 'relatedCoverings'],
    'IfcRelCoversSpaces':                   ['relatingSpace', 'relatedCoverings'],
    'IfcRelFillsElement':                   ['relatingOpeningElement', 'relatedBuildingElement'],
    'IfcRelFlowControlElements':            ['relatedControlElements', 'relatingFlowElement'],
    'IfcRelInterferesElements':             ['relatingElement', 'relatedElement'],
    'IfcRelReferencedInSpatialStructure':   ['relatedElements', 'relatingStructure'],
    'IfcRelSequence':                       ['relatingProcess', 'relatedProcess'],
    'IfcRelServicesBuildings':              ['relatingSystem', 'relatedBuildings'],
    'IfcRelSpaceBoundary':                  ['relatingSpace', 'relatedBuildingElement'],
    'IfcRelSpaceBoundary1stLevel':          ['relatingSpace', 'relatedBuildingElement'],
    'IfcRelSpaceBoundary2ndLevel':          ['relatingSpace', 'relatedBuildingElement']
}


# SIMPLIFIED_RELATIONSHIPS = {
#     'IfcRelationship',
#     'IfcRelAssigns',
#     'IfcRelDecomposes',
#     'IfcRelAggregates',
#     'IfcRelNests',
#     'IfcRelAssociates',
#     'IfcRelAssociatesClassification',
#     'IfcRelAssociatesDocument',
#     'IfcRelAssociatesLibrary',
#     'IfcRelAssociatesMaterial',
#     'IfcRelDefines',
#     'IfcRelDefinesByProperties',
#     'IfcRelDefinesByType',
#     'IfcRelConnects',
#     'IfcRelVoidsElement',
#     'IfcRelFillsElement',
#     'IfcRelContainedInSpatialStructure',
#     'IfcRelSequence'
# }


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


def create_id_dict(model, id_list):
    id_dict = dict.fromkeys(id_list, 0)
    count_references(model, id_dict)
    return id_dict


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

# def check_relationship_object(obj):
#     if isinstance(obj, dict):
#         if "globalId" in obj:
#             if "type" in obj:
#                 if obj["type"] in SIMPLIFIED_RELATIONSHIPS:
#                     return (obj["globalId"],obj)


def get_relationship_objects(data):
    for obj in data:
        if isinstance(obj, dict):
            if "globalId" in obj:
                if "type" in obj:
                    if obj["type"] in SIMPLIFIED_RELATIONSHIPS:
                        yield obj["globalId"], obj

    # return {check_relationship_object(x): x for x in data if check_relationship_object(x)}
    # return [x for x in fruits if "a" in x]
    # return list(filter(None, map(lambda x: check_relationship_object(x),data)))


def get_related(data, rel_key, globalId):
    rel_obj = get_object_by_id(data, globalId)
    for key in SIMPLIFICATIONS[rel_key]:
        if key in rel_obj:
            if isinstance(rel_obj[key], dict):
                if "ref" in rel_obj[key]:
                    return {
                        "type": rel_obj[key]["type"],
                        "ref": rel_obj[key]["ref"]
                    }
                else:
                    # print(f"ref not found: {rel_obj[key]}")
                    # delete_entities.add(rel_obj["type"])
                    return rel_obj[key]
            elif isinstance(rel_obj[key], tuple):
                # delete_entities.add(rel_obj["type"])
                return rel_obj[key]
            elif isinstance(rel_obj[key], list):
                # delete_entities.add(rel_obj["type"])
                return rel_obj[key]
            else:
                print(f"Object type not recognized: {rel_obj[key]}")
    # print(f"Simplified object type not found for: {rel_obj}")
    return False

def is_ref(obj, globalId):
    if isinstance(obj, dict):
        if "ref" in obj:
            if obj["ref"] == globalId:
                return True
    return False

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
        # print(list(map(lambda x: is_not_ref(x,globalid),obj)))
        # if all(list(map(lambda x: is_not_ref(x,globalid),obj))):
        #     print("yo")
        # if [False,False]:
        #     print("ja")
        # print(all([is_not_ref(x, globalid) for x in obj]))
        # raise Exception("End")
        return all([is_not_ref(x, globalid) for x in obj])
    return False


# def contains_ref(obj, globalid):
#     """ Search in given dict or list if a reference to given id is present"""

#     if isinstance(obj, dict):
#         return is_ref(obj, globalid)

#     elif isinstance(obj,list):
#         print(list(map(lambda x: is_ref(x,globalid),obj)))
#         if all(list(map(lambda x: is_ref(x,globalid),obj))):
#             print("yo")
#         if [False,False]:
#             print("ja")

#         # return all([is_ref(x, globalid) for x in obj])



def get_relationship_target(obj, globalid):
    # print(obj)
    # print(globalid)
    # raise Exception("End")
    # print("globalid")
    if isinstance(obj, dict):
        if "type" in obj:
            if obj["type"] in SIMPLIFIED_RELATIONSHIPS:
                entity_type = obj["type"]
                target = False
                for rel in SIMPLIFIED_RELATIONSHIPS[entity_type]:
                    if rel in obj:
                        if not_contains_ref(obj[rel], globalid):
                            # print(obj)
                            # print(globalid)
                            # print(obj[rel])
                            # raise Exception("End")
                            return obj[rel]
                # if source_list:
                #     raise Exception("End")
        # for key in obj:
        #     item = obj[key]
        #     source_list = False
        #     # ref = False
        #     # print(item)
        #     if isinstance(item, list):
        #         for refitem in item:
        #             if isinstance(refitem, dict):
        #                 if "ref" in refitem:
        #                     # ref = True
        #                     if refitem["ref"] == globalid:
        #                         source_list = True
        #     # if ref:
        #         if source_list == False:
        #             # Found the correct relationship direction
        #             return refitem
        #     else:
        #         if isinstance(item, dict):
        #             if "ref" in item:
        #                 # ref = True
        #                 if item["ref"] != globalid:
        #                     return item


# def simplify_relationships(obj, data, relationship_objects):
#     if isinstance(obj, dict):
#         for attrkey in obj:
#             attr = obj[attrkey]
#             if isinstance(attr, set):

#                 print("attr")
#                 print(attrkey)
#             # if isinstance(obj, dict):
#             #     if "ref" in obj:
#             #         globalid = obj["ref"]
#             #         if globalid in relationship_objects:
#             #             # del obj[item]
#             #             # print(relationship_objects[globalid])
#             #             # print(obj)
#             #             obj = get_relationship_target(relationship_objects[globalid], globalid)
#             #     else:
#             #         for item in list(obj):
#             #             simplify_relationships(obj[item], data, relationship_objects)
#     elif isinstance(obj, tuple):
#         for item in obj:
#             simplify_relationships(item, data, relationship_objects)
#     elif isinstance(obj, list):
#         for item in obj:
#             simplify_relationships(item, data, relationship_objects)


# def simplify_relationships(obj, data, relationship_objects):
#     if isinstance(obj, dict):
#         if "ref" in obj:
#             globalid = obj["ref"]
#             if globalid in relationship_objects:
#                 # del obj[item]
#                 # print(relationship_objects[globalid])
#                 # print(obj)
#                 obj = get_relationship_target(relationship_objects[globalid], globalid)
#         else:
#             for item in list(obj):
#                 simplify_relationships(obj[item], data, relationship_objects)
#     elif isinstance(obj, tuple):
#         for item in obj:
#             simplify_relationships(item, data, relationship_objects)
#     elif isinstance(obj, list):
#         for item in obj:
#             simplify_relationships(item, data, relationship_objects)

# def simplify_relationships(data, obj):
#     if isinstance(obj, dict):
#         for item in list(obj):
#             if item in list(SIMPLIFICATIONS):
#                 items = []
#                 for rel in obj[item]:
#                     if "ref" in rel:
#                         related = get_related(data, item, rel["ref"])
#                         if related:
#                             items.append(related)
#                 if items:
#                     obj[item] = items
#             else:
#                 simplify_relationships(data, obj[item])
#     elif isinstance(obj, list):
#         for item in obj:
#             simplify_relationships(data, item)

def simplify_relationships(data, obj, relationship_objects, obj_globalid):
    # print("simplify_relationships")
    if isinstance(obj, dict):
        if "globalId" in obj:
            obj_globalid = obj["globalId"]
        for item in list(obj):
            # print(type(obj[item]))
            if isinstance(obj[item], list):
                items = []
                for rel in obj[item]:
                    if isinstance(rel, dict):
                        # if item in list(SIMPLIFICATIONS):
                        # for rel in obj[item]:
                        if "ref" in rel:
                            globalid = rel["ref"]
                            # print(globalid)
                            if globalid in relationship_objects:
                                related = get_relationship_target(
                                    relationship_objects[globalid], obj_globalid)
                                if related:
                                    items.append(related)
                if items:
                    obj[item] = items
            else:
                simplify_relationships(data, obj[item], relationship_objects, obj_globalid)
    elif isinstance(obj, list):
        for item in obj:
            simplify_relationships(data, item, relationship_objects, obj_globalid)


def check_entity_orphaned(entity, id_dict):
    if "globalId" in entity:
        if entity["globalId"] in id_dict.keys():
            if id_dict[entity["globalId"]] == 1:
                return True
    return False


def remove_orphan_entities(data, id_dict):
    return [x for x in data if not check_entity_orphaned(x, id_dict)]

    # map(lambda x: data.remove(x),delete_entities)
    # return set(data) - set(delete_entities)

def remove_objectified_relationships(data):
    filtered_data = []
    for obj in data:
        if isinstance(obj, dict):
            if "globalId" in obj:
                if "type" in obj:
                    if obj["type"] not in SIMPLIFIED_RELATIONSHIPS:
                        filtered_data.append(obj)
    return filtered_data


with open(in_file_path, encoding='utf-8') as in_file:
    model = json.load(in_file)
    data = model["data"]

    id_list = get_global_ids(model)

    if len(id_list) != len(set(id_list)):
        print("In model contains duplicate GlobalId's!")
    id_dict = create_id_dict(model, id_list)

    with open("id_dict.json", 'w') as outfile:
        json.dump(id_dict, outfile, indent=2)

    count = sum(i == 0 for i in id_dict.values())
    print(f"In model contains {str(count)} orphaned objects")

    relationship_objects = dict(get_relationship_objects(data))
    # print(relationship_objects)
    simplify_relationships(data, data, relationship_objects, "")
    model["data"] = remove_objectified_relationships(data)

    id_list = get_global_ids(model)
    # if len(id_list) != len(set(id_list)):
    #     print("Out model contains duplicate GlobalId's!")
    # id_dict = create_id_dict(model, id_list)
    # count = sum(i == 0 for i in id_dict.values())
    # print(f"Out model contains {str(count)} orphaned objects")

    # # print(list(map(lambda x: x["type"],delete_entities)))
    # # model["data"] = remove_orphan_entities(data)

    # model["data"] = remove_orphan_entities(model["data"], id_dict)

    id_dict = create_id_dict(model, id_list)
    count = sum(i == 0 for i in id_dict.values())
    print(f"Out model contains {str(count)} orphaned objects")

    # # remove_orphan_attributes(data, id_dict)
    # # remove_empty_attributes(data)

    with open(out_file_path, 'w') as outfile:
        json.dump(model, outfile, indent=2)
