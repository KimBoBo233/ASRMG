class global_config:
    system_prefix = f"C:\\Users\\a\\research"
    prefix = f"{system_prefix}\\input\\",
    result_prefix = f"{system_prefix}\\result"

    datasetName = "train-ticket-manual"
    populationSizeOffset = 1, 2, 3, 4
    constrain = 0

    repeatTimes = 1,
    max_generations = 600,
    fast_thresh = 2 / 3

    cross_probability = 0.9,
    mutate_probability = 0.2,

    intra_cohesive_single_ift = 0.5
    worse_mutate_nums = 3
    worse_min_mutate_fitness = 1.5

    print_detail_gs = True
    print_fitness_compute = False
    print_svc_iteration_fitness = False
    print_sys_iteration_fitness_100 = True
    print_gen_fitness = False
    print_result_of_threads = True
    print_cross_log = False
    print_reconstruct_fitness = False

    tag_ratio_similarity_thresh_hold = 0.85,
    businessTopicCohesiveThreshold = 0.85,
    business_topic_filter_thresh_hold = 0.02,
    sameServiceWrongCutTimes = 1,
