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


main_keywords = ['IU']
download_dir = '../image_instagram/'
link_files_dir = './data/link_files/'
log_dir = './data/logs/'
cores = 4

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
