#!/usr/bin/env python3
"""
Debug script to test the API response and understand the encoding issue
"""

import asyncio
import aiohttp
import json

async def debug_api_call():
    headers = {
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

    url = "https://api.myhome.az/api/announcement/list?announcementType=2&page=1"

    async with aiohttp.ClientSession(headers=headers, auto_decompress=True) as session:
        try:
            print(f"Making request to: {url}")
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                print(f"Content-Type: {response.content_type}")
                print(f"Content-Encoding: {response.headers.get('content-encoding', 'None')}")

                # Try different methods to read the response
                print("\n=== Trying response.json() ===")
                try:
                    data = await response.json()
                    print(f"SUCCESS: Got JSON data with {len(data.get('data', []))} listings")
                    return data
                except Exception as e:
                    print(f"FAILED: {e}")

                # Reset response stream
                response._body = None

                print("\n=== Trying response.text() ===")
                try:
                    text = await response.text()
                    print(f"Text length: {len(text)}")
                    print(f"First 200 chars: {text[:200]}")

                    # Try to parse as JSON
                    data = json.loads(text)
                    print(f"SUCCESS: Parsed JSON from text with {len(data.get('data', []))} listings")
                    return data
                except Exception as e:
                    print(f"FAILED: {e}")

                # Reset response stream
                response._body = None

                print("\n=== Trying response.read() with encoding detection ===")
                try:
                    raw_data = await response.read()
                    print(f"Raw data length: {len(raw_data)}")
                    print(f"First 20 bytes: {raw_data[:20]}")

                    # Try different encodings
                    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            text = raw_data.decode(encoding)
                            data = json.loads(text)
                            print(f"SUCCESS with {encoding}: Got JSON data with {len(data.get('data', []))} listings")
                            return data
                        except Exception as e:
                            print(f"FAILED with {encoding}: {e}")

                except Exception as e:
                    print(f"FAILED reading raw data: {e}")

        except Exception as e:
            print(f"Request failed: {e}")

    return None

if __name__ == "__main__":
    result = asyncio.run(debug_api_call())
    if result:
        print(f"\nFinal result: Successfully got {len(result.get('data', []))} listings")
    else:
        print("\nFinal result: Failed to get data")