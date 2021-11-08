import pandas as pd
import math
import snscrape.modules.twitter as sntwitter #pip install git+https://github.com/JustAnotherArchivist/snscrape.git

num_of_tweets = 500
tweets = []

# SCRAPE -------------------------------------------------------------------------------------------------
user = 'cnnbrk'

#progress
last_i = 0
print_limiter = num_of_tweets / 10

print("Started scraping @" + user + "'s tweets... ")

for i, tweet in enumerate(sntwitter.TwitterSearchScraper('from:' + user).get_items()):
    if i > num_of_tweets:
        break
    if (i - last_i) >= print_limiter:
        last_i = i
        print(math.floor((i / num_of_tweets) * 100), '%')

    tweets.append([tweet.user.username, tweet.content, tweet.date]) #TODO: how to get if thread or not?
    #https://github.com/JustAnotherArchivist/snscrape/blob/master/snscrape/modules/twitter.py -> for tweet[options]
#---------------------------------------------------------------------------------------------------------

# PANDA --------------------------------------------------------------------------------------------------
tweets_panda = pd.DataFrame(tweets, columns=['username', 'content', 'date'])
tweets_panda.to_csv('./output/@' + user + '-last-' + str(num_of_tweets) + '.csv', sep=',', index = False)
#---------------------------------------------------------------------------------------------------------

print('Done!')