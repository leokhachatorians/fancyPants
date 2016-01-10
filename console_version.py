from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
import queue
import threading
import concurrent.futures
import time

count = 1

def saveImage(the_queue):
    global count
    while the_queue.qsize():
        try:
            data = the_queue.get()
        except queue.Empty:
            print('empty')
        name = '{}.jpg'.format(count)
        count += 1
        with open(str(name), 'wb') as handle:
            if not data.ok:
                pass
            for block in data.iter_content(4096):
                if not block:
                    break
                handle.write(block)

            handle.close()

def get_all_pictures(browser, page, the_queue):
    browser.get(page)
    browser.find_element_by_class_name('_oidfu').click()
    pictures_list = []

    while True:
        the_length = browser.execute_script(" return document.body.scrollHeight;")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_length = browser.execute_script(" return document.body.scrollHeight;")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.5);")
        print('Scrolling to the end...')

        if the_length == new_length:
            print('Reached the end.')
            break
        WebDriverWait(browser, 1)

    xpath = "//*[contains(concat(' ', normalize-space(@class), ' '), ' _icyx7 ')]"
    pictures = browser.find_elements_by_xpath(xpath)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        for url in pictures:
            executor.submit(get_request, url.get_attribute('src'), the_queue)

    return pictures_list

def get_request(image_url, the_queue):
    r = requests.get(image_url)
    try:
        the_queue.put(r)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    start_time = time.time()
    the_queue = queue.Queue()
    the_write_thread = threading.Thread(target=saveImage, args=(the_queue,))
    browser = webdriver.Firefox()
    base_page = 'https://www.instagram.com//'
    pictures = get_all_pictures(browser, base_page, the_queue)
    the_write_thread.start()

    try:
        browser.quit()
    except Exception as e:
        print(e)
        browser.close()
    except Exception as e:
        print(e)

    print("--- %s seconds ---" % (time.time() - start_time))