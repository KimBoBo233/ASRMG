from research_2.btc import bt_merge


def group_by_value(input_dict):
    result_dict = {}
    for key, value in input_dict.items():
        if value in result_dict:
            result_dict[value].append(key)
        else:
            result_dict[value] = [key]
    return result_dict


def sort_btc_and_category(all_business_topics, service_code, service_business_topic_cluster):
    business_grouped_topic_list = {}
    business_topic_group_dict = {}

    if service_code in service_business_topic_cluster:
        business_topic_group_dict = service_business_topic_cluster[service_code]
        business_grouped_topic_list = group_by_value(business_topic_group_dict)

    business_topic_clusters = {}
    for key in all_business_topics.keys():
        key_frequency_info = all_business_topics[key]
        key_weight = key_frequency_info['weight']
        is_topic = key_frequency_info['isTopic']
        if key in business_topic_group_dict:

            group_id = business_topic_group_dict[key]
            group_first_key = business_grouped_topic_list[group_id][0]
            if group_first_key in business_topic_clusters:
                business_topic_clusters[group_first_key]['weight'] += key_weight
                if is_topic:
                    business_topic_clusters[group_first_key]['isTopic'] = "true"
            else:
                business_topic_clusters[group_first_key] = {"info": group_first_key, "weight": key_weight,
                                                            "isTopic": "true"}
        else:
            if key in business_topic_clusters:
                business_topic_clusters[key]['weight'] += key_weight
            else:
                business_topic_clusters[key] = {"info": key, "weight": key_weight, "isTopic": is_topic}

    sorted_business_topics = bt_merge.sort_bt_or_btc(all_business_topics)
    sorted_clusters = bt_merge.sort_bt_or_btc(business_topic_clusters)

    business_topic = {}
    normal_topic = {}
    for tag in sorted_business_topics:
        if tag['isTopic'] == "true" and tag['percentage'] > 0.02:
            business_topic[tag['tag']] = tag
        else:
            normal_topic[tag['tag']] = tag

    cluster_business_topic = {}
    cluster_normal_topic = {}
    for tag in sorted_clusters:
        if tag['isTopic'] == "true" and tag['percentage'] > 0.02:
            cluster_business_topic[tag['tag']] = tag
        else:
            cluster_normal_topic[tag['tag']] = tag
    return sorted_business_topics, business_topic, normal_topic, cluster_business_topic, cluster_normal_topic
