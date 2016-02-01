from pyvirtualdisplay import Display
from selenium import webdriver
import requests
import queue
import concurrent.futures
import getpass
import time

count = 1

def saveImage(the_queue):
    global count

    while the_queue.qsize():
        try:
            data = the_queue.get()
            if data == '\n':
                print('Ending')
                running = False
                break
        except queue.Empty:
            pass
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

def login(browser, username, password):
    url = 'https://www.instagram.com/accounts/login/'
    browser.get(url)
    browser.implicitly_wait(1)

    username_box = browser.find_element_by_xpath("//input[@name='username']")
    password_box = browser.find_element_by_xpath("//input[@name='password']")
    login = browser.find_element_by_xpath('//*[@id="react-root"]/div/article/div/div[1]/div/form/button[1]')

    username_box.send_keys(username)
    password_box.send_keys(password)
    time.sleep(1)
    login.click()
    time.sleep(1)

def get_all_pictures(browser, user_to_scrape, the_queue):
    base_page = 'https://www.instagram.com/{}/'.format(user_to_scrape)
    browser.get(base_page)
    browser.find_element_by_class_name('_oidfu').click()

    print('Gathering all the images...')
    while True:
        the_length = browser.execute_script(" return document.body.scrollHeight;")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_length = browser.execute_script(" return document.body.scrollHeight;")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.5);")

        if the_length == new_length:
            print('Gathered all images, preparing for download.')
            break

    xpath = "//*[contains(concat(' ', normalize-space(@class), ' '), ' _icyx7 ')]"
    pictures = [pic.get_attribute('src').replace('/s640x640','') for pic in browser.find_elements_by_xpath(xpath)]
    close_browser(browser)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        print('Starting downloading.')
        for url in pictures:
            executor.submit(get_request, url, the_queue)
    print('Sending ending')
    the_queue.put('\n')
    print('Finished saving all photos.')

def check_login(brwoser):
    try:
        incorrect = browser.find_element_by_xpath('//*[@id="slfErrorAlert"]')
        return False
    except:
        return True

def check_account_to_scrape(browser, user_to_scrape):
    base_page = 'https://www.instagram.com/{}/'.format(user_to_scrape)
    browser.get(base_page)
    try:
        private = browser.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div/h2')
        return False
    except:
        return True

def get_scrape_account_name():
    account_name = input('Type in the account name you wish to download: ')
    return account_name

def get_request(image_url, the_queue):
    r = requests.get(image_url)
    try:
        the_queue.put(r)
    except Exception:
        pass

def close_browser(browser):
    try:
        browser.quit()
    except Exception as e:
        browser.close()

if __name__ == '__main__':
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    user_to_scrape = get_scrape_account_name()
    the_queue = queue.Queue()
    browser = webdriver.Firefox()
    start_time = time.time()
    login(browser, username, password)
    if check_login(browser):
        if check_account_to_scrape(browser, user_to_scrape):
            pictures = get_all_pictures(browser, user_to_scrape, the_queue)
            saveImage(the_queue)
        else:
            close_browser(browser)
            print("The <{}> is a private account.".format(user_to_scrape))
    else:
        close_browser(browser)
        print("Login information was incorrect")
    print("--- %s seconds ---" % (time.time() - start_time))