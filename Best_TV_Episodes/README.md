# Best TV Episodes
Use this tool to find the best episodes of any show! (Works best for procedural shows like: The Simpsons,
South Park, Spongebob Squarepants, etc...)

## How To Use
1. Google Search "Best episodes of {TV Show}"
2. Open all sites on the first page in new tabs
3. Run main.py
4. Add episodes shown in the sites using the following format: SEASON EPISODE - TITLE
   * Episodes titles are optional
5. Display Database
    * This displays the best episodes in descending order

## Features
1. Importing/Exporting data into .pkl files
2. Autosave data every given seconds
3. (Not Yet Implemented) Automatic Web-Scraper with Imdb integration
   * Performs all the steps in the "How to Use" section automatically

## How It Works
The more an episode appears in the "Best Episodes of ..." websites, the more likely it is better than other episodes.
For example: If season 5, episode 10 of South Park appears in 9 out of 10 "Best Episodes" lists,
then it is better than any other episode that appears in 8 out of 10 of the same "Best Episodes" lists.