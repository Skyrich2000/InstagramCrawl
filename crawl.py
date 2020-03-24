import os
import json
import time
import logging
import urllib.request
import urllib.error
from urllib.parse import urlparse, quote

import multiprocessing
from multiprocessing import Pool
from user_agent import generate_user_agent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


main_keywords = {'IU': 'lilyiu_'}
link_files_dir = './data/link_files/'
log_dir = './data/logs/'
path = './chromedriver/chromedriver'
number_of_scrolls = 99999
cores = 4
usr = ''
pwd = ''


def get_image_links_story(keyword, link_file_path):
    img_urls = set()
    driver = webdriver.Chrome(path)

    driver.get('https://www.instagram.com/')
    time.sleep(2.5)
    driver.find_element_by_xpath('//input[@name="username"]').send_keys(usr)
    driver.find_element_by_xpath('//input[@name="password"]').send_keys(pwd)
    driver.find_element_by_xpath('//button[@type="submit"]').click()
    time.sleep(5)

    driver.get("https://www.instagram.com/"+main_keywords[keyword]+"/")
    time.sleep(2)

    repeat = 9999
    try:
        driver.find_element_by_xpath('//span[@class="_2dbep "]').click()
        time.sleep(2)
    except Exception as e:
        print(keyword, ": No Story")
        repeat = 0

    for _ in range(repeat):
        try:
            attr = driver.find_element_by_xpath('//img[@class="y-yJ5  "]').get_attribute("srcset").split('http')[-1].split(" ")
            if int(attr[1][:-1]) >= 800:
                url = 'http' + attr[0]
                img_urls.add(url)
                print(keyword, ": Found story image url: " + url[-8:], attr[1])
            else:
                print(keyword, ': not bigger enough images')
        except Exception as e:
            print('No image url')
        try:
            driver.find_element_by_xpath('//button[@class="ow3u_"]').click()
            time.sleep(0.5)
        except Exception as e:
            print(keyword, ": End of story page")
            break
    time.sleep(3)

    try:
        driver.find_element_by_xpath('//div[@class="aoVrC D1yaK"]').click()
        time.sleep(2)
    except Exception as e:
        print(keyword, ": No highlights")
        repeat = 0

    for _ in range(repeat):
        try:
            attr = driver.find_element_by_xpath('//img[@class="y-yJ5  "]').get_attribute("srcset").split('http')[-1].split(" ")
            if int(attr[1][:-1]) >= 800:
                url = 'http' + attr[0]
                img_urls.add(url)
                print(keyword,": Found highlight image url: " + url[-8:], attr[1])
            else:
                print(keyword, ': not bigger enough images')
        except Exception as e:
            print(keyword, ': No image url')
        try:
            driver.find_element_by_xpath('//button[@class="ow3u_"]').click()
            time.sleep(0.5)
        except Exception as e:
            print(keyword, ": End of highlight page")
            break
    print(keyword,': totally get {0} images from story'.format(len(img_urls)))
    driver.quit()

    with open(link_file_path, 'w') as wf:
        for url in img_urls:
            wf.write(url + '\n')
    print(keyword, ': Store all the links in file {0}'.format(link_file_path))

def get_image_links(keyword, link_file_path):
    #options = webdriver.ChromeOptions()
    #options.add_argument('--no-sandbox')
    img_urls = set()
    img_sub_urls = set()
    driver = webdriver.Chrome(path)

    driver.get("https://www.instagram.com/"+main_keywords[keyword]+"/")

    for _ in range(number_of_scrolls):
        size = len(img_sub_urls)
        try:
            for href in driver.find_elements_by_xpath('//div[@class="v1Nh3 kIKUG  _bz0w"]'):
                print(keyword, href.find_element_by_tag_name("a").get_attribute("href"))
                img_sub_urls.add(href.find_element_by_tag_name("a").get_attribute("href"))
            if size == len(img_sub_urls):
                raise Exception("no more")
        except Exception as e:
            print(keyword, ": "+str(e))
            break
        driver.execute_script("window.scrollBy(0, 1000000)")
        time.sleep(1)
    print(keyword, ": reach the end of page or get the maximum number of requested images")
    
    print(keyword, ": link num", len(img_sub_urls))
    for img_sub_url in img_sub_urls:
        print(keyword, ": Search start", img_sub_url)
        driver.get(img_sub_url)
        #article = driver.find_element_by_xpath('//article')
        for _ in range(9999):
            for div in driver.find_elements_by_xpath('//div[@class="KL4Bh"]'):
                try:
                    attr = div.find_element_by_tag_name("img").get_attribute("srcset").split('http')[-1].split(" ")
                    if int(attr[1][:-1]) >= 800:
                        url = 'http' + attr[0]
                        img_urls.add(url)
                        print(keyword, ": Found image url: " +url[-8:], attr[1])
                    else :
                        print(keyword, 'not bigger enough images')
                except Exception as e:
                    print(keyword, ': No image url')
                    continue
            try:
                driver.find_element_by_xpath('//button[@class="  _6CZji"]').click()
                time.sleep(1)
            except Exception as e:
                print(keyword, ": end of page")
                break
    print(keyword, ': Process totally get {0} images'.format(len(img_urls)))
    driver.quit()

    with open(link_file_path, 'w') as wf:
        for url in img_urls:
            wf.write(url +'\n')
    print(keyword, ': Store all the links in file {0}'.format(link_file_path))

if __name__ == "__main__":
    for d in [link_files_dir, log_dir]:
        if not os.path.exists(d):
            os.makedirs(d)
    ###################################
    # get image links and store in file
    ###################################
    # single process
    # for keyword in main_keywords:
    #     link_file_path = link_files_dir + keyword
    #     get_image_links(keyword, supplemented_keywords, link_file_path)

    # multiple processes
    # default number of process is the number of cores of your CPU, change it by yourself
    
    p = Pool(cores)
    for keyword in main_keywords:
        #p.apply_async(get_image_links, args=(keyword, link_files_dir + keyword))
        p.apply_async(get_image_links_story, args=(keyword, link_files_dir + keyword + "s"))
    p.close()
    p.join()
    print('Fininsh getting all image links')
