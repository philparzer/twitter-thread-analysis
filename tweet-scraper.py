import pandas as pd
import math
import snscrape.modules.twitter as sntwitter #pip install git+https://github.com/JustAnotherArchivist/snscrape.git | #https://github.com/JustAnotherArchivist/snscrape/blob/master/snscrape/modules/twitter.py -> for tweet[options]
import PySimpleGUI as gui
import webbrowser

gui.theme('systemdefault')

output_filepath = './'
start_button_disabled = False

layout = [  
            [gui.Text('Username', size=(10,1)),gui.Input(key='-USERNAME-', size=(45,1), tooltip="enter a twitter username")],
            [gui.Text('Tweet Count', size=(10,1)),gui.Input(key='-NUM_OF_TWEETS-', size=(10,1), tooltip="n most recent tweets to be scraped")],
            [gui.Text('Output Folder', size=(10,1)),gui.Input('current directory', key='-OUTPUT_FILEPATH-', readonly=True, size=(45,1), tooltip="choose a folder for your .csv output"), gui.FolderBrowse()],
            [gui.Radio('Threads', 1 , default = True, pad=(1,20), key="-THREADS-"), gui.Radio('Tweets', 1, pad=(1,20), key="-TWEETS-"), gui.Radio('Replies', 1, pad=(1,20), key="-REPLIES-"), gui.Radio('All 3', 1, pad=(1,20), key="-ALL-")],
            [gui.Button('Start')],
            [gui.Text('Status', key='-STATUS-', pad=((5,0),(10,0)))],
            [gui.ProgressBar(max_value=100, orientation='h', key='progressBar', size=(40, 17))],
            [gui.Text('Repo', enable_events=True, text_color='blue', tooltip="link to Github repo", pad=((5,0),(15,0)))],
            [gui.Text('Creator', enable_events=True, text_color='blue', tooltip="link to creator's website", pad=((5,0),(5,5)))]
        ]      
 
window = gui.Window('Twitter Thread Scraper', layout)


def toggle_start_button():
    global start_button_disabled
    start_button_disabled = not start_button_disabled
    window['Start'].update(disabled = start_button_disabled)



def create_csv(user, num_of_tweets, threads_panda, tweets_panda, replies_panda, all_panda):

    if values['-THREADS-']:
        if threads_panda.empty:
            window['-STATUS-'].update('Done. No threads found in @' + user + '\'s last'  + str(num_of_tweets) + ' tweets', text_color='orange')
        else:
            threads_panda.to_csv(output_filepath + "@" + user.lower() + '-last' + str(num_of_tweets) + '-' + str(len(threads_panda)) + 'threads' + '.csv', sep=',', index = False, encoding='utf-8')
            window['-STATUS-'].update('Success! Found ' + str(len(threads_panda)) + ' complete threads in @' + user + '\'s last '  + str(num_of_tweets) + ' tweets', text_color='green')

    elif values['-TWEETS-']:
        if tweets_panda.empty:
            window['-STATUS-'].update('Done. No singular tweets found in @' + user + "'s last"  + str(num_of_tweets) + " tweets", text_color='orange')
        else:
            tweets_panda.to_csv(output_filepath + "@" + user.lower() + '-last' + str(num_of_tweets) + '-' + str(len(tweets_panda)) + 'tweets' + '.csv', sep=',', index = False, encoding='utf-8')
            window['-STATUS-'].update('Success! Found ' + str(len(tweets_panda)) + ' ' + 'singular tweets in @' + user + '\'s last '  + str(num_of_tweets) + ' tweets', text_color='green')
    
    elif values['-REPLIES-']:
        if replies_panda.empty:
            window['-STATUS-'].update('Done. No replies found in @' + user + "'s last"  + str(num_of_tweets) + " tweets", text_color='orange')
        else:
            replies_panda.to_csv(output_filepath + "@" + user.lower() + '-last' + str(num_of_tweets) + '-' + str(len(replies_panda)) + 'replies' + '.csv', sep=',', index = False, encoding='utf-8')
            window['-STATUS-'].update('Success! Found ' + str(len(replies_panda)) + ' ' + 'replies in @' + user + '\'s last '  + str(num_of_tweets) + ' tweets', text_color='green')

    elif values['-ALL-']:
        all_panda.to_csv(output_filepath + "@" + user.lower() + '-last' + str(num_of_tweets) + '-all' + '.csv', sep=',', index = False, encoding='utf-8')
        window['-STATUS-'].update('Success! Scraped ' +  str(len(all_panda)) + ' simple tweets, threads and replies from @' + user, text_color='green')

    else:
        window['-STATUS-'].update('OUTPUTERROR', text_color='red')

    window['progressBar'].update(100)


