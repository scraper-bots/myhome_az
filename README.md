# MyHome.az Real Estate Scraper

A comprehensive Python scraper for MyHome.az that extracts all real estate listings including both rental and sale announcements, retrieves phone numbers, and exports data to CSV and Excel formats.

## Features

- **Complete Data Extraction**: Scrapes all listings from both rental (announcementType=2) and sale (announcementType=1) categories
- **Phone Number Retrieval**: Gets contact phone numbers for each listing
- **Async Implementation**: Uses asyncio and aiohttp for efficient concurrent scraping
- **Rate Limiting**: Built-in delays to respect server resources
- **Error Handling**: Robust retry logic and exception handling
- **Multiple Export Formats**: Saves data to both CSV and Excel files
- **Detailed Logging**: Comprehensive logging for monitoring progress
- **Data Organization**: Excel export includes separate sheets for sales, rentals, and summary statistics

## Installation

1. Clone or download the scraper files
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper to get all listings:

```bash
python myhome_scraper.py
```

### What the Scraper Does

1. **Fetches Total Pages**: Determines how many pages exist for each announcement type
2. **Scrapes Listings**: Retrieves all listing data from all pages
3. **Gets Phone Numbers**: Fetches contact phone numbers for each listing
4. **Processes Data**: Extracts and structures all relevant information
5. **Exports Data**: Saves results to timestamped CSV and Excel files

## Data Fields Extracted

### Basic Information
- `id`: Unique listing identifier
- `title`: Listing title
- `description`: Full description
- `price`: Listed price
- `announcement_type`: "Rent" or "Sale"

### Property Details
- `area`: Property area in sotkas
- `room_count`: Number of rooms
- `floor_count`: Total floors in building
- `floor`: Floor number
- `house_area`: House area in square meters
- `rental_type`: Type of rental
- `is_repaired`: Repair status
- `document_id`: Document type

### Location Information
- `city`: City name, latitude, longitude
- `region`: Region name, latitude, longitude
- `village`: Village name, latitude, longitude
- `address`: Street address
- `lat`, `lng`: Exact coordinates
- `metro_stations`: Nearby metro stations

### Contact & Additional Info
- `phone_number`: Contact phone number(s)
- `user_id`: Listing owner ID
- `formatted_date`: Publication date
- `main_image_thumb`: Thumbnail image URL
- `is_vip`, `is_premium`: Premium listing flags
- `credit_possible`, `in_credit`: Credit options
- `is_price_decreased`: Price reduction flag

## Output Files

The scraper generates timestamped files:

### CSV Output
- `myhome_listings_YYYYMMDD_HHMMSS.csv`: Single file with all listings

### Excel Output
- `myhome_listings_YYYYMMDD_HHMMSS.xlsx`: Multi-sheet workbook containing:
  - **All Listings**: Complete dataset
  - **Sale Listings**: Sale announcements only
  - **Rent Listings**: Rental announcements only
  - **Summary**: Statistics and counts

## Performance

- **Rate Limiting**: 500ms delay between requests
- **Concurrent Processing**: Batch processing for efficiency
- **Retry Logic**: Automatic retries for failed requests
- **Error Recovery**: Continues operation despite individual failures

## API Endpoints Used

1. **Listings**: `https://api.myhome.az/api/announcement/list?announcementType={type}&page={page}`
2. **Phone Numbers**: `https://api.myhome.az/api/announcement/phone/{id}`

## Headers Configuration

The scraper uses proper headers to mimic browser requests:
- User-Agent: Chrome browser
- Accept: application/json
- Origin: https://myhome.az
- Referer: https://myhome.az/

## Logging

The scraper provides detailed logging:
- Progress updates for each batch
- Error messages for failed requests
- Summary statistics upon completion
- Rate limiting notifications

## Example Output

```
==================================================
SCRAPING COMPLETED SUCCESSFULLY
==================================================
Total listings scraped: 7644
Sale listings: 5887
Rent listings: 1757
Listings with phone numbers: 7521
Time taken: 1247.32 seconds
CSV file: myhome_listings_20250928_150423.csv
Excel file: myhome_listings_20250928_150423.xlsx
==================================================
```

## Error Handling

- **Rate Limiting**: Automatic backoff when rate limited
- **Network Errors**: Retry failed requests up to 3 times
- **Invalid Responses**: Skip and continue with next requests
- **Phone Number Failures**: Continue scraping even if phone retrieval fails

## Customization

You can modify the scraper by:
- Adjusting `rate_limit_delay` for different request intervals
- Changing `batch_size` for processing efficiency
- Modifying headers for different user agents
- Adding additional data fields to extract

## Legal Considerations

- This scraper is for educational and research purposes
- Respect the website's robots.txt and terms of service
- Use appropriate delays to avoid overloading the server
- Consider reaching out to MyHome.az for official API access for commercial use

## Requirements

- Python 3.7+
- aiohttp 3.9.1+
- pandas 2.1.4+
- openpyxl 3.1.2+