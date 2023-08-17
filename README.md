# EquiQuote Scraper

This code scrapes the links of the top 5 online stories from the Daily Mail, BBC, and The Sun homepages. It scrapes each story for its title, timestamp, byline, and article text. It then runs the article text through [EquiQuote](https://github.com/mawrxyz/source-gender-tool/), my tool to detect the gender of news sources and scrapes the results generated. Finally, it exports a CSV with the article data as well as results from EquiQuote.

This script is meant to help test the quality of results from EquiQuote, my 2023 dissertation project for my Master of Science in Computational and Data Journalism at Cardiff University. The three news outlets chosen were identified as the [top 3 news brands](https://pressgazette.co.uk/media-audience-and-business-data/media_metrics/most-popular-websites-news-uk-monthly-2/) in the UK by the Press Gazette in July 2023.

## Setup

1. **Clone this repository:**
   ```bash
   git clone https://gitfront.io/r/user-7653615/hHok8ubE1FTX/equiquote-scraper.git
   cd equiquote-scraper
   ```
2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Download the appropriate version of [ChromeDriver](https://chromedriver.chromium.org/home) for your system and place it in your PATH or specify its location in your code.**

## Running the scraper

1. **Make sure you are in the project directory and your virtual environment is activated:**

    ```bash
    cd your_repository
    source venv/bin/activate
    ```
2. **Run the scraper:**

    ```bash
    python scraper.py
    ```
3. **After running the scraper, you will find the scraped data in the `data` folder. The scraper increments the counter in `counter.txt` every time it runs and will stop after running five times. To reset it, replace the contents of `counter.txt` with "0".**

## (Optional) Scheduling the Scraper

Cron is a time-based job scheduler in Unix-like operating systems. You can use it to schedule the scraper to run at specific intervals, such as daily or weekly.

1. **Open your crontab file for editing:**

   ```bash
   crontab -e
   ```
This command opens the crontab file for the current user in the default text editor.

2. **Add a new line to schedule the scraper, specifying the desired frequency and directing the output to `cron.log`:**

In the editor, add a new line with the following format:

    ```bash
   0 * * * * cd /path/to/equiquote-scraper && /path/to/venv/bin/python /path/to/equiquote-scraper/scraper.py >> /path/to/equiquote-scraper/cron.log 2>&1
   ```

Replace /path/to/python, /path/to/scraper.py, and /path/to/cron.log with the appropriate paths. The >> redirects the standard output and the 2>&1 redirects the standard error to the specified log file.

In this example, the scraper will run every hour at minute 0. Adjust the cron schedule expression as needed.

3. **Save and exit the crontab editor. The scraper will now run automatically at the specified intervals and log the output and any errors to cron.log.**

## Licence
This project is licensed under the terms of the license provided in the `LICENSE.txt` file.