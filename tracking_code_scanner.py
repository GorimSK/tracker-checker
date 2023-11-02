import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re


# Define functions to find tracking codes using regex
def find_tracking_codes(page_source):
    tracking_codes = {
        'gtm': re.findall('GTM-[A-Z0-9]+', page_source),
        'meta_pixel': re.findall('fbq\\(\'init\', \'(\\d{15,16})\'\\)', page_source),
        'ua': re.findall('UA-\\d{4,10}-\\d{1,4}', page_source),
        'ga4': re.findall('G-[A-Z0-9]+', page_source),
        'google_ads_remarketing': re.findall('googleadservices\\.com/pagead/conversion/(\\d+)', page_source)
    }
    return {key: list(set(values)) for key, values in tracking_codes.items()}


# Function to initialize and use the headless browser
def scan_website(url):
    try:
        # Validate URL format
        if not re.match(r'https?://', url):
            raise ValueError("Invalid URL format. Please include http:// or https://")

        # Set up the Chrome driver options for Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set up the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Get the website
        driver.get(url)

        # Get the page source after JS execution
        page_source = driver.page_source

        # Quit the driver (close the browser)
        driver.quit()

        # Find tracking codes
        tracking_codes = find_tracking_codes(page_source)

        return tracking_codes

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return {}


# Streamlit app layout
st.title('Website Tracking Code Scanner')

# Input box for URL
url = st.text_input('Enter the URL of the website to check')

# Button to check for tracking codes
if st.button('Scan for Tracking Codes'):
    if url:
        try:
            tracking_codes = scan_website(url)
            if not tracking_codes:
                st.write("No tracking codes were found.")
            else:
                # Check and report each tracking code
                for code_type, codes in tracking_codes.items():
                    if codes:
                        st.success(f"{code_type.replace('_', ' ').title()} found:")
                        for code in codes:
                            st.write(f"{code_type.replace('_', ' ').title()} ID: {code}")
                    else:
                        st.info(f"{code_type.replace('_', ' ').title()} not found.")
        except ValueError as ve:
            st.error(ve)
    else:
        st.error("Please enter a URL to check.")

# To run the Streamlit app, use the command: 'streamlit run your_script.py'
