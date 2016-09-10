import time
import datetime
import re
import csv
import bs4
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

OUTPUT_FILE = "/home/elmaster/scraper/viarail/price.csv"


def get_random_int(min, max):
    return random.random() * (max - min + 1) + min


def make_output_file():
    header = ["scrape_date", "date", "time_departure", "time_arrival", "duration",
              "escape", "economy", "economy_plus", "business", "business_plus"]
    with open(OUTPUT_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def write_list_to_csv(data):
    with open(OUTPUT_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerows(data)


def clean_values(val):
    v1 = val.strip()
    v2 = re.sub('\d+ seat\D* at:', '', v1)
    v3 = v2.replace("$", "")
    return v3.strip()


def clean_duration(val):
    parsed = re.match("(\d+) hrs (\d+) m", val)
    hours = int(parsed.group(1))
    minutes = int(parsed.group(2))
    return hours * 60 + minutes


def extract_data(source):

    soup = bs4.BeautifulSoup(source, 'lxml')

    # Get current date
    date_raw = soup.find('li', class_='selected-calendar').get_text().strip()
    date = datetime.datetime.strptime(str(current_year) + date_raw, "%Y%b%d%A").date()

    # Extract the fare matrix
    fare_matrix = soup.find(id='fare-matrix')

    row_count = 1
    list_return = []
    for row in fare_matrix.find_all('div', class_='train-route-container'):

        print("Parsing row {row} for date {date}".format(row=row_count, date=date))

        all_time = row.find_all('span', class_='schedule-info')
        time_departure = all_time[0].get_text()
        time_arrival = all_time[1].get_text()

        duration_raw = row.find('div', class_='schedule-info-duration').get_text()
        duration = clean_duration(duration_raw)

        escape = row.find('div', class_='column column-special-fare').get_text()
        economy = row.find('div', class_='column column-economy-fare column-economy-discounted-fare').get_text()
        economy_plus = row.find('div', class_='column column-economy-fare column-economy-regular-fare').get_text()
        business = row.find('div', class_='column column-business-fare column-business-discounted-fare').get_text()
        business_plus = row.find('div', class_='column column-business-fare column-business-regular-fare').get_text()

        all_price_raw = [escape, economy, economy_plus, business, business_plus]

        # Clean
        all_price_clean = [clean_values(val) for val in all_price_raw]

        # Store
        row_count += 1
        all_output = [scrape_date, date, time_departure, time_arrival, duration] + all_price_clean
        list_return.append(all_output)

    return list_return

# Setting
scrape_date = datetime.datetime.now().strftime("%Y-%m-%d")
current_year = datetime.datetime.now().strftime("%Y")
current_day = str(int(datetime.datetime.now().strftime("%d")))

driver = webdriver.Chrome('/home/elmaster/chromedriver')  # Optional argument, if not specified will search path.

driver.get("http://www.viarail.ca/en")
time.sleep(10)

# One way trip
driver.find_element_by_id("ui-id-1-button").click()
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("ui-id-9").click()
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("cmbStationsFrom").click()
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("cmbStationsFrom").send_keys(u"montreal")
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("cmbStationsFrom").send_keys(Keys.ENTER)
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("cmbStationsTo").click()
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("cmbStationsTo").send_keys("sainte")
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("cmbStationsTo").send_keys(Keys.ENTER)
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_css_selector("button.continue").click()
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_css_selector("button.ui-datepicker-trigger").click()
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_link_text(str(current_day)).click()
time.sleep(get_random_int(0.5, 3))
driver.find_element_by_id("search-button").click()
time.sleep(get_random_int(5, 6))

# print(driver.window_handles)
driver.switch_to.window(window_name=driver.window_handles[-1])
time.sleep(get_random_int(0.5, 0.6))

# Scrape current page
parsed_data = extract_data(driver.page_source)
write_list_to_csv(parsed_data)

# Click on next date and get price for month ahead
for i in range(30):
    print("\n Click number: {}".format(i))
    time.sleep(get_random_int(0.5, 3))
    # Next date
    driver.find_element_by_xpath("//*[@id='calendar-tab-calendar']/ul/li[3]").click()

    parsed_data = extract_data(driver.page_source)
    write_list_to_csv(parsed_data)

driver.quit()
print("Done!")

# End
