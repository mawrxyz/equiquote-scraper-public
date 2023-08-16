#!/usr/bin/env python
# coding: utf-8

# # EquiQuote Scraper
# 
# This code scrapes the links of the top 5 online stories from the Daily Mail, BBC and The Sun homepages. It scrapes each story for its title, timestamp, byline and article text. It then runs the article text through [EquiQuote](https://github.com/mawrxyz/source-gender-tool/), my tool to detect the gender of news sources and scrapes the results generated. Finally, it exports a CSV with the article data as well as results from EquiQuote. 
# 
# This script is meant to help test the quality of results from EquiQuote for my dissertation project. The three news outlets chosen were identified as the [top 3 news brands](https://pressgazette.co.uk/media-audience-and-business-data/media_metrics/most-popular-websites-news-uk-monthly-2/) in the UK by the Press Gazette in July 2023.


from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from datetime import datetime
import json
from threading import Thread


# Run scraper only 5 times

def read_counter(filename="counter.txt"):
    with open(filename, 'r') as file:
        return int(file.read().strip())

def increment_counter(filename="counter.txt"):
    count = read_counter(filename)
    with open(filename, 'w') as file:
        file.write(str(count + 1))

# Check if we've run 5 times already
if read_counter() >= 5:
    exit()


# ## The Daily Mail


class ScrapeMailHomepage: 
    '''Get top 5 links that are NOT live pages from Mail Online homepage'''
    
    home_url = "https://www.dailymail.co.uk/home/index.html"
    
    def __init__(self, driver): 
        self.driver = driver
        self.driver.get(self.home_url)
        self.links = self.get_links()
    
    def get_links(self) -> list: 
        top_links = self.driver.find_elements(By.CSS_SELECTOR, '[itemprop="url"]')
        
        unique_urls = set()
        top_5_urls = []

        for link in top_links:
            full_url = link.get_attribute('href')
            if full_url.startswith("https://www.dailymail.co.uk") and "/live/" not in full_url and full_url not in unique_urls:
                unique_urls.add(full_url)
                top_5_urls.append(full_url)

            if len(top_5_urls) == 5:
                break

        return top_5_urls


class MailArticleContent: 
    '''Scrape the content from each Mail Online article'''
    
    def __init__(self, driver, url):
        self.driver = driver
        self.driver.get(url)
        
        self.wait = WebDriverWait(self.driver, 10)
        
        try:
            accept_button = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.button_127GD.primary_2xk2l'))
            )
            accept_button.click()
        except (NoSuchElementException, TimeoutException):
            print('No cookie consent prompt found')
            
        time.sleep(5)
        
        self.time = self.get_time()
        self.text = self.get_text()
        self.title = self.get_title()
        self.byline = self.get_byline()
        
        
    def get_time(self) -> str: 
        try:
            return self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "time"))).get_attribute("datetime")
        except (NoSuchElementException, TimeoutException): 
            return ""
        
    def get_text(self) -> str: 
        try:
            self.wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, "#js-article-text p.mol-para-with-font")))
            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "#js-article-text p.mol-para-with-font")
            return " ".join([p.text for p in paragraphs])
        except (NoSuchElementException, TimeoutException): 
            return ""
    
    
    def get_title(self) -> str: 
        try:
            return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#js-article-text h2"))).text
        except (NoSuchElementException, TimeoutException): 
            try:
                return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#js-article-text h1"))).text
            except (NoSuchElementException, TimeoutException):
                return ""
    
    def get_byline(self) -> str: 
        try:
            return self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "author"))).text
        except (NoSuchElementException, TimeoutException): 
            return ""


# ## BBC


