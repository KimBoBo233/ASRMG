import json
import research_2.btc.interface_btc as btc_merge
import research_2.btc.service_btc as service_btc
from research_2.btc import btc_binder
from research_2.config.global_config import global_config


def init(dataset_name):
    prefix = global_config.prefix[0]
    business_topic_csv = f"{prefix}{dataset_name}\\nlp-tags-weight-infer.csv"
    method_call_tree_csv = f"{prefix}{dataset_name}\\method-call-tree.csv"
    path_tree_csv = f"{prefix}{dataset_name}\\path-tree.csv"
    business_topic_cluster_json = f"{prefix}{dataset_name}\\serviceBusinessCluster.json"

    file = open(business_topic_cluster_json, mode="r")
    service_business_topic_cluster = json.load(file)
    file.close()

    interfaces = btc_merge.get_interface_with_btc(path_tree_csv, method_call_tree_csv, business_topic_csv,
                                                  service_business_topic_cluster)

    services = service_btc.get_service_with_btc(interfaces, service_business_topic_cluster)
    return interfaces, services


def read_granularity_smells(dataset_name):
    prefix = global_config.prefix[0]
    import pandas as pd
    itf_granularity_problems_csv = f"{prefix}{dataset_name}\\itf_granularity_problems2.csv"
    itf_granularity_problems_pd = pd.read_csv(itf_granularity_problems_csv)
    itf_problems = itf_granularity_problems_pd.to_dict("records")

    gs_interfaces = []
    for itf in itf_problems:
        service_code = itf["serviceCode"]
        interface_full_name = itf["interface"]
        gs_interfaces.append(interface_full_name)
    return gs_interfaces


def split_interfaces(interfaces, gs_interfaces_key):
    gs_interfaces = []
    normal_interfaces = []
    for interface in interfaces:
        full_name = interface['fullName']
        if full_name in gs_interfaces_key:
            gs_interfaces.append(interface)
        else:
            normal_interfaces.append(interface)
    return gs_interfaces, normal_interfaces
