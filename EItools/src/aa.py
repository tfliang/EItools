import bs4
import requests
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--proxy-server=47.254.84.58:41234')
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get("https://www.google.com")
element = driver.find_element_by_tag_name("body")
soup = bs4.BeautifulSoup(element.get_attribute("outerHTML"), 'html.parser')
for script in soup(["script", "style"]):
    script.extract()
text = soup.find('body').get_text().strip()
print(text)


