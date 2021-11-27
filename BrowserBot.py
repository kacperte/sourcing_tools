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
    """
    This class represent bot to move on LinkedIn platform and scrap information from profile
    """
    def __init__(self, username, password, query, n_pages):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
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
        driver = webdriver.Chrome(r'C:\Users\kacpe\OneDrive\Pulpit\Python\Projekty\chromedriver.exe', options=chrome_options)
        self.driver = driver
        self.username = username
        self.password = password
        self.query = query
        self.n_pages = n_pages
        self.login()

    def login(self):
        """
        Function to log into LinkedIn account
        :return: None
        """
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
        """
        Function that load web cookies from pickle format
        :return: None
        """
        print("## Loading cookie")
        with open("cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def save_cookies(self):
        """
        Function to save web cookies in pickle format
        :return:None
        """
        print("## Saving cookies")
        time.sleep(10)
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

    def url_parse(self):
        """
        Function that parse core link, string and number of page
        :return: string
        """
        url = "https://google.com/search?q="
        parse_query = urllib.parse.quote_plus(self.query)
        link = url + parse_query + "&start="
        return link

    def search_list(self):
        """
        Function that scrape every LinkedIn profile link in search result
        :return: Lists of links
        """
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
        """
        Function that scroll page to the bottom
        :return: None
        """
        total_height = int(self.driver.execute_script("return document.body.scrollHeight"))

        for i in range(1, total_height, 5):
            self.driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(1)

    def loading_all_elements(self):
        """
        Function that click every show_more button on LinkedIn page
        :return: None
        """
        containers = self.driver.find_elements_by_xpath("//li-icon[@class='pv-profile-section__toggle-detail-icon']")
        for button in containers:
            try:
                self.driver.execute_script('arguments[0].click()', button)
            except:
                pass
            try:
                button.click()
            except:
                pass


        # Load more skills
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
        except:
            pass
        self.scroll_down()

    def talent_mapping(self):
        links = self.search_list()
        list_of_lists = []
        n_links = len(links)
        print(f'## Profiles to scrap: {n_links}')
        for i, link in enumerate(links):
            print(f'## Proccessing {i+1}/{n_links}\n## Link: {link}')
            list_of_page = []
            self.driver.get(link)
            time.sleep(1)
            self.scroll_down()
            self.loading_all_elements()

            # Accomplishments
            accomplishments_list = []
            try:
                accomplishments = self.driver.find_elements_by_xpath(
                    "//li[""@class='pv-accomplishments-block__summary-list-item']")
                for i in accomplishments:
                    accomplishments_list.append(i.text)
            except selenium.common.exceptions.NoSuchElementException:
                pass

            # Licences and certifications
            licences_and_certifications_list = []
            try:
                licences_and_certifications = self.driver.find_elements_by_xpath("//li[""@class='pv"
                                                                                 "-profile"
                                                                                 "-section__sortable"
                                                                                 "-item "
                                                                                 "pv-certification"
                                                                                 "-entity "
                                                                                 "ember-view']")
                cer = licences_and_certifications[0].find_elements_by_xpath("//h3[@class='t-16 t-bold']")
                for _ in cer:
                    licences_and_certifications_list.append(_.text)
            except selenium.common.exceptions.NoSuchElementException:
                pass
            except IndexError:
                pass

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

            headline = self.driver.find_element_by_xpath(
                "//div[@class='text-body-medium break-words']").text

            summary = self.new_line_symbol_remover(self.driver.find_element_by_xpath(
                "//section[@class='pv-profile-section pv-about-section artdeco-card p5 mt4 ember-view']").text)

            # Education
            schools = self.driver.find_elements_by_xpath("//li[@class='pv-profile-section__list-item "
                                                         "pv-education-entity pv-profile-section__card-item "
                                                         "ember-view']")
            schools_info = []
            for info in schools:
                schools_info.append(self.new_line_symbol_remover(info.text))

            # Work experience
            jobs = self.driver.find_elements_by_xpath("//li[@class='pv-entity__position-group-pager "
                                                                 "pv-profile-section__list-item ember-view']")
            jobs_info = []
            for info in jobs:
                jobs_info.append(self.new_line_symbol_remover(info.text))

            # Skills
            skills = self.driver.find_elements_by_xpath(
                "//p[@class='pv-skill-category-entity__name tooltip-container']")
            skills_list = []
            for skill in skills:
                skills_list.append(skill.text)

            profile_text = ' '.join(str(elem) for elem in jobs_info) + \
                           ' '.join(str(elem) for elem in schools_info) + \
                           ' '.join(str(elem) for elem in skills_list) + \
                           ' '.join(str(elem) for elem in accomplishments_list) + \
                           ' '.join(str(elem) for elem in licences_and_certifications_list)

            final_text = profile_text.replace('.', ' ').\
                replace(',', ' ').\
                replace('•', ' ').\
                replace(':', ' ').\
                replace('-', ' ').\
                replace('…', ' ').\
                replace('(', ' ').\
                replace(')', ' ').\
                replace('–', ' ').\
                replace('/', ' ').\
                replace('?', ' ').\
                replace('+', ' ').\
                replace('☑', ' ').\
                replace('[', ' ').\
                replace(']', ' ')

            # Adding values to the list of page than adding to the list of list
            list_of_page.append(name[0])
            list_of_page.append(name[1])
            list_of_page.append(gender)
            list_of_page.append(localization)
            list_of_page.append(final_text)
            list_of_lists.append(list_of_page)

        df = pd.DataFrame(list_of_lists, columns=['firstname', 'lastname', 'gender', 'localization', 'profile_text'])
        df.to_csv('1.csv', index=False, sep=';', encoding='utf-8-sig')

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
