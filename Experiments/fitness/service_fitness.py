import numpy

from research_2.fitness import interface_fitness


def compute_svc_intra_cohesive(interfaces):
    svc_intra_cohesive_list = []
    for itf1 in interfaces:
        itf_intra_cohesive_list = interface_fitness.compute_itf_intra_cohesive(itf1, interfaces)
        svc_intra_cohesive_list.extend(itf_intra_cohesive_list)
    return svc_intra_cohesive_list


def compute_svc_inter_cohesive(service_interfaces, service_groups):
    inter_cohesive_list = []
    for itf in service_interfaces:
        indv_service_code = itf["serviceCode"]
        for group_service_code in service_groups:
            if group_service_code == indv_service_code:
                continue
        itf_inter_cohesive_list = interface_fitness.compute_itf_inter_cohesive(itf, service_groups)
        inter_cohesive_list.extend(itf_inter_cohesive_list)
    return inter_cohesive_list


def compute_service_fitness(service_groups):
    service_fitness = {}

    sys_intra = []
    sys_inter = []
    for service in service_groups:
        service_interfaces = service_groups[service]
        svc_intra_cohesive_list = compute_svc_intra_cohesive(service_interfaces)
        svc_intra_cohesive = numpy.mean(svc_intra_cohesive_list)
        sys_intra.extend(svc_intra_cohesive_list)

        svc_inter_cohesive_list = compute_svc_inter_cohesive(service_interfaces, service_groups)
        svc_inter_cohesive = numpy.mean(svc_inter_cohesive_list)
        sys_inter.extend(svc_inter_cohesive_list)

        service_fitness[service] = {"serviceCode": service,
                                    "intra_cohesive": svc_intra_cohesive,
                                    "inter_cohesive": svc_inter_cohesive}
    return service_fitness, numpy.mean(sys_intra), numpy.mean(sys_inter)
