from PySimpleGUI.PySimpleGUI import ToolTip
import pandas as pd
import math
import snscrape.modules.twitter as sntwitter #pip install git+https://github.com/JustAnotherArchivist/snscrape.git | #https://github.com/JustAnotherArchivist/snscrape/blob/master/snscrape/modules/twitter.py -> for tweet[options]
import PySimpleGUI as gui      

gui.theme('SystemDefault')

output_filepath = './'
start_button_disabled = False

layout = [  
            [gui.Text('Username', size=(10,1)),gui.Input(key='-USERNAME-', size=(45,1), tooltip="enter a twitter username")],
            [gui.Text('Tweet count', size=(10,1)),gui.Input(key='-NUM_OF_TWEETS-', size=(10,1), tooltip="specify the number of tweets you want to scrape")],
            [gui.Text('Output Folder', size=(10,1)),gui.Input('current directory', key='-OUTPUT_FILEPATH-', readonly=True, size=(45,1), tooltip="choose a folder for your .csv output"), gui.FolderBrowse()],
            [gui.Radio('Threads', 1 , default = True, pad=(1,20), key="-THREADS-"), gui.Radio('Tweets', 1, pad=(1,20), key="-TWEETS-"), gui.Radio('Replies', 1, pad=(1,20), key="-REPLIES-"), gui.Radio('Tweets & Replies', 1, pad=(1,20), key="-TNR-"), gui.Radio('All 4', 1, pad=(1,20), key="-MULTIPLE-")], #TODO: implement this
            [gui.Button('Start')],
            [gui.Text('Status', key='-STATUS-')],
            [gui.ProgressBar(max_value=100, orientation='h', key='progressBar', size=(40, 17))]
        ]      
 
window = gui.Window('Twitter Thread Scraper', layout)

def toggle_start_button():
    global start_button_disabled
    start_button_disabled = not start_button_disabled
    window['Start'].update(disabled = start_button_disabled)

def create_csv(tweets, user, num_of_tweets, type_of_scrape):
    tweets_panda = pd.DataFrame(tweets, columns=['username', 'content', 'likes', 'retweets', 'replies', 'id', 'conversationId', 'inReplyToUser']) #TODO: think about grouping threads by conversation id
    if tweets_panda.empty:
            window['-STATUS-'].update('No ' + type_of_scrape + ' found', text_color='red')
    else:
        
        if values['-MULTIPLE-']:
             window['-STATUS-'].update('Success! Scraped tweets, threads and replies from @' + user, text_color='green')

        else:
            window['-STATUS-'].update('Success! Scraped ' + str(len(tweets_panda)) + ' ' + type_of_scrape +' from @' + user, text_color='green')
        
        tweets_panda.to_csv(output_filepath + "@" + user.lower() + '-' + str(num_of_tweets) + '-' + type_of_scrape + '.csv', sep=',', index = False, encoding='utf-8') #FIXME: encoding doesn't work
        window['progressBar'].update(100)

def scrape_tweets(user, num_of_tweets):
    
    if user[0] == "@":
        user = user[1:]

    tweets = []
    threads = []
    replies = []
    all = []
    num_of_tweets = int(num_of_tweets)
    last_tweet = None
    last_tweet_was_thread = False

    last_i = 0
    progress_bar_update_limiter = num_of_tweets / 100

    try:

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper('from:' + user).get_items()):

            if i >= num_of_tweets:
                break

            if (i - last_i) >= progress_bar_update_limiter:
                last_i = i
                window['progressBar'].update(math.ceil((i / num_of_tweets) * 100))


        #FIXME: this doesnt work properly-----------------------------------------------------------------------------------------------------------

            replied_user = str(tweet.inReplyToUser)[20:] #slice url

            if last_tweet == None: #check if this is first iteration / first tweet
                print("first tweet")
                last_tweet = tweet

            elif replied_user == "": #check if this was start of thread
                print("no reply, could be start of thread")

                if last_tweet_was_thread:
                    threads.append([tweet.user.username, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount, tweet.id, tweet.conversationId, tweet.inReplyToUser])
                    last_tweet_was_thread = False
                    last_tweet = tweet
                
                else:
                    tweets.append([tweet.user.username, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount, tweet.id, tweet.conversationId, tweet.inReplyToUser])
                    all.append([tweet.user.username, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount, tweet.id, tweet.conversationId, tweet.inReplyToUser])

                

            elif replied_user == str(last_tweet.user.username): #found a thread
                threads.append([tweet.user.username, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount, tweet.id, tweet.conversationId, tweet.inReplyToUser])
                last_tweet = tweet
                last_tweet_was_thread = True

            else:
                replies.append([tweet.user.username, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount, tweet.id, tweet.conversationId, tweet.inReplyToUser])
                all.append([tweet.user.username, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount, tweet.id, tweet.conversationId, tweet.inReplyToUser])
        

        #-----------------------------------------------------------------------------------------------------------
        
        if values['-THREADS-']:
                type_of_scrape = 'threads'
                create_csv(threads, user, num_of_tweets, type_of_scrape)
        
        elif values['-TWEETS-']:
                type_of_scrape = 'tweets'
                create_csv(tweets, user, num_of_tweets, type_of_scrape)
        
        elif values['-REPLIES-']:
                type_of_scrape = 'replies'
                create_csv(replies, user, num_of_tweets, type_of_scrape)
        
        elif values['-TNR-']:
                type_of_scrape = 'tweets+replies'
                create_csv(all, user, num_of_tweets, type_of_scrape)

        elif values['-MULTIPLE-']:
            create_csv(threads, user, num_of_tweets, 'threads')
            create_csv(tweets, user, num_of_tweets, 'tweets')
            create_csv(replies, user, num_of_tweets, 'replies')
            create_csv(all, user, num_of_tweets, 'tweets+replies')

    except Exception as e:
        window['-STATUS-'].update(e, text_color='red') #TODO: add information on token error
    
     
while True:                      

    event, values = window.read()
    
    if event == 'Start':
        
        if values['-OUTPUT_FILEPATH-'] == 'current directory':
            output_filepath = "./"
        else:
            output_filepath = values["-OUTPUT_FILEPATH-"] + "/"
        
        if values["-USERNAME-"] == '':
            window['-STATUS-'].update('Enter a username', text_color='red')
            continue

        try:
            num_of_tweets = int(values['-NUM_OF_TWEETS-'])
            if (num_of_tweets < 1):
                window['-STATUS-'].update('Enter a number bigger than 0', text_color='red')
                continue

        except Exception as e:
            window['-STATUS-'].update('Enter a valid number of tweets', text_color='red')
            continue
        
        
        window["-STATUS-"].update("Scraping...", text_color='blue')
        toggle_start_button()
        scrape_tweets(values['-USERNAME-'], int(values['-NUM_OF_TWEETS-']))
        toggle_start_button()

    if event == gui.WIN_CLOSED or event == 'Exit':
        break


window.close()
quit()
