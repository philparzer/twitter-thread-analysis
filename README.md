# 🧵 twitter-thread-analysis

This repo will be used to gather and possible also visualize data for a research paper. The paper looks into variations in user engagement between threads and singular tweets. It's aim is to highlight possible benefits of using Twitter threads for science communication.

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
