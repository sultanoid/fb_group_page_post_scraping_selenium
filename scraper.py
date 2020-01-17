import traceback
import getpass
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import argparse
import csv
import calendar
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
parser = argparse.ArgumentParser(description='Non API public FB miner')

parser.add_argument('-p', '--pages', nargs='+',
                    dest="pages",
                    help="List the pages you want to scrape for recent posts")

parser.add_argument("-g", '--groups', nargs='+',
                    dest="groups",
                    help="List the groups you want to scrape for recent posts")

parser.add_argument("-d", "--depth", action="store",
                    dest="depth", default=5, type=int,
                    help="How many recent posts you want to gather -- in multiples of (roughly) 8.")

args = parser.parse_args()

BROWSER_EXE = '/usr/bin/firefox'
GECKODRIVER = dir_path +'/geckodriver'

FIREFOX_BINARY = FirefoxBinary(BROWSER_EXE)

#  Code to disable notifications pop up of Chrome Browser

PROFILE = webdriver.FirefoxProfile()
# PROFILE.DEFAULT_PREFERENCES['frozen']['javascript.enabled'] = False
PROFILE.set_preference("dom.webnotifications.enabled", False)
PROFILE.set_preference("app.update.enabled", False)
PROFILE.update_preferences()


class CollectPosts(object):
    """Collector of recent FaceBook posts.
           Note: We bypass the FaceBook-Graph-API by using a
           selenium FireFox instance!
           This is against the FB guide lines and thus not allowed.
           USE THIS FOR EDUCATIONAL PURPOSES ONLY. DO NOT ACTAULLY RUN IT.
    """

    def __init__(self, ids=["oxfess"], corpus_file=["oxfess"], depth=5, delay=2):
        self.ids = ids
        self.dump = corpus_file
        self.depth = depth + 1
        self.delay = delay
        # browser instance
        self.browser = webdriver.Firefox(executable_path=GECKODRIVER,
                                         firefox_binary=FIREFOX_BINARY,
                                         firefox_profile=PROFILE,)

        # creating CSV header
        with open(self.dump, "w", newline='', encoding="utf-8") as save_file:
            writer = csv.writer(save_file)
            writer.writerow(["Author", "uTime", "Text"])

    def strip(self, string):
        """Helping function to remove all non alphanumeric characters"""
        words = string.split()
        words = [word for word in words if "#" not in word]
        string = " ".join(words)
        clean = ""
        for c in string:
            if str.isalnum(c) or (c in [" ", ".", ","]):
                clean += c
        return clean

    def collect_page(self, page):
        # navigate to page
        self.browser.get(
            'https://www.facebook.com/' + page + '/')

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):

            # Scroll down to bottom
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(self.delay)

        # Once the full page is loaded, we can start scraping
        with open(self.dump, "a+", newline='', encoding="utf-8") as save_file:
            writer = csv.writer(save_file)
            links = self.browser.find_elements_by_link_text("See More")
            for link in links:
                try:
                    link.click()
                except:
                    pass
            posts = self.browser.find_elements_by_class_name(
                "userContentWrapper")
            poster_names = self.browser.find_elements_by_xpath(
                "//a[@data-hovercard-referer]")

            for count, post in enumerate(posts):
                # Creating first CSV row entry with the poster name (eg. "Donald Trump")
                analysis = [poster_names[count].text]

                # Creating a time entry.
                time_element = post.find_element_by_css_selector("abbr")
                utime = time_element.get_attribute("data-utime")
                analysis.append(utime)

                # Creating post text entry
                text = post.find_element_by_class_name("userContent").text
                status = self.strip(text)
                analysis.append(status)

                # Write row to csv
                writer.writerow(analysis)

    def collect_groups(self, group):
        # navigate to page
        self.browser.get(
            'https://www.facebook.com/groups/' + group + '/')

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):

            # Scroll down to bottom
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(self.delay)

        # Once the full page is loaded, we can start scraping
        with open(self.dump, "a+", newline='', encoding="utf-8") as save_file:
            writer = csv.writer(save_file)
            posts = self.browser.find_elements_by_class_name("userContentWrapper")
            # links = self.browser.find_elements_by_link_text("See More")
            # for link in links:
            #     try:
            #         link.click()
            #     except:
            #         pass
            poster_names = self.browser.find_elements_by_xpath("//a[@data-hovercard-referer]")

            for count, post in enumerate(posts):
                # Creating first CSV row entry with the poster name (eg. "Donald Trump")
                # analysis = [poster_names[count].text]
                flag = False
                data = ""
                continue_reading_author = ""
                continue_reading_post = ""
                try:
                    link = post.find_element_by_xpath(".//span[@class='text_exposed_link']//a")
                    link.click()
                    if (len(self.browser.window_handles) == 2):
                        self.browser.switch_to.window(window_name=self.browser.window_handles[-1])
                        flag = True
                except Exception as e: 
                    pass
                if flag:
                    element = WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "userContentWrapper")))
                    post = self.browser.find_element_by_class_name("userContentWrapper")
                analysis = [post.find_element_by_xpath(".//a[@data-hovercard-referer]").text]
                print(analysis)

                # Creating a time entry.
                time_element = post.find_element_by_css_selector("abbr")
                utime = time_element.get_attribute("data-utime")
                analysis.append(utime)
                pprint(post)
                # Creating post text entry
                text = post.find_element_by_class_name("userContent").text
                pprint(text)
                # text2=post.find_element_by_class_name('text_exposed_show').text
                # print(text2)
                # status = self.strip(text)
                analysis.append(text)
                if flag:
                    self.browser.close()
                    self.browser.switch_to.window(window_name=self.browser.window_handles[0])

                # Write row to csv
                writer.writerow(analysis)

    def get_data_and_close_last_tab(self):
        if (len(self.driver.window_handles) == 2):
            self.driver.switch_to.window(window_name=self.driver.window_handles[-1])
            self.driver.close()
            self.driver.switch_to.window(window_name=self.driver.window_handles[0])

    def collect(self, typ):
        if typ == "groups":
            print(self.ids)
            self.collect_groups(self.ids)
            # for iden in self.ids:
            #     self.collect_groups(iden)
        elif typ == "pages":
            self.collect_page(self.ids)
            # for iden in self.ids:
            #     self.collect_page(iden)
        # self.browser.close()

    def safe_find_element_by_id(self, elem_id):
        try:
            return self.browser.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def login(self, email, password):
        try:

            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()

            # filling the form
            self.browser.find_element_by_name('email').send_keys(email)
            self.browser.find_element_by_name('pass').send_keys(password)

            # clicking on login button
            self.browser.find_element_by_id('loginbutton').click()
            # if your account uses multi factor authentication
            mfa_code_input = self.safe_find_element_by_id('approvals_code')

            if mfa_code_input is None:
                return

            mfa_code_input.send_keys(input("Enter MFA code: "))
            self.browser.find_element_by_id('checkpointSubmitButton').click()

            # there are so many screens asking you to verify things. Just skip them all
            while self.safe_find_element_by_id('checkpointSubmitButton') is not None:
                dont_save_browser_radio = self.safe_find_element_by_id('u_0_3')
                if dont_save_browser_radio is not None:
                    dont_save_browser_radio.click()

                self.browser.find_element_by_id(
                    'checkpointSubmitButton').click()

        except Exception as e:
            print("There's some error in log in.")
            print(sys.exc_info()[0])
            exit()


if __name__ == "__main__":

    # with open('credentials.txt') as f:
    #     email = f.readline().split('"')[1]
    #     password = f.readline().split('"')[1]
    #
    #     if email == "" or password == "":
    #         print(
    #             "Your email or password is missing. Kindly write them in credentials.txt")
    #         exit()
    file_dir=dir_path+"/Data/"
    email=input("Enter your email/username : ")
    password=getpass.getpass(prompt='Enter Password:')
    while True:
        try:
            type = input("Enter 1 for scraping from Group or Enter 2 for scraping from Page: ")
            if(type=="1"):
                group_name=input("Enter Group Name:")
                print("Depth:")
                depth=int(input())
                file_name=input("Enter the filename you want to save:")
                file_name=file_dir+file_name + ".csv"
                C = CollectPosts(ids=group_name,corpus_file=file_name ,depth=depth)
                C.login(email, password)
                C.collect("groups")
            if (type == "2"):
                page_name = input("Enter Page Name:")
                print("Depth:")
                depth = int(input())
                file_name = input("Enter the filename you want to save:")
                file_name = file_dir+file_name + ".csv"
                C = CollectPosts(ids=page_name,corpus_file=file_name ,depth=depth)
                C.login(email, password)
                C.collect("pages")
        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())