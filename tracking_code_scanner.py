import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
import time

# Define functions to find tracking codes using regex
def find_tracking_codes(page_source, driver):
    tracking_codes = {
        'gtm': re.findall('GTM-[A-Z0-9]+', page_source),
        'meta_pixel': re.findall(r"fbq\('init', '(\d{15,16})'\)", page_source),
        'ua': re.findall('UA-\d{4,10}-\d{1,4}', page_source),
        'ga4': re.findall('G-[A-Z0-9]+', page_source)
    }

    # Extract Google Ads Remarketing requests from network logs
    network_logs = driver.execute_script("return window.performance.getEntries();")
    remarketing_urls = {
        entry['name'] for entry in network_logs
        if "googleads.g.doubleclick.net" in entry['name'] or "www.googleadservices.com" in entry['name']
    }
    # You can use a regex to extract specific IDs from the URLs if needed
    tracking_codes['google_ads_remarketing'] = list(remarketing_urls)

    return {key: list(set(values)) for key, values in tracking_codes.items() if values}

# Function to initialize and use the headless browser
def scan_website(url):
    driver = None
    try:
        # Set up the Chrome driver options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set up the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Get the website
        driver.get(url)

        # Wait for the page to load and JS to execute (adjust the sleep time as necessary)
        time.sleep(5)

        # Get the page source after JS execution
        page_source = driver.page_source
        if page_source is None:
            st.error("Failed to retrieve the page source.")
            return {}

        # Find tracking codes
        tracking_codes = find_tracking_codes(page_source, driver)

        return tracking_codes

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return {}
    finally:
        if driver:
            driver.quit()

# Streamlit app layout
st.title('Website Tracking Code Scanner')

# Input box for URL
url = st.text_input('Enter the URL of the website to check')

# Button to check for tracking codes
if st.button('Scan for Tracking Codes'):
    if url:
        tracking_codes = scan_website(url)
        found_any = False
        # Check and report each tracking code
        for code_type, codes in tracking_codes.items():
            if codes:
                found_any = True
                st.success(f"{code_type.replace('_', ' ').title()} found:")
                for code in codes:
                    st.write(f"{code_type.replace('_', ' ').title()} ID: {code}")
            else:
                if code_type == 'meta_pixel':
                    st.error("Meta Pixel not found")
                else:
                    st.info(f"{code_type.replace('_', ' ').title()} not found.")

        if not found_any:
            st.error("No tracking codes were found.")
    else:
        st.error("Please enter a URL to check.")
