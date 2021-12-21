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
            [gui.Text('Tweet Count', size=(10,1)),gui.Input(key='-NUM_OF_TWEETS-', size=(10,1), tooltip="n most recent tweets to be scraped")],
            [gui.Text('Output Folder', size=(10,1)),gui.Input('current directory', key='-OUTPUT_FILEPATH-', readonly=True, size=(45,1), tooltip="choose a folder for your .csv output"), gui.FolderBrowse()],
            [gui.Radio('Threads', 1 , default = True, pad=(1,20), key="-THREADS-"), gui.Radio('Tweets', 1, pad=(1,20), key="-TWEETS-"), gui.Radio('Replies', 1, pad=(1,20), key="-REPLIES-"), gui.Radio('Threads, Tweets & Replies', 1, pad=(1,20), key="-ALL-")], #TODO: implement this
            [gui.Button('Start')],
            [gui.Text('Status', key='-STATUS-')],
            [gui.ProgressBar(max_value=100, orientation='h', key='progressBar', size=(40, 17))]
        ]      
 
window = gui.Window('Twitter Thread Scraper', layout)


def toggle_start_button():
    global start_button_disabled
    start_button_disabled = not start_button_disabled
    window['Start'].update(disabled = start_button_disabled)


def create_csv(data, user):

    all_panda = pd.DataFrame(data, columns=['username', 'content', 'likes', 'retweets', 'replies', 'id', 'conversationId', 'inReplyToUser', 'date']) #TODO: think about grouping threads by conversation id

    replies = []
    thread_conv_ids = []

    #filtering for double conversationIds
    threads_panda = all_panda.groupby('conversationId').filter(lambda x: len(x) > 2)

    for index, row in threads_panda.iterrows():

        if row['inReplyToUser'] != None:
            
            if str(row['inReplyToUser'])[20:] != str(row['username']):
                replies.append(row)#FIXME: not sure if this works
                threads_panda.drop(index, inplace=True)
            
            else:
                thread_conv_ids.append(row['conversationId'])
               
        
                
    #filtering another time to weed out replies
    threads_panda = threads_panda.groupby('conversationId').filter(lambda x: len(x) > 2) #TODO: think about output file grouping? maybe toplevel thread tweet -> where conversationId = id
    
    #FIXME: not sure if this works
    replies_panda = pd.DataFrame(replies, columns=['username', 'content', 'likes', 'retweets', 'replies', 'id', 'conversationId', 'inReplyToUser', 'date'])

    #FIXME: not sure if this works
    tweets_panda = all_panda.groupby('id').filter(lambda x: len(x) < 2)

    for index, row in tweets_panda.iterrows():

        if row['inReplyToUser'] != None:
            tweets_panda.drop(index, inplace=True)

        elif row['conversationId'] in thread_conv_ids:
            tweets_panda.drop(index, inplace=True)

    #GUI LOGIC
    if values['-THREADS-']:
        threads_panda.to_csv(output_filepath + "@" + user.lower() + '-' + str(len(threads_panda)) + '-' + 'threads' + '.csv', sep=',', index = False, encoding='utf-8') #FIXME: encoding doesn't work
        window['-STATUS-'].update('Success! Scraped ' + str(len(threads_panda)) + ' ' + 'threads' +' from @' + user, text_color='green')

    elif values['-TWEETS-']:#FIXME: not sure if this works
        tweets_panda.to_csv(output_filepath + "@" + user.lower() + '-' + str(len(tweets_panda)) + '-' + 'tweets' + '.csv', sep=',', index = False, encoding='utf-8')
        window['-STATUS-'].update('Success! Scraped ' + str(len(tweets_panda)) + ' ' + 'tweets' +' from @' + user, text_color='green')
    
    elif values['-REPLIES-']:#FIXME: not sure if this works
        replies_panda.to_csv(output_filepath + "@" + user.lower() + '-' + str(len(replies_panda)) + '-' + 'replies' + '.csv', sep=',', index = False, encoding='utf-8')
        window['-STATUS-'].update('Success! Scraped ' + str(len(replies_panda)) + ' ' + 'replies' +' from @' + user, text_color='green')

    elif values['-ALL-']:
        all_panda.to_csv(output_filepath + "@" + user.lower() + '-' + str(len(all_panda)) + '-' + 'all' + '.csv', sep=',', index = False, encoding='utf-8')
        window['-STATUS-'].update('Success! Scraped ' +  str(len(all_panda)) + ' tweets, threads and replies from @' + user, text_color='green')

    window['progressBar'].update(100)


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
            
        create_csv(tweets, user)

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
