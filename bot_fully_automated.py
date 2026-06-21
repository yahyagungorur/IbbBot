from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from bs4 import BeautifulSoup
import asyncio
import threading
import os
import sys
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

def element_exists(by, value):
    try:
        driver.find_element(by, value)
        return True
    except NoSuchElementException:
        return False
def logger(message):
    try:
        now = datetime.now()
        print(f"{now.strftime('%d/%m/%Y %H:%M:%S')} - {message}", end="", flush=True)
    except Exception as e:
        print(f"Something went wrong: {e}\n", flush=True)
def sendMessages(message):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        response = requests.post(url, data=payload)
        print(f"Message sent! {message}" if response.status_code == 200 else f"Failed: {message}", response.text)
    except Exception as e:
            logger(f"Something went wrong: {e}\n")
def FilterSession(hour,day,isNight):
    beginHour = hour.split(" - ")[0]
    if isNight :
        if ((beginHour == "18:00" or beginHour == "20:00" ) and day in ("Pazartesi","Perşembe","Cuma")) or ( (beginHour == "16:00" or beginHour == "17:00") and day in ("Cumartesi", "Pazar")):
        #if ((beginHour == "16:00" or beginHour == "17:00") and day in ("Cumartesi", "Pazar")):
            return True
        else :
            return False
    else :
        if (beginHour == "09:00" or beginHour == "10:00") and day in ("Cumartesi", "Pazar"): #(beginHour == "12:00") or ( (beginHour == "09:00" or beginHour == "10:00") and day in ("Cumartesi", "Pazar")):
            return True
        else :
            return False
def setWebDriver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--blink-settings=imagesEnabled=false")

    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2,
    }
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)
def deleteChatBotIcon(driver):
            driver.execute_script("""
            let chatWidget = document.querySelector('etiya-chat-widget');
            if (chatWidget) {
                chatWidget.remove();
            }
        """)  
def set_zoom(driver, zoom="10%"):
    driver.execute_script(f"document.body.style.zoom='{zoom}'")


def handle_approval_checkbox(driver, timeout=2):
    """Try to find and check approval checkbox using robust fallback locators."""
    locators = [
        (By.ID, "pageContent_cboxOnay"),
        (By.CSS_SELECTOR, 'input[id$="cboxOnay"]'),
        (By.XPATH, "//input[@type='checkbox' and (contains(@id,'cboxOnay') or contains(@name,'cboxOnay'))]"),
    ]

    for by, value in locators:
        try:
            checkbox = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )

            if checkbox.is_selected():
                return True

            try:
                checkbox.click()
            except Exception:
                driver.execute_script("arguments[0].click();", checkbox)

            return True
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            logger(f"Approval checkbox locator failed ({by}={value}): {e}\n")
            continue

    return False



searchStringRes = "SMS doğrulama kodu hatalı"
checkbox_id = ""
driver = setWebDriver()
bot_token = os.environ['BOT_TOKEN']
chat_id = os.environ['CHAT_ID']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']

session_string = os.environ.get('SESSION_STRING', '')
client = TelegramClient(StringSession(session_string), api_id, api_hash)

waiting_for_next = False
otp = ""

@client.on(events.NewMessage)

async def handler(event):
    global waiting_for_next
    global otp

    text = event.raw_text

    # Step 1: detect trigger
    if "SEANS BULUNDU" in text:
        print("Trigger detected ✅")
        waiting_for_next = True
        return

    # Step 2: capture next message
    if waiting_for_next:
        print("Next message:", text)
        otp = text

        # reset flag
        waiting_for_next = False


def start_telegram():
    client.start()
    client.run_until_disconnected()

# Run both start() and run_until_disconnected() in the same background thread
client_thread = threading.Thread(target=start_telegram, daemon=True)
client_thread.start()
time.sleep(3)

