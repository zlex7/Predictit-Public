import selenium
import time
from selenium import webdriver
import requests

chrome_options = selenium.webdriver.chrome.options.Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-application-cache')
driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)  # Optional argument, if not specified will search path.
num_iterations = 10
#time.sleep(5) # Let the user actually see something!
#search_box = driver.find_element_by_name('q')
#search_box.send_keys('ChromeDriver')
#search_box.submit()
total_selenium_time = 0
total_requests_time = 0
for i in range(0,num_iterations):
	start = time.time()
	driver.get('http://www.twitter.com/realDonaldTrump')
	stop = time.time()
	total_selenium_time += (stop - start)
	start = time.time()
	requests.get('http://www.twitter.com/realDonaldTrump')
	total_requests_time += (time.time() - start)

print('average time with selenium = %f' % (total_selenium_time/num_iterations))
print('average time with requests = %f' % (total_requests_time/num_iterations))

#time.sleep(5) # Let the user actually see something!
#driver.quit()

