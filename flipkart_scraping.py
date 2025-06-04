import logging
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys
import time

logging.basicConfig(level=logging.INFO)

def scrape_flipkart(product_name):
    driver = None
    try:
        options = Options()
        # options.add_argument("--headless") # Uncomment this for production without browser GUI
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36")

        logging.info("Initializing WebDriver for Flipkart...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Always start on the main Flipkart page for consistent behavior
        driver.get("https://www.flipkart.com/")
        logging.info("Navigated to Flipkart.com")

        # Attempt to close login popup
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button._2doB4z"))
            ).click()
            logging.info("Closed login popup.")
        except Exception as e:
            logging.info(f"No login popup found or could not close it: {e}")

        # Search for the product
        logging.info("Attempting to find search box...")
        search_box_selectors = [
            "input._3704LK",
            "input.Pke_EE",
            "input[title='Search for products, brands and more']" # Robust selector by title
        ]
        search_box = None
        for selector in search_box_selectors:
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue

        if not search_box:
            raise Exception("Search box element not found.")

        # Potentially use a more specific query for certain items
        # Example: if user searched "potato", use "fresh potato" for the search query
        # This is a small optimization but filtering is the main solution
        # product_name_for_search = product_name
        # if product_name.lower() == "potato":
        #     product_name_for_search = "fresh potato" # Still might not be enough on its own

        search_box.send_keys(product_name) # Use original product_name
        logging.info(f"Entered '{product_name}' into search box.")

        logging.info("Attempting to find and click search button...")
        search_button_selectors = [
            "button.L0Z3Pu",
            "button[type='submit']",
            "button._2iLDpG",
            "svg._34RNph" # Magnifying glass icon
        ]
        search_button = None
        for selector in search_button_selectors:
            try:
                search_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                search_button.click()
                logging.info(f"Clicked search button using selector: {selector}")
                break
            except Exception as e:
                logging.debug(f"Search button selector '{selector}' failed: {e}")
                continue

        if not search_button:
            logging.info("No explicit search button found, attempting to press ENTER on search box.")
            search_box.send_keys(Keys.ENTER)
            logging.info("Pressed ENTER on search box.")
            time.sleep(2) # Give a little extra time after ENTER

        # --- NEW: Attempt to apply category filter for groceries ---
        grocery_keywords_for_filter = ["potato", "onion", "tomato", "ginger", "garlic", "vegetable", "fruit"] # Add more
        if any(keyword in product_name.lower() for keyword in grocery_keywords_for_filter):
            logging.info(f"'{product_name}' identified as potential grocery item. Attempting to apply 'Vegetables' filter.")
            try:
                # Based on your screenshot, this XPath should be robust
                # Look for the link within the "Fresh Vegetables" category
                # It's an anchor tag with title "Fresh Vegetables" likely under CATEGORIES
                
                # First, ensure the CATEGORIES section is visible if it's collapsible
                # (Not strictly necessary if always expanded, but good practice)
                # category_header = WebDriverWait(driver, 5).until(
                #     EC.presence_of_element_located((By.XPATH, "//div[text()='CATEGORIES']"))
                # )

                # Find the 'Fresh Vegetables' link/element
                # Try by title attribute, or exact text, or specific classes
                fresh_vegetables_filter_selectors = [
                    # This XPath finds an 'a' tag whose 'title' attribute contains 'Fresh Vegetables'
                    "//a[contains(@title, 'Fresh Vegetables')]",
                    # This XPath finds an 'a' tag within a div with class '_1KOcBL' and span text 'Fresh Vegetables'
                    "//div[@class='_1KOcBL']//span[text()='Fresh Vegetables']/ancestor::a",
                    # Direct link class for Fresh Vegetables if it's common
                    "a[href*='/fresh-vegetables/']"
                ]
                
                fresh_vegetables_filter = None
                for selector in fresh_vegetables_filter_selectors:
                    try:
                        # Use XPath or CSS_SELECTOR as appropriate
                        if selector.startswith("//"): # It's an XPath
                            fresh_vegetables_filter = WebDriverWait(driver, 7).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else: # It's a CSS Selector
                            fresh_vegetables_filter = WebDriverWait(driver, 7).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        fresh_vegetables_filter.click()
                        logging.info(f"Clicked 'Fresh Vegetables' filter using selector: {selector}")
                        time.sleep(5) # Wait for results to re-filter
                        break # Filter applied, exit loop
                    except Exception as e:
                        logging.debug(f"Filter selector '{selector}' failed: {e}")
                        continue

                if not fresh_vegetables_filter:
                    logging.warning("Could not find or click 'Fresh Vegetables' filter. Proceeding with unfiltered results.")

            except Exception as e:
                logging.warning(f"Error attempting to apply 'Fresh Vegetables' filter: {e}")

        # --- End NEW filtering logic ---


        # Wait for search results to load (first product card)
        logging.info("Waiting for first product result to appear...")
        product_container_selectors = [
            "div[data-id]",
            "div._1AtVbE",
            "div.slAVV4", # Seen in your onion screenshot for individual product containers
            "div._7UHT_c" # Another common product wrapper
        ]

        found_container = False
        for selector in product_container_selectors:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                found_container = True
                break
            except:
                continue
        
        if not found_container:
            raise Exception("Search results or first product card did not load within timeout.")
        
        logging.info("Search results or first product card loaded.")

        # Find all product containers
        product_containers = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
        if not product_containers: # Also try other main container if data-id doesn't yield
             product_containers = driver.find_elements(By.CSS_SELECTOR, "div._1AtVbE")
        if not product_containers:
            product_containers = driver.find_elements(By.CSS_SELECTOR, "div.slAVV4") # From onion screenshot

        logging.info(f"Found {len(product_containers)} potential product result containers after filtering attempt.")

        output_data = None

        if not product_containers:
            logging.warning("No product containers found on the page after all attempts.")
        else:
            for container in product_containers:
                title = None
                price_str = None
                link = None

                # ---- Title Extraction ----
                title_selectors = [
                    "a.wjcEIp",            # New: Found for 'tomato ketchup' and likely for veggies too
                    "div._4rR01T",        # Common for electronics
                    "a.s1Q9rs",            # Another common product title/link
                    "h1[itemprop='name']", # Generic high-level title
                    "span.B_NuCI",         # Another common title class
                    "div.col.col-7-12 > div:nth-child(1)", # Common for text in product card
                    "a.s1Q9rs"             # Specific for onion link text from your screenshot
                ]
                for selector in title_selectors:
                    try:
                        title_element = container.find_element(By.CSS_SELECTOR, selector)
                        title = title_element.text.strip()
                        if title:
                            # Optional: Add a check here to ensure it's not "chips" if searching for "potato"
                            if product_name.lower() == "potato" and "chips" in title.lower():
                                title = None # Skip this if it's chips and we're looking for potato
                                continue
                            break
                    except:
                        continue

                # ---- Price Extraction ----
                price_selectors = [
                    "div.Nx9bqj",
                    "div.Nx9bqj._4b5DiR",
                    "div._30jeq3._1_WHN1",
                    "div._30jeq3",
                    "span.current-price",
                    "span._8VnyB",
                    "div._30jeq3" # Very common price class
                ]
                for selector in price_selectors:
                    try:
                        price_element = container.find_element(By.CSS_SELECTOR, selector)
                        price_str = price_element.text.replace("₹", "").replace(",", "").strip()
                        if price_str:
                            break
                    except:
                        continue
                
                price = None
                if price_str:
                    try:
                        price = float(price_str)
                    except ValueError:
                        logging.warning(f"Could not convert price string '{price_str}' to float from container {container.get_attribute('data-id')}.")

                # ---- Link Extraction ----
                link_selectors = [
                    "a.wjcEIp",          # New: Found for 'tomato ketchup' and likely for veggies too
                    "a._1fQZEK",        # Common for electronics
                    "a.CGtC98",          # Specific for iPhone 15 link
                    "a.IRpwQq",           # Another general link class
                    "a[rel='noopener noreferrer']" # Generic link that opens in new tab
                ]
                for selector in link_selectors:
                    try:
                        link_element = container.find_element(By.CSS_SELECTOR, selector)
                        link = link_element.get_attribute('href')
                        if link and not link.startswith("http"):
                            link = "https://www.flipkart.com" + link
                        if link:
                            break
                    except:
                        continue

                if title and price is not None and link:
                    output_data = {
                        "title": title,
                        "price": price,
                        "link": link
                    }
                    logging.info(f"Successfully extracted data for: {title}")
                    break

            if output_data:
                print(json.dumps(output_data))
            else:
                logging.warning("No complete product data found after trying all containers.")
                print(json.dumps(None))

    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}", exc_info=True)
        print(json.dumps(None))

    finally:
        if driver:
            driver.quit()
            logging.info("WebDriver closed.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        product_name = sys.argv[1]
        scrape_flipkart(product_name)
    else:
        logging.error("Please provide a product name as an argument.")
        print(json.dumps(None))