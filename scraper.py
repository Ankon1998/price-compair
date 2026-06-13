import gspread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import datetime
import time

# 1. Connect to Google Sheets
gc = gspread.service_account(filename='credentials.json') # Your downloaded JSON key
sh = gc.open('PC Parts Tracker').sheet1 # Replace with your Sheet name

# 2. Setup Headless Browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
driver = webdriver.Chrome(options=chrome_options)

# 3. Read URLs from the Sheet
urls = sh.col_values(3) # Assuming URLs are in Column C (Index 3)
start_row = 2 # Skipping the header row

# 4. Scraping Logic
for i, url in enumerate(urls[1:], start=start_row):
    if not url:
        continue
        
    driver.get(url)
    time.sleep(3) # Let the page load
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    price = "N/A"
    status = "Unknown"
    
    # --- Star Tech Logic ---
    if "startech.com.bd" in url:
        # Note: CSS classes change, inspect the live page to verify these
        price_tag = soup.select_one('.price-new') 
        status_tag = soup.select_one('.product-info-data product-status')
        if price_tag: price = price_tag.text.strip()
        if status_tag: status = status_tag.text.strip()
            
    # --- TechLand Logic ---
    elif "techlandbd.com" in url:
        price_tag = soup.select_one('.text-lg sm:text-xl lg:text-2xl font-bold text-[#1c4289]')
        status_tag = soup.select_one('. text-green-600  font-medium')
        if price_tag: price = price_tag.text.strip()
        if status_tag: status = status_tag.text.strip()
            
    # --- Ryans Logic ---
    elif "ryanscomputers.com" in url:
        price_tag = soup.select_one('.rp-block .new-sp-text') 
        status_tag = soup.select_one('.stock-status-class') # Inspect to find exact class
        if price_tag: price = price_tag.text.strip()
        if status_tag: status = status_tag.text.strip()

    # 5. Update the Sheet
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sh.update(f'D{i}', [[price]])  # Column D: Price
    sh.update(f'E{i}', [[status]]) # Column E: Status
    sh.update(f'G{i}', [[timestamp]]) # Column G: Last Updated

driver.quit()