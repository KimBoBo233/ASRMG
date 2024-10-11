import concurrent.futures
import copy
import ctypes
import json
import random

import numpy
from deap import base, creator, tools

import strategy
from research_2.config import fixed_combination
from research_2.config.global_config import global_config
from research_2.group import group_util

creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))
creator.create("Individual", dict, fitness=creator.FitnessMulti)


def initialize_population_default(construct_interface, candidate_service, refer_interface,
                                  split_candidate, default_size, target_size):
    population = []
    new_refer = []
    if target_size > default_size:
        new_refer = refer_interface
        index = 0
        for itf in construct_interface:
            itf["serviceCode"] = split_candidate[index % len(split_candidate)]
            population.append(creator.Individual(itf))
            index += 1
    if target_size == default_size:
        new_refer = refer_interface
        for itf in construct_interface:
            population.append(creator.Individual(itf))
    if target_size < default_size:
        for itf in construct_interface:
            itf_indv = creator.Individual(itf)
            if itf_indv["serviceCode"] not in candidate_service:
                rand_index = random.randint(0, len(candidate_service) - 1)
                itf_indv["serviceCode"] = candidate_service[rand_index]
            population.append(itf_indv)

        for itf in refer_interface:
            if itf["serviceCode"] not in candidate_service:
                rand_index = random.randint(0, len(candidate_service) - 1)
                itf_indv = creator.Individual(itf)
                itf_indv["serviceCode"] = candidate_service[rand_index]
                population.append(itf_indv)
            else:
                new_refer.append(itf)

    return population, new_refer


def calculate_fitness(population, refer_interface):
    from research_2.fitness import interface_fitness
    interface_fitness.compute_fitness_of_interface(population, refer_interface)


def crossover(indv_1, indv_2, together, all):
    if indv_1['serviceCode'] == indv_2['serviceCode']:
        return indv_1, indv_2
    for together_group in together:
        if indv_1["endpointName"] in together_group and indv_2["endpointName"] in together_group:
            return indv_1, indv_2

    indv_1_service_code = indv_1['serviceCode']
    indv_2_service_code = indv_2['serviceCode']

    indv_1['serviceCode'] = indv_2_service_code
    indv_2['serviceCode'] = indv_1_service_code

    for together_group in together:
        if indv_1["endpointName"] in together_group:
            for indv in all:
                if indv["endpointName"] in together_group and not indv_1 == indv:
                    indv['serviceCode'] = indv_2_service_code
        if indv_2["endpointName"] in together_group:
            for indv in all:
                if indv["endpointName"] in together_group and not indv_2 == indv:
                    indv['serviceCode'] = indv_1_service_code

    return creator.Individual(indv_1), creator.Individual(indv_2)


def mutate(individual, candidate_services, together, all):
    group = group_util.group_by_service(all)
    try:
        old_service_code = individual['serviceCode']

        randindex = random.randint(0, len(candidate_services) - 1)
        while old_service_code == candidate_services[randindex]:
            randindex = random.randint(0, len(candidate_services) - 1)

        mutate_lib_id = list(candidate_services)[randindex]
        individual['serviceCode'] = mutate_lib_id
        for together_group in together:
            if individual["endpointName"] in together_group:
                for indv in all:
                    if indv["endpointName"] in together_group:
                        indv['serviceCode'] = mutate_lib_id

        return individual
    except IndexError:
        print(randindex)


toolbox = base.Toolbox()
toolbox.register("evaluate", calculate_fitness)
toolbox.register("mate", crossover)

toolbox.register("mutate", mutate)
toolbox.register("select", tools.selNSGA2)

from research_2.fitness import service_fitness


def print_pop_metrics(generation, interface_pop, refer_interfaces):
    total_itf_intra_ = 0
    total_itf_inter_ = 0
    for itf in interface_pop:
        total_itf_intra_ += itf.fitness.values[0]
        total_itf_inter_ += itf.fitness.values[1]
    avg_itf_intra = total_itf_intra_ / len(interface_pop)
    avg_itf_inter = total_itf_inter_ / len(interface_pop)

    service_groups = group_util.group_by_service(interface_pop + refer_interfaces)

    service_fitnesses, sys_intra, sys_inter = service_fitness.compute_service_fitness(service_groups)

    return avg_itf_intra, avg_itf_inter, service_fitnesses, len(service_groups)


