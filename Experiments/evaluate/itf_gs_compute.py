import numpy
import numpy as np
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score
from research_2.config.global_config import global_config


def get_node_by_name(graph, node_name):
    return graph.nodes[node_name]


def cluster_interface_by_business_topic_similarity(interface_info_list, service_code, two_node_metric_dict):
    data_points = []

    topic_set = set()
    for interface_info in interface_info_list:
        interface_full_name = interface_info['fullName']
        business_topics = interface_info['clusterBusinessTopics']
        for key in business_topics:
            topic_set.add(key)
        data_points.append(interface_full_name)
    if len(data_points) == 1:
        return None
    if len(data_points) == 2:
        return {data_points[0]: 0, data_points[1]: 1}
    similarity_matrix = np.zeros((len(data_points), len(data_points)))
    for i, data_point_i in enumerate(data_points):
        for j, data_point_j in enumerate(data_points):
            if data_point_i == data_point_j:
                similarity_matrix[i, j] = 0
            else:
                two_interface_info = two_node_metric_dict[data_point_i + "<--->" + data_point_j]
                similarity_matrix[i, j] = two_interface_info['topicCohesive']

    silhouette_scores = {}
    for i in range(2, len(interface_info_list)):
        cluster_algorithm = SpectralClustering(n_clusters=i, affinity='precomputed', random_state=42)
        cluster_algorithm.fit(similarity_matrix)
        labels = cluster_algorithm.labels_

        silhouette_avg = silhouette_score(similarity_matrix, labels)
        silhouette_scores[i] = silhouette_avg

    max_score_cluster_num = 0
    max_score = -1
    for cluster_num, score in silhouette_scores.items():
        if max_score < score:
            max_score = score
            max_score_cluster_num = cluster_num
    cluster_algorithm = SpectralClustering(n_clusters=max_score_cluster_num, affinity='precomputed', random_state=42)
    cluster_algorithm.fit(similarity_matrix)
    labels = cluster_algorithm.labels_

    interface_cluster_dict = {}
    for i in range(0, len(labels)):
        interface_info = interface_info_list[i]
        interface_cluster_dict[interface_info['fullName']] = labels[i]

        interface_info.update({"clusterInService": labels[i]})
    return interface_cluster_dict