class ScrapeBBCHomepage: 
    '''Get top 5 links that are NOT live pages or videos from BBC homepage'''
    
    home_url = "https://www.bbc.co.uk/news"
    
    def __init__(self, driver): 
        self.driver = driver
        self.driver.get(self.home_url)
        self.links = self.get_links()
    
    def get_links(self) -> list: 
        top_stories = self.driver.find_element(By.ID, 'nw-c-topstories-domestic')
        top_links = top_stories.find_elements(By.CSS_SELECTOR, 'a.gs-c-promo-heading')
        
        unique_urls = set()
        top_5_urls = []

        for link in top_links:
            full_url = link.get_attribute('href')
            if full_url.startswith("https://www.bbc.co.uk/news") and "/live/" not in full_url             and "/av/" not in full_url and full_url not in unique_urls:
                unique_urls.add(full_url)
                top_5_urls.append(full_url)

            if len(top_5_urls) == 5:
                break

        return top_5_urls

class BBCArticleContent: 
    '''Scrape the content for each BBC article'''
    
    def __init__(self, driver, url):
        self.driver = driver
        self.driver.get(url)
        
        self.time = self.get_time()
        self.text = self.get_text()
        self.title = self.get_title()
        self.byline = self.get_byline()
    
    def get_time(self) -> str: 
        try:
            time_element = self.driver.find_element(By.CSS_SELECTOR, 'time[data-testid="timestamp"]')
            return time_element.get_attribute('dateTime')
        except NoSuchElementException: 
            return ""
        
    def get_text(self) -> str: 
        paragraphs = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-component="text-block"] p.ssrcss-1q0x1qg-Paragraph.e1jhz7w10')
        return " ".join([p.text for p in paragraphs if 'ssrcss-xbdn93-ItalicText.e5tfeyi2' not in p.get_attribute('class')])
    
    def get_title(self) -> str: 
        return self.driver.find_element(By.CSS_SELECTOR, "h1#main-heading").text
    
    def get_byline(self) -> str: 
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "div.ssrcss-68pt20-Text-TextContributorName").text
        except NoSuchElementException: 
            return ""


# ## The Sun


class ScrapeSunHomepage: 
    '''Get top 5 links that are NOT TV videos from The Sun homepage'''
    
    home_url = "https://www.thesun.co.uk/"
    
    def __init__(self, driver): 
        self.driver = driver
        self.driver.get(self.home_url)
        self.links = self.get_links()
    
    def get_links(self) -> list: 
        
        # Get the link in the div with class "splash-teaser-container"
        splash_link = self.driver.find_element(By.CSS_SELECTOR, '.splash-teaser-container a.splash-teaser_link')
        splash_url = splash_link.get_attribute('href')

        # Get the top links in the divs with class "teaser__copy-container"
        teaser_links = self.driver.find_elements(By.CSS_SELECTOR, '.new-block.sun-row-v2.teaser.teaser--main.customiser-v2-layout-5-large-4 .teaser__copy-container a.text-anchor-wrap')

        unique_urls = set()
        top_5_urls = []

        # Add the splash url to the list
        top_5_urls.append(splash_url)

        for link in teaser_links:
            full_url = link.get_attribute('href')
            if full_url.startswith("https://www.thesun.co.uk/") and "/tv/" not in full_url and full_url not in unique_urls:
                top_5_urls.append(full_url)

            # Stop after 5 links
            if len(top_5_urls) == 5:
                break


        return top_5_urls


class SunArticleContent: 
    '''Scrape the content from each The Sun article'''
    
    def __init__(self, driver, url):
        self.driver = driver
        self.driver.get(url)
        
        self.wait = WebDriverWait(self.driver, 10)
        
        try:
            iframe_element = driver.find_element(By.CSS_SELECTOR, "#sp_message_iframe_808654")
            driver.switch_to.frame(iframe_element)
            accept_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Fine By Me!"]'))
            )
            accept_button.click()
            driver.switch_to.default_content()
        except (NoSuchElementException, TimeoutException):
            print('No cookie consent prompt found')
        
        self.time = self.get_time()
        self.text = self.get_text()
        self.title = self.get_title()
        self.byline = self.get_byline()
        
    def get_time(self) -> str: 
        try:
            return self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "time"))).get_attribute("datetime")
        except (NoSuchElementException, TimeoutException): 
            return ""
        
    def get_text(self) -> str: 
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.article__content p")))
            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "div.article__content p")
            return " ".join([p.text for p in paragraphs])
        except (NoSuchElementException, TimeoutException): 
            return ""
    
    
    def get_title(self) -> str: 
        try:
            return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.article__headline"))).text
        except (NoSuchElementException, TimeoutException): 
            return ""
    
    def get_byline(self) -> str: 
        try:
            return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[rel="author"]'))).text
        except (NoSuchElementException, TimeoutException): 
            return ""


