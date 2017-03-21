# Average Sentence Bot

This is the code for the @AverageSentence twitter bot. When it is mentioned, it will search twitter for the words following its screen name and create a markov chain based on the searched tweets. When possible, it will reply to the user who mentioned @AverageSentence with random a sentence chosen from the markov chain.

## Setup

First install the packages in `requirements.txt`.

Then, you must edit `twitterConfig.ini` to contain valid API keys and their secrets, and the correct rate limits (these should already be correct). 

## Start up

```
from AverageSentence import Bot


tweetsPerSearch = 2000 // (Default = 1000) Number of tweets added to the markov chain for each mention
maxOverlapRatio = .65   // (Default = .7) Maximum percentence of overlap the created reply can have with an existing tweet

t = Bot(tweetsPerSearch, maxOverlapRatio)
t.start()
```
