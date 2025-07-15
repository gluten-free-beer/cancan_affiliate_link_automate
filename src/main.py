import os
from traceback import format_exc
import re
from dotenv import load_dotenv

load_dotenv()  # take environment variables

input_dir = os.getenv("INPUT_DIR")
output_dir = os.getenv("OUTPUT_DIR")

src_dir = os.path.join(os.getcwd(), "src")


def batchOp(merchant, filename, headless=True, forceLogin=False):
    from utils import (
        initSelenDriver,
        prepDriver,
        checkRedoLogin,
        readCsvFile,
        loadLocalJsonFile,
        writeLocalJsonFile,
        getTrackingLinks,
        naturalSleep,
        findElSelenium,
        closeSelenDriver,
    )
    from params import DOMAIN_PAGE

    flabel, ext = filename.split(".")

    data = []
    if ext == "csv":
        data = readCsvFile(os.path.join(src_dir, input_dir, filename))
    else:
        obj = loadLocalJsonFile(os.path.join(src_dir, input_dir, filename))
        if obj is not None:
            data = obj["data"]
    result = {}
    if os.path.exists(os.path.join(src_dir, output_dir, merchant, f"{flabel}.json")):
        result = loadLocalJsonFile(
            os.path.join(src_dir, output_dir, merchant, f"{flabel}.json")
        )

    data = [x for x in data if x["provider"] == merchant and x["BOID"] not in result]
    if len(data):
        driver = None
        dobj = DOMAIN_PAGE[merchant]
        userid = None
        login = False
        if not forceLogin:
            login = checkRedoLogin(merchant)
        if headless and login:
            headless = False
        if dobj["type"] == "hub":
            if merchant == "gumroad":
                tempid = os.getenv("GUMROAD_ID")
                if len(tempid):
                    userid = tempid
            if userid is None:
                driver = initSelenDriver(headless=headless)
                if driver is None:
                    raise Exception("driver is bad")

                driver = prepDriver(
                    driver, domain=merchant, forceLogin=forceLogin, headless=headless
                )
                managepage = dobj["init"]
                driver.get(managepage)
                naturalSleep(5)
                pel = findElSelenium(driver, dobj["id_extraction"], "xpath")
                if pel is not None:
                    ptext = pel.text
                    q = dobj["querykey"]
                    u = re.search(rf"\?{q}=(\d+)", ptext)
                    if u is not None:
                        userid = u.group(1)
                        print(
                            "your Gumroad user id is {} ==> you may add it to the env file.".format(
                                userid
                            )
                        )
            if userid is None:
                raise Exception("cannot get {} user id".format(merchant))
        else:
            driver = initSelenDriver(headless=headless)

            if driver is None:
                raise Exception("driver is bad")
            driver = prepDriver(
                driver, domain=merchant, forceLogin=forceLogin, headless=headless
            )
        for bobj in data:
            boid = bobj["BOID"]
            url = bobj["url"]
            link = None
            if dobj["type"] == "single":
                driver.get(url)
                naturalSleep(5)
                link = getTrackingLinks(driver, merchant)
            elif dobj["type"] == "hub" and dobj["method"] == "queryparam":
                q = dobj["querykey"]
                link = f"{url}?{q}={userid}"
            if link is not None:
                result[boid] = link
                print(boid, "===>", link)

        if len(result):
            writeLocalJsonFile(
                result,
                os.path.join(src_dir, output_dir, merchant, f"{flabel}.json"),
                verbose=True,
            )
        closeSelenDriver(driver=driver)
    else:
        print("nothing to process here")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", help="headless?", default=1, type=int)
    parser.add_argument("--reset", help="reset?", default=0, type=int)
    args = parser.parse_args()

    from utils import removeDirectory

    merch = None
    filename = None
    force_login = False
    headless = args.headless
    print(
        "This program helps marketers automate the workflow to generate affiliate links. You will need to log in for the first time or when the cookies expire. Please refrain from using this software to abuse or game any system."
    )

    target = input(
        "Which platform are we processing today? [1] Amazon [2] Aliexpress [3] Gumroad \n"
    )
    if target == "1":
        merch = "amazon"
    elif target == "3":
        merch = "gumroad"
        print(
            "for gumroad products, you only need to attach a pair of query parameter ?a=<USERID>. you can manually set your userid in the .env file."
        )
    elif target == "2":
        merch = "aliexpress"
        c = (
            input(
                f"Aliexpress is strict about the use of automated scripts. You will need to log in, even with cookies. Continue? (y/n) \n"
            )
            .strip()
            .lower()
        )
        if c == "no":
            print("Exiting program.")
            sys.exit(0)
        force_login = True
        headless = False

    if merch is not None:
        print(f"Make sure you have placed the CANDY file in /{input_dir}/.")
        fileopt = (
            input("Which file are we using? Default: candy.json \n") or "candy.json"
        )
        filepath = os.path.join(src_dir, input_dir, fileopt)
        if os.path.exists(filepath):
            filename = fileopt
        else:
            print("the file does not exist:", filepath)

        if filename is not None:
            try:
                if args.reset:
                    removeDirectory(os.path.join(src_dir, output_dir, merch))
                batchOp(
                    merchant=merch,
                    filename=filename,
                    headless=headless,
                    forceLogin=force_login,
                )
            except Exception as e:
                print(e, format_exc())