# ## Getting EquiQuote Results


def get_equiquote_results(text_list):
    '''Run article text through local version of EquiQuote and scrape results'''
    
    def content_has_loaded(driver):
        results_container = driver.find_element(By.CSS_SELECTOR, "div#results_container")
        current_content = results_container.text

        time.sleep(5) 

        new_content = results_container.text

        return current_content == new_content 
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print("Error initialising webdriver:", e)
        return

    try:
        driver.get("http://localhost:5000")
    except Exception as e:
        print("Error loading app:", e)
        return []

    wait = WebDriverWait(driver, 150)
    
    recommendations_list = []
    sources_detected_list = []

    for text in text_list:
        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea#article_text")))
            text_box = driver.find_element(By.CSS_SELECTOR, "textarea#article_text")
            text_box.clear()
            text_box.send_keys(text)
        except Exception as e:
            print("Error entering text into textbox:", e)
            continue  # Move on to the next text

        try:
            time.sleep(2)
            submit_button = driver.find_element(By.CSS_SELECTOR, "button#analyse-button")
            driver.execute_script("arguments[0].click();", submit_button)
            wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "div#results_statement").is_displayed())
        except Exception as e:
            print("Error submitting or waiting for results:", e)
            continue  # Move on to the next text

        try:
            wait.until(content_has_loaded)
            time.sleep(2)
            recommendations_element = driver.find_element(By.ID, 'recommendations')
            recommendations_list.append(recommendations_element.text)
            
            # Get the sources_detected table by id and extract the data
            sources_detected_table = driver.find_element(By.ID, 'source_table')
            
            # Get header row and extract keys from th elements
            header_row = sources_detected_table.find_element(By.TAG_NAME, 'tr')
            header_cells = header_row.find_elements(By.TAG_NAME, 'th')
            keys = [cell.text for cell in header_cells]

            rows = sources_detected_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip header row
            table_data = []

            for row in rows:
                cell_data_dict = {}
                cells = row.find_elements(By.TAG_NAME, 'td')
                for key, cell in zip(keys, cells):
                    # Extract text from td
                    td_text = cell.text.split('\n')[0]

                    # Try to extract text from tool-tip (span), if present
                    try:
                        span_element = cell.find_element(By.TAG_NAME, 'span')
                        # Use get_attribute('textContent') to get text even if the span is hidden
                        span_text = span_element.get_attribute('textContent')
                        final_text = f"{td_text}: {span_text}"
                    except NoSuchElementException:
                        final_text = td_text

                    cell_data_dict[key] = final_text
                table_data.append(cell_data_dict)

            sources_detected_list.append(json.dumps(table_data))
        except Exception as e:
            print("Error retrieving the results:", e)
            continue  # Move on to the next text

        try:
            reset_button = driver.find_element(By.CSS_SELECTOR, "button#reset-button")
            reset_button.click()
        except Exception as e:
            print("Error clicking the reset button:", e)
            continue  # Move on to the next text
        
    driver.quit()
    return recommendations_list, sources_detected_list


# ## Putting it all together


