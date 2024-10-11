import numpy
from research_2.config.global_config import global_config


def compute_itf_intra_cohesive(indv, service_interfaces):
    from research_2.evaluate import btc_cohesive

    intra_cohesive_list = []
    if len(service_interfaces) == 1:
        intra_cohesive_list.append(global_config.intra_cohesive_single_ift)
        intra_cohesive_list.append(global_config.intra_cohesive_single_ift)
        return intra_cohesive_list

    for itf in service_interfaces:
        if itf["fullName"] == indv["fullName"]:
            continue
        cohesive = btc_cohesive.compute_cohesive(indv, itf)
        if global_config.print_fitness_compute:
            print("intra_cohesive", indv['fullName'], itf['fullName'], cohesive)
        intra_cohesive_list.append(cohesive)
    return intra_cohesive_list


def compute_itf_inter_cohesive(indv, service_group):
    from research_2.evaluate import btc_cohesive

    inter_cohesive_list = []
    indv_service_code = indv["serviceCode"]
    for group_service_code in service_group:
        if group_service_code == indv_service_code:
            continue
        service_interfaces = service_group[group_service_code]
        for itf in service_interfaces:
            cohesive = btc_cohesive.compute_cohesive(indv, itf)
            if global_config.print_fitness_compute:
                print("inter_cohesive", indv['fullName'], itf['fullName'], cohesive)
            inter_cohesive_list.append(cohesive)
    return inter_cohesive_list


def compute_fitness_of_interface(population, refer_interface):
    interfaces = population + refer_interface
    from research_2.group import group_util
    service_group = group_util.group_by_service(interfaces)

    for indv in population:
        service_code = indv["serviceCode"]
        service_interfaces = service_group[service_code]
        intra_cohesive_list = compute_itf_intra_cohesive(indv, service_interfaces)
        inter_cohesive_list = compute_itf_inter_cohesive(indv, service_group)

        intra_cohesive = numpy.mean(intra_cohesive_list)
        inter_cohesive = numpy.mean(inter_cohesive_list)
        indv.fitness.values = (intra_cohesive, inter_cohesive)

    return None


def compute_fitness_of_interface_evaluate(population, refer_interface):
    interfaces = population + refer_interface
    from research_2.group import group_util
    service_group = group_util.group_by_service(interfaces)

    for indv in interfaces:
        service_code = indv["serviceCode"]
        service_interfaces = service_group[service_code]
        intra_cohesive_list = compute_itf_intra_cohesive(indv, service_interfaces)
        inter_cohesive_list = compute_itf_inter_cohesive(indv, service_group)

        intra_cohesive = numpy.mean(intra_cohesive_list)
        inter_cohesive = numpy.mean(inter_cohesive_list)
        indv.fitness.values = (intra_cohesive, inter_cohesive)

    return None
