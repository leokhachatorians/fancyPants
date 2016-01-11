from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
import queue
import threading
import concurrent.futures
import time
import getpass

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

    while True:
        the_length = browser.execute_script(" return document.body.scrollHeight;")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_length = browser.execute_script(" return document.body.scrollHeight;")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.5);")
        print('Scrolling to the end...')

        if the_length == new_length:
            print('Reached the end.')
            break

    xpath = "//*[contains(concat(' ', normalize-space(@class), ' '), ' _icyx7 ')]"
    pictures = browser.find_elements_by_xpath(xpath)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        for url in pictures:
            executor.submit(get_request, url.get_attribute('src'), the_queue)

def login(browser, username, password):
    url = 'https://www.instagram.com/accounts/login/'
    browser.get(url)
    browser.implicitly_wait(1)
    # try:
    #     #browser.find_element_by_class_name('_k6cv7').click()
    #     browser.find_element_by_xpath('//a[@class="_k6cv7")
    # except Exception as e:
    #     pass
    # try:
        #browser.find_element_by_class_name('_rz1lq').click()
    # browser.find_element_by_xpath('//*[@id="react-root"]/div/article/div/div[1]/div/form/button').click()
    # except Exception as e:
    #     pass

    username_box = browser.find_element_by_xpath("//input[@name='username']")
    password_box = browser.find_element_by_xpath("//input[@name='password']")
    login = browser.find_element_by_xpath('//*[@id="react-root"]/div/article/div/div[1]/div/form/button[1]')

    username_box.send_keys(username)
    password_box.send_keys(password)
    # time.sleep(1)
    login.click()
    # time.sleep(3)

def get_request(image_url, the_queue):
    r = requests.get(image_url)
    try:
        the_queue.put(r)
    except Exception:
        pass

if __name__ == '__main__':
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    start_time = time.time()
    the_queue = queue.Queue()
    the_write_thread = threading.Thread(target=saveImage, args=(the_queue,))
    browser = webdriver.Firefox()
    login(browser, username, password)
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