def run_scrape_task():
    '''Get links to top 5 news articles from Mail Online, BBC and The Sun homepages,
    scrape their content, run them through EquiQuote and export all of the article data and results as a CSV'''
    
    def scrape_articles(driver, links, source_name):
        articles_data = []
        text_list = []

        for link in links:
            article_data = {'link': link}
            try:
                if source_name == "BBC":
                    article = BBCArticleContent(driver, link)
                elif source_name == "Mail":
                    article = MailArticleContent(driver, link)
                elif source_name == "Sun":
                    article = SunArticleContent(driver, link)
                else:
                    raise ValueError(f"Unknown source_name: {source_name}")

                try:
                    article_data['title'] = article.title
                except Exception as e:
                    print(f"Error retrieving title for link {link}:", e)
                    article_data['title'] = 'N/A'

                try:
                    article_data['byline'] = article.byline
                except Exception as e:
                    print(f"Error retrieving byline for link {link}:", e)
                    article_data['byline'] = 'N/A'

                try:
                    article_data['time'] = article.time
                except Exception as e:
                    print(f"Error retrieving time for link {link}:", e)
                    article_data['time'] = 'N/A'

                try:
                    article_data['text'] = ' '.join(article.text.split()[:1000])
                except Exception as e:
                    print(f"Error retrieving text for link {link}:", e)
                    article_data['text'] = 'N/A'

                print(f"Article data found: {article_data}")
                articles_data.append(article_data)
                text_list.append(article_data['text'])
            except Exception as e:
                print(f"Error processing article link {link}:", e)
                article_data['title'] = 'N/A'
                article_data['byline'] = 'N/A'
                article_data['time'] = 'N/A'
                article_data['text'] = 'N/A'
                articles_data.append(article_data) 
                
        driver.quit()
        results_recommendations = []
        results_sources_detected = []
        
        try:
            # Get results from EquiQuote
            results_recommendations, results_sources_detected = get_equiquote_results(text_list)
            
            # Incorporate the results into articles_data
            for i, data in enumerate(articles_data):
                data['recommendations'] = results_recommendations[i] if i < len(results_recommendations) else 'N/A'
                data['sources_detected'] = results_sources_detected[i] if i < len(results_sources_detected) else 'N/A'
        except Exception as e:
            print("Error getting results from EquiQuote:", e)
            for data in articles_data:
                data['results'] = 'N/A'

        # Save the articles data to a CSV
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"data/{source_name}_{date_str}.csv"

        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['title', 'byline', 'time', 'link', 'text', 'recommendations', 'sources_detected']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for data in articles_data:
                    writer.writerow(data)
        except Exception as e:
            print("Error writing to CSV:", e)

        print(f"Data exported to {filename}")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print("Error initialising webdriver:", e)
        return
    
    try:
        mail_home = ScrapeMailHomepage(driver)
        print("Mail Online links found: ", mail_home.links)
    except Exception as e:
        print("Error scraping Mail Online homepage:", e)
        return

    try:
        bbc_home = ScrapeBBCHomepage(driver)
        print("BBC links found: ", bbc_home.links)
    except Exception as e:
        print("Error scraping BBC homepage:", e)
        return
    
    try:
        sun_home = ScrapeSunHomepage(driver)
        print("Sun links found: ", sun_home.links)
    except Exception as e:
        print("Error scraping Sun homepage:", e)
        return
    
    driver.quit()

    def scrape_articles_threaded(links, source_name):
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            scrape_articles(driver, links, source_name)
            driver.quit()
        except Exception as e:
            print(f"Error in scrape_articles_threaded for {source_name}:", e)

    # Create separate threads for each source
    mail_thread = Thread(target=scrape_articles_threaded, args=(mail_home.links, "Mail"))
    bbc_thread = Thread(target=scrape_articles_threaded, args=(bbc_home.links, "BBC"))
    sun_thread = Thread(target=scrape_articles_threaded, args=(sun_home.links, "Sun"))

    # Start the threads
    mail_thread.start()
    bbc_thread.start()
    sun_thread.start()

    # Wait for all threads to complete
    mail_thread.join()
    bbc_thread.join()
    sun_thread.join()

    print("All scrape tasks completed")


run_scrape_task()


# Increment the counter after a successful run
increment_counter()

