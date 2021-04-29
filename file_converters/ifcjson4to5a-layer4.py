import json
import copy

import ifcjson

in_file_path = "../Samples/IFC_2x3/Duplex_layer3.json"
out_file_path = "../Samples/IFC_2x3/Duplex_layer4.json"


def faceset_to_obj(entity):
    if "type" in entity:
        if entity["type"] == "IfcTriangulatedFaceSet":
            if "coordinates" in entity:
                if "coordList" in entity["coordinates"]:
                    if "coordIndex" in entity:
                        verts = entity["coordinates"]["coordList"]
                        verts_list = map(lambda x:' '.join(map(str, x)),verts)
                        vert_string = 'v ' + '\nv '.join(verts_list) + '\n'
                        
                        faces = entity["coordIndex"]
                        faces_list = map(lambda x:' '.join(map(str, x)),faces)
                        face_string = 'f ' + '\nf '.join(faces_list) + '\n'
                        return vert_string + face_string


def tesselations_to_obj(data):
    for entity in data:
        if "type" in entity:
            if entity["type"] == "IfcShapeRepresentation":
                if entity["representationType"] == "Tessellation":
                    if "items" in entity:
                        entity["items"] = list(map(lambda x: faceset_to_obj(x),entity["items"]))
                        entity["representationType"] = "OBJ"

with open(in_file_path, encoding='utf-8') as in_file:
    model = json.load(in_file)
    data = model["data"]

    tesselations_to_obj(data)

    with open(out_file_path, 'w') as outfile:
        json.dump(model, outfile, indent=2)