def perform_algorithm(repeat_index, start_pop, candiate_service, refer_interfaces, together):
    max_generations = global_config.max_generations[0]
    cross_probability = global_config.cross_probability[0]
    mutate_probability = global_config.mutate_probability[0]

    print_pop_metrics(generation=-1, interface_pop=start_pop, refer_interfaces=refer_interfaces)
    population = start_pop
    candidate_services = candiate_service

    pop_intra_ = []
    pop_inter = []
    pop_merge = []
    results = []
    service_fitness_ = []
    for generation in range(max_generations):

        offspring = [toolbox.clone(ind) for ind in population]

        for i in range(1, len(offspring), 2):
            if random.random() < cross_probability:
                offspring[i - 1], offspring[i] = toolbox.mate(offspring[i - 1], offspring[i], together, offspring)
                del offspring[i - 1].fitness.values, offspring[i].fitness.values

        for i in range(len(offspring)):
            if random.random() < mutate_probability:
                offspring[i] = toolbox.mutate(offspring[i], candidate_services, together, offspring)
                del offspring[i].fitness.values

        toolbox.evaluate(offspring, refer_interfaces)

        select_population = toolbox.select(offspring + population, len(population))
        select_population = strategy.removeDuplicate(select_population, population, offspring, together,
                                                     refer_interfaces)

        population = select_population
        if generation >= 0:
            toolbox.evaluate(population, refer_interfaces)
            strategy.mutate_worse_indv(population, candidate_services, toolbox, population + refer_interfaces)
            population = strategy.handle_together(population, together, refer_interfaces)

            fitness_list = []
            service_list = []
            for indv in population:
                fitness_list.append(indv.fitness.values[0] + (1 - indv.fitness.values[1]))
            for indv in population + refer_interfaces:
                service_list.append(indv["serviceCode"])
            service_set = set(service_list)
            empty_service = list(set(candiate_service) - service_set)
            min_index = numpy.argsort(fitness_list)
            min_index_change = [0] * len(min_index)
            for i in range(len(empty_service)):
                for j in range(len(min_index)):
                    bad_indv = population[min_index[j]]
                    svc_code = bad_indv["serviceCode"]
                    count = 0
                    for indv in population + refer_interfaces:
                        if indv["serviceCode"] == svc_code:
                            count += 1
                    if count <= 1:
                        continue
                    else:
                        if min_index_change[min_index[j]] == 1:
                            continue
                        else:
                            bad_indv["serviceCode"] = empty_service[i]
                            min_index_change[min_index[j]] = 1
                            break

        toolbox.evaluate(population, refer_interfaces)

        metrics = print_pop_metrics(generation=generation + 1, interface_pop=population,
                                    refer_interfaces=refer_interfaces)

        pop_intra_.append(metrics[0])
        pop_inter.append(metrics[1])
        pop_merge.append(metrics[0] + (1 - metrics[1]))
        service_fitness_.append(metrics[2])
        results.append(copy.deepcopy(population))

    return pop_intra_, pop_inter, pop_merge, service_fitness_, results, repeat_index


import preprocess.initiator as initiator


def pre_handle_candidate(population_offset, candidate_service, exclude_services, dataset_name):
    default_size = len(candidate_service)
    actual_size = default_size + population_offset

    split_candidate = []
    new_candidate_service = []
    if actual_size > default_size:
        sample_num = population_offset if population_offset <= len(exclude_services) else len(exclude_services)
        exclude_service_sample = random.sample(exclude_services, sample_num)
        for candidate in candidate_service:
            if candidate not in exclude_service_sample:
                new_candidate_service.append(candidate)

        for i in range(0, population_offset):
            new_candidate_service.append("NEW_SPLIT_SERVICE_" + str(i))
            split_candidate.append("NEW_SPLIT_SERVICE_" + str(i))
        candidate_service = new_candidate_service
    if actual_size == default_size:
        pass

    if actual_size < default_size:
        if dataset_name == "petclinic":
            if population_offset == -1:
                candidate_service.remove("spring-petclinic-customers-service")
        if dataset_name == "train-ticket-manual":

            if population_offset == -1:
                candidate_service.remove("ts-admin-basic-info-service")
            if population_offset == -2:
                candidate_service.remove("ts-admin-basic-info-service")
                candidate_service.remove("ts-security-service")
            if population_offset == -3:
                candidate_service.remove("ts-admin-basic-info-service")
                candidate_service.remove("ts-security-service")
                candidate_service.remove("ts-basic-service")
    return candidate_service, split_candidate, default_size, actual_size


