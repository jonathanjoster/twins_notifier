from selenium import webdriver
import time
import schedule
import requests
from bs4 import BeautifulSoup
import re
from linebot import LineBotApi
from linebot.models import TextSendMessage
from webdriver_manager.chrome import ChromeDriverManager
        
def notify_line(message):
    ACCESS_TOKEN = '69N4y4iIcptDyKgHV1rcXAxg+Qt9cbSdy2uM/4fGOh7mOpFsCP+acGvimo6uONer4f8QNEQbqOUEt51L3JnEaQ1sHkGMUyyeKeR2znbEKTA6JUUSoUEKRGlcapO1781xy0pnNdOaOCrywTRVywK5AAdB04t89/1O/w1cDnyilFU='
    USER_ID = 'Udd54191c66c7d1acad4296a387e6dc63'
    
    line_bot_api = LineBotApi(ACCESS_TOKEN)
    messages = TextSendMessage(text=message)
    line_bot_api.push_message(USER_ID, messages=messages)
    
def scrape():
    # for DH_KEY_TOO_SMALL Error
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
    
    try:
        # visit website
        url = 'https://twins.tsukuba.ac.jp/campusweb/campusportal.do'
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(url)
        
        # log in
        userName_input = browser.find_element_by_name('userName')
        userName_input.send_keys('0012018113269')
        password_input = browser.find_element_by_name('password')
        password_input.send_keys('Mero3650')
        login_button = browser.find_element_by_tag_name('button')
        login_button.click()
        time.sleep(10)
        
        # 掲示一覧
        tab_kj = browser.find_elements_by_id('tab-kj')
        tab_kj[0].click()
        time.sleep(10)

        # 在学生へのお知らせ
        show_mores = browser.find_elements_by_link_text('…もっと読む')
        show_mores[2].click()
        time.sleep(10)

        # get newest 5 topics
        res = requests.get(browser.current_url, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        latest_5 = []
        for i in range(5, 11):
            tr = soup.find_all('tr')[i]
            latest_5.append(re.split('\s\s\s+', tr.text.replace('\n', '').replace('\r', '').strip()))
        
        # new record
        record_new = str(latest_5)
        
        # old record
        try:
            with open('record.txt') as f:
                record_old = f.read()
        except:
            record_old = ''
        
        # write on record.txt
        if record_new == record_old: return
        with open('record.txt', 'w') as f:
            f.write(record_new)
            
        # make notification
        message = 'New notice on Twins!\n'
        to_notify = [i for i in eval(record_new) if i not in eval(record_old)]
        for i in range(len(to_notify)):
            message += f'{str(to_notify[i][0])}\n'
        message += 'Further information: https://twins.tsukuba.ac.jp/'
        notify_line(message)
        
    finally:    
        browser.quit()

def main():
    schedule.every(3).hours.do(scrape)
    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == '__main__':
    main()