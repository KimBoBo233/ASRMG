def group_by_service(interfaces):
    service_group = {}
    for itf in interfaces:
        service_code = itf['serviceCode']
        if service_code not in service_group:
            service_group[service_code] = []

        service_group[service_code].append(itf)
    return service_group
