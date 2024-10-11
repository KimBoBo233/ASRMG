import json
import os

import numpy
import pandas
from deap import creator, base

from research_2.btc import bt_merge
from research_2.config.global_config import global_config
from research_2.group import group_util
from research_2.preprocess import initiator

creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))
creator.create("Individual", dict, fitness=creator.FitnessMulti)

from research_2.fitness import service_fitness


def print_pop_metrics(generation, interface_pop, refer_interfaces):
    total_itf_intra_ = 0
    total_itf_inter_ = 0
    for itf in interface_pop:
        new_service_code = itf["serviceCode"]
        endpoint_name = itf["endpointName"]
        full_name = itf["fullName"]
        split_ = full_name.split(":")
        if global_config.print_reconstruct_fitness:
            print("intra={:.5f},inter={:.5f}".format(itf.fitness.values[0], itf.fitness.values[1]),
                  "\t", split_[0], "-->", new_service_code, "\t", endpoint_name, )
        total_itf_intra_ += itf.fitness.values[0]
        total_itf_inter_ += itf.fitness.values[1]
    avg_itf_intra = total_itf_intra_ / len(interface_pop)
    avg_itf_inter = total_itf_inter_ / len(interface_pop)

    for itf in refer_interfaces:
        new_service_code = itf["serviceCode"]
        endpoint_name = itf["endpointName"]
        full_name = itf["fullName"]
        split_ = full_name.split(":")
        if global_config.print_reconstruct_fitness:
            print("refer intra={:.5f},inter={:.5f}".format(itf.fitness.values[0], itf.fitness.values[1]),
                  "\t", split_[0], "-->", new_service_code, "\t", endpoint_name, )
        total_itf_intra_ += itf.fitness.values[0]
        total_itf_inter_ += itf.fitness.values[1]
    all_interfaces = interface_pop + refer_interfaces
    service_groups = group_util.group_by_service(all_interfaces)

    service_fitnesses, sys_intra, sys_inter = service_fitness.compute_service_fitness(service_groups)

    return avg_itf_intra, avg_itf_inter, service_fitnesses, len(service_groups), sys_intra, sys_inter


def prepare_data_after_evaluate(refer, reconstruct_result):
    interfaces = refer + reconstruct_result

    btc_dict = {}
    for itf in interfaces:
        service_code = itf['serviceCode']
        if service_code not in btc_dict:
            btc_dict[service_code] = {}

        business_btc = itf['clusterBusinessTopics']
        normal_btc = itf['clusterNormalTopics']
        for key in business_btc:
            btc = business_btc[key]
            if key not in btc_dict[service_code]:
                btc_dict[service_code][key] = {"info": btc['tag'], "weight": btc['weight'], "isTopic": btc['isTopic']}
            else:
                btc_dict[service_code][key]['weight'] += btc['weight']

        for key in normal_btc:
            btc = normal_btc[key]
            if key not in btc_dict[service_code]:
                btc_dict[service_code][key] = {"info": btc['tag'], "weight": btc['weight'], "isTopic": btc['isTopic']}
            else:
                btc_dict[service_code][key]['weight'] += btc['weight']
    services = {}

    for service_code in btc_dict:
        service_btc = btc_dict[service_code]
        sorted_clusters = bt_merge.sort_bt_or_btc(service_btc)
        cluster_business_topic = {}
        cluster_normal_topic = {}
        for tag in sorted_clusters:
            if tag['isTopic'] == "true" and tag['percentage'] > 0.02:
                cluster_business_topic[tag['tag']] = tag
            else:
                cluster_normal_topic[tag['tag']] = tag

        services[service_code] = {
            "serviceCode": service_code,
            "clusterBusinessTopics": cluster_business_topic,
            "clusterNormalTopics": cluster_normal_topic
        }

    return interfaces, services


def compute_metrics(refer, reconstruct_result, method_call_tree_csv, interface_json):
    population = []
    for itf in reconstruct_result:
        population.append(creator.Individual(itf))
    refers = []
    for itf in refer:
        refers.append(creator.Individual(itf))

    reconstruct_result = population
    from research_2.fitness import interface_fitness
    interface_fitness.compute_fitness_of_interface_evaluate(reconstruct_result, refers)
    btc_metrics = print_pop_metrics(-1, reconstruct_result, refers)

    from research_2.evaluate import data_coherence
    data_metrics = data_coherence.compute(reconstruct_result, refers, method_call_tree_csv, interface_json)
    return btc_metrics, data_metrics


def load_result(data_set_name, pop_size, constrain):
    system_prefix = global_config.system_prefix
    file_name = f"pop={pop_size}_gen=600_cp=0.9_mp=0.2_fast=1_constrain={constrain}.json"

    result_prefix = f"{system_prefix}\\result\\{data_set_name}"
    method_call_tree_csv = f"{system_prefix}\\input\\{data_set_name}\\method-call-tree.csv"
    interface_data_json = f"{system_prefix}\\input\\{data_set_name}\\interface_data_{data_set_name}.json"

    file = open('{}\\{}'.format(result_prefix, file_name), mode="r")
    reconstructed_data = json.load(file)
    refer_file = open('{}\\refer_{}'.format(result_prefix, file_name), mode="r")
    refers = json.load(refer_file)["times"]
    each_iter_f = open('{}\\each_{}'.format(result_prefix, file_name), mode="r")
    each_iter = json.load(each_iter_f)["times"]

    return refers, reconstructed_data, each_iter, method_call_tree_csv, interface_data_json