def main (): 
    logger("Bot started...\n")
    try :

        driver.get("https://online.spor.istanbul/uyegiris")
        set_zoom(driver)        

        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        # Fill login form
        driver.find_element(By.NAME, "txtTCPasaport").send_keys(os.environ['TC_PASSPORT'])
        driver.find_element(By.NAME, "txtSifre").send_keys(os.environ['TC_PASSWORD'])
        driver.find_element(By.NAME, "txtSifre").send_keys(Keys.RETURN)

        # Wait for the redirect (add explicit waits if needed)
        driver.implicitly_wait(5)

        # Print the current URL (should be the redirected one)
        print("Redirected to:", driver.current_url)

        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        # Optional: go to another page
        driver.get("https://online.spor.istanbul/uyespor")
        #print(driver.page_source)
        #set_zoom(driver)        

        time.sleep(15)
        
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pageContent_rptListe_lbtnSeansSecim_0"))
        )

        btnSeansSecim = driver.find_element(By.ID, "pageContent_rptListe_lbtnSeansSecim_0")
        btnSeansSecim.click()
        #print("Page source snippet:", driver.page_source) 
        print("Title:", driver.title)
        print("Current URL:", driver.current_url)
        last_update_id = 203305487
        approval_missing_logged = False
        while True:
            set_zoom(driver)        
            deleteChatBotIcon(driver)
        

            found = False
            randevu = "Boş randevu yok"
            
            # Get panels - handle if page is updating
            try:
                panels = driver.find_elements(By.CSS_SELECTOR, ".panel.panel-info")
            except StaleElementReferenceException as e:
                logger(f"Panels became stale, retrying...{e}\n")
                time.sleep(0.5)
                continue
            if not approval_missing_logged:
                for panel_index in range(len(panels)):
                    try:
                        # Re-fetch panels on each iteration to avoid stale references
                        panels = driver.find_elements(By.CSS_SELECTOR, ".panel.panel-info")
                        if panel_index >= len(panels):
                            break  # Panel no longer exists
                        
                        panel = panels[panel_index]
                        html = panel.get_attribute('outerHTML')
                        soup = BeautifulSoup(html, 'html.parser')
                        #date = soup.select_one(".panel-heading h3").get_text(strip=True)
                        date_raw = soup.select_one(".panel-heading h3").get_text(separator="\n", strip=True)
                        day, full_date = date_raw.split("\n")    
                        sessions = soup.select(".well")
                        for session in sessions:
                            try :
                                found = False
                                #seviye = session.select_one("span[title='Seans Seviyesi']").get_text(strip=True)
                                kort = session.select_one("label[title='Salon Adı']").get_text(strip=True)
                                kontenjan = session.select_one("span[title='Kalan Kontenjan']").get_text(strip=True)
                                #filtering
                                if kontenjan == "0":
                                    continue
                                
                                saat = session.select_one("span[id*='lblSeansSaat']").get_text(strip=True)
                                if FilterSession(saat,day,False) or os.environ.get('FULLY_SEARCHABLE', 'False').lower() == 'true':# and kort == 'KAPALI TENİS KORTU 3':
                                    print(f"date : {date_raw}\n")
                                    found = True

                                            
                                checkbox = session.select_one("input[type='checkbox']")

                                if found and checkbox is not None:
                                    checkbox_id = checkbox["id"]

                                if found and element_exists(By.ID, checkbox_id):
                                    set_zoom(driver)        
                                    deleteChatBotIcon(driver)
                                    randevu = f"{date_raw}\n{session.text}"
                                    for _attempt in range(3):
                                        try:
                                            checkbox = driver.find_element(By.ID, checkbox_id)
                                            checkbox.click()
                                            break
                                        except StaleElementReferenceException:
                                            if _attempt == 2:
                                                raise
                                            time.sleep(0.2)
                                    set_zoom(driver)        
                                    deleteChatBotIcon(driver) 
                                    
                                                # Handle approval checkbox - may not always be present
                                    approved = handle_approval_checkbox(driver)
                                    if not approved:
                                        if not approval_missing_logged:
                                            print("Approval checkbox not found on current page state. Not continuing without it.\n")
                                            approval_missing_logged = True
                                            continue  # If we had to handle approval, refresh to ensure we're on the right page state
                                        print("Approval checkbox not found on current page state. Continuing without it.\n")

                                    else:
                                        approval_missing_logged = False
                                        print("Approval checkbox found and handled.\n")                           # ✅ Click the save button
                                    for _attempt in range(3):
                                        try:
                                            button = driver.find_element(By.ID, "lbtnKaydet")
                                            button.click()
                                            break
                                        except StaleElementReferenceException:
                                            if _attempt == 2:
                                                raise
                                            time.sleep(0.2)
                                    found = True
                                    print(randevu)
                                    logger(f"{randevu}\n")
                                    break
                            except StaleElementReferenceException as e:
                                logger(f"Session element became stale, skipping...{e}\n")
                                continue  # Skip this session
                            except Exception as inner_e:
                                logger(f"Session error: {inner_e}\n")
                        if found :
                            break
                    except StaleElementReferenceException as e:
                        logger(f"Panel became stale, will retry on next refresh...{e}\n")
                        continue  # Skip this panel
                    except Exception as outer_e:
                        logger(f"Panel error: {outer_e}\n")
                    
            now = datetime.now()
            formatted = now.strftime("%d/%m/%Y %H:%M:%S")
            print(f"{formatted} - {randevu}")
            #logger(f"{formatted} - {randevu}\n")
        
            if randevu != "Boş randevu yok":    
                sendMessages(f"<b>🔥SEANS BULUNDU</b>\n{randevu}")

                wrongSMSCodeCount = 0
                message = ""
                set_zoom(driver)        
                deleteChatBotIcon(driver)  
                while message == "" :
                    message = otp       
                    if message != "":
                        if message == "0" : #cancel appointment
                            message = ""
                            break
                        driver.find_element(By.ID, "pageContent_txtDogrulamaKodu").send_keys(message)  
                        button = driver.find_element(By.ID, "btnCepTelDogrulamaGonder")
                        button.click()
                        logger(f"driver.page_source - {driver.page_source}\n")
                        
                        html = driver.page_source
                        # Parse with BeautifulSoup
                        soup = BeautifulSoup(html, 'html.parser')

                        # Extract the message from the notification box
                        span = soup.select_one('div[data-notify="container"] span[data-notify="message"]')
                        notify=""
                        if span:
                            notify = span.get_text(strip=True)
                            print("Message:", notify)                    
                        if searchStringRes in notify:
                            wrongSMSCodeCount+=1
                            sendMessages(f"<b>❌ {notify}</b>")
                            message=""
                            if wrongSMSCodeCount == 3:
                                break
                        elif "tanımlandı" in notify:
                            sendMessages(f"<b>✅ {notify}</b>")
                            btnSeansSecim.click()
                            break
                        else:
                            sendMessages(f"<b>❌ {notify}</b>")
                            break           
                    time.sleep(1)  # Delay to prevent rate-limiting
                if message == "" and checkbox_id != "":
                    sendMessages(f"<b>❌ İPTAL EDİLDİ</b>\n{randevu}")
                    driver.back()
                    checkbox = driver.find_element(By.ID, checkbox_id)
                    checkbox.click()   
            time.sleep(1)
            driver.refresh()
    except Exception as e:
        if driver:
            driver.quit()  # Use quit() instead of close() for proper cleanup
        logger(f"Bot stoppped...\nSomething went wrong: {e}\n")


if __name__ == "__main__":
    while True:
        try:
            main()
            break  # Exit if no error
        except Exception as e:
            logger(f"Error: {e}")
            print("Restarting in 3 seconds...")
            time.sleep(3)
            os.execv(sys.executable, ['python'] + sys.argv)