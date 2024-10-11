from research_2.config.global_config import global_config


def compute_cohesive(btc1_info, btc2_info):
    tag_ratio_similarity_thresh_hold = global_config.tag_ratio_similarity_thresh_hold[0]
    business_btc1 = btc1_info['clusterBusinessTopics']
    normal_btc1 = btc1_info['clusterNormalTopics']
    business_btc2 = btc2_info['clusterBusinessTopics']
    normal_btc2 = btc2_info['clusterNormalTopics']

    total_business_topic_percentage = 0
    total_normal_topic_percentage = 0
    for tag in business_btc1:
        topic_info = business_btc1[tag]
        total_business_topic_percentage += topic_info['percentage']
    for tag in normal_btc1:
        topic_info = normal_btc1[tag]
        total_normal_topic_percentage += topic_info['percentage']

    for tag in business_btc2:
        topic_info = business_btc2[tag]
        total_business_topic_percentage += topic_info['percentage']
    for tag in normal_btc2:
        topic_info = normal_btc2[tag]
        total_normal_topic_percentage += topic_info['percentage']

    common_business_topic_key = business_btc1.keys() & business_btc2.keys()
    common_business_topic_percentage = 0
    for key in common_business_topic_key:
        if key in business_btc1 and key in business_btc2:
            business_topic1_percentage = business_btc1[key]['percentage']
            business_topic2_percentage = business_btc2[key]['percentage']
            business_topic1_rank = business_btc1[key]['rank']
            business_topic2_rank = business_btc2[key]['rank']

            percentage_rate = business_topic1_percentage / business_topic2_percentage
            rank_rate = business_topic1_rank / business_topic2_rank
            percentage_rate = percentage_rate if percentage_rate <= 1 else 1 / percentage_rate
            rank_rate = rank_rate if rank_rate <= 1 else 1 / rank_rate
            if percentage_rate >= tag_ratio_similarity_thresh_hold or rank_rate >= tag_ratio_similarity_thresh_hold:
                common_business_topic_percentage += business_topic1_percentage
                common_business_topic_percentage += business_topic2_percentage
    common_business_topic_rate = common_business_topic_percentage / total_business_topic_percentage if total_business_topic_percentage != 0 else 0

    normal_topic1_key = normal_btc1.keys()
    normal_topic2_key = normal_btc2.keys()

    common_normal_topic_key = normal_topic1_key & normal_topic2_key
    common_normal_topic_percentage = 0
    for key in common_normal_topic_key:
        if key in normal_btc1 and key in normal_btc2:
            normal_topic1_percentage = normal_btc1[key]['percentage']
            normal_topic2_percentage = normal_btc2[key]['percentage']
            normal_topic1_rank = normal_btc1[key]['rank']
            normal_topic2_rank = normal_btc2[key]['rank']

            percentage_rate = normal_topic1_percentage / normal_topic2_percentage
            rank_rate = normal_topic1_rank / normal_topic2_rank
            percentage_rate = percentage_rate if percentage_rate <= 1 else 1 / percentage_rate
            rank_rate = rank_rate if rank_rate <= 1 else 1 / rank_rate

            if percentage_rate >= tag_ratio_similarity_thresh_hold or rank_rate >= tag_ratio_similarity_thresh_hold:
                common_normal_topic_percentage += normal_topic1_percentage
                common_normal_topic_percentage += normal_topic2_percentage
    common_normal_topic_rate = common_normal_topic_percentage / total_normal_topic_percentage if total_normal_topic_percentage != 0 else 0

    return common_business_topic_rate * 0.95 + common_normal_topic_rate * 0.05


def calculate_node_topic_cohesive(graph, node1, node2):

    btc1_info = graph.nodes[node1]['data']
    btc2_info = graph.nodes[node2]['data']

    return compute_cohesive(btc1_info, btc2_info)
