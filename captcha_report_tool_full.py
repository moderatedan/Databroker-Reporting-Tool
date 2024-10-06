from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# List of URLs to report
urls = [
    "https://absolutepeoplesearch.com",
    "https://freebackgroundcheck.org",
    "https://gladiknow.com",
    "https://golookup.com",
    "https://infotracer.com",
    "https://staterecords.org",
    "https://nuwber.com",
    "https://propeoplesearch.com",
    "https://searchsystems.net",
    "https://recordsfinder.com",
    "https://texaswarrantroundup.org",
    "https://advancedbackgroundchecks.com",
    "https://affordablebackgroundchecks.com",
    "https://beenverified.com",
    "https://bumper.com",
    "https://callercenter.com",
    "https://courtcasefinder.com",
    "https://cyberbackgroundchecks.com",
    "https://familytreenow.com",
    "https://fastbackgroundcheck.com",
    "https://fastpeoplesearch.com",
    "https://findpeoplesearch.com",
    "https://freepeopledirectory.com",
    "https://govwarrantsearch.org",
    "https://idstrong.com",
    "https://idtrue.com",
    "https://neighborwho.com",
    "https://numberguru.com",
    "https://open-public-records.com",
    "https://ownerly.com",
    "https://peoplefinders.com",
    "https://peoplelooker.com",
    "https://peoplesearchnow.com",
    "https://peoplesmart.com",
    "https://quickpeopletrace.com",
    "https://reversephonecheck.com",
    "https://searchpeoplefree.com",
    "https://searchquarry.com",
    "https://smartbackgroundchecks.com",
    "https://spyfly.com",
    "https://telephonedirectories.us",
    "https://texasarrests.org",
    "https://truepeoplesearch.com",
    "https://usa-people-search.com",
    "https://usatrace.com",
    "https://usphonebook.com",
    "https://usrecords.net",
    "https://uswarrants.org",
    "https://yellowbook.com"
]

# Initialize WebDriver for Firefox
driver = webdriver.Firefox()

# Function to handle confirmation
def handle_confirmation():
    try:
        time.sleep(2)  # Wait for the confirmation page to load
        print("Report sent, proceeding to next URL.")
    except Exception as e:
        print(f"Error handling confirmation: {e}")

# Function to report phishing
def report_phishing(url):
    driver.get('https://safebrowsing.google.com/safebrowsing/report_phish/?hl=en')
    time.sleep(2)  # Let the page load

    # Find the input field for the URL and submit
    input_field = driver.find_element(By.NAME, 'url')
    input_field.send_keys(url)

    # Enter reason (description)
    reason_field = driver.find_element(By.NAME, 'dq')  # 'dq' should be the correct name for the description
    reason = "This site is publicly publishing and selling details about me and others. Please remove it to protect people's privacy. The site also does not provide a proper way to remove unauthorized data."
    reason_field.send_keys(reason)

    # Wait for manual CAPTCHA solving
    print(f"Please solve the CAPTCHA for {url}")
    input("Press Enter after solving the CAPTCHA...")

    # Submit the form
    submit_button = driver.find_element(By.NAME, 'submit')
    submit_button.click()

    handle_confirmation()  # Handle the confirmation page

# Function to report badware
def report_badware(url):
    driver.get('https://safebrowsing.google.com/safebrowsing/report_badware/?hl=en')
    time.sleep(2)

    # Find the input field for the URL and submit
    input_field = driver.find_element(By.NAME, 'url')
    input_field.send_keys(url)

    # Enter reason (description)
    reason_field = driver.find_element(By.NAME, 'dq')  # 'dq' should be the correct name for the description
    reason = "This site is publicly publishing and selling details about me and others. Please remove it to protect people's privacy. The site also does not provide a proper way to remove unauthorized data."
    reason_field.send_keys(reason)

    # Wait for manual CAPTCHA solving
    print(f"Please solve the CAPTCHA for {url}")
    input("Press Enter after solving the CAPTCHA...")

    # Submit the form
    submit_button = driver.find_element(By.NAME, 'submit')
    submit_button.click()

    handle_confirmation()  # Handle the confirmation page

# Loop through URLs and report
for url in urls:
    report_phishing(url)
    report_badware(url)

# Quit the browser after all reports
driver.quit()
