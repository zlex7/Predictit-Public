import requests
import time
import sys
import os

open('correct-trump.tweets','w+').write(requests.get("https://twitter.com/realDonaldTrump").content)

#os.remove('trump.tweets')
#os.remove('scrape.times')
scrape_times = open('scrape.times','w+')

while True:
	tweet_html = open('trump.tweets','w+')
	#print('loop')
	#print(requests.get("https://twitter.com/realDonaldTrump").content)
	start = time.time()
	r = requests.get("https://twitter.com/realDonaldTrump")
	content = r.content
	status_code = r.status_code
	stop = time.time()
	tweet_html.write(content)
	tweet_html.close()
	scrape_times.write('scrape took %s seconds, status code = %d\n' % (stop - start, status_code))
	scrape_times.flush()
	#sys.stdout.close()
	#sys.stdout = open('trump.tweets', 'w')
	#print(tweet_html.read())
	old_tweet_html = open('trump-old.tweets','w+')
	old_tweet_html.write(content)
	old_tweet_html.close()
