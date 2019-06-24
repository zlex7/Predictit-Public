import requests
import mechanicalsoup
import random
from fake_useragent import UserAgent
import pickle
from predictit.proxy_server import get_proxy_ips


LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '1234567890'
WORDS = [line.rstrip() for line in open("./names.txt")]

EMAILS = ["comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
  "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
  "live.com"]
"""
		self.browser.session.headers.update({
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\
			(KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}
		)"""
class AccountSpoofer:

	def __init__(self):
		self.browser = mechanicalsoup.Browser()
		self.reg_file = open("./accounts.pkl", "ab")


	def make_username(self, num_end=5):
		"""
		Creates a username string in the format:
		
		WORD1 + WORD2 + number * (random num_end) 

		"""
		# Truncate username to 15 characters
		username = random.choice(WORDS) + "".join(random.choice(NUMBERS) for _ in range(num_end))
		return username[-15:]

	def make_email(self, username):
		return self.weave_user(username) + "@" + random.choice(EMAILS)


	def make_password(self):
		rand_num = random.random()
		password = ""
		if rand_num < 0.5:
			password = "".join([random.choice(LETTERS+NUMBERS) for _ in range(random.choice([7, 8, 9, 10, 11, 12]))])
		elif rand_num < 0.7:
			password = random.choice(WORDS) + random.choice(NUMBERS)
			password += "".join([random.choice(NUMBERS) for _ in range(8-len(password))])
			password = password[0].upper() + password[1:]
		else:
			password = random.choice(NUMBERS) + random.choice(LETTERS) + random.choice(WORDS) + random.choice(WORDS)
			password += random.choice(NUMBERS)
			password = password[1].upper() + password[1:]
		return password


	def weave_user(self, username):
		"""
		Weave in random characters (periods, numbers, letters) into the username field for the email 
		to make it appear a little different than the Predcitit username
		"""
		rand_num = random.random()
		username = username [:-3]
		weave_dot_loc = random.choice(range(1, len(username)-1))
		if rand_num > 0.85:
			username = username[:weave_dot_loc] + "." + username[weave_dot_loc:]
		username += "".join([random.choice(LETTERS+NUMBERS) for _ in range(int(rand_num*4))])
		return username


	def create_account(self):
		rand_num = random.choice(range(4, 7))
		username = self.make_username(num_end=rand_num)
		email = self.make_email(username)
		password = self.make_password()
		credentials = {"username": username, "password": password, "email": email}
		print("[~] Credentials: %s" % credentials)
		# resp = ProxyRequests('https://www.predictit.org/api/Account/Register')
		# resp.set_headers({'User-Agent': UserAgent().random})
		# resp.post(credentials)
		# print("[~] Proxy Used: %s" % resp.get_proxy_used())

		# if resp.get_status_code() == 200:
		# 	pickle.dump(credentials, self.reg_file)
		# 	print("[~] Fake Email Successfully Created")
		# else:
		# 	print("[~] Error Occurred when creating account. HTML Response: %d" % resp.get_status_code())
		# 	print("[~] Response Content: %s" % resp.get_headers())

		self.browser.session.headers.update()
		self.browser.session.proxies = {"http":"http://104.248.215.169:80"}
		print("[~] Sending browser request.")

		resp = self.browser.post('https://www.predictit.org/api/Account/Register', credentials)
		if resp.status_code == 200:
			pickle.dump(credentials, self.reg_file)
			print("[~] Fake Email Successfully Created")
		else:
			print("[~] Error Occurred when creating account. HTML Response: %d" % resp.status_code)
			print("[~] Response Content: %s" % resp.content)



a = AccountSpoofer()
for i in range(1000):
	a.create_account()




# Proxy Time


# print("Username Test:")
# for i in range(100):
# 	print(make_email())

# acc = make_email()
# r = browser.post('https://www.predictit.org/api/Account/Register',
#         		acc)

# # Rotate User Agent
# # Use Proxy
# # Scrape using this

# print(r)
# print(r.content)