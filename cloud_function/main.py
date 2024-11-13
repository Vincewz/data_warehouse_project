from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import time

def get_driver():
    """Configure Chrome WebDriver"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = '/usr/bin/google-chrome'
    
    return webdriver.Chrome(options=options)

def scrape_gpu_data():
    """Scrape GPU data from LDLC website"""
    print("Starting scraping process...")
    driver = None
    data = []
    current_date = datetime.now().date()  # Changé ici pour retourner un objet date

    try:
        driver = get_driver()
        base_url = "https://www.ldlc.com"
        url = f"{base_url}/informatique/pieces-informatique/carte-graphique-interne/c4684/"
        
        print(f"Accessing URL: {url}")
        driver.get(url)
        time.sleep(5)

        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            products = soup.find_all('li', class_='pdt-item')
            
            print(f"Found {len(products)} products on current page")

            for product in products:
                name = product.find('h3', class_='title-3').text.strip()
                info = product.find('p', class_='desc').text.strip()
                price_div = product.find('div', class_='price')
                price = price_div.text.strip() if price_div else "N/A"
                
                try:
                    price_clean = float(price.replace('€', '').replace(',', '.').strip())
                except ValueError:
                    price_clean = None

                data.append({
                    "nom": name,
                    "description": info,
                    "prix": price_clean,
                    "date_scraping": current_date
                })

            next_link = soup.find('li', class_='next')
            if next_link and next_link.find('a'):
                relative_url = next_link.find('a')['href']
                url = base_url + relative_url
                driver.get(url)
                time.sleep(5)
            else:
                break

    finally:
        if driver:
            driver.quit()

    df = pd.DataFrame(data)
    df['date_scraping'] = pd.to_datetime(df['date_scraping']).dt.date  # Conversion explicite en date
    return df

def upload_to_bigquery(df):
    """Upload dataframe to BigQuery"""
    try:
        print(f"Starting upload to BigQuery with {len(df)} rows")
        
        # Nettoyage des données
        df['nom'] = df['nom'].fillna('')
        df['description'] = df['description'].fillna('')
        df['date_scraping'] = df['date_scraping'].fillna(datetime.now().date())
        
        client = bigquery.Client()
        table_id = 'gpu-project-441109.gpu_dataset.graphics_cards'
        
        # Configuration sans spécifier le schéma
        job_config = bigquery.LoadJobConfig(
            write_disposition='WRITE_APPEND'
        )
        
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        result = job.result()
        print(f"Successfully uploaded {len(df)} rows to BigQuery")
        return True
    except Exception as e:
        print(f"Error uploading to BigQuery: {str(e)}")
        print(f"Data sample: {df.head()}")
        raise e

def main(event):
    """Main function logic"""
    try:
        df = scrape_gpu_data()
        if not df.empty:
            upload_to_bigquery(df)
            return ("Success", 200)
        return ("No data scraped", 400)
    except Exception as e:
        print(f"Error: {str(e)}")
        return (str(e), 500)

def hello_pubsub(event, context=None):
    """Cloud Function entry point"""
    return main(event)

if __name__ == "__main__":
    main(None)