def evaluate_process(data_set_name, pop_size, times, constrain):
    refers, reconstructed_data, each_iter, method_call_tree_csv, interface_data_json = load_result(
        data_set_name,
        pop_size, constrain)

    each_iter = each_iter[times]
    reconstruct_detail = reconstructed_data["times"][times]["max_intra_ge"]

    refer = refers[times]["refer"]
    reconstruct_result = reconstruct_detail["reconstruct_result"]

    btc_metrics, data_metrics = compute_metrics(refer, reconstruct_result, method_call_tree_csv, interface_data_json)

    interfaces, services = prepare_data_after_evaluate(refer, reconstruct_result)
    print(f"pop={pop_size}")
    print(f'{times}({reconstruct_detail["ge_number"]}),')
    print(
        f"intra_\tinter_\tdata_coh\tdata_cop\tsys_intra\tsys_inter"
    )
    print(
        f"{btc_metrics[0]}"
        f"\t{btc_metrics[1]}"
        f"\t{data_metrics[0]}"
        f"\t{data_metrics[1]}"
        f"\t{btc_metrics[4]}"
        f"\t{btc_metrics[5]}"
    )



def evaulate_default(data_set_name):
    interfaces, services = initiator.init(data_set_name)

    gs_interfaces_key = initiator.read_granularity_smells(data_set_name)

    for interface in interfaces:
        interface["methodCallTree"] = None
        interface["allSortedBusinessTopics"] = None
    gs_interfaces, normal_interfaces = initiator.split_interfaces(interfaces, gs_interfaces_key)

    dict = {
        "reconstruct": gs_interfaces,
        "refer": normal_interfaces
    }
    system_prefix = global_config.system_prefix
    method_call_tree_csv = f"{system_prefix}\\input\\{data_set_name}\\method-call-tree.csv"
    interface_data_json = f"{system_prefix}\\input\\{data_set_name}\\interface_data_{data_set_name}.json"
    btc_metrics, data_metrics = compute_metrics(normal_interfaces, gs_interfaces, method_call_tree_csv,
                                                interface_data_json)
    print(
        f"intra_\tinter_\tdata_coh\tdata_cop\tsys_intra\tsys_inter"
    )
    print(
        f"{btc_metrics[0]}\t{btc_metrics[1]}\t{data_metrics[0]}\t{data_metrics[1]}\t{btc_metrics[4]}\t{btc_metrics[5]}"
    )


def evaluate_fitness_correct(data_set_name, pop_size, constrain):
    refers, reconstructed_data, each_iter, method_call_tree_csv, interface_data_json = load_result(
        data_set_name,
        pop_size,
        constrain)

    correct_result = {}
    for times in range(0, 20):
        refer = refers[str(times)]["refer"]

        reconstruct_detail = reconstructed_data["times"][str(times)]["max_intra_ge"]
        reconstruct_result = reconstruct_detail["reconstruct_result"]
        intra_from_json = reconstruct_detail["intra_"]
        inter_from_json = reconstruct_detail["inter_"]

        btc_metrics, data_metrics = compute_metrics(refer, reconstruct_result, method_call_tree_csv,
                                                    interface_data_json)
        similar = str(intra_from_json)[:7] == str(btc_metrics[0])[:7] \
                  and str(inter_from_json)[:7] == str(btc_metrics[1])[:7]
        correct_result[str(times)] = {
            "ge_num": reconstruct_detail["ge_number"],
            "intra_json": intra_from_json,
            "intra_": btc_metrics[0],

            "inter_json": inter_from_json,
            "inter_": btc_metrics[1],
            "sim": similar
        }
    return correct_result


def fast_evaluate(data_set_name, constrain, pop_list):
    for pop_size in pop_list:
        times = 0

        refers, reconstructed_data, each_iter, method_call_tree_csv, interface_data_json = load_result(
            data_set_name,
            pop_size,
            constrain)

        refer = refers[times]["refer"]

        reconstruct_detail = reconstructed_data["times"][times]["max_intra_ge"]
        reconstruct_result = reconstruct_detail["reconstruct_result"]

        btc_metrics, data_metrics = compute_metrics(refer, reconstruct_result, method_call_tree_csv,
                                                    interface_data_json)

        print(
            f"{pop_size}\t\t"
            f"{times}\t"
            f"{btc_metrics[0]}\t"
            f"{btc_metrics[1]}\t"
            f"{data_metrics[0]}\t"
            f"{data_metrics[1]}\t"
            f"{btc_metrics[4]}\t"
            f"{btc_metrics[5]}\t"
        )


if __name__ == "__main__":
    data_set_name = "BookStoreApp"

    pop_size = "8"
    constrain = "1"
    times = "11"
    use_human = False

    evaluate_process(data_set_name, pop_size, times, constrain)
