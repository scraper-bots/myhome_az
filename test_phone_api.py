#!/usr/bin/env python3
"""
Test script to verify phone API calls with correct headers
"""

import asyncio
import aiohttp
import zstandard as zstd

async def test_phone_api():
    """Test phone API with correct headers"""

    # Original headers from your phone API request
    phone_headers = {
        'accept': '*/*',  # Key difference from listings API
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
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

    # Test with a known listing ID (from your original example)
    test_listing_id = 8908

    async with aiohttp.ClientSession(auto_decompress=False) as session:
        url = f"https://api.myhome.az/api/announcement/phone/{test_listing_id}"

        print(f"Testing phone API with listing ID: {test_listing_id}")
        print(f"URL: {url}")
        print("Headers:")
        for key, value in phone_headers.items():
            print(f"  {key}: {value}")

        try:
            async with session.get(url, headers=phone_headers) as response:
                print(f"\nResponse status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")

                if response.status == 200:
                    # Handle compression
                    content_encoding = response.headers.get('content-encoding', '').lower()
                    raw_data = await response.read()

                    print(f"Content-Encoding: {content_encoding}")
                    print(f"Raw data length: {len(raw_data)}")

                    # Decompress if needed
                    if content_encoding == 'zstd':
                        try:
                            decompressor = zstd.ZstdDecompressor()
                            decompressed = decompressor.decompress(raw_data, max_output_size=10*1024*1024)
                            phone_data = decompressed.decode('utf-8')
                        except Exception as e:
                            print(f"Failed to decompress: {e}")
                            return
                    else:
                        try:
                            phone_data = raw_data.decode('utf-8')
                        except UnicodeDecodeError as e:
                            print(f"Failed to decode: {e}")
                            return

                    print(f"Phone number(s): {phone_data}")
                    return phone_data

                elif response.status == 429:
                    print("Rate limited (429)")
                    return None
                else:
                    print(f"Failed with status {response.status}")
                    return None

        except Exception as e:
            print(f"Request failed: {e}")
            return None

if __name__ == "__main__":
    result = asyncio.run(test_phone_api())
    if result:
        print(f"\nSUCCESS: Got phone number: {result.strip()}")
    else:
        print("\nFAILED: Could not get phone number")