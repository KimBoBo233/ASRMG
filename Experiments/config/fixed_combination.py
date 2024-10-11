def load_exclude(data_set_name):
    exclude_service = []
    if data_set_name == "mall4cloud":
        exclude_service = []
    elif data_set_name == "train-ticket-manual":
        exclude_service = ["ts-config-service", "ts-contacts-service", "ts-price-service", "ts-station-service"]

    return exclude_service


# fixed_combination
def fixed_combination(data_set_name):
    together = []
    if data_set_name == "BookStoreApp":
        together = [
            ["POST:/image/upload", "GET:/image/{imageId}"]
        ]
    if data_set_name == "mall4cloud":
        together = [
            ["GET:/sys_config/info/{key}", "POST:/sys_config/save"],
            ["POST:/ua/captcha/check", "POST:/ua/captcha/get"],
            ["POST:/feign/skuStockLock/lock", "DELETE:/a/sku_stock_lock", "GET:/a/sku_stock_lock"],
        ]
    elif data_set_name == "train-ticket-manual":
        together = [

            ["GET:/api/v1/adminbasicservice/adminbasic/trains",
             "DELETE:/api/v1/adminbasicservice/adminbasic/trains/{id}",
             "PUT:/api/v1/adminbasicservice/adminbasic/trains",
             "POST:/api/v1/adminbasicservice/adminbasic/trains"]
        ]
    elif data_set_name == "spring-cloud-shop":
        together = [
            [
                "POST:/user/app/send/code/sms",
                "GET:/platform/sms/page",
                "GET:/platform/sms/{smsTemplateCode}/info",
                "PUT:/platform/sms/modify"
            ],
            [
                "POST:/cart/app/orders/create",
                "POST:/cart/app/cart/delete/batch",
                "POST:/cart/app/cart/create"
            ],
            [
                "POST:/settlement/submit",
                "POST:/settlement/check",
                "POST:/settlement/create"
            ]
        ]
    return together
