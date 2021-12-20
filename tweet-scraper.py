from PySimpleGUI.PySimpleGUI import ToolTip
import pandas as pd
import math
import snscrape.modules.twitter as sntwitter #pip install git+https://github.com/JustAnotherArchivist/snscrape.git
import PySimpleGUI as gui      

gui.theme('SystemDefault')

output_filepath = './'

layout = [  
            [gui.Text('Username', size=(10,1)),gui.Input(key='-USERNAME-', size=(45,1), tooltip="enter a twitter username")],
            [gui.Text('Tweet count', size=(10,1)),gui.Input(key='-NUM_OF_TWEETS-', size=(10,1), tooltip="specify the number of tweets you want to scrape")],
            [gui.Text('Output Folder', size=(10,1)),gui.Input('current directory', key='-OUTPUT_FILEPATH-', readonly=True, size=(45,1), tooltip="choose a folder for your .csv output"), gui.FolderBrowse()],
            [gui.Radio('only Threads', 1 , default = True, pad=(1,20)), gui.Radio('only Tweets', 1, pad=(1,20)), gui.Radio('Both', 1, pad=(1,20))], #TODO: implement this
            [gui.Button('Start')],
            [gui.Text('Status', key='-STATUS-')],
            [gui.ProgressBar(max_value=100, orientation='h', key='progressBar', size=(40, 17))]
        ]      
 

window = gui.Window('Twitter Thread Scraper', layout)

def create_csv(tweets, user, num_of_tweets):
    tweets_panda = pd.DataFrame(tweets, columns=['username', 'content', 'likes'])
    if tweets_panda.empty:
        window['-STATUS-'].update('No tweets found (check for typos in username)', text_color='red')
    else:
        window['-STATUS-'].update('Success (scraped <= ' + str(num_of_tweets) + ' tweets from @' + user + ')', text_color='green') #TODO: after thread/tweet/both implementation make choice visible in filename
        tweets_panda.to_csv(output_filepath + "@" + user.lower() + '-last-' + str(num_of_tweets) + '.csv', sep=',', index = False, encoding='utf-8')
        window['progressBar'].update(100)


def scrape_tweets(user, num_of_tweets):
    tweets = []
    
    if user[0] == "@":
        user = user[1:]

    num_of_tweets = int(num_of_tweets)

    last_i = 0
    progress_bar_update_limiter = num_of_tweets / 100 #change int magic number (default of 100) -> if value bigger => more updates, if smaller => less updates

    try:

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper('from:' + user).get_items()):

            if i >= num_of_tweets:
                break

            if (i - last_i) >= progress_bar_update_limiter:
                last_i = i
                window['progressBar'].update(math.ceil((i / num_of_tweets) * 100))

            #TODO: check if thread or not + #https://github.com/JustAnotherArchivist/snscrape/blob/master/snscrape/modules/twitter.py -> for tweet[options]
            tweets.append([tweet.user.username, tweet.content, tweet.likeCount])
            
            
        create_csv(tweets, user, num_of_tweets)


    except Exception as e:
        window['-STATUS-'].update(e, text_color='red')
    
     
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
        scrape_tweets(values['-USERNAME-'], int(values['-NUM_OF_TWEETS-']))
            
    if event == gui.WIN_CLOSED or event == 'Exit':
        break


window.close()
quit()
