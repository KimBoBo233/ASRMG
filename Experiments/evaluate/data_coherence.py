import numpy
import pandas
import json

from research_2.group import group_util


def handle_annotations(annotations):
    annotations = str(annotations)
    if annotations.startswith("org.springframework.web.bind.annotation.PostMapping"):
        request_spring_type = "POST"
    elif annotations.startswith("org.springframework.web.bind.annotation.GetMapping"):
        request_spring_type = "GET"
    elif annotations.startswith("org.springframework.web.bind.annotation.DeleteMapping"):
        request_spring_type = "DELETE"
    elif annotations.startswith("org.springframework.web.bind.annotation.PutMapping"):
        request_spring_type = "PUT"
    elif annotations.startswith("org.springframework.web.bind.annotation.PatchMapping"):
        request_spring_type = "PATCH"
    elif annotations.startswith("org.springframework.web.bind.annotation.RequestMapping"):
        request_spring_type = "REQUEST"
    else:
        raise Exception("request_type 未解析：", annotations)

    split = annotations.split("(")
    api = split[1][:-1]

    if api.endswith("/"):
        api = api[:-1]
    return request_spring_type, api


def is_sub_collection(child, target):
    is_sub = True
    for c in child:
        if c in target:
            pass
        else:
            is_sub = False
    return is_sub


def calculate_field_score(p1, p2):
    p1_fields = p1["fields"]
    p2_fields = p2["fields"]

    common_field = []
    for field1 in p1_fields:
        for field2 in p2_fields:
            if field1 == field2:
                common_field.append(field1)

    is_sub_ = False
    if len(p1_fields) > len(p2_fields):
        is_sub_ = is_sub_collection(p2_fields, p1_fields)
    else:
        is_sub_ = is_sub_collection(p1_fields, p2_fields)
    if is_sub_:
        return 1.0

    field_score = len(common_field) * 2 / len(p1_fields + p2_fields)
    return field_score


def calculate_param_coupling(params1, params2):
    params1_data_bean = [param for param in params1 if param["isDataBean"] == "True"]
    p1_normal_bean = [param for param in params1 if param["isDataBean"] == "False"]
    params2_data_bean = [param for param in params2 if param["isDataBean"] == "True"]
    p2_normal_bean = [param for param in params2 if param["isDataBean"] == "False"]

    data_bean_score, params1_data_bean, params2_data_bean = calculate_data_bean_scores(params1_data_bean,
                                                                                       params2_data_bean)
    p1_normal_score, p1_normal_bean = calculate_normal_data_beans(p1_normal_bean, params2_data_bean, [])
    p2_normal_score, p2_normal_bean = calculate_normal_data_beans(p2_normal_bean, params1_data_bean, [])

    common_params_normal = []
    for p1 in p1_normal_bean:
        for p2 in p2_normal_bean:
            if p1 == p2:
                common_params_normal.append(p1)
                break
    normal_bean_len = len(p1_normal_bean + p2_normal_bean)
    normal_score = len(common_params_normal) * 2 / normal_bean_len if not normal_bean_len == 0 else 0

    return ((p2_normal_score + p1_normal_score) / 2 + normal_score) * 0.2 + data_bean_score * 0.8


def swap(params1_data_bean, params2_data_bean):
    new_1 = []
    for item in params2_data_bean:
        new_1.append(item)
    new_2 = []
    for item in params1_data_bean:
        new_2.append(item)
    return new_1, new_2


