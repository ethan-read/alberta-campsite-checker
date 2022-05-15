from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os

"""
Bookings are not accessible on the website until 9:00 AM Alberta time.
"""
url='https://www.albertaparks.ca/albertaparksca/visit-our-parks/camping-in-albertas-parks/online-reservations/'



def set_config(filename: str):
    with open(filename) as f:
        lines = f.readlines()
    config = {'facility_name': str, "arrival_month": str, "arrival_day": int,
    "departure_month": str, "departure_day": int, 'access_type': str,
    'service_type': str, 'site_size': str}
    for line in lines:
        if line and line[0] not in ('#', '\n'):
            x = line.split(maxsplit=1)
            if len(x) < 2:
                raise ValueError(f'config field {line} left blank')
            field, value = x[0].strip(':'), x[1].strip()
            if config.get(field) is str:
                config[field] = value
                continue
            if config.get(field) is int:
                if value.isdigit() and 0 <= int(value) <= 31: # won't catch stuff like feb 30 but whatever
                    config[field] = value
                    continue

            raise ValueError(f'Incorrect format for {line}')
    return config


def open_browser(url: str, headless=True):
    opts = Options()
    if headless:
        opts.add_argument('--headless')
    driver = Firefox(options=opts)
    driver.get(url)
    return driver


def find_facility(driver, config):
    """
    Navigates to the booking page for the facility name given in config.
    """
    searchbar = driver.find_element(by=By.CSS_SELECTOR, value='input[type=search]')
    searchbar.send_keys(config["facility_name"])

    try:
        result = driver.find_element(by=By.ID, value='tableData').find_element(
            By.TAG_NAME, "tr").find_element(
            by=By.CLASS_NAME, value='button')
        result.click()
        driver.switch_to.window(driver.window_handles[1])
    except NoSuchElementException:
        driver.quit()
        raise ValueError(f'{config["facility_name"]} facility not found')

    try:
        # The booking page only allows a certain number of users at once and you typically
        # have to wait for 10 seconds or so
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, 'groupCamping')))

    except TimeoutException:
        driver.quit()
        raise TimeoutError('Timeout')



def select_month(driver, month):
    while driver.find_element(by=By.CLASS_NAME, value='monthCurrent').find_element(
            by=By.TAG_NAME, value='span').text != (month + ' 2022'):

        next_month = driver.find_element(by=By.CLASS_NAME, value='mainHeading').find_element(
            by=By.CLASS_NAME, value='monthRight')

        next_month.click()

def select_day(driver, day):
    day_span = driver.find_element(by=By.CLASS_NAME, value='datePicker').find_element(
        By.XPATH,f"//*[text()={day}]")

    day_span.click()

def select_dates(driver, config):
    start_date = driver.find_element(by=By.ID, value='startDateInput')
    start_date.click()
    select_month(driver, config['arrival_month'])
    select_day(driver, config["arrival_day"])

    end_date = driver.find_element(by=By.ID, value='endDateInput')
    end_date.click()

    select_month(driver, config["departure_month"])
    select_day(driver, config["departure_day"])


# Filling in the campsite options
def fill_options(driver, config):
    warnings = ''

    try:
        services = Select(driver.find_element(by=By.ID, value='serviceTypes').find_element(
            by=By.TAG_NAME, value='select'))
        services.select_by_visible_text(config["service_type"])
    except NoSuchElementException:
        warnings += f'\nNotice: his service choice of {config["service_type"]} is not available at {config["facility_name"]}'


    try:
        types = Select(driver.find_element(by=By.ID, value='siteType').find_element(
            by=By.TAG_NAME, value='select'))
        types.select_by_visible_text(config["access_type"])
    except NoSuchElementException:
        warnings += f'\nThe site with access {config["access_type"]} is not available at {config["facility_name"]}'

    try:
        sizes = Select(driver.find_element(by=By.ID, value='campingUnitSize').find_element(
            by=By.TAG_NAME, value='select'))
        sizes.select_by_visible_text(config["site_size"])
    except NoSuchElementException:
        warnings += f'\nThe site size of {config["site_size"]} is not available at {config["facility_name"]}'

    return warnings


def get_facility_name(driver):
    """
    The website's search function has autocompletion and searches for more than just the facility name.
    This function obtains the actual results to notify the user.

    """
    location_data = driver.find_element(by=By.CLASS_NAME, value='locationName')
    facility_name = location_data.find_element(by=By.TAG_NAME, value='h3').get_attribute('innerHTML')
    park_name = location_data.find_element(By.TAG_NAME, 'h6').get_attribute('innerHTML')
    return facility_name, park_name

def count_matches(driver):
    matches = driver.find_element(by=By.CLASS_NAME, value='siteMatchDetails').find_element(
        by=By.CLASS_NAME, value='siteCount').find_element(by=By.CLASS_NAME, value='number').text

    total_available = driver.find_element(by=By.CLASS_NAME, value='siteMatchDetails').find_element(
        by=By.CLASS_NAME, value='reservableSiteCount').find_element(by=By.CLASS_NAME, value='number').text
    return matches, total_available


def generate_message(config):
    driver = open_browser(url, headless=True)

    find_facility(driver, config)
    select_dates(driver, config)
    warnings = fill_options(driver, config)
    facility_name, park_name = get_facility_name(driver)
    matches, total_available = count_matches(driver)

    driver.quit()

    if total_available == 0:
        msg = 'No available campsites at {config["facility_name]}'
    else:
        msg = f'At {facility_name}, {park_name}, {total_available} sites are available from '+\
        f'{config["arrival_day"]}-{config["arrival_month"]} to {config["departure_day"]}-{config["departure_month"]} and {matches} match your search criteria'

    msg += warnings

    return msg

if __name__ == '__main__':
    config = set_config(os.path.join(os.path.dirname(__file__), 'config.txt'))
    print(generate_message())

