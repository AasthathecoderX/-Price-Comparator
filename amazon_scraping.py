import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Chrome options
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--headless") # Keep headless commented out for now for debugging!
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/555.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/555.36")

# Get product name from command-line argument
if len(sys.argv) > 1:
    product_name = sys.argv[1]
else:
    product_name = "potato"
    logging.info(f"No product name provided, defaulting to '{product_name}'")

# Initialize driver
driver = None
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    grocery_keywords_for_direct_nav = ["potato", "onion", "tomato", "ginger", "garlic", "vegetable", "fruit", "milk", "bread", "rice", "dal", "sugar", "salt", "flour", "atta", "oil", "ghee"]
    
    if any(keyword in product_name.lower() for keyword in grocery_keywords_for_direct_nav):
        logging.info(f"'{product_name}' identified as a potential grocery item. Attempting direct navigation to Amazon Fresh.")
        amazon_fresh_url = "https://www.amazon.in/fresh?ref_=nav_cs_fresh"
        driver.get(amazon_fresh_url)
        logging.info(f"Navigated to Amazon Fresh: {amazon_fresh_url}")
        
        # --- Handle potential full-page modal/overlay first ---
        try:
            logging.info("Attempting to dismiss any full-page modal/overlay...")
            
            close_button_selectors = [
                "button[data-action='a-popover-close']", 
                ".a-icon.a-icon-close-small", 
                "input[data-action='a-popover-close']", 
                "#attach-close_decorate",
                "span.a-button-inner button.a-button-close"
            ]
            
            modal_closed = False
            for selector in close_button_selectors:
                try:
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    close_button.click()
                    logging.info(f"Successfully clicked modal close button with selector: {selector}")
                    modal_closed = True
                    time.sleep(1) # Small sleep after click
                    break 
                except:
                    logging.debug(f"Modal close button with selector '{selector}' not found or not clickable.")
            
            if not modal_closed:
                logging.info("No common close button found or clickable. Trying ESC key.")
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                logging.info("Sent ESC key to dismiss potential pop-up.")
                time.sleep(1) # Small sleep after ESC

            WebDriverWait(driver, 10).until_not(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.a-modal-scroller, div.a-popover-modal-header, #a-popover-content")) 
            )
            logging.info("Waited for potential full-page modal/overlay to disappear.")

        except Exception as e_modal_dismiss:
            logging.info(f"No full-page modal/overlay found or successfully dismissed, proceeding. ({e_modal_dismiss})")
            

       
        try:
            glow_ingress_block = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "glow-ingress-block")) 
            )
            glow_ingress_block.click()
            logging.info("Clicked on location block after modal dismissal (if it appeared).")

            try:
                confirm_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-action='GLUXConfirmClose'] input[type='submit'], #GLUXConfirmClose, #GLUXZipUpdateLink, #GLUXConfirmClose.a-button-primary"))
                )
                confirm_button.click()
                logging.info("Clicked 'Confirm' or 'Update' button in location modal (after glow-ingress-block click).")
                time.sleep(1)
            except Exception as e_confirm:
                logging.info(f"No explicit confirmation button found or clickable in location modal after glow-ingress-block click, proceeding. ({e_confirm})")

            WebDriverWait(driver, 5).until_not(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.a-popover-modal-header, #a-popover-content"))
            )
            logging.info("Waited for potential smaller location modal to disappear.")

        except Exception as e_location_block:
            logging.info(f"Location block not found or interactable after initial modal dismissal, or no further action needed. ({e_location_block})")


        # --- Enhanced Search Box Interaction ---
        logging.info("Attempting to interact with the search box.")
        search_box = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "twotabsearchtextbox"))
        )
       
        search_box.click()
        logging.info("Clicked the search box.")
        
        
        time.sleep(0.5) 

        
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "twotabsearchtextbox"))
        )
        
        

        search_box.send_keys(product_name)
        logging.info(f"Typed '{product_name}' into search box.")
        search_box.submit()
        logging.info(f"Submitted search for '{product_name}' within Amazon Fresh.")

    else:
       
        driver.get("https://www.amazon.in/")
        logging.info("Navigated to Amazon.in (main page).")
        
        
        try:
            logging.info("Attempting to dismiss any full-page modal/overlay on main page...")
            close_button_selectors = [
                "button[data-action='a-popover-close']", 
                ".a-icon.a-icon-close-small", 
                "input[data-action='a-popover-close']", 
                "#attach-close_decorate",
                "span.a-button-inner button.a-button-close"
            ]
            modal_closed = False
            for selector in close_button_selectors:
                try:
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    close_button.click()
                    logging.info(f"Successfully clicked modal close button with selector: {selector} on main page.")
                    modal_closed = True
                    time.sleep(1)
                    break
                except:
                    logging.debug(f"Modal close button with selector '{selector}' not found or not clickable on main page.")
            
            if not modal_closed:
                logging.info("No common close button found or clickable on main page. Trying ESC key.")
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                logging.info("Sent ESC key to dismiss potential pop-up on main page.")
                time.sleep(1)

            WebDriverWait(driver, 10).until_not(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.a-modal-scroller, div.a-popover-modal-header, #a-popover-content")) 
            )
            logging.info("Waited for potential full-page modal/overlay to disappear on main page.")
        except Exception as e_modal_dismiss_main:
            logging.info(f"No full-page modal/overlay found or successfully dismissed on main page, proceeding. ({e_modal_dismiss_main})")


        # --- Enhanced Search Box Interaction for main page ---
        logging.info("Attempting to interact with the search box on main page.")
        search_box = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.click() # Explicitly click
        logging.info("Clicked the search box on main page.")
        time.sleep(0.5) # Short delay
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "twotabsearchtextbox"))
        )
        search_box.send_keys(product_name)
        logging.info(f"Typed '{product_name}' into search box on main page.")
        search_box.submit()
        logging.info(f"Submitted search for '{product_name}' on main Amazon page.")

    # Wait for search results to load (consistent for both paths)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-result-list.s-search-results"))
    )
    logging.info("Search results page loaded.")

    output_data = None

    results = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
    logging.info(f"Found {len(results)} potential product result containers.")

    if results:
        for i, result_element in enumerate(results):
            logging.debug(f"Attempting to extract data from product result {i+1}")
            try:
                title_span_element = result_element.find_element(By.CSS_SELECTOR, "h2 span")
                title = title_span_element.text.strip()
                logging.debug(f"Found title: {title}")

                if product_name.lower() == "potato" and "chips" in title.lower():
                    logging.debug(f"Skipping '{title}' as it contains 'chips' for 'potato' search.")
                    continue

                link_element = result_element.find_element(By.CSS_SELECTOR, "a.a-link-normal.s-underline-text, a.a-link-normal.s-no-outline")
                link = link_element.get_attribute("href")
                logging.debug(f"Found link: {link}")

                price_whole = ""
                price_fraction = ""
                
                try:
                    price_whole_element = result_element.find_element(By.CSS_SELECTOR, "span.a-price-whole")
                    price_whole = price_whole_element.text.replace(",", "").strip()
                    logging.debug(f"Found price whole: {price_whole}")
                except Exception as e_whole:
                    logging.debug(f"Price whole not found for title '{title}': {e_whole}")
                    pass 

                try:
                    price_fraction_element = result_element.find_element(By.CSS_SELECTOR, "span.a-price-fraction")
                    price_fraction = price_fraction_element.text.strip()
                    logging.debug(f"Found price fraction: {price_fraction}")
                except Exception as e_fraction:
                    logging.debug(f"Price fraction not found for title '{title}': {e_fraction}")
                    pass

                price = None
                if price_whole:
                    price_str = price_whole
                    if price_fraction:
                        price_str += f".{price_fraction}"
                    try:
                        price = float(price_str)
                        logging.debug(f"Parsed price: {price}")
                    except ValueError:
                        logging.warning(f"Could not convert price string '{price_str}' to float for title: {title}")
                        price = None
                
                if title and link and price is not None:
                    output_data = {"title": title, "price": price, "link": link}
                    logging.info(f"Successfully extracted data for: {title}")
                    break
                else:
                    logging.debug(f"Skipping product {i+1} due to missing data: Title='{title}', Price='{price}', Link='{link}'")

            except Exception as e:
                logging.debug(f"Failed to extract all details from product result {i+1} (possibly sponsored or different layout): {e}")

        if output_data:
            print(json.dumps(output_data))
        else:
            logging.warning("No complete product data found after trying all results with current selectors.")
            print(json.dumps(None))
    else:
        logging.warning("No search results found at all with the main product container selector: div[data-component-type='s-search-result']")
        print(json.dumps(None))

except Exception as e:
    logging.error(f"An unexpected error occurred during scraping: {e}", exc_info=True)
    print(json.dumps(None))

finally:
    if 'driver' in locals() and driver:
        driver.quit()
        logging.info("WebDriver closed.")