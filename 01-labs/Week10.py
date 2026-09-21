
get_ipython().system('pip install pandas requests beautifulsoup4')

import time
from bs4 import BeautifulSoup
import pandas as pd
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Educational purpose scraper - ISYS5002)',
    'Accept': 'text/html,application/xhtml+xml',
}

print("Setup complete!")


# In[7]:


# Cell 2: Download the Web Page
url = 'http://books.toscrape.com/'

# Send HTTP GET request
response = requests.get(url, headers=headers)

# Check if request was successful
if response.status_code == 200:
  print(
      f"Successfully downloaded the page! Content length:"
      f" {len(response.text)} characters"
  )
else:
  print(f"Failed to download the page. Status code: {response.status_code}")

# View first 300 characters of raw HTML
print("\nHTML Preview:")
print(response.text[:300])


# In[8]:


# Cell 3: Parse HTML with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Extract and print the page title
page_title = soup.title.text
print(f"Page title: {page_title}")


# In[9]:


# Cell 4: Extract Book Information
book_containers = soup.find_all('article', class_='product_pod')
print(f"Found {len(book_containers)} books on this page.")

titles = []
prices = []
ratings = []

for book in book_containers:
    # Extract title
    title = book.h3.a['title']
    titles.append(title)

    # Extract price
    price = book.find('p', class_='price_color').text
    prices.append(price)

    # Extract star rating
    star_rating = book.find('p', class_='star-rating')['class'][1]
    ratings.append(star_rating)

# Assemble initial DataFrame
books_df = pd.DataFrame({
    'Title': titles,
    'Price': prices,
    'Rating': ratings
})

# Display first 5 rows
books_df.head()


# In[10]:


# Cell 5: Clean and Process Data

# Clean price: remove currency characters and convert to float
books_df['Price'] = (
    books_df['Price'].str.replace('Â', '').str.replace('£', '').astype(float)
)

# Map string ratings to numeric values (1 to 5)
rating_mapping = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5,
}
books_df['Rating'] = books_df['Rating'].map(rating_mapping)

# Display cleaned DataFrame preview
print("Cleaned Data Preview:")
display(books_df.head())

# Basic summary statistics
print("\nBasic Statistics:")
display(books_df.describe())

# Calculate average price grouped by rating
print("\nAverage Price by Rating:")
avg_price_by_rating = books_df.groupby('Rating')['Price'].mean().sort_index()
display(avg_price_by_rating)


# In[11]:


# Cell 6: Scrape Multiple Pages (Pages 1 to 3)

all_titles = []
all_prices = []
all_ratings = []

# Loop through pages 1, 2, and 3
for page_num in range(1, 4):
  if page_num == 1:
    page_url = 'http://books.toscrape.com/'
  else:
    page_url = f'http://books.toscrape.com/catalogue/page-{page_num}.html'

  # Add a 1-second delay for polite scraping
  time.sleep(1)

  resp = requests.get(page_url, headers=headers)

  if resp.status_code == 200:
    print(f"Successfully scraped page {page_num}")
    p_soup = BeautifulSoup(resp.text, 'html.parser')
    containers = p_soup.find_all('article', class_='product_pod')

    for book in containers:
      all_titles.append(book.h3.a['title'])
      all_prices.append(book.find('p', class_='price_color').text)
      all_ratings.append(book.find('p', class_='star-rating')['class'][1])
  else:
    print(f"Failed to scrape page {page_num}")

# Assemble multi-page DataFrame
all_books_df = pd.DataFrame({
    'Title': all_titles,
    'Price': all_prices,
    'Rating': all_ratings,
})

# Clean multi-page dataset
all_books_df['Price'] = (
    all_books_df['Price']
    .str.replace('Â', '')
    .str.replace('£', '')
    .astype(float)
)
all_books_df['Rating'] = all_books_df['Rating'].map(rating_mapping)

print(f"\nTotal books scraped across 3 pages: {len(all_books_df)}")
display(all_books_df.head(10))


# In[12]:


# Cell 7: Save Scraped Data to CSV File
all_books_df.to_csv('scraped_books.csv', index=False)
print("Data successfully saved to 'scraped_books.csv' in your workspace!")

