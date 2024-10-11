def get_interface_function_call_tree(method_call_tree_pd, request_type, annotation_value):
    try:

        if request_type == "POST":
            request_spring_type = "org.springframework.web.bind.annotation.PostMapping"
        elif request_type == "GET":
            request_spring_type = "org.springframework.web.bind.annotation.GetMapping"
        elif request_type == "DELETE":
            request_spring_type = "org.springframework.web.bind.annotation.DeleteMapping"

        elif request_type == "PUT":
            request_spring_type = "org.springframework.web.bind.annotation.PutMapping"
            annotation_name = "org.springframework.web.bind.annotation.PutMapping" + "(" + annotation_value + ")"
        elif request_type == "PATCH":
            request_spring_type = "org.springframework.web.bind.annotation.PatchMapping"
            annotation_name = "org.springframework.web.bind.annotation.PatchMapping" + "(" + annotation_value + ")"
        elif request_type == "REQUEST":
            request_spring_type = "org.springframework.web.bind.annotation.RequestMapping"
            annotation_name = "org.springframework.web.bind.annotation.RequestMapping" + "(" + annotation_value + ")"
        else:
            raise Exception("request_type 未解析：", request_type)
        annotation_name = "{}({})".format(request_spring_type, annotation_value)

        query_if_by_annotation_df = method_call_tree_pd.query('`annotations` == "' + annotation_name + '"')

        if query_if_by_annotation_df.empty:
            if annotation_value.endswith("/"):
                annotation_value = annotation_value[:-1]
                annotation_name = "{}({})".format(request_spring_type, annotation_value)
                query_if_by_annotation_df = method_call_tree_pd.query('`annotations` == "' + annotation_name + '"')
            else:
                annotation_value += "/"
                annotation_name = "{}({})".format(request_spring_type, annotation_value)
                query_if_by_annotation_df = method_call_tree_pd.query('`annotations` == "' + annotation_name + '"')
        return query_if_by_annotation_df['raw_tree_json'].values[0]
    except IndexError:
        pass


def bind_interface_and_method(interfaces, method_call_tree_csv):
    import pandas as pd
    import json
    method_call_pd = pd.read_csv(method_call_tree_csv)

    for interface in interfaces:
        endpoint_name = interface['endpointName']
        service_code = interface['serviceCode']
        split = endpoint_name.split(":")
        if len(split) > 1:
            request_type = split[0]
            annotation_value = split[1]

            method_call_tree_str = get_interface_function_call_tree(method_call_tree_pd=method_call_pd,
                                                                    request_type=request_type,
                                                                    annotation_value=annotation_value)
            method_call_tree = json.loads(method_call_tree_str)
            interface['methodCallTree'] = method_call_tree

    return interfaces
