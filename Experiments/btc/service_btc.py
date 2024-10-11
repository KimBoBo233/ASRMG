import research_2.btc.btc_binder as btc_binder
import research_2.btc.bt_merge as bt_merge


def get_service_with_btc(interfaces, service_business_topic_cluster):
    service_business_topics = {}
    for itf in interfaces:
        service_code = itf['serviceCode']
        bt_list = list(itf['allBusinessTopics'].values())
        for item in bt_list:
            item['tag'] = item['info']
            item['isTopicRelate'] = item['isTopic']
        if service_code not in service_business_topics:
            service_business_topics[service_code] = []
        else:
            service_business_topics[service_code].extend(bt_list)
    service_infos = {}

    for service_code in service_business_topics:
        business_topic_list = service_business_topics[service_code]
        merge_bt = bt_merge.merge_duplicate_topics2(business_topic_list)

        sorted_business_topics, business_topic, normal_topic, cluster_business_topic, cluster_normal_topic = \
            btc_binder.sort_btc_and_category(merge_bt, service_code, service_business_topic_cluster)
        service_info = {}
        service_info["allSortedBusinessTopics"] = sorted_business_topics
        service_info["businessTopics"] = business_topic
        service_info["normalTopics"] = normal_topic
        service_info["clusterBusinessTopics"] = cluster_business_topic
        service_info["clusterNormalTopics"] = cluster_normal_topic
        service_info["allBusinessTopics"] = merge_bt
        service_info["serviceCode"] = service_code

        service_infos[service_code] = service_info
    return service_infos
