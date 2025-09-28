#!/usr/bin/env python3
"""
MyHome.az Real Estate Scraper
Scrapes all listings from MyHome.az API including both rental and sale announcements
Retrieves phone numbers for each listing and saves data to CSV and Excel formats
"""

import asyncio
import aiohttp
import csv
import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
import zstandard as zstd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MyHomeScraper:
    def __init__(self):
        self.base_url = "https://api.myhome.az/api/announcement"
        self.headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'access-control-allow-origin': '*',
            'authorization': 'Bearer undefined',
            'dnt': '1',
            'origin': 'https://myhome.az',
            'priority': 'u=1, i',
            'referer': 'https://myhome.az/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
        }
        self.session = None
        self.all_listings = []
        self.rate_limit_delay = 0.5  # 500ms delay between requests

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout,
            auto_decompress=False  # Disable auto-decompression since we handle zstd manually
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Fetch data from URL with retry logic"""
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(self.rate_limit_delay)
                async with self.session.get(url) as response:
                    if response.status == 200:
                        # Handle different compression types
                        content_encoding = response.headers.get('content-encoding', '').lower()
                        raw_data = await response.read()

                        # Decompress if needed
                        if content_encoding == 'zstd':
                            try:
                                decompressor = zstd.ZstdDecompressor()
                                decompressed = decompressor.decompress(raw_data, max_output_size=100*1024*1024)  # 100MB max
                                text = decompressed.decode('utf-8')
                                return json.loads(text)
                            except Exception as e:
                                logger.error(f"Failed to decompress zstd data from {url}: {e}")
                                return None
                        elif content_encoding in ['gzip', 'deflate', 'br']:
                            # aiohttp should handle these automatically, but try manual if needed
                            try:
                                text = await response.text()
                                return json.loads(text)
                            except Exception as e:
                                logger.error(f"Failed to decode compressed data from {url}: {e}")
                                return None
                        else:
                            # No compression or unknown compression
                            try:
                                text = raw_data.decode('utf-8')
                                return json.loads(text)
                            except UnicodeDecodeError:
                                # Try different encodings
                                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                                    try:
                                        text = raw_data.decode(encoding)
                                        return json.loads(text)
                                    except (UnicodeDecodeError, json.JSONDecodeError):
                                        continue
                                logger.error(f"Could not decode response from {url}")
                                return None
                            except json.JSONDecodeError as e:
                                logger.error(f"Invalid JSON from {url}: {e}")
                                return None
                    elif response.status == 429:  # Rate limited
                        wait_time = (attempt + 1) * 2
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:
                    return None
                await asyncio.sleep((attempt + 1) * 2)
        return None

    async def get_total_pages(self, announcement_type: int) -> int:
        """Get total number of pages for given announcement type"""
        url = f"{self.base_url}/list?announcementType={announcement_type}&page=1"
        data = await self.fetch_with_retry(url)
        if data and 'meta' in data:
            return data['meta']['last_page']
        return 0

    async def fetch_listings_page(self, announcement_type: int, page: int) -> List[Dict]:
        """Fetch listings for a specific page"""
        url = f"{self.base_url}/list?announcementType={announcement_type}&page={page}"
        data = await self.fetch_with_retry(url)
        if data and 'data' in data:
            return data['data']
        return []

    async def fetch_phone_number(self, listing_id: int) -> str:
        """Fetch phone number for a specific listing"""
        url = f"{self.base_url}/phone/{listing_id}"
        try:
            await asyncio.sleep(self.rate_limit_delay)
            async with self.session.get(url) as response:
                if response.status == 200:
                    # Handle compression for phone responses too
                    content_encoding = response.headers.get('content-encoding', '').lower()
                    raw_data = await response.read()

                    if content_encoding == 'zstd':
                        try:
                            decompressor = zstd.ZstdDecompressor()
                            decompressed = decompressor.decompress(raw_data, max_output_size=10*1024*1024)  # 10MB max for phone
                            phone_data = decompressed.decode('utf-8')
                        except Exception as e:
                            logger.error(f"Failed to decompress phone data for listing {listing_id}: {e}")
                            return ""
                    else:
                        try:
                            phone_data = raw_data.decode('utf-8')
                        except UnicodeDecodeError:
                            # Try different encodings
                            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                                try:
                                    phone_data = raw_data.decode(encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                logger.error(f"Could not decode phone response for listing {listing_id}")
                                return ""

                    # Clean up phone number (remove whitespace, handle multiple numbers)
                    phones = phone_data.strip().split('\n')
                    return ', '.join([phone.strip() for phone in phones if phone.strip()])
                else:
                    logger.warning(f"Failed to get phone for listing {listing_id}: HTTP {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Error fetching phone for listing {listing_id}: {e}")
            return ""

    async def process_listings_batch(self, listings: List[Dict], announcement_type: int) -> List[Dict]:
        """Process a batch of listings and get their phone numbers"""
        processed_listings = []

        # Create semaphore to limit concurrent phone requests
        semaphore = asyncio.Semaphore(5)

        async def process_single_listing(listing):
            async with semaphore:
                phone_number = await self.fetch_phone_number(listing['id'])
                processed_listing = self.extract_listing_data(listing, announcement_type, phone_number)
                return processed_listing

        # Process all listings in the batch concurrently
        tasks = [process_single_listing(listing) for listing in listings]
        processed_listings = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_listings = [listing for listing in processed_listings if not isinstance(listing, Exception)]

        return valid_listings

    def extract_listing_data(self, listing: Dict, announcement_type: int, phone_number: str) -> Dict:
        """Extract and structure relevant data from listing"""
        address_info = listing.get('address', {})
        city = address_info.get('city', {})
        region = address_info.get('region', {})
        village = address_info.get('village', {})

        # Extract metro stations
        metro_stations = listing.get('metro_stations', [])
        metro_names = ', '.join([station.get('name', '') for station in metro_stations])

        return {
            'id': listing.get('id'),
            'title': listing.get('title', ''),
            'description': listing.get('description', ''),
            'price': listing.get('price', ''),
            'announcement_type': 'Rent' if announcement_type == 2 else 'Sale',
            'area': listing.get('area', ''),
            'room_count': listing.get('room_count'),
            'floor_count': listing.get('floor_count'),
            'floor': listing.get('floor'),
            'house_area': listing.get('house_area'),
            'rental_type': listing.get('rental_type'),
            'is_repaired': listing.get('is_repaired'),
            'is_vip': listing.get('is_vip'),
            'is_premium': listing.get('is_premium'),
            'credit_possible': listing.get('credit_possible'),
            'in_credit': listing.get('in_credit'),
            'document_id': listing.get('document_id'),
            'status': listing.get('status'),
            'formatted_date': listing.get('formatted_date', ''),
            'user_id': listing.get('user_id'),
            'phone_number': phone_number,
            'main_image_thumb': listing.get('main_image_thumb', ''),
            'city': city.get('name', '') if city else '',
            'city_lat': city.get('lat', '') if city else '',
            'city_lng': city.get('lng', '') if city else '',
            'region': region.get('name', '') if region else '',
            'region_lat': region.get('lat', '') if region else '',
            'region_lng': region.get('lng', '') if region else '',
            'village': village.get('name', '') if village else '',
            'village_lat': village.get('lat', '') if village else '',
            'village_lng': village.get('lng', '') if village else '',
            'address': address_info.get('address', ''),
            'lat': address_info.get('lat', ''),
            'lng': address_info.get('lng', ''),
            'metro_stations': metro_names,
            'is_favorite': listing.get('is_favorite'),
            'is_price_decreased': listing.get('is_price_decreased'),
        }

    async def scrape_announcement_type(self, announcement_type: int) -> List[Dict]:
        """Scrape all listings for a specific announcement type"""
        type_name = "Rent" if announcement_type == 2 else "Sale"
        logger.info(f"Starting to scrape {type_name} listings...")

        total_pages = await self.get_total_pages(announcement_type)
        if total_pages == 0:
            logger.error(f"Could not get total pages for announcement type {announcement_type}")
            return []

        logger.info(f"Found {total_pages} pages for {type_name} listings")

        all_listings = []
        batch_size = 10  # Process pages in batches

        for batch_start in range(1, total_pages + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, total_pages)
            logger.info(f"Processing pages {batch_start}-{batch_end} of {total_pages} for {type_name}")

            # Fetch pages in the current batch
            page_tasks = []
            for page in range(batch_start, batch_end + 1):
                task = self.fetch_listings_page(announcement_type, page)
                page_tasks.append(task)

            batch_results = await asyncio.gather(*page_tasks, return_exceptions=True)

            # Collect all listings from this batch
            batch_listings = []
            for result in batch_results:
                if not isinstance(result, Exception) and result:
                    batch_listings.extend(result)

            if batch_listings:
                # Process listings to get phone numbers
                processed_listings = await self.process_listings_batch(batch_listings, announcement_type)
                all_listings.extend(processed_listings)
                logger.info(f"Processed {len(processed_listings)} listings from batch {batch_start}-{batch_end}")

            # Small delay between batches
            await asyncio.sleep(1)

        logger.info(f"Completed scraping {len(all_listings)} {type_name} listings")
        return all_listings

    async def scrape_all_listings(self) -> List[Dict]:
        """Scrape all listings from both rental and sale announcements"""
        logger.info("Starting comprehensive scraping of MyHome.az...")

        # Scrape both announcement types concurrently
        tasks = [
            self.scrape_announcement_type(1),  # Sale
            self.scrape_announcement_type(2)   # Rent
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_listings = []
        for result in results:
            if not isinstance(result, Exception):
                all_listings.extend(result)

        self.all_listings = all_listings
        logger.info(f"Total listings scraped: {len(all_listings)}")
        return all_listings

    def save_to_csv(self, filename: str = None):
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"myhome_listings_{timestamp}.csv"

        if not self.all_listings:
            logger.warning("No data to save")
            return

        filepath = Path(filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if self.all_listings:
                fieldnames = self.all_listings[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.all_listings)

        logger.info(f"Data saved to CSV: {filepath}")
        return filepath

    def save_to_excel(self, filename: str = None):
        """Save scraped data to Excel file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"myhome_listings_{timestamp}.xlsx"

        if not self.all_listings:
            logger.warning("No data to save")
            return

        filepath = Path(filename)

        # Create DataFrame
        df = pd.DataFrame(self.all_listings)

        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # All listings
            df.to_excel(writer, sheet_name='All Listings', index=False)

            # Sale listings only
            sale_df = df[df['announcement_type'] == 'Sale']
            if not sale_df.empty:
                sale_df.to_excel(writer, sheet_name='Sale Listings', index=False)

            # Rent listings only
            rent_df = df[df['announcement_type'] == 'Rent']
            if not rent_df.empty:
                rent_df.to_excel(writer, sheet_name='Rent Listings', index=False)

            # Summary statistics
            summary_data = {
                'Metric': ['Total Listings', 'Sale Listings', 'Rent Listings', 'With Phone Numbers'],
                'Count': [
                    len(df),
                    len(sale_df),
                    len(rent_df),
                    len(df[df['phone_number'] != ''])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        logger.info(f"Data saved to Excel: {filepath}")
        return filepath


async def main():
    """Main function to run the scraper"""
    start_time = time.time()

    async with MyHomeScraper() as scraper:
        # Scrape all listings
        listings = await scraper.scrape_all_listings()

        if listings:
            # Save to both CSV and Excel
            csv_file = scraper.save_to_csv()
            excel_file = scraper.save_to_excel()

            # Print summary
            sale_count = len([l for l in listings if l['announcement_type'] == 'Sale'])
            rent_count = len([l for l in listings if l['announcement_type'] == 'Rent'])
            with_phone = len([l for l in listings if l['phone_number']])

            print(f"\n{'='*50}")
            print(f"SCRAPING COMPLETED SUCCESSFULLY")
            print(f"{'='*50}")
            print(f"Total listings scraped: {len(listings)}")
            print(f"Sale listings: {sale_count}")
            print(f"Rent listings: {rent_count}")
            print(f"Listings with phone numbers: {with_phone}")
            print(f"Time taken: {time.time() - start_time:.2f} seconds")
            print(f"CSV file: {csv_file}")
            print(f"Excel file: {excel_file}")
            print(f"{'='*50}")
        else:
            print("No listings were scraped. Please check the logs for errors.")

if __name__ == "__main__":
    asyncio.run(main())