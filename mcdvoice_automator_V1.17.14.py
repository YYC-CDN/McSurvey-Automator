# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 22:17:28 2025

@author: MrBungle
"""

"""
McDVoice Survey Automator 2025 - fresh browser for each code, closed after survey complete
Version 1.17.13 (Cleaned, removed logging/csv, fixed Service import)
@author: MrBungle
"""

import sys
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import tkinter as tk
from tkinter import filedialog

MAX_SURVEYS_PER_MONTH = 5
SHORT_WAIT_TIME = 5  # seconds for waits

positive_comments = [
    "Lucy, Logan, and Lena always brighten my day with their cheerful greetings and friendly smiles. They should be charging for sunshine at this point!",
    "The excellent service from Lucy, Logan, and Lena makes every visit feel special and appreciated. Honestly, I feel like a VIP every time!",
    "Lucy, Logan, and Lena's warm and welcoming attitude create such a happy atmosphere in the restaurant. It's like being hugged by a whole team of happy, talented people!",
    "I appreciate how Lucy, Logan, and Lena go above and beyond to make sure every customer feels valued. If there were a customer service Olympics, they'd take home the gold every time.",
    "Lucy, Logan, and Lena’s professionalism and kindness shine through in every interaction. They're basically the Avengers of customer service!",
    "Their friendly nature and helpfulness make Lucy, Logan, and Lena stand out as exceptional employees. Forget ‘best in the business’, they’re in a league of their own!",
    "Every time Lucy, Logan, and Lena assist me, I feel like I’m in great hands. I trust them more than I trust my phone's autocorrect.",
    "The energy and dedication Lucy, Logan, and Lena bring to their work is truly inspiring. I’m convinced they secretly have superpowers… or at least a very strong coffee supply.",
    "Lucy, Logan, and Lena consistently provide fast and accurate service with a smile. It’s like magic, but without the wands and capes... well, maybe they have capes.",
    "Thanks to Lucy, Logan, and Lena, ordering at McDonald's is always a positive and smooth experience. They make fast food feel like fine dining.",
    "Lucy, Logan, and Lena’s attention to detail guarantees that every order is perfect. I think they secretly have a crystal ball and can see what I want before I even order.",
    "The enthusiasm Lucy, Logan, and Lena show while working is contagious and uplifting. I leave with a smile, and sometimes I even end up skipping the line just to see them again!",
    "It’s a joy to be served by Lucy, Logan, and Lena who truly care about customer satisfaction. They make you feel like you're not just a customer, but an honored guest... maybe even royalty.",
    "Lucy, Logan, and Lena’s cheerful greetings make me want to come back again and again. If happiness were a currency, they’d be billionaires by now.",
    "The teamwork between Lucy, Logan, and Lena ensures that everything runs flawlessly. They make synchronized swimming look easy, but in a fast food restaurant!",
    "Lucy, Logan, and Lena handle busy times with grace and efficiency. They should be hired as consultants for every busy airport lounge in the world.",
    "Their consistent positive attitude brightens the restaurant environment for everyone. Honestly, I’ve had bad days, but a visit with them is like instant therapy.",
    "Lucy, Logan, and Lena make every customer feel like a valued guest rather than just a number. If I could, I’d give them all a trophy for ‘Best Customer Service’ every time.",
    "The respect Lucy, Logan, and Lena show to customers and colleagues is admirable. They treat everyone like family — the fun, supportive kind of family.",
    "Lucy, Logan, and Lena always take the time to answer questions and make recommendations. I’m convinced they have a PhD in McDonald's menu suggestions.",
    "Their patience and kindness during busy hours are remarkable. I honestly think they’ve figured out how to slow down time during rush hour.",
    "Lucy, Logan, and Lena manage the drive-thru and counter with speed and smiles. If I ever need to speed up my own life, I’ll be asking them for tips.",
    "I am impressed by how well Lucy, Logan, and Lena remember orders and names. It’s like they have a photographic memory... or possibly mind-reading abilities.",
    "Every visit feels like a personal experience thanks to Lucy, Logan, and Lena. I almost feel like I’m the star of a reality show every time I step up to the counter.",
    "Lucy, Logan, and Lena’s service sets a high standard for others to follow. If there were a customer service 'Hall of Fame', they’d all have their plaques.",
    "Because of Lucy, Logan, and Lena, the atmosphere feels welcoming and friendly at all times. Seriously, I wouldn’t be surprised if they had a secret handshake.",
    "Lucy, Logan, and Lena’s positive energy makes McDonald's my favorite fast food choice. I’m pretty sure they’re secretly part-time motivational speakers too.",
    "Their natural hospitality and care improve each dining experience. If there were an award for ‘Best McDonald’s Crew’, they’d win it every time, hands down.",
    "Lucy, Logan, and Lena show pride in their work and it truly shows in service quality. They're not just employees; they're like the McDonald's dream team.",
    "Thanks to Lucy, Logan, and Lena, McDonald's service feels fast, friendly, and flawless. If McDonald's was a sports team, they'd be the MVPs, no question."
]
 

ORDER_METHOD = "R000455.2"
VISIT_TYPE_DINE_IN = "R004000.1"
VISIT_TYPE_CARRY_OUT = "R004000.3"
REWARDS = "R000444.2"
PROBLEM = "R010000.2"
FAVORITE = "R002000.1"
BRAND_TRUST = "R003000.1"
DEMOGRAPHIC_IDS = [
    "R012000.6",
    "R013000.8",
    "R014000.7",
]

def human_delay(min_sec=1, max_sec=3):
    delay = random.uniform(min_sec, max_sec)
    print(f"Sleeping for {delay:.2f} seconds")
    time.sleep(delay)

def robust_select_radio(driver, radio, max_retries=10):
    radio_id = radio.get_attribute("id")
    for attempt in range(max_retries):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", radio)
            if radio.is_selected():
                return True
            ActionChains(driver).move_to_element(radio).pause(2).click().perform()
            time.sleep(2)
            radio = driver.find_element(By.ID, radio_id)
            if radio.is_selected():
                return True
            time.sleep(2)
        except (StaleElementReferenceException, TimeoutException):
            time.sleep(2)
    return False

def robust_select_radio_by_id(driver, radio_id):
    try:
        radio = driver.find_element(By.ID, radio_id)
        return robust_select_radio(driver, radio)
    except Exception:
        return False

def select_no_on_my_rewards(driver):
    try:
        wait = WebDriverWait(driver, SHORT_WAIT_TIME)
        no_radio = wait.until(EC.element_to_be_clickable((By.ID, REWARDS)))
        if not no_radio.is_selected():
            no_radio.click()
            time.sleep(2)
            if no_radio.is_selected():
                return True
        return no_radio.is_selected()
    except TimeoutException:
        return False

def select_breakfast_checkbox(driver):
    try:
        wait = WebDriverWait(driver, SHORT_WAIT_TIME)
        cb = wait.until(EC.element_to_be_clickable((By.ID, "R000504")))
        if not cb.is_selected():
            cb.click()
            time.sleep(2)
        return True
    except TimeoutException:
        return False

def select_mcdonalds_brand(driver):
    try:
        labels = driver.find_elements(By.TAG_NAME, "label")
        for label in labels:
            if "mcdonald" in label.text.lower():
                rid = label.get_attribute("for")
                if rid:
                    radio = driver.find_element(By.ID, rid)
                    if not radio.is_selected():
                        radio.click()
                    return True
        return False
    except:
        return False

def universal_satisfaction_selector(driver):
    rows = driver.find_elements(By.CSS_SELECTOR, "tr[role=radio], tr[id^=FNSR]")
    count = 0
    for row in rows:
        try:
            radio = row.find_element(By.CSS_SELECTOR, "input[type=radio][value=5]")
            if robust_select_radio(driver, radio):
                count += 1
        except:
            continue
    return count

def wait_for_all_radios(driver):
    wait = WebDriverWait(driver, SHORT_WAIT_TIME)
    radio_ids = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tr[role=radio], tr[id^=FNSR]")
    for row in rows:
        try:
            radio = row.find_element(By.CSS_SELECTOR, "input[type=radio][value=5]")
            radio_ids.append(radio.get_attribute("id"))
        except Exception:
            continue

    def all_selected(drv):
        for rid in radio_ids:
            try:
                r = drv.find_element(By.ID, rid)
                if not r.is_selected():
                    return False
            except Exception:
                return False
        return True

    wait.until(all_selected)

def wait_for_page_change(driver, old_html):
    wait = WebDriverWait(driver, SHORT_WAIT_TIME)
    try:
        wait.until(lambda d: d.execute_script("return document.documentElement.outerHTML") != old_html)
    except TimeoutException:
        pass

def prompt_file():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title="Select the text file with survey codes", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    root.destroy()
    return path

def complete_survey(validation_code):
    # Change console window title on Windows
    os.system("title MCDVoice Automator")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

# The following arguments will reduce browser logging
    options.add_argument("--log-level=3")  # Only fatal errors
    options.add_argument("--disable-logging")
    options.add_argument("--disable-notifications")  # Blocks notification prompts
    options.add_experimental_option("excludeSwitches", ["enable-logging"])


    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, SHORT_WAIT_TIME)

    try:
        driver.get("https://www.mcdvoice.com/")
        driver.execute_script("document.title = 'MCDV SECURE APPLICATION';")

        cn_fields = [wait.until(EC.presence_of_element_located((By.ID, f"CN{i}"))) for i in range(1, 7)]
        for seg, elem in zip(validation_code.split("-"), cn_fields):
            elem.send_keys(seg)
            time.sleep(random.uniform(1, 3))

        old_html = driver.page_source
        driver.find_element(By.ID, "NextButton").click()
        wait_for_page_change(driver, old_html)

        robust_select_radio_by_id(driver, ORDER_METHOD)

        old_html = driver.page_source
        driver.find_element(By.ID, "NextButton").click()
        wait_for_page_change(driver, old_html)

        choice = random.choice([VISIT_TYPE_DINE_IN, VISIT_TYPE_CARRY_OUT])
        robust_select_radio_by_id(driver, choice)

        old_html = driver.page_source
        driver.find_element(By.ID, "NextButton").click()
        wait_for_page_change(driver, old_html)

        robust_select_radio_by_id(driver, REWARDS)

        old_html = driver.page_source
        driver.find_element(By.ID, "NextButton").click()
        wait_for_page_change(driver, old_html)

        select_no_on_my_rewards(driver)
        select_breakfast_checkbox(driver)
        select_mcdonalds_brand(driver)

        while True:
            time.sleep(2)
            wait_for_all_radios(driver)
            universal_satisfaction_selector(driver)

            for qid in [PROBLEM, FAVORITE, BRAND_TRUST] + DEMOGRAPHIC_IDS:
                try:
                    robust_select_radio_by_id(driver, qid)
                except Exception:
                    pass

            try:
                textarea = driver.find_element(By.TAG_NAME, "textarea")
                textarea.clear()
                textarea.send_keys(random.choice(positive_comments))
                time.sleep(random.uniform(2, 4))
            except Exception:
                pass

            try:
                old_html = driver.page_source
                next_btn = wait.until(EC.element_to_be_clickable((By.ID, "NextButton")))
                time.sleep(2)
                ActionChains(driver).move_to_element(next_btn).pause(2).click().perform()
                wait_for_page_change(driver, old_html)
            except Exception:
                break

    finally:
        driver.quit()

def print_large_m():
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    logo = r"""
 _


 __  __     ___     __    _               _                                