def calculate_data_bean_scores(params1_data_bean, params2_data_bean):
    if len(params1_data_bean) == 0 or len(params2_data_bean) == 0:
        return 0, params1_data_bean, params2_data_bean
    if len(params1_data_bean) > len(params2_data_bean):
        params1_data_bean, params2_data_bean = swap(params1_data_bean, params2_data_bean)
    dict = {}
    for index_1 in range(0, len(params1_data_bean)):
        p1 = params1_data_bean[index_1]
        dict[index_1] = {}
        for index_2 in range(0, len(params2_data_bean)):
            p2 = params2_data_bean[index_2]
            common_fields_score = calculate_field_score(p1, p2)
            dict[index_1].update({
                index_2: common_fields_score
            })

    params1_match_index = []
    params2_match_index = []
    for p1_index in dict.keys():
        if p1_index in params1_match_index:
            continue
        p2_scores = dict[p1_index]
        max_score = -999
        max_index = -1
        for p2_index in p2_scores.keys():
            if p2_index in params2_match_index:
                continue
            p2_s = p2_scores[p2_index]
            if max_score < p2_s:
                max_score = p2_s
                max_index = p2_index
        params1_match_index.append(p1_index)
        params2_match_index.append(max_index)
    scores = []
    for i in range(0, len(params1_match_index)):
        scores.append(dict[params1_match_index[i]][params2_match_index[i]])

    remain_data_bean_1 = []
    for i in range(0, len(params1_data_bean)):
        if i not in params1_match_index:
            remain_data_bean_1.append(params1_data_bean[i])
    remain_data_bean_2 = []
    for i in range(0, len(params2_data_bean)):
        if i not in params2_match_index:
            remain_data_bean_2.append(params2_data_bean[i])
    return numpy.mean(scores), remain_data_bean_1, remain_data_bean_2


def calculate_normal_data_beans(normal_beans, data_beans, all_data_bean):
    if len(data_beans) == 0 or len(normal_beans) == 0:
        return 0, normal_beans

    data_bean_full_names = [item["fullName"] for item in data_beans]
    normal_match = {}
    for normal_bean in normal_beans:
        normal = normal_bean["paramName"]
        normal_match[normal] = {
            "match": 0,
            "ambiguous": 0,
            "info": normal_bean
        }
        for data_bean in data_beans:
            fields = data_bean["fields"]
            for field in fields:
                str_field = str(field["name"])
                str_normal = str(normal)

                if str_normal == str_field:
                    normal_match[normal]["match"] += 1
                    continue
                try:
                    if str_normal.lower().index(str(data_bean["simpleName"] + str_field).lower()) >= 0:
                        normal_match[normal]["match"] += 1
                        continue
                except ValueError:
                    continue
        for data_bean in all_data_bean:
            if data_bean["fullName"] in data_bean_full_names:
                continue

            fields = data_bean["fields"]
            for field in fields:
                str_field = str(field["name"])
                str_normal = str(normal)

                if str_normal == str_field:
                    normal_match[normal]["ambiguous"] += 1
                    continue
    normal_score = []
    unmatch_bean = []
    for normal_str in normal_match.keys():
        match_ambiguous = normal_match[normal_str]
        match = match_ambiguous["match"]
        ambiguous = match_ambiguous["ambiguous"]
        if match == 0:
            normal_score.append(0)
            unmatch_bean.append(match_ambiguous["info"])
            continue
        else:
            normal_score.append(match / (match + ambiguous))
    return numpy.mean(normal_score), unmatch_bean


def calculate_param_cohesion(params1, params2, all_data_bean):
    p1_data_bean = [param for param in params1 if param["isDataBean"] == "True"]
    p1_normal_bean = [param for param in params1 if param["isDataBean"] == "False"]
    p2_data_bean = [param for param in params2 if param["isDataBean"] == "True"]
    p2_normal_bean = [param for param in params2 if param["isDataBean"] == "False"]
    data_bean_score, p1_data_bean, p2_data_bean = calculate_data_bean_scores(p1_data_bean,
                                                                             p2_data_bean)

    p1_normal_score, p1_normal_bean = calculate_normal_data_beans(p1_normal_bean, p2_data_bean,
                                                                  all_data_bean)
    p2_normal_score, p2_normal_bean = calculate_normal_data_beans(p2_normal_bean, p1_data_bean,
                                                                  all_data_bean)

    common_params_normal = []
    for p1 in p1_normal_bean:
        for p2 in p2_normal_bean:
            if p1 == p2:
                common_params_normal.append(p1)
                break
    normal_bean_len = len(p1_normal_bean + p2_normal_bean)
    normal_score = len(common_params_normal) * 2 / normal_bean_len if not normal_bean_len == 0 else 0
    return ((p2_normal_score + p1_normal_score) / 2 + normal_score) * 0.2 + data_bean_score * 0.8


