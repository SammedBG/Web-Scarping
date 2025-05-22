from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # run without UI
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--log-level=3")  # optional: suppress logs
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

def scrape_amazon(search_keyword, city_pincode, max_pages=1):
    titles, ratings, discount_prices, original_prices, rating_counts, availabilities = ([] for _ in range(6))
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    pages_scraped = 0

    try:
        driver.get('https://www.amazon.in/')
        driver.maximize_window()

        location_btn = wait.until(EC.element_to_be_clickable((By.ID, 'nav-global-location-popover-link')))
        location_btn.click()

        pincode_input = wait.until(EC.presence_of_element_located((By.ID, 'GLUXZipUpdateInput')))
        pincode_input.clear()
        pincode_input.send_keys(city_pincode)

        apply_btn = wait.until(EC.element_to_be_clickable((By.ID, 'GLUXZipUpdate')))
        apply_btn.click()
        time.sleep(3)
        driver.refresh()
        time.sleep(2)

        search_box = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        search_box.clear()
        search_box.send_keys(search_keyword)
        driver.find_element(By.ID, 'nav-search-submit-button').click()

        for page in range(max_pages):
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']")))
            Products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

            for product in Products:
                try:
                    link = product.find_element(By.XPATH, ".//a[contains(@class,'a-link-normal s-no-outline')]").get_attribute('href')
                    driver.execute_script("window.open(arguments[0])", link)
                    driver.switch_to.window(driver.window_handles[1])

                    wait.until(EC.presence_of_element_located((By.ID, 'productTitle')))

                    try: title = driver.find_element(By.ID, 'productTitle').text
                    except: title = "N/A"

                    try: rating = driver.find_element(By.XPATH, "//span[@id='acrPopover']").get_attribute("title")
                    except: rating = "N/A"

                    try: discount_price = driver.find_element(By.XPATH, "//span[contains(@class,'priceToPay')]").text
                    except: discount_price = "N/A"

                    try: original_price = driver.find_element(By.XPATH, "//span[@class='a-price a-text-price']").text
                    except: original_price = "N/A"

                    try:
                        rating_count = driver.find_element(By.XPATH,".//span[@id='acrCustomerReviewText']").text.split()[0]
                    except: rating_count = "N/A"

                    try:
                        availability = driver.find_element(By.ID, "buy-now-button")
                        availability = "In Stock" if availability.is_displayed() else "Out of Stock"
                    except:
                        availability = "N/A"

                    titles.append(title)
                    ratings.append(rating)
                    discount_prices.append(discount_price)
                    original_prices.append(original_price)
                    rating_counts.append(rating_count)
                    availabilities.append(availability)

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    continue

            pages_scraped += 1

            try:
                next_btn = driver.find_element(By.XPATH, "//a[contains(@class,'s-pagination-next')]")
                driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                next_btn.click()
                time.sleep(3)
            except:
                break

    finally:
        driver.quit()

    result_df = pd.DataFrame({
        'Title': titles,
        'Rating': ratings,
        'Discount Price': discount_prices,
        'Original Price': original_prices,
        'Rating Count': rating_counts,
        'Availability': availabilities
    })

    download_dir = os.path.join(os.getcwd(), "backend", "downloads")
    os.makedirs(download_dir, exist_ok=True)

    file_name = f"output_{search_keyword}_{city_pincode}.xlsx"
    file_path = os.path.join(download_dir, file_name)

    result_df.to_excel(file_path, index=False)

    return {
        "pages_scraped": pages_scraped,
        "total_products": len(result_df),
        "file_name": file_name,
        "data": result_df.to_dict(orient="records")
    }

