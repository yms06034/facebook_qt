from webdriver_manager.chrome import ChromeDriverManager
from subprocess import CREATE_NO_WINDOW
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup as bs
import pandas as pd

import pyperclip
import time
import datetime
import os, sys

# from facebook import append_log


def top_to_bottom(browser, i = None):
    start = time.time()
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(2.5)

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(1)
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                return
        last_height = new_height  
        if i:
            if (time.time() - start) > i:
                break
                
def print_csv(f_name, name, contact, city):
    try:
        df = pd.DataFrame({"이름":name,
                            "연락처":contact,
                            "지역":city})
        df = df.fillna('null')
        numbers = df['연락처'].str.split('년').str.get(0).str[-4:]
        int_values = []
        for item in numbers:
            if item.isdigit():
                int_values.append(int(item))
            else:
                int_values.append('없음')
        df.isnull().sum()
        df = df.fillna('null')
        numbers = df['연락처'].str.split('년').str.get(0).str[-4:]
        int_values = []
        for item in numbers:
            if item.isdigit():
                int_values.append(int(item))
            else:
                int_values.append('없음')
        df['출생연도'] = int_values
        df.columns = ['이름', '연락처', '지역', '출생연도']
        df['지역'] = df['지역'].str.split('이전 거주지').str.get(1).str.split('현재').str.get(0).fillna('표시할 장소 없음')     
        
        if len(df[df['연락처'].str.contains('\+82')]) >= 1:
            df['연락처'] = df['연락처'].str.split('\+82 ').str.get(1).str[0:12].fillna('없음')
            df.index[df['연락처'].str.contains('1')]
            phone_num = df.index[df['연락처'].str.contains('1')]
            df.loc[phone_num, '연락처'] = "0" + df.loc[phone_num, '연락처']
        else:
            df['연락처'] = '없음'
        df.to_csv(f"{f_name}.csv", encoding='UTF-8')
        
    except Exception as ex:
#         print(f'{len(name)} {len(contact)} {len(city)}')
        df = pd.DataFrame({"이름":name,
                            "연락처":contact,
                            "지역":city})
#         print(ex)
        df.to_csv(f"{f_name}.csv", encoding='UTF-8')