|  \/  | __| \ \   / /__ (_) ___ ___     / \   _ __  _____      _____ _ __ 
| |\/| |/ _` |\ \ / / _ \| |/ __/ _ \   / _ \ | '_ \/ __\ \ /\ / / _ \ '__|
| |  | | (_| | \ V / (_) | | (_|  __/  / ___ \| | | \__ \\ V  V /  __/ |   
|_|__|_|\__,_|  \_/ \___/|_|\___\___| /_/   \_\_| |_|___/ \_/\_/ \___|_|   
 / ___| ___ _ __   ___ _ __ __ _| |_ ___  _ __                             
| |  _ / _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|                            
| |_| |  __/ | | |  __/ | | (_| | || (_) | |                               
 \____|\___|_| |_|\___|_|  \__,_|\__\___/|_|                               

  V1.17.14
  10/02/25
  Puno jebe ovu trenutnu administraciju.
  

"""
    print(f"{YELLOW}{logo}{RESET}")

def main_cli():
    print_large_m()
    print("You are about to run software designed to automate McDVoice.com")
    print("This scrip takes FOREVER to run 5 surveys. But it works")
    if len(sys.argv) < 2:
        print("Find your Survey Codes text file...")
        file_path = prompt_file()
        if not file_path:
            print("No file selected. Exiting.")
            sys.exit()
        with open(file_path, "r", encoding="utf-8") as file:
            codes = [line.strip() for line in file if line.strip()]
        codes = codes[:MAX_SURVEYS_PER_MONTH]
        for i, code in enumerate(codes):
            print(f"Starting survey {i + 1} of {len(codes)} with code {code}")
            complete_survey(code)
        print("\nDone with all surveys. Please switch IP if running more.")
    else:
        code = sys.argv[1]
        complete_survey(code)

if __name__ == "__main__":
    main_cli()
