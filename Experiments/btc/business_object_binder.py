from research_2.btc import bt_merge


def recurisivly_bind_call_tree(method_call_tree, business_topic_dict):
    business_topic_list = []

    method_class = method_call_tree['className']
    method_name = method_call_tree['methodName']
    full_method_name = method_class + ":" + method_name

    if full_method_name in business_topic_dict:
        method_and_tag_info = business_topic_dict[full_method_name]

        business_topics_list = eval(method_and_tag_info['tag'])
        if not business_topics_list:
            business_topics_list = None
        else:
            business_topic_list.extend(business_topics_list)
        method_call_tree['businessTopics'] = business_topics_list

    if 'children' in method_call_tree:
        children = method_call_tree['children']
        if children:
            for next_method in children:
                business_topic_list.extend(recurisivly_bind_call_tree(next_method, business_topic_dict))

    return business_topic_list


def business_topic_csv_to_full_name_dict(business_topic_csv):
    import pandas as pd
    business_topic_list = pd.read_csv(business_topic_csv).to_dict("records")
    method_business_topics_dict = {}
    for business_topic_info in business_topic_list:
        class_name = business_topic_info['className']
        method_name = business_topic_info['methodName']
        full_method_name = class_name + ":" + method_name
        method_business_topics_dict[full_method_name] = business_topic_info
    return method_business_topics_dict


def bind_business_object(interfaces: [], business_topic_csv) -> []:
    business_topic_dict = business_topic_csv_to_full_name_dict(business_topic_csv)

    for interface in interfaces:
        method_call_tree = interface['methodCallTree']
        business_topic_list = recurisivly_bind_call_tree(method_call_tree, business_topic_dict)
        topics = bt_merge.merge_duplicate_topics(business_topic_list)
        interface['allBusinessTopics'] = topics
    return interfaces
