def get_interface_with_btc(path_tree_csv, method_call_tree_csv, business_topics_csv, service_business_topic_cluster):
    import research_2.path.path_reader as path_reader
    interfaces = path_reader.get_all_interfaces(path_tree_csv)

    import research_2.btc.interface_method_binder as interface_method_binder
    interfaces = interface_method_binder.bind_interface_and_method(interfaces, method_call_tree_csv)

    import research_2.btc.business_object_binder as business_object_binder
    interfaces = business_object_binder.bind_business_object(interfaces, business_topics_csv)

    import research_2.btc.btc_binder as btc_binder

    for interface in interfaces:
        all_business_topics = interface['allBusinessTopics']
        service_code = interface['serviceCode']

        sorted_business_topics, business_topic, normal_topic, cluster_business_topic, cluster_normal_topic = \
            btc_binder.sort_btc_and_category(all_business_topics, service_code, service_business_topic_cluster)
        interface["allSortedBusinessTopics"] = sorted_business_topics
        interface["businessTopics"] = business_topic
        interface["normalTopics"] = normal_topic
        interface["clusterBusinessTopics"] = cluster_business_topic
        interface["clusterNormalTopics"] = cluster_normal_topic

    return interfaces
