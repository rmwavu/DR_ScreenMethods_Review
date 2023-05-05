from selenium import webdriver

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup


# declare and also attain the path to the driver
# downloaded_path = ChromeDriverManager().install()

# print("Storage path:", downloaded_path)

# storage path
downloaded_path = r'C:\Users\ANDROMEDA\.wdm\drivers\chromedriver\win32\109.0.5414\chromedriver.exe'

# declare options
simple_otions = webdriver.ChromeOptions()

# ignore any validations
simple_otions.add_argument('--ignore-certificate-errors')

# run in incognito
simple_otions.add_argument('--incognito')

# ensure its hidden
simple_otions.add_argument('--headless')


# initialize the driver
driver_instance = webdriver.Chrome(service=Service(downloaded_path), options=simple_otions)

# test the openning of the site
driver_instance.get('https://www.sciencedirect.com/search?qs=machine%20learning%20diabetic%20retinopathy&date=2009-2023&show=100')

# store the page contents
page_data = driver_instance.page_source

# create beautiful soup instance
soup_instance = BeautifulSoup(page_data, 'lxml')

found_data = soup_instance.find_all('div')

print(found_data)