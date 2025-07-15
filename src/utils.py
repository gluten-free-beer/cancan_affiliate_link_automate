from selenium.webdriver.chrome.webdriver import WebDriver
import os

src_dir = os.path.join(os.getcwd(), "src")
browser = os.getenv("BROWSER_TYPE")

def getTimestamp():
    from time import time
    import math

    return math.floor(time())


def rmtree(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        try:
            for file in files:
                os.remove(os.path.join(root, file))
            for _dir in dirs:
                os.rmdir(os.path.join(root, _dir))
        except Exception as e:
            print(e)
    os.rmdir(directory)


def removeDirectory(dir_path):
    if os.path.isdir(dir_path):
        rmtree(dir_path)


def naturalSleep(seconds=1, mintime=1):
    from time import sleep
    from random import randint

    r = randint(-200, 200) / 100
    sleeptime = round(max(mintime, seconds + r), 1)

    sleep(sleeptime)


def initSelenDriver(headless=True, windowSize=(1820, 960), type=browser):
    from selenium import webdriver
    import undetected_chromedriver as uc
    import traceback

    driver = None
    options = None

    if type == "chrome":
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        driver = uc.Chrome(options=options)
    
        return driver
        
    if type == "firefox":
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0"
        from webdriver_manager.firefox import GeckoDriverManager
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service

        options = FirefoxOptions()
        options.add_argument(f"user-agent={user_agent}")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        if type == "firefox":
            driver = webdriver.Firefox(
                service=Service(GeckoDriverManager().install()), options=options
            )

        driver.set_window_size(windowSize[0], windowSize[1])

    except Exception as e:
        print("init selen error:", e, traceback.format_exc())
    finally:
        return driver


def closeSelenDriver(driver, action="quit"):
    if driver is not None:
        if action == "quit":
            driver.quit()
        elif action == "close":
            driver.close()


def saveCookieSelenium(driver, dpath, filename="default.cookies"):
    import json
    import os

    if not os.path.isdir(dpath):
        os.makedirs(dpath)
    with open(os.path.join(dpath, filename), "w") as filehandler:
        print("saving cookies")
        json.dump(driver.get_cookies(), filehandler)
    return driver


def loadCookieSelenium(driver, dpath, filename="default.cookies"):
    import json
    import os

    driver.delete_all_cookies()
    cookie_path = os.path.join(dpath, filename)
    try:
        with open(cookie_path, "r") as cookiesfile:
            cookies = json.load(cookiesfile)
            if cookies:
                print("adding cookies")
                for cookie in cookies:
                    driver.add_cookie(cookie)
        return driver
    except Exception as e:
        print(f"cannot load cookies: {e} --- {cookie_path}")
    return None


def scrollByAmount(driver, amount=1, direction="Y"):
    from selenium.webdriver import ActionChains

    wsize = driver.get_window_size()
    wheight = wsize["height"]
    ActionChains(driver).scroll_by_amount(0, int(wheight * amount)).perform()


def checkRedoLogin(domain):
    import json
    from params import COOKIE_KEYS

    ts = getTimestamp()
    redo = True
    cookie_path = os.path.join(
        src_dir, "misc", f"cookies/chrome/{domain}", "default.cookies"
    )
    keys = COOKIE_KEYS.copy()
    key = keys["default"]
    if domain in keys:
        key = keys[domain]

    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, "r") as cookiesfile:
                cookies = json.load(cookiesfile)
                if cookies:
                    for cookie in cookies:
                        if cookie["name"] == key:
                            if cookie["expiry"] < ts:
                                print("expired cookies ---> need to log in again")
                            else:
                                redo = False
                                break
        except Exception as e:
            print(f"cannot load cookies: {e} --- {cookie_path}")
    print("redo cookies?", redo)
    return redo


