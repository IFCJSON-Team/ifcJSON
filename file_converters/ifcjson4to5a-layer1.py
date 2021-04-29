import json
import itertools

import ifcjson

def count_references(obj, id_dict):
    if isinstance(obj, dict):
        map(lambda x: count_references(obj[x],id_dict),obj.keys())
        for item in obj.items():
            count_references(item,id_dict)
        if "ref" in obj:
            if obj["ref"] in id_dict:
                id_dict[obj["ref"]] += 1
    elif isinstance(obj, (list, set, tuple)):
        [count_references(item,id_dict) for item in obj]

def get_global_ids(obj):
    id_list = []
    if isinstance(obj, dict):
        id_list = list(itertools.chain(*map(lambda x: get_global_ids(obj[x]), obj)))
        if "globalId" in obj:
            id_list.append(obj["globalId"])
    elif isinstance(obj, (list, set, tuple)):
        id_list = list(itertools.chain(*map(lambda x: get_global_ids(x), obj)))
    return id_list

def create_id_dict(id_list):
    return dict.fromkeys(id_list, 0)

in_file_path = "../Samples/IFC_2x3/Duplex_A_20110907_optimized.ifc"
out_file_path = "../Samples/IFC_2x3/Duplex_layer1.json"

model = ifcjson.IFC2JSON4(in_file_path, False, GEOMETRY="tessellate").spf2Json()

# Check
id_list = get_global_ids(model)
if len(id_list) != len(set(id_list)):
    print("Model contains duplicate GlobalId's!")
id_dict = create_id_dict(id_list)

count_references(model, id_dict)
count = sum(i == 0 for i in id_dict.values())
print(f"Model contains {str(count)} orphaned objects")

with open(out_file_path, 'w') as outfile:
    json.dump(model, outfile, indent=2)