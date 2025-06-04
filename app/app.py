from flask import Flask, render_template, request, flash, redirect
import subprocess
import os
import logging
import json
from fuzzywuzzy import fuzz
import sys
from selenium import webdriver

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# Configure logging
logging.basicConfig(level=logging.INFO)

def are_same_product(title1, title2, threshold=80):
    """Uses fuzzy matching to determine if two product titles are likely the same."""
    if not title1 or not title2:
        return False
    similarity_score = fuzz.ratio(title1.lower(), title2.lower())
    return similarity_score >= threshold

@app.route('/', methods=['GET', 'POST'])
def search_product():
    if request.method == 'POST':
        searched_product = request.form.get('sproduct')

        if not searched_product:
            flash("Please enter a product to search.", "error")
            return render_template('home.html')

        try:
            # Run Amazon scraper
            amazon_data = scrape_amazon(searched_product)

            # Run Flipkart scraper
            flipkart_data = scrape_flipkart(searched_product)

            if amazon_data and flipkart_data:
                amazon_title = amazon_data.get('title', '')
                flipkart_title = flipkart_data.get('title', '')

                if are_same_product(amazon_title, flipkart_title):
                    amazon_price = amazon_data.get('price')
                    flipkart_price = flipkart_data.get('price')
                    amazon_link = amazon_data.get('link')
                    flipkart_link = flipkart_data.get('link')

                    if amazon_price is not None and flipkart_price is not None and amazon_link and flipkart_link:
                        if amazon_price < flipkart_price:
                            flash(f"Amazon has the lower price: ₹{amazon_price}", "success")
                            return redirect(amazon_link)  # Redirect to Amazon
                        elif flipkart_price < amazon_price:
                            flash(f"Flipkart has the lower price: ₹{flipkart_price}", "success")
                            return redirect(flipkart_link)  # Redirect to Flipkart
                        else:
                            flash(f"Prices are the same: Amazon - ₹{amazon_price}, Flipkart - ₹{flipkart_price}", "info")
                            return render_template('results.html', amazon=amazon_data, flipkart=flipkart_data) # Show both
                    else:
                        flash("Could not retrieve price or link from both websites.", "error")
                        return render_template('results.html', amazon=amazon_data, flipkart=flipkart_data) # Show available data
                else:
                    flash("Could not confidently compare prices as the products seem different.", "warning")
                    return render_template('results.html', amazon=amazon_data, flipkart=flipkart_data) # Show available data

            else:
                flash("Could not retrieve product data from both websites.", "error")
                return render_template('results.html', amazon=amazon_data, flipkart=flipkart_data) # Show available data

        except Exception as e:
            logging.error(f"Error comparing prices: {e}")
            flash("An error occurred while comparing prices.", "error")

    return render_template('home.html')


def scrape_amazon(product_name):
    try:
        base_dir = r"C:\Users\Aastha\Desktop\Price_Comp_final"
        amazon_script_path = os.path.join(base_dir, "amazon_scraping.py")
        # Use sys.executable to ensure the virtual environment's python is used
        amazon_command = [sys.executable, amazon_script_path, product_name]
        result_str = subprocess.check_output(amazon_command, text=True, stderr=subprocess.PIPE).strip()
        logging.info(f"Amazon scraper raw result: {result_str}")
        if result_str == "null":
            return None
        result = json.loads(result_str)
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running Amazon scraper: {e.output} {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from Amazon scraper: {e}, Raw Output: '{result_str}'")
        return None
    except FileNotFoundError:
        logging.error(f"Amazon scraping script not found at {amazon_script_path}. Please check the path.")
        return None
    except Exception as e:
        logging.error(f"General error in scrape_amazon: {e}", exc_info=True)
        return None


# In app.py
def scrape_flipkart(product_name):
    try:
        base_dir = r"C:\Users\Aastha\Desktop\Price_Comp_final"
        flipkart_script_path = os.path.join(base_dir, "flipkart_scraping.py")
        
        # Capture stdout and stderr
        process = subprocess.run(
            [sys.executable, flipkart_script_path, product_name],
            capture_output=True, # Use capture_output for Python 3.7+
            text=True,
            check=False # Do not raise CalledProcessError immediately
        )
        
        result_str = process.stdout.strip()
        error_output = process.stderr.strip()

        logging.info(f"Flipkart scraper raw stdout: {result_str}")
        if error_output:
            logging.error(f"Flipkart scraper raw stderr: {error_output}")
        
        if process.returncode != 0:
            logging.error(f"Flipkart scraper exited with non-zero code {process.returncode}")
            return None

        if result_str == "null":
            return None
        
        result = json.loads(result_str)
        return result
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from Flipkart scraper: {e}, Raw Output: '{result_str}'")
        return None
    except FileNotFoundError:
        logging.error(f"Flipkart scraping script not found at {flipkart_script_path}. Please check the path.")
        return None
    except Exception as e:
        logging.error(f"General error in scrape_flipkart: {e}", exc_info=True)
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)