def prepDriver(driver, domain, browser=browser, forceLogin=False, headless=True) -> WebDriver:
    from time import sleep
    from selenium.common.exceptions import WebDriverException
    import os
    from params import DOMAIN_PAGE

    ndriver = None
    try:
        if driver is None:
            initSelenDriver(headless=headless, type=browser)
        init_page = DOMAIN_PAGE[domain]["init"]
        driver.get(init_page)
        sleep(3)

        cookiePath = os.path.join(src_dir, "misc", f"cookies/{browser}/{domain}")
        redo = True

        if not forceLogin and os.path.exists(cookiePath):
            ndriver = loadCookieSelenium(driver=driver, dpath=cookiePath)
            sleep(3)
            scrollByAmount(driver, 0.6)
            if ndriver is not None:
                redo = False
                ndriver.get(init_page)
                sleep(2)
        if redo:
            print("Please sign in.")
            login_page = DOMAIN_PAGE[domain]["login"]
            driver.get(login_page)
            tries = 0
            while tries < 5:
                sleep(15)
                ndriver = saveCookieSelenium(driver=driver, dpath=cookiePath)
                if not checkRedoLogin(domain=domain):
                    ndriver.get(init_page)
                    sleep(5)
                    break
                tries += 1

    except WebDriverException as e:
        print(e)

    return ndriver


def getCurrentUrl(driver):
    return driver.execute_script("return document.location.href;")


def selenClickSimple(driver, clickable):
    from selenium.webdriver import ActionChains

    ActionChains(driver).click(clickable).perform()


def waitTillElemLocated(driver, value, attr="id", waitsec=10):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        if attr == "id":
            element = WebDriverWait(driver, waitsec).until(
                EC.presence_of_element_located((By.ID, value))
            )
        elif attr == "xpath":
            element = WebDriverWait(driver, waitsec).until(
                EC.presence_of_element_located((By.XPATH, value))
            )
        elif attr == "class":
            element = WebDriverWait(driver, waitsec).until(
                EC.presence_of_element_located((By.CLASS_NAME, value))
            )
    except Exception as e:
        print(e)


def findElSelenium(
    driver, value, attribute="id", multiple=False, sequence=0, wait=False
):
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException

    try:
        if wait:
            waitTillElemLocated(driver=driver, value=value, attr=attribute)

        if attribute == "id":
            return driver.find_element(By.ID, value)
        elif attribute == "class":
            if multiple or sequence:
                els = driver.find_elements(By.CLASS_NAME, value)
                if sequence:
                    if len(els) and len(els) >= sequence:
                        return els[sequence - 1]
                    return None
                return els
            return driver.find_element(By.CLASS_NAME, value)
        elif attribute == "linktext":
            if multiple:
                return driver.find_elements(By.LINK_TEXT, value)
            return driver.find_element(By.LINK_TEXT, value)
        elif attribute == "partlt":
            if multiple:
                return driver.find_elements(By.PARTIAL_LINK_TEXT, value)
            return driver.find_element(By.PARTIAL_LINK_TEXT, value)
        elif attribute == "tagname":
            if multiple:
                return driver.find_elements(By.TAG_NAME, value)
            return driver.find_element(By.TAG_NAME, value)
        elif attribute == "xpath":
            if multiple:
                return driver.find_elements(By.XPATH, value)
            return driver.find_element(By.XPATH, value)
    except NoSuchElementException:
        pass
    except Exception as e:
        print(e)
    return None


def readCsvFile(file_path):
    if os.path.exists(file_path):
        results = []
        with open(file_path, mode="r") as infile:
            import csv

            reader = csv.DictReader(infile)
            for row in reader:
                results.append(row)
        return results
    return None


def loadLocalJsonFile(filepath):
    import json

    data = None
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                f.close()
            except Exception as e:
                print(e, filepath)
    return data


def writeLocalJsonFile(content, filepath, verbose=False):
    import json

    if content is None:
        print("input is null")
        return
    dirpath = os.path.dirname(filepath)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    with open(filepath, "w+", encoding="utf-8") as f:
        if content is not None and len(content):
            json.dump(content, f, ensure_ascii=False)
        f.close()
        if verbose:
            print("file written to:", filepath)


def getTrackingLinks(driver, merchant):
    from params import DOMAIN_PAGE

    if merchant in DOMAIN_PAGE:
        attr = DOMAIN_PAGE[merchant]["method"]
        naturalSleep(4)
        b = findElSelenium(
            driver, DOMAIN_PAGE[merchant]["get_link_btn"], attribute=attr, wait=True
        )
        if b is not None:
            selenClickSimple(driver=driver, clickable=b)

            textarea = findElSelenium(
                driver, DOMAIN_PAGE[merchant]["get_link"], wait=True, attribute=attr
            )
            if textarea is not None:
                text_value = textarea.get_attribute("value")
                return text_value
    return None
