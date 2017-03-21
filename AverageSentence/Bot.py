from AverageSentence.Twitter import User
from AverageSentence.Tweet import Mention

class Bot(object):

	def __init__(self, tweetsPerSearch=1000, maxOverlapRatio=.7):
		self.tweetsPerSearch = tweetsPerSearch
		self.maxOverlapRatio = maxOverlapRatio

		self.twitter = User()

	def getSearchResults(self, searchTerms):
		results = []
		for term in searchTerms:
			results += self.twitter.search(term, self.tweetsPerSearch)

		return results

	def getReply(self, mention):
		reply = ''
		while not reply:
			try:
				searchResults = self.getSearchResults(mention.getSearchTerms())
				mention.addSearchResultsToReply(searchResults)
				reply = mention.getReply(self.maxOverlapRatio)
			except InsufficientDataError as e:
				print('Could not build reply. Trying again with more search terms.')

		return reply

	def postReply(self, reply, mentionId):
		try:
			print(reply)
			if len(reply) <= 140:
				self.twitter.postMentionReply(reply, mentionId)
			else:
				print('Reply is too long to post.')
		except twitter.error.TwitterError as e:
			print(e.message)

	def start(self):
		while True:
			for status in self.twitter.newMentions():
				m = Mention(status, self.twitter.getScreenName())
				try:
					reply = self.getReply(m)
					self.postReply(reply, status.id)
				except TermCountError as e:
					print(e.message)
