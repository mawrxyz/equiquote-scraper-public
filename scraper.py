#!/usr/bin/env python
# coding: utf-8

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
            if full_url.startswith("https://www.bbc.co.uk/news") and "/live/" not in full_url and "/av/" not in full_url and full_url not in unique_urls:
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
            
        time.sleep(5) # Wait because the pages seem to take some time to fully load dynamically
        
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

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print("Error initializing webdriver:", e)
        return

    try:
        driver.get("http://localhost:5000")
    except Exception as e:
        print("Error loading app:", e)
        return []

    wait = WebDriverWait(driver, 150)
    recommendations_list = []
    source_suggestions_list = []
    sources_detected_list = []

    for text in text_list:
        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea#article_text")))
            text_box = driver.find_element(By.CSS_SELECTOR, "textarea#article_text")
            text_box.clear()
            text_box.send_keys(text)
            print("Text entered into textbox")
        except Exception as e:
            print("Error entering text into textbox:", e)
            recommendations_list.append('N/A')
            source_suggestions_list.append('N/A')
            sources_detected_list.append('N/A')

        try:
            time.sleep(2)
            submit_button = driver.find_element(By.CSS_SELECTOR, "button#analyse-button")
            driver.execute_script("arguments[0].click();", submit_button)
            print("Text submitted")
        except Exception as e:
            print("Error submitting or waiting for results:", e)
            recommendations_list.append('N/A')
            source_suggestions_list.append('N/A')
            sources_detected_list.append('N/A')

        try:
            wait.until(EC.visibility_of_element_located((By.ID, 'loading-spinner')))
            print("Loading results")
            wait.until(EC.invisibility_of_element_located((By.ID, 'loading-spinner')))
            print("Done loading results")
        except Exception as e:
            print("Results did not load:", e)
            recommendations_list.append('N/A')
            source_suggestions_list.append('N/A')
            sources_detected_list.append('N/A')
        
        try:
            temp_message_element = driver.find_element(By.ID, "temp-message")
            if temp_message_element.is_displayed():
                print("Generating source suggestions")
                # Temp-message is present and displayed, wait for it to disappear
                wait.until_not(EC.presence_of_element_located((By.ID, "temp-message")))
                print("Source suggestions generated")
        except NoSuchElementException:
            # Temp-message is not present, nothing to wait for
            pass
        except TimeoutException:
            # Temp-message did not disappear within the timeout period
            print("Warning: temp-message did not disappear within the timeout period.")

        try:
            # Click on each link in the "li" elements and get the source suggestions
            job_links_ul = driver.find_element(By.ID, "job_links_ul")
            job_links = job_links_ul.find_elements(By.TAG_NAME, "a")
            if not job_links:  # Check if the list of job links is empty
                source_suggestions_list.append("N/A")
            else:
                print("Source suggestions found.")
                for job_link in job_links:
                    job_link.click()
                    wait.until(EC.visibility_of_element_located((By.ID, "myModal")))
                    print("Modal opened")
                    modal_body = driver.find_element(By.ID, "modal_body")
                    source_suggestions_list.append({"job": job_link.text, "suggestions": modal_body.text})
                    print("Suggestions for ", job_link.text, ":", modal_body.text)
                    # Close the modal
                    close_button = driver.find_element(By.CLASS_NAME, "close")
                    close_button.click()
                    print("Modal closed")
        except NoSuchElementException:
            print("No job links found.")

        try:
            recommendations_element = driver.find_element(By.ID, 'recommendations')
            recommendations_list.append(recommendations_element.text)
            print("Results statement and text: ", recommendations_element.text)
        except Exception as e:
            print("Error retrieving the results:", e)
            recommendations_list.append('N/A')
            source_suggestions_list.append('N/A')
            sources_detected_list.append('N/A')

        try:
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

            if not table_data:
                sources_detected_list.append("N/A")
            else:
                sources_detected_list.append(json.dumps(table_data))
                print("Sources detected: ", sources_detected_list)
        except Exception as e:
            print("Error processing the sources_detected table:", e)
            sources_detected_list.append('N/A')
        
        try:
            reset_button = driver.find_element(By.CSS_SELECTOR, "button#reset-button")
            reset_button.click()
            print("Clicked to reset")
        except Exception as e:
            print("Error clicking the reset button:", e)
            continue  # Move on to the next text

    driver.quit()
    return recommendations_list, source_suggestions_list, sources_detected_list


# ## Putting it all together


def run_scrape_task():
    '''Get links to top 5 news articles from BBC, Mail Online and The Sun homepages,
    scrape their content, run them through EquiQuote and export all of the article data and results as a CSV'''
    
    def sanitise_text(text):
        return ''.join(char if ord(char) <= 0xFFFF else '' for char in text)
    
    def scrape_articles(driver, links, source_name):
        articles_data = []
        text_list = []

        for link in links:
            article_data = {'link': link, 'title': 'N/A', 'byline': 'N/A', 'time': 'N/A', 'text': 'N/A', 'recommendations': 'N/A', 'source_suggestions': 'N/A', 'sources_detected': 'N/A'}
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
                    article_data['text'] = ' '.join(article.text.split()[:1000]) # Take only first 1000 words
                    article_data['text'] = sanitise_text(article_data['text'])
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
        results_sources_suggested = []
        results_sources_detected = []
        
        try:
            # Get results from EquiQuote
            results_recommendations, results_sources_suggested, results_sources_detected = get_equiquote_results(text_list)
            
            # Incorporate the results into articles_data
            for i, data in enumerate(articles_data):
                data['recommendations'] = results_recommendations[i] if i < len(results_recommendations) else 'N/A'
                data['sources_detected'] = results_sources_detected[i] if i < len(results_sources_detected) else 'N/A'
                data['source_suggestions'] = results_sources_suggested[i] if i < len(results_sources_suggested) else 'N/A'
        except Exception as e:
            print("Error getting results from EquiQuote:", e)
            for data in articles_data:
                data['recommendations'] = 'N/A'
                data['sources_detected'] = 'N/A'
                data['source_suggestions'] = 'N/A'

        # Save the articles data to a CSV
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"data/{source_name}_{date_str}.csv"

        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['title', 'byline', 'time', 'link', 'text', 'recommendations', 'source_suggestions', 'sources_detected']
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
        bbc_home = ScrapeBBCHomepage(driver)
        print("BBC links found: ", bbc_home.links)
    except Exception as e:
        print("Error scraping BBC homepage:", e)
        return
    
    try:
        mail_home = ScrapeMailHomepage(driver)
        print("Mail Online links found: ", mail_home.links)
    except Exception as e:
        print("Error scraping Mail Online homepage:", e)
        return
    
    try:
        sun_home = ScrapeSunHomepage(driver)
        print("Sun links found: ", sun_home.links)
    except Exception as e:
        print("Error scraping Sun homepage:", e)
        return
    
    driver.quit()

    def execute_scrape(links, source_name):
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            scrape_articles(driver, links, source_name)
        except Exception as e:
            print(f"Error in scraping articles for {source_name}:", e)
        finally:
            driver.quit()

    execute_scrape(bbc_home.links, "BBC")
    execute_scrape(mail_home.links, "Mail")
    execute_scrape(sun_home.links, "Sun")

    print("All scrape tasks completed")


run_scrape_task()


# Increment the counter after a successful run
increment_counter()

