import os
from traceback import format_exc

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
    )

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
        login = False
        if not forceLogin:
            login = checkRedoLogin(merchant)
        if headless and login:
            headless = False

        driver = initSelenDriver(headless=headless)
        driver = prepDriver(driver, domain=merchant, forceLogin=forceLogin)
        if driver is not None:

            for bobj in data:
                boid = bobj["BOID"]
                url = bobj["url"]
                driver.get(url)
                naturalSleep(5)

                link = getTrackingLinks(driver, merchant)
                if link is not None:
                    result[boid] = link
                    print(boid, "===>", link)

            if len(result):
                writeLocalJsonFile(
                    result,
                    os.path.join(src_dir, output_dir, merchant, f"{flabel}.json"),
                    verbose=True,
                )
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
        "Which platform are we processing today? [1] - Amazon [2] - Aliexpress \n"
    )
    if target == "1":
        merch = "amazon"
    elif target == "2":
        merch = "aliexpress"
        c = (
            input(
                f"Aliexpress is strict about the use of automated scripts. You will need to log in yourself every time. Continue? (y/n) \n"
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
                print(e)
