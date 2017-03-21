import time
import configparser
import twitter

class LimitReachedError(Exception):

	def __init__(self, event):
		self.message = event + '(event) called after rate limit reached'

class RateLimiter(object):

	def __init__(self, event, limitPeriod, callLimit):
		self.event = event
		self.limitPeriod = int(limitPeriod)
		self.callLimit = int(callLimit)

		self.calls = 0
		self.startTime = 0

		self.waitTime = 0

	def timeLeft(self):
		timeLeft = self.limitPeriod - (time.time() - self.startTime)
		if timeLeft < 0:
			self.reset()
			return self.limitPeriod

		return timeLeft

	def callsLeft(self):
		callsLeft = self.callLimit - self.calls
		if callsLeft < 1:
			raise LimitReachedError(self.event)

		return callsLeft

	def reset(self):
		self.startTime = time.time()
		self.calls = 0

	def call(self):
		try:
			self.waitTime += self.timeLeft() // self.callsLeft()
			self.calls += 1
		except LimitReachedError as error:
			print('\n' + error.message)
			self.wait(self.timeLeft())

	def wait(self, waitTime=None):
		waitTime = waitTime or self.waitTime
		while waitTime > 0:
			print('\r' + self.event + ': Wait ' + str(waitTime) + ' seconds...', end=' ')
			waitTime -= 1
			time.sleep(1)
		self.waitTime = 0


class User(object):

	def __init__(self):
		config = configparser.ConfigParser()
		config.read('twitterConfig.ini')

		self.api = twitter.Api(
			consumer_key=config['API Keys']['consumer_key'], 
			consumer_secret=config['API Keys']['consumer_secret'], 
			access_token_key=config['API Keys']['access_token_key'], 
			access_token_secret=config['API Keys']['access_token_secret'],
			sleep_on_rate_limit=True
		)
		self.limiters = {
			'getSearch': RateLimiter(
				'getSearch', 
				config['Rate Limits']['limit_period'], 
				config['Rate Limits']['get_search']
			),
			'getMentions': RateLimiter(
				'getMentions', 
				config['Rate Limits']['limit_period'], 
				config['Rate Limits']['get_mentions']
			)
		}
		self.maxSearchCount = int(config['Search']['max_count'])

		self.lastMentionId = ''
		self.setLastMentionId()

	def setLastMentionId(self):
		try:
			f = open('lastMentionId.txt', 'r')
			self.lastMentionId = f.read()
			f.close()
		except FileNotFoundError:
			lastMentions = self.newMentions(1)
			if lastMentions:
				self.updateLastMentionId(lastMentions[0].id)
			pass

	def updateLastMentionId(self, mentionId):
		self.lastMentionId = mentionId
		f = open('lastMentionId.txt', 'w')
		f.write(str(mentionId))
		f.close()

	def getScreenName(self):
		return self.api.VerifyCredentials().screen_name

	def search(self, searchTerm, count):

		def getSearch(term, max_id=None, count=self.maxSearchCount):
			self.limiters['getSearch'].call()
			return self.api.GetSearch(term=term, count=count, max_id=max_id)

		self.limit()

		results = getSearch(searchTerm, None, (count % self.maxSearchCount) + 1)
		while results and len(results) < count:
			maxId = results[-1].id
			results += getSearch(searchTerm, maxId)
			if maxId == results[-1].id:
				break

		return results

	def newMentions(self, count=None):
		self.limit()
		self.limiters['getMentions'].call()
		mentions = self.api.GetMentions(since_id=self.lastMentionId, count=count)
		mentions.reverse()
		return mentions

	def postMentionReply(self, statusText, mentionId):
		self.api.PostUpdate(statusText, in_reply_to_status_id=mentionId)
		self.updateLastMentionId(mentionId)
		self.limit()

	def limit(self):
		for limiter in self.limiters.values():
			limiter.wait()
