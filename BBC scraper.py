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


class ScrapeBBCHomepage: 
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
            if full_url.startswith("https://www.bbc.co.uk/news") and full_url not in unique_urls:
                unique_urls.add(full_url)
                top_5_urls.append(full_url)

            if len(top_5_urls) == 5:
                break

        return top_5_urls

class BBCArticleContent: 
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
        return "\n\n".join([p.text for p in paragraphs if 'ssrcss-xbdn93-ItalicText.e5tfeyi2' not in p.get_attribute('class')])
    
    def get_title(self) -> str: 
        return self.driver.find_element(By.CSS_SELECTOR, "h1#main-heading").text
    
    def get_byline(self) -> str: 
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "div.ssrcss-68pt20-Text-TextContributorName").text
        except NoSuchElementException: 
            return ""


def get_equiquote_results(text_list):
    
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
        print("Error initializing webdriver:", e)
        return

    try:
        driver.get("http://localhost:5000")
    except Exception as e:
        print("Error loading app:", e)
        return []

    wait = WebDriverWait(driver, 150)
    
    results = []

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
            results_element = driver.find_element(By.CSS_SELECTOR, "div#results_container")
            results.append(results_element.text)
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
    return results


def run_scrape_task():
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print("Error initializing webdriver:", e)
        return

    try:
        bbc_home = ScrapeBBCHomepage(driver)
    except Exception as e:
        print("Error scraping BBC homepage:", e)
        driver.quit()
        return

    articles_data = []
    text_list = []

    for link in bbc_home.links:
        try:
            article = BBCArticleContent(driver, link)
            article_data = {
                'title': article.title,
                'byline': article.byline,
                'time': article.time,
                'text': article.text
            }
            print(f"Article data found: {article_data}")
            articles_data.append(article_data)
            trimmed_text = ' '.join(article.text.split()[:1000])
            text_list.append(trimmed_text)
        except Exception as e:
            print(f"Error processing article link {link}:", e)

    driver.quit()

    results = []
    try:
        # Get results from EquiQuote
        results = get_equiquote_results(text_list)
        
        # Incorporate the results into articles_data
        for i, data in enumerate(articles_data):
            data['results'] = results[i] if i < len(results) else 'N/A'
    except Exception as e:
        print("Error getting results from EquiQuote:", e)
        for data in articles_data:
            data['results'] = 'N/A'

    # Save the articles data to a CSV
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"BBC_{date_str}.csv"

    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['title', 'byline', 'time', 'text', 'results']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in articles_data:
                writer.writerow(data)
    except Exception as e:
        print("Error writing to CSV:", e)
        return

    print(f"Data exported to {filename}")


run_scrape_task()