def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--no-sandbox')
    options.add_argument('no-sandox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    options.add_argument('incognito')

    # options.add_argument('headless')
    # Header Setting
    # service = Service(ChromeDriverManager().install())
    # service.creationflags = CREATE_NO_WINDOW
    # browser = webdriver.Chrome(options=options)
    chrome_service = Service('chromedriver')
    chrome_service.creationflags = CREATE_NO_WINDOW
    chrome_service = Service(executable_path="chromedriver.exe")
    browser = webdriver.Chrome(service=chrome_service, options=options)
    #open facebook
    browser.get("https://www.facebook.com/")
    time.sleep(2)
    
    return browser

def login(browser, id, pwd):
    #log info, search keyword
    USER = id
    PWD = pwd

    #login
    elem_id = browser.find_element("id", "email")
    pyperclip.copy(USER)
    elem_id.send_keys(Keys.CONTROL, "v")
    time.sleep(2)

    elem_pw = browser.find_element("id", "pass")
    pyperclip.copy(PWD)
    elem_pw.send_keys(Keys.CONTROL, "v")
    elem_pw.send_keys("\n")
    time.sleep(3)

    if "?sk=welcome" in browser.current_url:
        return 1
    else:
        return 0



def block_alert(browser):
    #except block alert
    try:
        elem_block = browser.find_element("xpath", "/html/body/div[3]/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div")
        elem_block.click()
    except:
        pass
    try:
        elem_block = browser.find_element('xpath', '/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div')
        elem_block.click()
    except:
        pass
    time.sleep(1)

#search
def search(browser, i_keyword, num):
    keyword = i_keyword
    number = int(num)
        
    #save elements
    name, contact, city = [], [], []
    error = []

    #search keyword in order
    browser.get(f"https://www.facebook.com/search/groups/?q={keyword}")
    time.sleep(2)
    
    block_alert(browser)

    #show only public groups
    elem_public = browser.find_element('xpath', '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div/div[2]/div/div[9]/div[2]/div[2]/div/div[2]/div/input')
    elem_public.click()

    top_to_bottom(browser, 5)
    time.sleep(5)
    
    #get group links
    soup_groups = bs(browser.page_source, "html.parser")
    top_elements = soup_groups.find_all(class_="x1yztbdb")
    groups_href = []

    try:
        for t in top_elements:
            groups_href.append(t.find("a").attrs['href'])
    except Exception as ex:
        print(ex)
    
    #add 'members' at the end to open members page directly
    final_href = []
    for g in groups_href:
        final_href.append(g[:len(g)-11]+'members')
    
    #save all group names and file names
    group_name, f_name = [], []

    #loop with groups
    for i in final_href:
        #open the group page
        browser.get(i)
        
        #except block alert
        block_alert(browser)
        
    # scroll to bottom
        member = browser.find_element('xpath', '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div/div[1]/h2/span/span/span/strong')
        member = member.text[4:]
        member = member.replace(',', '')
        member = 10
        while True:
            top_to_bottom(browser)
            time.sleep(1.5)

            #get pofile links
            soup_profile = bs(browser.page_source, "html.parser")
            h_list = soup_profile.find_all('h1')
            top_elements = soup_profile.find_all(class_="x1lq5wgf xgqcy7u x30kzoy x9jhf4c x1lliihq")

            #get profile links
            profile_list = []
            profile_href = []
            for j in top_elements:
                profile_list.append(j.find("a").attrs['href'])
                
            if len(profile_list) >= (int(member)*0.9):
                break
        
        #get profile lists
        for j in profile_list:
            profile_href.append('https://www.facebook.com/profile.php?id='+j[j.index('user/')+5:-1])

        #get group name
        for h in h_list:
            if h.text == '알림': continue
            elif h.text == '검색결과': continue
            else: g_name = h.text
        print(g_name)

        url = 'php?id='
        print(len(profile_href))
        
        #loop with profiles
        for j in profile_href:
            try:
                if len(name) >= number:
                    break
                print(profile_href.index(j))
                #open the profile page
                browser.get(j)
                #is profile link with id or numbers
                temp = browser.current_url
                if url in temp:
                    link = j + '&sk='
                else:
                    link = temp[:temp.index('?')]
                #open 
                browser.get(link+"about_contact_and_basic_info")
                soup_info = bs(browser.page_source, "html.parser")
                soup_name = soup_info.find(class_="x78zum5 x15sbx0n x5oxk1f x1jxijyj xym1h4x xuy2c7u x1ltux0g xc9uqle")
                soup_info_contact = soup_info.find(class_="xyamay9 xqmdsaz x1gan7if x1swvt13")
                t_cont = soup_info_contact.text
                if '+82 ' in t_cont:
                    contact.append(t_cont)
                    name.append(soup_name.find("h1").text)
                    browser.get(link+"about_places")
                    soup_info = bs(browser.page_source, "html.parser")
                    soup_info_city = soup_info.find(class_="xyamay9 xqmdsaz x1gan7if x1swvt13")
                    city.append(soup_info_city.text)
                else: continue

            except:
                l_name = len(name)
                l_cont = len(contact)
                l_city = len(city)
                print(browser.current_url)
                error.append(browser.current_url)
                if l_name > l_cont:
                    contact.append('이전 거주지표시할 장소 없음')
                    try:
                        browser.get(link+"about_places")
                        soup_info = bs(browser.page_source, "html.parser")
                        soup_info_ct = soup_info.find(class_="xyamay9 xqmdsaz x1gan7if x1swvt13")
                        city.append(soup_info_ct.text)
                    except:
                        city.append('')
                elif l_cont > l_city:
                    city.append('')
                else: 
                    continue
                                
        # get real time
        timestamp = datetime.datetime.now()
        t_stamp = timestamp.strftime("%Y-%m-%d_%H%M%S")
        t_filename = f'{keyword}_{t_stamp}'
        
        if len(name) == 0:
            group_name.append(g_name)
            f_name.append(' ')
            print(f'{g_name}: nothing in there')
            continue
        else:
            print_csv(t_filename, name, contact, city)
            print(f'{g_name}: {t_filename}')
            group_name.append(g_name)
            f_name.append(t_filename)

        if len(name) >= number:
            break

    if len(name) == 0:
        f_name.append(' ')
        print(f'{keyword}: nothing in there')
    else:
        print_csv(t_filename, name, contact, city)
        print(f'{keyword}: {t_filename}')
        f_name.append(t_filename)
    
    # timestamp = datetime.datetime.now()
    # t_stamp = timestamp.strftime("%Y-%m-%d_%H%M%S")
    # final_filename = f'{keyword}_filelist_{t_stamp}'

    # df = pd.DataFrame({"그룹 이름":group_name,
    #                    "파일명":f_name})
    
    # df.to_csv(f"{final_filename}.csv", encoding='UTF-8')

    return t_filename