def reconstruct_process(skips, together, exclude_services, population_offsets, constrain, dataset_name):
    for population_offset in population_offsets:
        interfaces, services = initiator.init(dataset_name)

        gs_interfaces_key = initiator.read_granularity_smells(dataset_name)
        gs_interfaces, normal_interfaces = initiator.split_interfaces(interfaces, gs_interfaces_key)

        gs_interfaces_after_skip = []
        for gs_interface in gs_interfaces:
            if gs_interface['endpointName'] in skips:
                normal_interfaces.append(gs_interface)
            else:
                gs_interfaces_after_skip.append(gs_interface)

        repeat_result_of_GA = {}
        repeat_result_of_GA["times"] = {}
        each_gen_fitness = {}
        each_gen_fitness["times"] = {}
        repeat_refer_of_GA = {}
        repeat_refer_of_GA["times"] = {}

        repeat_time = global_config.repeatTimes[0]
        actual_size = 0
        for i in range(0, repeat_time):
            candidate_service = list(services.keys())
            new_candidate_service, split_candidate, default_size, actual_size = pre_handle_candidate(
                population_offset=population_offset,
                candidate_service=copy.deepcopy(candidate_service),
                exclude_services=copy.deepcopy(exclude_services),
                dataset_name=dataset_name)

            start_pop, refer_interface = initialize_population_default(
                construct_interface=copy.deepcopy(gs_interfaces_after_skip),
                candidate_service=copy.deepcopy(new_candidate_service),
                refer_interface=copy.deepcopy(normal_interfaces),
                split_candidate=copy.deepcopy(split_candidate),
                default_size=default_size,
                target_size=actual_size)
            calculate_fitness(start_pop, refer_interface)

            start_pop_deep = copy.deepcopy(start_pop)
            candidate_service_deep = copy.deepcopy(new_candidate_service)
            refer_interface_deep = copy.deepcopy(refer_interface)
            intra_, inter_, merge_sys_cohesive, service_fitness_, results, repeat_index = perform_algorithm(
                repeat_index=i,
                start_pop=start_pop_deep,
                candiate_service=candidate_service_deep,
                refer_interfaces=refer_interface_deep,
                together=together)

            argmax = numpy.argmax(intra_)
            m_argmax = numpy.argmax(merge_sys_cohesive)
            argmin = numpy.argmin(inter_)

            results_new = json.loads(json.dumps(results))
            for result in results_new[argmax]:
                result["methodCallTree"] = None
                result["allSortedBusinessTopics"] = None
            for result in results_new[m_argmax]:
                result["methodCallTree"] = None
                result["allSortedBusinessTopics"] = None
            for result in results_new[argmin]:
                result["methodCallTree"] = None
                result["allSortedBusinessTopics"] = None
            for result in refer_interface_deep:
                result["methodCallTree"] = None
                result["allSortedBusinessTopics"] = None

            each_gen_fitness["times"][repeat_index] = {
                "intra_": intra_,
                "inter_": inter_
            }

            repeat_result_of_GA["times"][repeat_index] = {
                "max_merge_ge": {
                    "merge_score_": merge_sys_cohesive[m_argmax],
                    "intra_": intra_[m_argmax],
                    "inter_": inter_[m_argmax],
                    "service_fitness_": service_fitness_[m_argmax],
                    "ge_number": str(m_argmax),
                    "reconstruct_result": results_new[m_argmax],
                },
                "max_intra_ge": {
                    "intra_": intra_[argmax],
                    "inter_": inter_[argmax],
                    "service_fitness_": service_fitness_[argmax],
                    "ge_number": str(argmax),
                    "reconstruct_result": results_new[argmax],
                },
                "min_inter_ge": {
                    "intra_": intra_[argmin],
                    "inter_": inter_[argmin],
                    "service_fitness_": service_fitness_[argmin],
                    "ge_number": str(argmin),
                    "reconstruct_result": results_new[argmin],
                }
            }

            repeat_refer_of_GA["times"][repeat_index] = {
                "refer": refer_interface_deep
            }

        max_generations = global_config.max_generations[0]
        cp = global_config.cross_probability[0]
        mp = global_config.mutate_probability[0]
        file_name = "pop={}_gen={}_cp={}_mp={}_fast=1_constrain={}.json".format(
            actual_size,
            max_generations,
            cp,
            mp,
            constrain
        )

        each_gen_fitness_file = "each_" + file_name
        refer_file = "refer_" + file_name

        result_prefix = f"{global_config.result_prefix}\\{dataset_name}\\"
        with open('{}\\{}'.format(result_prefix, file_name), 'w') as file:
            json.dump(repeat_result_of_GA, file)
            file.close()

        with open('{}\\{}'.format(result_prefix, each_gen_fitness_file), 'w') as file:
            json.dump(each_gen_fitness, file)
            file.close()

        with open('{}\\{}'.format(result_prefix, refer_file), 'w') as file:
            json.dump(repeat_refer_of_GA, file)
            file.close()


if __name__ == "__main__":
    skips = []
    together = []
    exclude_services = []

    dataset_name = global_config.datasetName
    constrain = global_config.constrain
    population_offsets = global_config.populationSizeOffset

    dataset_names = "train-ticket"
    constrain = 1, 0
    population_offsets = -3, -2, -1, 0, 1, 2, 3, 4

    for cons in constrain:
        exclude_services = fixed_combination.load_exclude(dataset_name)
        if cons == 1:
            together = fixed_combination.fixed_combination(dataset_name)

        reconstruct_process(skips, together, exclude_services, population_offsets, cons, dataset_name)
