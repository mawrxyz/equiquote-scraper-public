# EquiQuote Scraper

This code scrapes the links of the top 5 online stories from the Daily Mail, BBC and The Sun homepages. It scrapes each story for its title, timestamp, byline and article text. It then runs the article text through [EquiQuote](https://github.com/mawrxyz/source-gender-tool/), my tool to detect the gender of news sources and scrapes the results generated. Finally, it exports a CSV with the article data as well as results from EquiQuote. 

This script is meant to help test the quality of results from EquiQuote for my dissertation project. The three news outlets chosen were identified as the [top 3 news brands](https://pressgazette.co.uk/media-audience-and-business-data/media_metrics/most-popular-websites-news-uk-monthly-2/) in the UK by the Press Gazette in July 2023.