def create_pandas(data, user, num_of_tweets):
    all_panda = pd.DataFrame(data, columns=['username', 'content', 'likes', 'retweets', 'replies', 'id', 'conversationId', 'inReplyToUser', 'date'])

    #------------------------------------
    #THREADS
    thread_conv_ids = []
    threads_panda = all_panda

    for index, row in threads_panda.iterrows():

        if row['inReplyToUser'] != None:
            
            if str(row['inReplyToUser'])[20:] != str(row['username']):
                threads_panda.drop(index, inplace=True)
            
            else: 
                thread_conv_ids.append(row['conversationId'])
                          
    #filtering to weed out singular tweets and incomplete threads
    threads_panda = threads_panda.groupby('conversationId').filter(lambda x: len(x) > 1)
    
    #------------------------------------
    #REPLIES
    replies_panda = pd.DataFrame(data, columns=['username', 'content', 'likes', 'retweets', 'replies', 'id', 'conversationId', 'inReplyToUser', 'date'])
    
    for index, row in replies_panda.iterrows():
        if row['inReplyToUser'] == None or str(row['inReplyToUser'])[20:] == str(row['username']):
            replies_panda.drop(index, inplace=True)


    #------------------------------------
    #TWEETS TODO: this needs testing, could probably be implemented cleaner (remove thread_conv_ids)
    tweets_panda = pd.DataFrame(data, columns=['username', 'content', 'likes', 'retweets', 'replies', 'id', 'conversationId', 'inReplyToUser', 'date'])

    for index, row in tweets_panda.iterrows():

        if row['inReplyToUser'] != None:
            tweets_panda.drop(index, inplace=True)

        elif row['conversationId'] in thread_conv_ids:
            tweets_panda.drop(index, inplace=True)

    #------------------------------------
    create_csv(user, num_of_tweets, threads_panda, tweets_panda, replies_panda, all_panda)



def scrape_tweets(user, num_of_tweets):
    
    if user[0] == "@":
        user = user[1:]

    tweets = []
    num_of_tweets = int(num_of_tweets)

    last_i = 0
    progress_bar_update_limiter = num_of_tweets / 100

    try:

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper('from:' + user).get_items()):

            if i >= num_of_tweets:
                break

            if (i - last_i) >= progress_bar_update_limiter:
                last_i = i
                window['progressBar'].update(math.ceil((i / num_of_tweets) * 100))


            tweets.append([tweet.user.username, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount, tweet.id, tweet.conversationId, tweet.inReplyToUser, tweet.date])

        create_pandas(tweets, user, num_of_tweets)

    except Exception as e:

        if repr(e) == "ScraperException('Unable to find guest token')":
            window['-STATUS-'].update('API Timeout: Wait a second, then try again', text_color='red')

        else:
            window['-STATUS-'].update(e, text_color='red')
    
     
while True:                      

    event, values = window.read()
    
    if event == 'Repo':
        webbrowser.open('https://github.com/philparzer/twitter-thread-analysis')

    if event == 'Creator':
        webbrowser.open('https://philippparzer.com/')

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