def compute_data_cohension(itf, interface_in_group):
    if len(interface_in_group) == 1:
        return 0

    data_beans = itf["dataBean"]
    itf_params = data_beans["paramsType"]
    cohension_list = []
    all_data_bean = []
    all_data_bean_dict = {}
    for interface in interface_in_group:
        if interface["fullName"] == itf["fullName"]:
            continue
        params = interface["dataBean"]["paramsType"]
        for param in params:
            if param["isDataBean"] == "True":
                if param["fullName"] not in all_data_bean_dict:
                    all_data_bean_dict[param["fullName"]] = param
                    all_data_bean.append(param)

    for interface in interface_in_group:
        if itf["fullName"] == interface["fullName"]:
            continue
        interface_params = interface["dataBean"]["paramsType"]
        coh = calculate_param_cohesion(itf_params, interface_params, all_data_bean)
        if not coh == 0:
            cohension_list.append(coh)

    return numpy.mean(cohension_list) if len(cohension_list) > 0 else 0


def compute_data_coupling(itf, itf_groups):
    coupling_list = []
    coupling_names = []
    itf_group = itf["serviceCode"]
    data_beans = itf["dataBean"]
    itf_params = data_beans["paramsType"]

    for group in itf_groups:
        if group == itf_group:
            continue
        group_interfaces = itf_groups[group]
        for interface in group_interfaces:
            interface_params = interface["dataBean"]["paramsType"]
            coup = calculate_param_coupling(itf_params, interface_params)
            if not coup == 0:
                coupling_list.append(coup)
                coupling_names.append(interface["endpointName"])
    if len(coupling_list) > 0:
        return numpy.mean(coupling_list), coupling_list, coupling_names
    else:
        return 0, coupling_list, coupling_names


def compute(reconstruct_result, refer, method_call_tree_csv, interface_json):
    reconstruct_result, refer = match_itf_data(reconstruct_result, refer, method_call_tree_csv, interface_json)

    itf_group = group_util.group_by_service(reconstruct_result + refer)

    group_data_metric = {}
    for group in itf_group:
        interface_in_group = itf_group[group]
        group_coh = []
        group_cop = []

        group_cop_list = []
        group_cop_list_names = []
        for interface in interface_in_group:
            coh = compute_data_cohension(interface, interface_in_group)
            cop, cop_list, coupling_names = compute_data_coupling(interface, itf_group)

            interface["data_coh"] = coh
            interface["data_cop"] = cop
            group_coh.append(coh)
            group_cop.append(cop)
            group_cop_list.append(cop_list)
            group_cop_list_names.append(coupling_names)
        group_data_metric[group] = {
            "coh": numpy.mean(group_coh),
            "cop": numpy.mean(group_cop)
        }

    coh_list = []
    cop_list = []
    for itf in reconstruct_result:
        coh_list.append(itf["data_coh"])
        cop_list.append(itf["data_cop"])
    return numpy.mean(coh_list), numpy.mean(cop_list), group_data_metric


def match_itf_data(reconstruct_result, refer, method_call_tree_csv, interface_json):
    method_calls = pandas.read_csv(method_call_tree_csv).to_dict("records")

    file = open(interface_json, mode="r")
    interface_databean = json.load(file)
    file.close()

    interface_data_dict = {}
    for itf_databean in interface_databean:
        itf_databean_method = itf_databean['interfaceName']
        itf_databean_class = itf_databean['classFullName']

        find = False
        for itf_entry_method in method_calls:
            class_name = itf_entry_method['className']
            method_name = itf_entry_method['methodName']
            annotations = itf_entry_method["annotations"]

            if itf_databean_method == method_name and itf_databean_class == class_name:
                find = True
                request_spring_type, api = handle_annotations(annotations)
                service_code = itf_databean["serviceCode"]
                itf_full_name = f"{service_code}:{request_spring_type}:{api}"
                interface_data_dict[itf_full_name] = itf_databean

        if find == False:
            print("not match", itf_databean_class, itf_databean_method)

    for item in reconstruct_result:
        full_name = item['fullName']
        databean = interface_data_dict[full_name]

        item["dataBean"] = databean

    for item in refer:
        full_name = item['fullName']
        databean = interface_data_dict[full_name]

        item["dataBean"] = databean
    return reconstruct_result, refer