def compute_granularity_smells(graph, interface_nodes, two_node_metric_dict):
    topic_cohesive_cliff_point = global_config.businessTopicCohesiveThreshold[0]

    same_topic_interface_between_service = {}
    same_service_wrong_cut_interface_dict = {}

    for key in two_node_metric_dict:
        two_node_metric_info = two_node_metric_dict[key]
        node1_info = two_node_metric_dict[key]['node1']
        node2_info = two_node_metric_dict[key]['node2']

        node1_service_code = node1_info['serviceCode']
        node2_service_code = node2_info['serviceCode']

        node1_name = two_node_metric_info['node1Name']
        node2_name = two_node_metric_info['node2Name']
        inter_interface_cohesive = two_node_metric_info['topicCohesive']

        if node1_service_code == node2_service_code:
            if inter_interface_cohesive <= 1 - topic_cohesive_cliff_point:
                if node1_name not in same_service_wrong_cut_interface_dict:
                    same_service_wrong_cut_interface_dict[node1_name] = {"topicCohesive": -1,
                                                                         "nodeName": node1_name,
                                                                         "nodeServiceCode": node1_service_code,
                                                                         "wrongCutTimesInService": 0,
                                                                         "wrongCutWithInService": []}
                if same_service_wrong_cut_interface_dict[node1_name]['topicCohesive'] <= inter_interface_cohesive:
                    same_service_wrong_cut_interface_dict[node1_name].update({
                        "nodeName": node1_name,
                        "mostWrongCutNodeName": node2_name,
                        "mostWrongCutServiceCode": node2_service_code,
                        "topicCohesive": inter_interface_cohesive
                    })

                same_service_wrong_cut_interface_dict[node1_name]['wrongCutTimesInService'] += 1
                same_service_wrong_cut_interface_dict[node1_name]['wrongCutWithInService'].append({
                    "nodeName": node1_name,
                    "wrongCutNodeName": node2_name,
                    "wrongCutServiceCode": node2_service_code,
                    "topicCohesive": inter_interface_cohesive
                })

        else:
            if inter_interface_cohesive >= topic_cohesive_cliff_point:
                if node1_name not in same_topic_interface_between_service:
                    same_topic_interface_between_service[node1_name] = {"topicCohesive": -1,
                                                                        "nodeName": node1_name,
                                                                        "nodeServiceCode": node1_service_code,
                                                                        "wrongCutTimesBetweenService": 0,
                                                                        "wrongCutWithBetweenService": []}

                same_topic_interface_between_service[node1_name]['wrongCutWithBetweenService'].append({
                    "nodeName": node1_name,
                    "wrongCutNode": node2_name,
                    "wrongCutServiceCode": node2_service_code,
                    "topicCohesive": inter_interface_cohesive
                })
    for interface_name in interface_nodes:
        interface_info = get_node_by_name(graph, interface_name)['data']
        interface_info.update({"wrongCutTimesInService": 0, "wrongCutWithInService": []})

    for interface_name in same_service_wrong_cut_interface_dict:
        update_info = same_service_wrong_cut_interface_dict[interface_name]
        interface_info = get_node_by_name(graph, interface_name)['data']
        interface_info.update({
            "wrongCutTimesInService": update_info['wrongCutTimesInService'],
            "wrongCutWithInService": update_info['wrongCutWithInService']
        })

    service_interfaces_dict = {}
    service_need_cluster_dict = {}
    for interface_name in interface_nodes:
        interface_info = get_node_by_name(graph, interface_name)['data']
        service_code = interface_info['serviceCode']
        if service_code not in service_interfaces_dict:
            service_interfaces_dict[service_code] = []

        service_interfaces_dict[service_code].append(interface_info)
        if 'wrongCutTimesInService' in interface_info and interface_info['wrongCutTimesInService'] != 0:
            service_need_cluster_dict[service_code] = True

    for service_code in service_interfaces_dict:
        if service_code not in service_need_cluster_dict:
            continue
        interface_info_list = service_interfaces_dict[service_code]

        interface_clusters = cluster_interface_by_business_topic_similarity(interface_info_list, service_code,
                                                                            two_node_metric_dict)
        if not interface_clusters:
            continue
        cluster_wrong_cut_number_list = {}
        for interface_name in interface_clusters:
            interface_info = get_node_by_name(graph, interface_name)['data']
            cluster_id = interface_clusters[interface_name]
            if cluster_id not in cluster_wrong_cut_number_list:
                cluster_wrong_cut_number_list[cluster_id] = []
            cluster_wrong_cut_number_list[cluster_id].append(interface_info['wrongCutTimesInService'])
        wrong_cut_min = 99999
        min_wrong_cut_cluster = 0
        for cluster_id in cluster_wrong_cut_number_list:
            wrong_cut_list = cluster_wrong_cut_number_list[cluster_id]
            wrong_cut_mean = numpy.mean(numpy.asarray(wrong_cut_list))
            if wrong_cut_min > wrong_cut_mean:
                wrong_cut_min = wrong_cut_mean
                min_wrong_cut_cluster = cluster_id

        for interface_name in interface_clusters:
            cluster_id = interface_clusters[interface_name]
            if cluster_id == min_wrong_cut_cluster:
                continue
            interface_info = get_node_by_name(graph, interface_name)['data']
            interface_info.update({"isSameServiceWrongCut": True})


    for interface_info in same_topic_interface_between_service.values():
        node_name = interface_info['nodeName']
        node1_info = get_node_by_name(graph, node_name)['data']

        node1_info.update(
            {
                "haveTopicInOtherService": True,
                "similarTopicInfo": {
                    "similarTopicInterfaces": interface_info['wrongCutWithBetweenService'],
                }
            }
        )
