# EquiQuote Scraper

This code scrapes the links of the top 5 online stories from the Daily Mail, BBC, and The Sun homepages. It scrapes each story for its title, timestamp, byline, and article text. It then runs the article text through [EquiQuote](https://github.com/mawrxyz/source-gender-tool/), my tool to detect the gender of news sources and scrapes the results generated. Finally, it exports a CSV with the article data as well as results from EquiQuote.

This script is meant to help test the quality of results from EquiQuote, my 2023 dissertation project for my Master of Science in Computational and Data Journalism at Cardiff University. The three news outlets chosen were identified as the [top 3 news brands](https://pressgazette.co.uk/media-audience-and-business-data/media_metrics/most-popular-websites-news-uk-monthly-2/) in the UK by the Press Gazette in July 2023.

## Set Up

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

5. **Run the scraper:**

    ```bash
    python scraper.py
    ```

After running the scraper, you will find the scraped data in the `data` folder. The scraper increments the counter in `counter.txt` every time it runs and will stop after running five times. To reset it, replace the contents of `counter.txt` with "0".

## (Optional) Scheduling the Scraper

Cron is a time-based job scheduler in Unix-like operating systems. You can use it to schedule the scraper to run at specific intervals, such as daily or weekly.

1. **Open your crontab file for editing:**

   ```bash
   crontab -e
   ```

2. **Add a new cron job:**

In the editor, add a new line with the following format:

   ```bash
   0 * * * * cd /path/to/equiquote-scraper && /path/to/venv/bin/python /path/to/equiquote-scraper/scraper.py >> /path/to/equiquote-scraper/cron.log 2>&1
   ```

Replace /path/to/python, /path/to/scraper.py, and /path/to/cron.log with the appropriate paths. The >> redirects the standard output and the 2>&1 redirects the standard error to the specified log file.

In this example, the scraper will run every hour at minute 0. Adjust the cron schedule expression as needed.

3. **Save and exit the editor:**

After adding the cron job, save the changes and exit the text editor. The scraper should now run automatically at the specified intervals and log the output and any errors to `cron.log`. You can view the scheduled tasks by typing: 

   ```bash
   crontab -l
   ```

**Note for vi and vim users:** If your default editor is vi or vim, you'll need to enter "insert mode" before you can begin typing in the file. To do this, press the i key. You can then start editing the file. When you're done editing, press the Esc key to exit insert mode. To save your changes and exit the editor, type :wq and press Enter. If you want to exit without saving changes, type :q! and press Enter.

## Licence
This project is licensed under the terms of the license provided in the `LICENSE.txt` file.