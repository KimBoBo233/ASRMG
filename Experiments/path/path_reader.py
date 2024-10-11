def get_all_interfaces(path_file):
    import pandas as pd
    import json
    path_tree_csv_pd = pd.read_csv(path_file)
    path_group_dict = path_tree_csv_pd.to_dict("index")
    interfaces = []
    for path_id in path_group_dict:
        path_info = path_group_dict[path_id]
        rootNode = json.loads(path_info['root'])
        interface_in_trace = recurisivly_read_trace(rootNode)
        interfaces.extend(interface_in_trace)

    unique_interfaces = [dict(t) for t in set([tuple(d.items()) for d in interfaces])]
    return unique_interfaces


def recurisivly_read_trace(interface_tree_node: dict) -> []:
    interface_list = []
    endpoint_name = interface_tree_node['endpointName']
    service_code = interface_tree_node['serviceCode']
    if endpoint_name[0] == "{":
        index = endpoint_name.find("}")
        endpoint_name = endpoint_name[1:index] + ":" + endpoint_name[index + 1:]

    split = endpoint_name.split(":")
    if len(split) > 1:
        interface_list.append({
            "serviceCode": service_code,
            "endpointName": endpoint_name,
            "fullName": service_code + ":" + endpoint_name
        })
        if 'childs' in interface_tree_node:
            children = interface_tree_node['childs']
            if children:
                for c in children:
                    call_order = recurisivly_read_trace(c)
                    for item in call_order:
                        interface_list.append(item)


    else:
        annotation_value = split[0]
    return interface_list
