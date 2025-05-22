# scraper.py
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
    # initialize all lists
    titles, ratings, discounts, originals, counts, stocks, images, links = [[] for _ in range(8)]
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    pages_scraped = 0

    try:
        driver.get('https://www.amazon.in/')
        driver.maximize_window()
        # set pincode
        wait.until(EC.element_to_be_clickable((By.ID, 'nav-global-location-popover-link'))).click()
        p_in = wait.until(EC.presence_of_element_located((By.ID, 'GLUXZipUpdateInput')))
        p_in.clear(); p_in.send_keys(city_pincode)
        wait.until(EC.element_to_be_clickable((By.ID, 'GLUXZipUpdate'))).click()
        time.sleep(2); driver.refresh(); time.sleep(2)

        # initial search
        sb = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        sb.clear(); sb.send_keys(search_keyword)
        driver.find_element(By.ID, 'nav-search-submit-button').click()

        for page in range(max_pages):
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']")))
            products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

            for prod in products:
                try:
                    # link + image
                    link = prod.find_element(By.XPATH, ".//a[contains(@class,'a-link-normal s-no-outline')]").get_attribute('href')
                    img  = prod.find_element(By.XPATH, ".//img").get_attribute('src')

                    # open detail tab
                    driver.execute_script("window.open(arguments[0])", link)
                    driver.switch_to.window(driver.window_handles[1])
                    wait.until(EC.presence_of_element_located((By.ID, 'productTitle')))

                    # scrape details
                    title = driver.find_element(By.ID, 'productTitle').text.strip()
                    try: rating = driver.find_element(By.XPATH, "//span[@id='acrPopover']").get_attribute('title')
                    except: rating = "N/A"
                    try: discount = driver.find_element(By.XPATH, "//span[contains(@class,'priceToPay')]").text
                    except: discount = "N/A"
                    try: original = driver.find_element(By.XPATH, "//span[@class='a-price a-text-price']").text
                    except: original = "N/A"
                    try:
                        count = driver.find_element(By.ID, 'acrCustomerReviewText').text.split()[0]
                    except:
                        count = "N/A"
                    try:
                        buy = driver.find_element(By.ID, 'buy-now-button')
                        stock = "In Stock" if buy.is_displayed() else "Out of Stock"
                    except:
                        stock = "N/A"

                    # append
                    titles.append(title)
                    ratings.append(rating)
                    discounts.append(discount)
                    originals.append(original)
                    counts.append(count)
                    stocks.append(stock)
                    images.append(img)
                    links.append(link)

                    # close detail tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception:
                    # skip any product that errors
                    driver.switch_to.window(driver.window_handles[0])
                    continue

            pages_scraped += 1
            # next page
            try:
                nb = driver.find_element(By.XPATH, "//a[contains(@class,'s-pagination-next')]")
                driver.execute_script("arguments[0].scrollIntoView()", nb)
                nb.click(); time.sleep(2)
            except:
                break

    finally:
        driver.quit()

    result_df = pd.DataFrame({
        'Title': titles,
        'Rating': ratings,
        'Discount Price': discounts,
        'Original Price': originals,
        'Rating Count': counts,
        'Availability': stocks,
        'Image': images,
        'ProductLink': links
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
