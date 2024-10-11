import random

import numpy

from research_2.config.global_config import global_config
from research_2.evaluate import btc_cohesive


def ALX(population):
    lib_remove_index = random.randint(0, len(population) - 1)
    lib_insert_index = random.randint(0, len(population) - 1)

    remove_lib = population[lib_remove_index]
    insert_lib = population[lib_insert_index]

    remove_class_index = random.randint(0, len(remove_lib['lib_class']) - 1)
    remove_class = remove_lib['lib_class'][remove_class_index]
    del remove_lib['lib_class'][remove_class_index]

    insert_lib['lib_class'].append(remove_class)
    return population


def _2P2C(population):
    return population


def _1PNC(population):
    pass


def get_individuals_by_name(duplicate_name, population):
    result = []
    for indv in population:
        if indv['fullName'] == duplicate_name:
            result.append(indv)
    return result


def select_better_fitness_indv(duplicate_indvs):
    max = -999
    max_fitness_indv = None
    for indv in duplicate_indvs:
        fitness = indv.fitness.values
        score = fitness[0] + (1 - fitness[1])
        if score > max:
            max = score
            max_fitness_indv = indv
    return max_fitness_indv


def get_better_in_duplicate(select_population):
    duplicate_individual_count = {}
    for select_individual in select_population:
        service_code = select_individual['fullName']
        if service_code not in duplicate_individual_count:
            duplicate_individual_count[service_code] = 1
        else:
            duplicate_individual_count[service_code] += 1

    duplicate_names = []
    for key in duplicate_individual_count:
        if duplicate_individual_count[key] > 1:
            duplicate_names.append(key)

    better_indv_in_duplicate = []
    for duplicate_name in duplicate_names:
        duplicate_indvs = get_individuals_by_name(duplicate_name, select_population)
        better_fitness_indv = select_better_fitness_indv(duplicate_indvs)
        better_indv_in_duplicate.append(better_fitness_indv)
    return better_indv_in_duplicate, duplicate_names


def get_better_in_miss(select_population, population, offspring):
    miss_individuals = []
    indiv_names = [indv['fullName'] for indv in population]
    select_names = [indv['fullName'] for indv in select_population]
    missed_names = set(indiv_names).difference(set(select_names))
    for miss_name in missed_names:
        indvs_1 = get_individuals_by_name(miss_name, population)
        indvs_2 = get_individuals_by_name(miss_name, offspring)
        better_miss_individual = select_better_fitness_indv(indvs_1 + indvs_2)
        miss_individuals.append(better_miss_individual)
    return miss_individuals


def get_best_service_code(indv, refer, candidate_services):
    cohesives = {}
    for itf in refer:
        if itf["fullName"] == indv["fullName"]:
            continue
        if itf["serviceCode"] not in candidate_services:
            continue
        service_code = itf["serviceCode"]
        if service_code not in cohesives:
            cohesives[service_code] = []
        cohesive = btc_cohesive.compute_cohesive(indv, itf)
        cohesives[service_code].append(cohesive)

    mean_cohesive = []
    for service_code in cohesives:
        mean_cohesive.append(numpy.mean(cohesives[service_code]))
    argmax = numpy.argmax(mean_cohesive)
    return list(cohesives.keys())[argmax], mean_cohesive[argmax]


def mutate_worse(indv, refer, candidate_services, toolbox):
    best_service_code, cohesive_value = get_best_service_code(indv, refer, candidate_services)
    indv["serviceCode"] = best_service_code


def mutate_worse_indv(mutate_indv, candidate_services, toolbox, refer):
    worse_mutate_nums = global_config.worse_mutate_nums

    fitness_list = []
    for indv in mutate_indv:
        fitness_list.append(indv.fitness.values[0] + (1 - indv.fitness.values[1]))

    sorted_indices = numpy.argsort(fitness_list)
    worse_fitness = []
    if worse_mutate_nums >= len(mutate_indv):
        top_n_indices = sorted_indices
        worse_fitness = fitness_list
    else:
        top_n_indices = sorted_indices[:worse_mutate_nums]
        for index in top_n_indices:
            worse_fitness.append(fitness_list[index])

    if numpy.mean(worse_fitness) > global_config.worse_min_mutate_fitness:
        return
    else:
        if worse_mutate_nums >= len(mutate_indv):
            for indv in mutate_indv:
                mutate_worse(indv, refer, candidate_services, toolbox)
        else:
            for index in top_n_indices:
                indv = mutate_indv[index]
                mutate_worse(indv, refer, candidate_services, toolbox)


def handle_together(select_pop, together, refer_interfaces):
    for together_group in together:
        together_indv = []
        refer_first = None
        for indv in select_pop:
            if indv["endpointName"] in together_group:
                together_indv.append(indv)

        for tog_indv in together_group:
            for refer_indv in refer_interfaces:
                if refer_indv["endpointName"] == tog_indv:
                    refer_first = refer_indv
                    break

        if refer_first:
            for indv in together_indv:
                indv["serviceCode"] = refer_first["serviceCode"]
        better_indv = select_better_fitness_indv(together_indv)
        for indv in together_indv:
            indv["serviceCode"] = better_indv["serviceCode"]

    return select_pop


def removeDuplicate(select_population, parent, offspring, together, refer_interfaces):
    better_indv_in_duplicate, duplicate_names = get_better_in_duplicate(select_population)

    better_indv_in_miss = get_better_in_miss(select_population, parent, offspring)

    new_pop = []
    for individual in select_population:
        if not individual['fullName'] in duplicate_names:
            new_pop.append(individual)

    for better_dup_indv in better_indv_in_duplicate:
        new_pop.append(better_dup_indv)

    for better_miss_indv in better_indv_in_miss:
        new_pop.append(better_miss_indv)
    select_pop = new_pop

    handle_together(select_pop, together, refer_interfaces)

    return select_pop
