DOMAIN_PAGE = {
    "amazon": {
        "login": "https://www.amazon.com/sign-in",
        "init": "https://www.amazon.com",
        "method": "id",
        "get_link_btn": "amzn-ss-get-link-button",
        "get_link": "amzn-ss-text-shortlink-textarea",
    },
    "aliexpress": {
        "login": "https://login.aliexpress.com",
        "init": "https://www.aliexpress.com",
        "method": "xpath",
        "get_link_btn": "//button[contains(@class, 'get-link-pro-button')]",
        "get_link": "//div[@class='next-loading-wrap'] //input",
    }
}
