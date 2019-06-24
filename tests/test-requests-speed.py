import selenium
import time
from selenium import webdriver
import requests

num_iterations = 10
total_requests_time = 0
for i in range(0,num_iterations):
	start = time.time()
	requests.get('http://www.twitter.com/potus')
	print(time.time() - start)
