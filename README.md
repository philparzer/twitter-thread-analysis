

# <img src="https://raw.githubusercontent.com/philparzer/twitter-thread-analysis/main/assets/threads_logo.png" width=6%></img> twitter-thread-analysis

This repo will be used to gather and possibly also visualize data for a research paper. The paper looks into variations in user engagement between threads and singular tweets. Its aim is to highlight possible benefits of using Twitter threads for science communication.

## HOW TO

- make sure <a href="https://www.python.org/downloads/" target="_blank">Python</a> and <a href="https://git-scm.com/downloads" target="_blank">Git</a> is installed
- <a href="https://packaging.python.org/en/latest/tutorials/installing-packages/" target="_blank">install needed packages</a><br>
```console> 
pip install pandas
pip install pysimplegui
pip install git+https://github.com/JustAnotherArchivist/snscrape.git
```
- run tweet-scraper.py <br>
```console>
python tweet-scraper.py
```

## TODOs

- [x] add Tweet / Thread / Both mechanic
- [x] improve UX and add status messages
- [ ] expose output tweet properties in GUI
- [ ] add cancel scrape button
- [ ] compile

## POSSIBLE UPDATES

- [ ] implement visualization / plots
- [ ] do something about second caveat
- [ ] change GUI theme on mac

## IMPORTANT CAVEATS

1. Numbers don't always add up. E.g. Tweet Count = 100 -> 25 threads, 15 replies 55 tweets. This usually happens if not all parts of a thread are included in a given corpus size.
2. If a thread's initial tweet is a reply, this initial data point is categorized as a reply, and therefore not included in the threads output.
3. The scraper is in dire need of more testing, expect bugs and always check your output for errors (+ feel free to contact me)
