# OpenSea NFT Image Scraper

This project is a Python-based GUI application that allows users to scrape and download NFT images from OpenSea collections. It provides an easy-to-use interface for fetching metadata and images from any OpenSea collection using the collection's slug.

## Features

- Fetch metadata for all NFTs in a specified OpenSea collection
- Download all NFT images from the collection
- Export metadata to CSV
- User-friendly GUI with progress tracking
- Configurable download path

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/NplusM420/opensea-scraper.git
   cd opensea-scraper
   ```

2. Install the required dependencies:
   ```
   pip install requests tkinter
   ```

   Note: `tkinter` is usually included with Python installations. If you encounter any issues, you may need to install it separately depending on your system.

3. Obtain an API key from OpenSea:
   - Go to [OpenSea Developers](https://docs.opensea.io/reference/api-keys)
   - Follow the instructions to get your API key

## Usage

1. Run the script:
   ```
   python opensea_scraper.py
   ```

2. In the GUI:
   - Click on "Settings" in the menu bar and select "Set API Key" to enter your OpenSea API key
   - Enter the collection slug in the "Enter Collection Slug" field
   - Specify a download path or use the "Browse" button to select a directory
   - Click "Fetch Data" to start the scraping process

3. The application will fetch metadata and download images for all NFTs in the collection. Progress will be displayed in the status bar and progress bar.

4. Once the fetch is complete, you can click "Export Metadata" to save the metadata as a CSV file.

## Notes

- The scraper assumes that token IDs in the collection range from 0 to 7776. If a collection has a different range, you may need to modify the code accordingly.
- Rate limiting is implemented to avoid overloading the OpenSea API. If you encounter issues, you may need to adjust the delay between requests.
- Large collections may take a significant amount of time to scrape completely.

## Troubleshooting

If you encounter any issues:
1. Check the `opensea_scraper.log` file for detailed error messages
2. Ensure your API key is correctly set and has the necessary permissions
3. Verify your internet connection
4. Make sure you have write permissions in the specified download directory

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/NplusM420/opensea-scraper/issues) if you want to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.