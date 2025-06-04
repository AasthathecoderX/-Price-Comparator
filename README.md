# 🛒 Price Comparator

Compare product prices across Amazon and Flipkart to find the best deals! This application features a Flask-based web interface for quick, real-time comparisons directly from your browser.

## Table of Contents

* Features
* How it Works
* Project Structure
* Setup and Installation
    * Prerequisites
    * Installation Steps
* Usage
* Configuration



## Features

* **Real-time Price Comparison:** Get current prices for products from Amazon and Flipkart. 💰
* **Product Title Matching:** Uses fuzzy string matching (`fuzzywuzzy`) to compare product titles and assess if they are likely the same item across platforms. 🧩
* **User-Friendly Interface:** Clean and responsive design using Bootstrap 5. ✨
* **Clear Feedback:** Provides flash messages for search status, errors, and comparison outcomes. 💬
* **Direct Links:** Links directly to the product page on Amazon and Flipkart for easy purchasing. 🔗
* **Comprehensive Error Handling:** Robust error handling for scraping failures, timeouts, and JSON decoding issues. ⚠️

## How it Works

The Price Comparator operates in two main parts:

### Web Scraping (Backend):

* When a user enters a product name, the Flask backend executes separate Python scripts (`amazon_scraping.py` and `flipkart_scraping.py`) using `subprocess`. 🐍
* These scripts (which are assumed to use tools like Selenium and a WebDriver) navigate to the respective e-commerce sites, search for the product, extract the title, price, and product URL. 🌐
* The scraped data is returned to the Flask app as a JSON object. 📦

### Flask Application (Web Interface & API Gateway):

* The Flask app receives the scraped data.
* It uses `fuzzywuzzy` to compare the titles from Amazon and Flipkart to determine if they refer to the same product, providing a confidence score. ✅
* Based on the availability of data and the comparison result, it renders either the search form (`index.html`) or the results page (`result.html`), along with appropriate messages. 📊
* *(Future/API Aspect)*: In an API-driven model, this Flask app would instead return JSON data directly to a mobile application. 📲



Here is the full README formatted correctly in Markdown, ready to be pasted into a .md file:
Markdown


### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.8+** 🐍
* **pip** (Python package installer) 📦

### Installation Steps

1.  **Clone the Repository (or create project files):**

    ```bash
    git clone <your-repo-url>
    cd Price_Comp_final
    ```
    (If you don't have a repo, create the `Price_Comp_final` directory and place `app.py`, `amazon_scraping.py`, `flipkart_scraping.py`, and the `static/` and `templates/` folders inside it.)

2.  **Create a Virtual Environment (Recommended):** 🖥️

    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:** 🚀

    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:** ⚙️

    Install all required Python packages. You'll need `Flask`, `fuzzywuzzy`, and whatever libraries your scraping scripts use (e.g., `selenium`, `BeautifulSoup4`, `requests`).
    ```bash
    pip install Flask fuzzywuzzy python-Levenshtein selenium beautifulsoup4 requests
    ```

5.  **Download WebDriver:** 🌐

    Your scraping scripts (`amazon_scraping.py`, `flipkart_scraping.py`) likely use `selenium` which requires a WebDriver (e.g., ChromeDriver for Google Chrome or GeckoDriver for Mozilla Firefox).
    * **ChromeDriver:**
        * Check your Chrome browser version.
        * Download the corresponding ChromeDriver from the [official ChromeDriver website](https://chromedriver.chromium.org/downloads).
    * **GeckoDriver:**
        * Download the GeckoDriver for Firefox from the [Mozilla GitHub releases](https://github.com/mozilla/geckodriver/releases).

    **Place the downloaded WebDriver executable** in a directory that is in your system's `PATH`, or specify its path directly in your `amazon_scraping.py` and `flipkart_scraping.py` scripts (e.g., `webdriver.Chrome(executable_path='/path/to/chromedriver')`).

6.  **Configure Scrapers (Optional but Recommended):** 🛠️

    * Review `amazon_scraping.py` and `flipkart_scraping.py`.
    * Ensure they correctly handle:
        * Headless browser mode (for server deployment).
        * User-Agent headers (to mimic real browser requests).
        * Error handling for CAPTCHAs, dynamic content, or anti-scraping measures.
        * **Crucially, ensure these scripts print only the JSON output to `stdout` as their last action, with any logging going to `stderr`.** This is vital for `app.py` to correctly parse their output.

7.  **Set Flask Secret Key:** 🔑

    In `app.py`, change `app.secret_key = os.urandom(24)` to a more secure, randomly generated key for production environments. For development, `os.urandom(24)` is sufficient.

## Usage

1.  **Start the Flask Application:** 

    Ensure your virtual environment is active.
    ```bash
    python app.py
    ```
    The application will typically run on `http://127.0.0.1:8000/` (or `localhost:8000`).

2.  **Open in Browser:** 

    Navigate to `http://localhost:8000/` in your web browser.

3.  **Enter Product Name:** 

    Type the product you want to compare (e.g., "Apple iPhone 15 Pro", "Daawat Basmati Rice 5kg") into the search bar and click "Search for Prices".

4.  **View Results:** 

    The application will display results from Amazon and Flipkart, indicate which one has a lower price (if comparable), or provide warnings if products are different or data could not be retrieved.

## Configuration

* **`app.py`**:
    * `app.secret_key`: Essential for Flask's session management and security. 
    * `logging.basicConfig`: Configures server-side logging for debugging. 
    * `are_same_product(threshold)`: Adjust the `threshold` for `fuzzywuzzy` to control how strictly product titles are matched (default is 75). 
    * Scraper paths: Ensure `app.root_path` correctly points to where your `amazon_scraping.py` and `flipkart_scraping.py` scripts are located. 

* **`static/style.css`**: Customize the look and feel of the application. 




