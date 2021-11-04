import pandas as pd
import time
import pickle
import os
import urllib

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re


class Browser:
    def __init__(self, username, password, query, n_pages):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        prefs = {
            "download_restrictions": 3,
        }
        chrome_options.add_experimental_option(
            "prefs", prefs
        )
        driver = webdriver.Chrome(r'C:\Users\kacpe\Downloads\chromedriver.exe', options=chrome_options)
        self.driver = driver
        self.username = username
        self.password = password
        self.query = query
        self.n_pages = n_pages
        self.login()

    def login(self):
        if os.path.isfile('cookies.pkl') is True:
            self.driver.get('https://www.linkedin.com')
            self.load_cookie()
            print("## Success!")

        else:
            print("## Catching cookies")
            self.driver.get("https://www.linkedin.com/login")
            self.driver.find_element_by_id('username').send_keys(self.username)
            self.driver.find_element_by_id('password').send_keys(self.password)
            self.driver.find_element_by_id('password').send_keys("\n")
            try:
                self.driver.find_elements_by_xpath("//*[contains(text(),'Skip']").click()
            except:
                pass
            self.save_cookies()
            print("## Success!")

    def load_cookie(self):
        print("## Loading cookie")
        with open("cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def save_cookies(self):
        print("## Saving cookies")
        time.sleep(10)
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

    def url_parse(self):
        url = "https://google.com/search?q="
        parse_query = urllib.parse.quote_plus(self.query)
        link = url + parse_query + "&start="
        return link

    def search_list(self):
        print(f"## Search query: {self.query}")
        links = []
        for page in range(1, self.n_pages):
            time.sleep(0.25)
            url = self.url_parse()
            self.driver.get(url + str(page))
            try:
                self.driver.find_element_by_xpath("//input[@type='submit']").click()
            except:
                pass

            time.sleep(2)
            search = self.driver.find_elements_by_xpath('//div[@class="yuRUbf"]//a[@href]')
            if len(search) <= 0:
                search = self.driver.find_elements_by_xpath('//div[@class="kCrYT"]//a[@href]')
            for h in search:
                href = h.get_attribute("href")
                if 'google' not in href:
                    links.append(href)
        return links

    def scroll_down(self):
        total_height = int(self.driver.execute_script("return document.body.scrollHeight"))

        for i in range(1, total_height, 5):
            self.driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(1)

    def talent_mapping(self):
        links = self.search_list()
        for link in links:
            self.driver.get(link)
            time.sleep(1)
            self.scroll_down()
            try:
                self.driver.execute_script("arguments[0].click();", WebDriverWait(
                    self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='pv-profile"
                                                                                 "-section__card-action-bar "
                                                                                 "pv-skills-section__additional-skills "
                                                                                 "artdeco-container-card-action-bar "
                                                                                 "artdeco-button "
                                                                                 "artdeco-button--tertiary "
                                                                                 "artdeco-button--3 "
                                                                                 "artdeco-button--fluid "
                                                                                 "artdeco-button--muted']"))))
            except selenium.common.exceptions.TimeoutException:
                print(f"Load more skills button not located")

            name = self.new_line_symbol_remover(self.driver.find_element_by_xpath(
                "//h1[@class='text-heading-xlarge inline t-24 v-align-middle break-words']").text)
            name = name.split()
            gender = ''
            if name[0].endswith('a') is True:
                gender += 'F'
            else:
                gender += 'M'

            localization = self.driver.find_element_by_xpath(
                "//span[@class='text-body-small inline t-black--light break-words']").text

            schools_name = self.driver.find_elements_by_xpath("//h3[@class='pv-entity__school-name t-16 t-black "
                                                              "t-bold']")
            graduation_titles = self.driver.find_elements_by_xpath("//p[@class='pv-entity__secondary-title "
                                                                   "pv-entity__degree-name t-14 t-black t-normal']")
            specialization_degrees = self.driver.find_elements_by_xpath("//p[@class='pv-entity__secondary-title "
                                                                        "pv-entity__fos t-14 t-black t-normal']")
            school_list = []
            for school_name, graduation_title, specialization_degree in zip(
                    schools_name, graduation_titles, specialization_degrees):
                graduation_title = self.school_text_formater(graduation_title.text)
                specialization_degree = self.school_text_formater(specialization_degree.text)
                info = [school_name.text, graduation_title, specialization_degree]
                school_list.append(info)
            print(school_list)

            job_titles = self.driver.find_elements_by_xpath("//h3[@class='t-16 t-black t-bold']")
            companies = self.driver.find_elements_by_xpath(
                "//p[@class='pv-entity__secondary-title t-14 t-black t-normal']")
            employment_periods = self.driver.find_elements_by_xpath("//h4[@class='t-14 t-black--light t-normal']")
            jobs_list = []
            for job_title, company, employment_period in zip(job_titles, companies, employment_periods):
                employment_period = self.employment_period_formater(employment_period.text)
                info = [job_title.text, company.text, employment_period]
                jobs_list.append(info)

            skills = self.driver.find_elements_by_xpath(
                "//p[@class='pv-skill-category-entity__name tooltip-container']")
            skills_list = []
            for skill in skills:
                skills_list.append(skill.text)

    def extract_text_from_profile_to_df(self, filename):
        links = self.search_list()
        print(f"## Extracting content form {len(links)} profiles")
        list_of_lists = []
        i = 1
        for link in links:
            list_of_page = []
            self.driver.get(link)
            print(f'## {i}/{len(links)}\n{link}')
            i += 1
            time.sleep(2)
            first_and_lastname = self.new_line_symbol_remover(self.driver.find_element_by_xpath(
                "//h1[@class='text-heading-xlarge inline t-24 v-align-middle break-words']").text)
            headline = self.driver.find_element_by_xpath(
                "//div[@class='text-body-medium break-words']").text
            localization = self.driver.find_element_by_xpath(
                "//span[@class='text-body-small inline t-black--light break-words']").text
            summary = self.new_line_symbol_remover(self.driver.find_element_by_xpath(
                "//section[@class='pv-profile-section pv-about-section artdeco-card p5 mt4 ember-view']").text)
            jobs = self.driver.find_elements_by_xpath(
                "//li[@class='pv-entity__position-group-pager pv-profile-section__list-item ember-view']")

            jobs_text = ''
            for job in jobs:
                jobs_text += job.text + ' '
            jobs_text = self.new_line_symbol_remover(jobs_text)

            schools = self.driver.find_elements_by_xpath("//li[@class='pv-profile-section__list"
                                                         "-item pv-education-entity "
                                                         "pv-profile-section__card-item "
                                                         "ember-view']")
            schools_text = ''
            for school in schools:
                schools_text += school.text + ' '
            schools_text = self.new_line_symbol_remover(schools_text)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            try:
                self.driver.find_element_by_xpath("//button[@class='pv-profile-section__card-action-bar "
                                                  "pv-skills-section__additional-skills "
                                                  "artdeco-container-card-action-bar artdeco-button "
                                                  "artdeco-button--tertiary artdeco-button--3 "
                                                  "artdeco-button--fluid artdeco-button--muted']").click()
            except:
                pass

            skills = self.driver.find_elements_by_xpath(
                "//p[@class='pv-skill-category-entity__name tooltip-container']")
            skills_text = ''
            for skill in skills:
                skills_text += skill.text + ' '
            skills_text = self.new_line_symbol_remover(skills_text)

            achievements = self.driver.find_elements_by_xpath("//li[@class='pv-accomplishments-block__summary-list"
                                                              "-item']")
            achievements_text = ''
            for achievement in achievements:
                achievements_text += achievement.text + ' '
            achievements_text = self.new_line_symbol_remover(achievements_text)
            profile_text = headline + ' ' + summary + ' ' + jobs_text + ' ' + schools_text + ' ' + skills_text + \
                           ' ' + achievements_text

            list_of_page.append(first_and_lastname)
            list_of_page.append(localization)
            list_of_page.append(profile_text)
            list_of_lists.append(list_of_page)

            time.sleep(1)
        df = pd.DataFrame(list_of_lists, columns=['first_and_lastname', 'localization', 'profile_text'])
        df.to_csv(filename, index=False, sep=';')
        print('## File was created')

    @staticmethod
    def new_line_symbol_remover(text):
        format_text = text.replace('\n', ' ')

        return format_text

    @staticmethod
    def employment_period_formater(text):
        pattern1 = re.compile(r'Czas zatrudnienia(?:[\n]+(\d+)[ ]*lata?)?(?:[ \\n]+(\d+)[ ]*mies\.)?')
        pattern2 = re.compile(r'Czas zatrudnienia(?:[\n]+(\d+)[ ]*rok?)?(?:[ \\n]+(\d+)[ ]*mies\.)?')
        if 'lata' in text:
            for x in pattern1.finditer(text):
                years, months = x.groups()
                if years or months:
                    total_months = int(years or 0) * 12 + int(months or 0)
                    return total_months
        else:
            for x in pattern2.finditer(text):
                years, months = x.groups()
                if years or months:
                    total_months = int(years or 0) * 12 + int(months or 0)
                    return total_months

    @staticmethod
    def school_text_formater(text):
        pattern1 = r'Tytuł/stopień wykształcenia'
        pattern2 = r'Kierunek studiów'
        if pattern1 in text:
            format_text = text.replace('\n', '')
            format_text = format_text.replace(pattern1, '')
        else:
            format_text = text.replace('\n', '')
            format_text = format_text.replace(pattern2, '')

        return format_text
