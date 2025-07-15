DOMAIN_PAGE = {
    "amazon": {
        "type": "single",
        "login": "https://www.amazon.com/sign-in",
        "init": "https://www.amazon.com",
        "method": "id",
        "get_link_btn": "amzn-ss-get-link-button",
        "get_link": "amzn-ss-text-shortlink-textarea",
    },
    "aliexpress": {
        "type": "single",
        "login": "https://login.aliexpress.com",
        "init": "https://www.aliexpress.com",
        "method": "xpath",
        "get_link_btn": "//button[contains(@class, 'get-link-pro-button')]",
        "get_link": "//div[@class='next-loading-wrap'] //input",
    },
    "gumroad": {
        "type": "hub",
        "login": "https://gumroad.com/users/sign_in",
        "init": "https://gumroad.com/products/affiliated?affiliates=true",
        "method": "queryparam",
        "querykey": "a",
        "id_extraction": "//main/form/section[2] //p",
    },
}

COOKIE_KEYS = {
    "default": "at-main",
    "amazon": "session-id",
    "aliexpress": "uid",
    "gumroad": "_gumroad_guid",
}
