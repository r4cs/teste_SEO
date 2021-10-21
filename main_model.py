import time
import urllib.parse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from time import sleep
from xlsxwriter import Workbook
import os
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm


class App:
    def __init__(self, target_query, owned_domain,  excluded_urls_list,
                 path='/Users/rac_hell/SEO_TEST'):
        self.target_query = target_query
        self.owned_domain = owned_domain
        self.excluded_urls_list = excluded_urls_list
        self.number_result = "10"
        self.path = path
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver') #Change this to your ChromeDriver path.
        self.error = False
        if self.error is False:
            self.possible_oportunities_dict = self.open_and_execute_target_query()
            print("possible_oportunities_dict: ",  self.possible_oportunities_dict)
            self.oportunities(self.possible_oportunities_dict)
            # self.clean_query_links(raw_result)
        # if self.error is False:
        #     self.scroll_down()
        # if self.error is False:
        #     if not os.path.exists(path):
        #         os.mkdir(path)
        #     self.downloading_images()
        # sleep(3)
        # self.driver.close()

    def write_captions_to_excel_file(self, images, caption_path):
        print('writing to excel')
        workbook = Workbook(os.path.join(caption_path, 'captions.xlsx'))
        worksheet = workbook.add_worksheet()
        row = 0
        worksheet.write(row, 0, 'Image name')       # 3 --> row number, column number, value
        worksheet.write(row, 1, 'Caption')
        row += 1
        for index, image in enumerate(images):
            filename = 'image_' + str(index) + '.jpg'
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption exists'
            worksheet.write(row, 0, filename)
            worksheet.write(row, 1, caption)
            row += 1
        workbook.close()

    def download_captions(self, images):
        captions_folder_path = os.path.join(self.path, 'captions')
        if not os.path.exists(captions_folder_path):
            os.mkdir(captions_folder_path)
        self.write_captions_to_excel_file(images, captions_folder_path)
        '''for index, image in enumerate(images):
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption exists for this image'"
            file_name = 'caption_' + str(index) + '.txt'
            file_path = os.path.join(captions_folder_path, file_name)
            link = image['src']
            with open(file_path, 'wb') as file:
                file.write(str('link:' + str(link) + '\n' + 'caption:' + caption).encode())'''

    def downloading_images(self):
        self.all_images = list(set(self.all_images))
        self.download_captions(self.all_images)
        print('Length of all images', len(self.all_images))
        for index, image in enumerate(self.all_images):
            filename = 'image_' + str(index) + '.jpg'
            image_path = os.path.join(self.path, filename)
            link = image['src']
            print('Downloading image', index)
            response = requests.get(link, stream=True)
            try:
                with open(image_path, 'wb') as file:
                    shutil.copyfileobj(response.raw, file)  # source -  destination
            except Exception as e:
                print(e)
                print('Could not download image number ', index)
                print('Image link -->', link)

    def scroll_down(self):
        try:
            no_of_posts = self.driver.find_element_by_xpath('//span[text()=" posts"]').text
            no_of_posts = no_of_posts.replace(' posts', '')
            no_of_posts = str(no_of_posts).replace(',', '')  # 15,483 --> 15483
            no_of_posts = int(no_of_posts)
            if self.no_of_posts > 12:
                no_of_scrolls = int(no_of_posts/12) + 3
                try:
                    for value in range(no_of_scrolls):
                        soup = BeautifulSoup(self.driver.page_source, 'lxml')
                        for image in soup.find_all('img'):
                            self.all_images.append(image)

                        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        sleep(2)
                except Exception as e:
                    self.error = True
                    print(e)
                    print('Some error occurred while trying to scroll down')
            sleep(10)
        except Exception:
            print('Could not find no of posts while trying to scroll down')
            self.error = True

    # def clean_query_links(self, raw_result):
    #     import re
    #     to_remove = []
    #     clean_links = []
    #     for i, l in enumerate(raw_result.values()):
    #         print(i)
    #         print(l)
    #         clean = re.search('\/url\?q\=(.*)\&sa', l) # CHANGE THIS REGEX
    #         if clean is None:
    #             to_remove.append(i)
    #             continue
    #         clean_links.append(clean.group(1))
    #     print("to_remove list: ", to_remove)
    #     print("\nclean_links list: ", clean_links)

    def open_and_execute_target_query(self):
        ua = UserAgent()
        excluded = str(["-"+exclude for exclude in self.excluded_urls_list]).replace("[", "").replace("]", "").replace("'", "")
        query = self.target_query + " -inurl:" + excluded
        query = urllib.parse.quote_plus(query)
        search_url = "https://www.google.com.br/search?q=" + query + "&num=" + str(self.number_result)
        self.driver.get(search_url)
        response = requests.get(search_url) #  ,  {"User-Agent": ua.data_randomize})
        soup = BeautifulSoup(response.text, "html.parser")
        raw_result = {}
        try:
            for loop, result in enumerate(self.driver.find_elements_by_xpath('//div[@id="search"]//div[@class="g"]')):
                title = result.find_element_by_xpath('.//h3').text
                link = result.find_element_by_xpath('.//div[@class="yuRUbf"]/a').get_attribute('href')
                detail = result.find_element_by_xpath('//div[@class="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf"]').text

                raw_result['title 0'+str(loop+1)] = title
                raw_result['link 0'+str(loop+1)] = link
                raw_result['detail 0'+str(loop+1)] = detail

        except Exception as e:
            print("Exception: ", e)
        # for key, value in raw_result.items():
        #     print(key, ":")
        #     print(value)
        return raw_result
        # try:
        #     self.clean_query_links(raw_result)
        # except Exception as e:
        #     print("Exception: ", e)


    def oportunities(self, oportunities_dict):
        # print("oportunities_dict: ", oportunities_dict)
        opportunity = []
        error_manual = []
        for url in tqdm(oportunities_dict.items(), ncols=100):
            if str(url).find("link"):
                print(url)
        #     print("link: ", link)
        #     tries = 0
        #     while tries < 10:
        #         try:
        #             self.driver.get(url)
        #             time.sleep(6)
        #             body = self.driver.page_source
        #             soup = BeautifulSoup(body, 'html.parser')
        #             hyperlinks = []
        #             for a in soup.find_all('a', href=True):
        #                 hyperlinks.append(a['href'])
        #             found = False
        #             for h in hyperlinks:
        #                 if self.owned_domain in h:
        #                     print('False Alert')
        #                     found = True
        #                     break
        #             if found == False:
        #                 print('Opportunity Found')
        #                 opportunity.append(url)
        #             print('oportunities: ', opportunity)
        #             self.driver.quit()
        #             break
        #         except:
        #             tries = tries + 1
        #             if tries == 10:
        #                 print('Error')
        #                 error_manual.append(url)

    def close_dialog_box(self):
        # reload page
        sleep(2)
        self.driver.get(self.driver.current_url)
        sleep(3)

        try:
            sleep(3)
            not_now_btn = self.driver.find_element_by_xpath('//*[text()="Not Now"]')
            sleep(3)

            not_now_btn.click()
            sleep(1)
        except Exception:
            pass


    def close_settings_window_if_there(self):
        try:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            pass

    def log_in(self, ):
        try:
            log_in_button = self.driver.find_element_by_link_text('Log in')
            log_in_button.click()
            sleep(3)
        except Exception:
            self.error = True
            print('Unable to find login button')
        else:
            try:
                user_name_input = self.driver.find_element_by_xpath('//input[@aria-label="Phone number, username, or email"]')
                user_name_input.send_keys(self.username)
                sleep(1)

                password_input = self.driver.find_element_by_xpath('//input[@aria-label="Password"]')
                password_input.send_keys(self.password)
                sleep(1)

                user_name_input.submit()
                sleep(1)

                self.close_settings_window_if_there()
            except Exception:
                print('Some exception occurred while trying to find username or password field')
                self.error = True



if __name__ == '__main__':
    # App("moda ~sustentavel")
    App("moda ~sustentavel", "https://www.useimpacto.com.br",
        ['wikipedia', 'facebook', 'instagram', 'pinterest',
         'mercadolivre', 'twitter', 'magalu', "magazineluiza",
         'aliexpress', "amaro", "lojasrenner"
         ]
        )
