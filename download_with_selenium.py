# -*- coding: utf-8 -*-
# @Author: WuLC
# @Date:   2017-09-27 23:02:19
# @Last Modified by:   Arthur 
# @Last Modified time: 2020-03-11 15:36:58


####################################################################################################################
# Download images from google with specified keywords for searching
# search query is created by "main_keyword + supplemented_keyword"
# if there are multiple keywords, each main_keyword will join with each supplemented_keyword
# Use selenium and urllib, and each search query will download any number of images that google provide
# allow single process or multiple processes for downloading
# Pay attention that since selenium is used, geckodriver and firefox browser is required
####################################################################################################################

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


main_keywords = {'아이유': 'lilyiu_', '차은우': 'eunwo.o_c'}
download_dir = '../image_instagram/'
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

    driver.find_element_by_xpath('//span[@class="_2dbep "]').click()
    time.sleep(2)
    for _ in range(9999):
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

    driver.find_element_by_xpath('//div[@class="aoVrC D1yaK"]').click()
    time.sleep(2)

    for _ in range(9999):
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
    
def download_images(link_file_path, download_dir, log_dir, sub=""):
    """download images whose links are in the link file
    
    Args:
        link_file_path (str): path of file containing links of images
        download_dir (str): directory to store the downloaded images
    
    Returns:
        None
    """
    print('Start downloading with link file {0}..........'.format(link_file_path+sub))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    main_keyword = link_file_path.split('/')[-1]
    log_file = log_dir + 'download_selenium_{0}.log'.format(main_keyword)
    logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode="a+", format="%(asctime)-15s %(levelname)-8s  %(message)s")
    img_dir = download_dir + main_keyword + '/'
    count = 0
    headers = {}
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    # start to download images
    with open(link_file_path+sub, 'r') as rf:
        for link in rf:
            try:
                o = urlparse(link)
                ref = o.scheme + '://' + o.hostname
                #ref = 'https://www.google.com'
                ua = generate_user_agent()
                headers['User-Agent'] = ua
                headers['referer'] = ref
                print('\n{0}\n{1}\n{2}'.format(link.strip(), ref, ua))
                req = urllib.request.Request(link.strip(), headers = headers)
                response = urllib.request.urlopen(req)
                data = response.read()
                file_path = img_dir + '{0}{1}.jpg'.format(count, sub)
                with open(file_path,'wb') as wf:
                    wf.write(data)
                print('Process-{0} download image {1}/{2}{3}.jpg'.format(main_keyword, main_keyword, count, sub))
                count += 1
                if count % 10 == 0:
                    print('Process-{0} is sleeping'.format(main_keyword))
                    time.sleep(2)

            except urllib.error.URLError as e:
                print('URLError')
                logging.error('URLError while downloading image {0}reason:{1}'.format(link, e.reason))
                continue
            except urllib.error.HTTPError as e:
                print('HTTPError')
                logging.error('HTTPError while downloading image {0}http code {1}, reason:{2}'.format(link, e.code, e.reason))
                continue
            except Exception as e:
                print('Unexpected Error')
                logging.error('Unexpeted error while downloading image {0}error type:{1}, args:{2}'.format(link, type(e), e.args))
                continue

if __name__ == "__main__":
    for d in [download_dir, link_files_dir, log_dir]:
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
        p.apply_async(get_image_links, args=(keyword, link_files_dir + keyword))
        p.apply_async(get_image_links_story, args=(keyword, link_files_dir + keyword + "s"))
    p.close()
    p.join()
    print('Fininsh getting all image links')

    ###################################
    # download images with link file
    ###################################
    # single process
    # for keyword in main_keywords:
    #     link_file_path = link_files_dir + keyword
    #     download_images(link_file_path, download_dir)

    # multiple processes
    # default number of process is the number of cores of your CPU, change it by yourself
    p = Pool(cores)
    for keyword in main_keywords:
        p.apply_async(download_images, args=(link_files_dir + keyword, download_dir, log_dir))
        p.apply_async(download_images, args=(link_files_dir + keyword, download_dir, log_dir, 's'))
    p.close()
    p.join()
    print('Finish downloading all images')
