def merge_duplicate_topics2(business_topic_list):
    business_topic_dict = {}
    for business_topic in business_topic_list:
        weight_ = business_topic['weight']
        relate_ = business_topic['isTopic']
        word = business_topic['info']
        if word in business_topic_dict:
            business_topic_dict[word]['weight'] += weight_
        else:
            business_topic_dict[word] = {"info": word, "weight": weight_, "isTopic": relate_}
    return business_topic_dict


def merge_duplicate_topics(business_topic_list):
    business_topic_dict = {}
    for business_topic in business_topic_list:
        weight_ = business_topic['weight']
        business_topic_info = business_topic['tag']

        relate_ = business_topic_info['isTopicRelate']
        word = business_topic_info['lemma']
        if word in business_topic_dict:
            business_topic_dict[word]['weight'] += weight_
        else:
            business_topic_dict[word] = {"info": word, "weight": weight_, "isTopic": relate_}
    return business_topic_dict


def sort_bt_or_btc(business_topic_clusters):
    total = 0
    interface_tags_tuple = []
    for key, value in business_topic_clusters.items():
        total += value['weight']
        interface_tags_tuple.append((value['info'], value['weight'], value['isTopic']))
    sorted_interface_tags = sorted(interface_tags_tuple, key=lambda x: x[1], reverse=True)

    sorted_clusters = []
    for i in range(0, len(sorted_interface_tags)):
        cluster_info = sorted_interface_tags[i]
        sorted_clusters.append(
            {"tag": cluster_info[0], "weight": cluster_info[1], "percentage": cluster_info[1] / total,
             "isTopic": cluster_info[2],
             "rank": i + 1}
        )
    return sorted_clusters
