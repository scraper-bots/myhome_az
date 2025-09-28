#!/usr/bin/env python3
"""
Quick test of phone functionality with updated headers
"""

import asyncio
from myhome_scraper import MyHomeScraper

async def test_phone_with_updated_headers():
    """Test phone functionality with corrected headers"""

    async with MyHomeScraper() as scraper:
        # Test a few listings from the first page
        print("Fetching first page of listings...")
        listings = await scraper.fetch_listings_page(2, 1)  # Rent listings

        if not listings:
            print("Failed to get listings")
            return

        print(f"Got {len(listings)} listings, testing phone retrieval for first 3...")

        # Test phone numbers for first 3 listings
        for i, listing in enumerate(listings[:3]):
            listing_id = listing['id']
            title = listing.get('title', 'No title')[:50]

            print(f"\nTesting listing {i+1}:")
            print(f"  ID: {listing_id}")
            print(f"  Title: {title}...")

            phone = await scraper.fetch_phone_number(listing_id)
            if phone:
                print(f"  ✅ Phone: {phone}")
            else:
                print(f"  ❌ No phone retrieved")

        print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_phone_with_updated_headers())