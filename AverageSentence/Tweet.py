import markovify
import re

class InsufficientDataError(Exception):

	def __init__(self):
		self.message = 'Not enough data provided to create a best tweet.'


class TermCountError(Exception):

	def __init__(self, requestedTermCount, termCount):
		message = 'The requested term count (' + str(requestedTermCount) 
		message += ') is greater than the existing number of terms (' + str(termCount)
		message += ') or not positive.'
		self.message = message

class MarkovTweet(object):

	def __init__(self, length=140):
		self.length = length
		self.chain = markovify.NewlineText('')

	def formatStatusText(self, status):
		text = status.text.replace('\n', ' ')
		return re.sub(r'RT @\w+:', '', text).strip() + '\n'

	def addSearchResults(self, searchResults):
		tweets = ''
		for status in searchResults:
			tweets += self.formatStatusText(status)

		self.chain = markovify.combine([self.chain, markovify.NewlineText(tweets)])

	def average(self, max_overlap_ratio=.7):
		average = self.chain.make_short_sentence(self.length, max_overlap_ratio=max_overlap_ratio)
		if average:
			return average
		else:
			raise InsufficientDataError()

	def reset(self):
		self.chain = markovify.NewlineText('')



class Mention(object):

	def __init__(self, mention, mentionedScreenName, length=140):
		self.replyTo = '@' + mention.user.screen_name
		self.reply = MarkovTweet(length - (len(self.replyTo) + 1))

		mentioned = '@' + mentionedScreenName
		self.terms = [t for t in mention.text.split() if t.lower() != mentioned.lower()]
		self.searchTermsCount = 0

	def __str__(self):
		return self.text

	def getSearchTerms(self):
		termCount = len(self.terms)
		if self.searchTermsCount > termCount:
			raise TermCountError(self.searchTermsCount, termCount)
		else:
			self.searchTermsCount += 1

		searchTerms = []
		termLength = ((termCount - 1) // self.searchTermsCount) + 1
		for i in range(0, termCount, termLength):
			searchTerms.append(' '.join(self.terms[i:(i + termLength)]))

		return searchTerms

	def addSearchResultsToReply(self, searchResults):
		self.reply.addSearchResults(searchResults)

	def getReply(self, max_overlap_ratio=.7):
		return self.replyTo + ' ' + self.reply.average(max_overlap_ratio)

		