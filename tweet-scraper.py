import pandas as pd
import math
import snscrape.modules.twitter as sntwitter #pip install git+https://github.com/JustAnotherArchivist/snscrape.git
import PySimpleGUI as gui      

progressBar = gui.ProgressBar(max_value=100, orientation='h', key='progressBar')


def create_csv(tweets, user, num_of_tweets):
    tweets_panda = pd.DataFrame(tweets, columns=['username', 'content', 'likes'])
    tweets_panda.to_csv('./output/@' + user + '-last-' + str(num_of_tweets) + '.csv', sep=',', index = False)


def scrape_tweets(user, num_of_tweets):
    print(user)
    print(num_of_tweets)
    tweets = []

    num_of_tweets = int(num_of_tweets)

    last_i = 0
    print_limiter = num_of_tweets / 10

    print("Started scraping @" + user + "'s tweets... ")

    scraped_tweets = sntwitter.TwitterSearchScraper('from:' + user).get_items()

    for i, tweet in enumerate(scraped_tweets):

        if i >= num_of_tweets:
            break

        if (i - last_i) >= print_limiter:
            last_i = i
            progressBar.update(math.floor((i / num_of_tweets) * 100))
            print(math.floor((i / num_of_tweets) * 100), '%')

        #TODO: check if thread or not + #https://github.com/JustAnotherArchivist/snscrape/blob/master/snscrape/modules/twitter.py -> for tweet[options]
        tweets.append([tweet.user.username, tweet.content, tweet.likeCount])
        
        
    create_csv(tweets, user, num_of_tweets)
    
#PYGUI-------------------------------------------------------------------------------------------------
layout = [    
            [gui.Text('Enter username'),gui.Input(key='-USERNAME-')],
            [gui.Text('Enter number of tweets'),gui.Input(key='-NUM_OF_TWEETS-')],
            [gui.Radio('Threads', 1 , default = True), gui.Radio('Tweets', 1)],
            [gui.Button('Start')],
            [progressBar]
        ]      

window = gui.Window('Twitter Thread Scraper', layout)      

while True:                             # The Event Loop
    event, values = window.read()
    if event == 'Start':
        scrape_tweets(values['-USERNAME-'], int(values['-NUM_OF_TWEETS-']))
        break      
    if event == gui.WIN_CLOSED or event == 'Exit':
        break      

window.close()



num_of_tweets = 3000

#---------------------------------------------------------------------------------------------------------