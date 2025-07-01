import os

def batchOp(merchant, filename, headless=True):
    from utils import (
        initSelenDriver,
        prepDriver,
        checkRedoLogin,
        readCsvFile,
        loadLocalJsonFile,
        writeLocalJsonFile,
        getAmazonSs,
    )

    login = checkRedoLogin(merchant)
    if headless and login:
        headless = False
    flabel, ext = filename.split(".")
    driver = initSelenDriver(headless=headless)
    driver = prepDriver(driver, domain=merchant)
    if driver is not None:
        data = []
        if ext == "csv":
            data = readCsvFile(
                os.path.join(os.getcwd(), "resources", merchant, filename)
            )
        else:
            obj = loadLocalJsonFile(
                os.path.join(os.getcwd(), "resources", merchant, filename)
            )
            if obj is not None:
                data = obj["data"]
        data = [x for x in data if x["provider"] == merchant]
        result = {}
        if os.path.exists(os.path.join("output", merchant, f"{flabel}.json")):
            result = loadLocalJsonFile(
                os.path.join("output", merchant, f"{flabel}.json")
            )
        for bobj in data:
            boid = bobj["BOID"]
            if boid not in result:
                url = bobj["url"]
                driver.get(url)
                if merchant == "amazon":
                    link = getAmazonSs(driver)
                    if link is not None:
                        result[boid] = link
                        print(boid, "===>", link)

        if len(result):
            writeLocalJsonFile(
                result,
                os.path.join("output", merchant, f"{flabel}.json"),
                verbose=True,
            )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", help="headless?", default=1, type=int)
    parser.add_argument("--reset", help="reset?", default=0, type=int)
    args = parser.parse_args()

    from utils import removeDirectory

    merch = None
    filename = None

    print(
        "This program helps marketers automate the workflow to generate affiliate links. You will need to log in for the first time or when the cookies expire. Please refrain from using this software to abuse or game any system."
    )

    target = input("Which platform are we processing today? [1] - Amazon \n")
    if target == "1":
        merch = "amazon"
        print(f"Make sure you have placed the CANDY file in /resources/{merch}/.")
        fileopt = input("Which file are we using? Default: candy.json \n") or "candy.json"
        filepath = os.path.join(os.getcwd(), "resources", merch, fileopt)
        if os.path.exists(filepath):
            filename = fileopt
        else:
            print("the file does not exist:", filepath)

    if merch is not None and filename is not None:
        try:
            if args.reset:
                removeDirectory(os.path.join("output", merch))
            batchOp(merchant="amazon", filename=filename, headless=args.headless)
        except Exception as e:
            print(e)
