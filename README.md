# Gold Price Video Generator

This project automatically generates short, vertical videos displaying the latest gold prices in Thailand. It's designed to create content for social media platforms.

## Features

-   **Data Scraping:** Scrapes the latest gold prices from the Gold Traders Association of Thailand website.
-   **Video Generation:** Creates 1080x1920 (vertical) video clips.
-   **Customizable Panels:** Displays gold prices in a visually appealing and easy-to-read format, including Thai language support.
-   **Dynamic Backgrounds:** Randomly selects a background video for each generation.
-   **Price Change Indicators:** Shows whether the gold price has increased or decreased compared to the previous update.

## Requirements

-   Python 3.x
-   `playwright`
-   `requests`
-   `moviepy`
-   `numpy`
-   `Pillow`

You can install the required Python libraries using pip:

```bash
pip install playwright requests moviepy numpy pillow
```

You also need to install the browser binaries for Playwright:

```bash
playwright install
```

## Usage

1.  **Scrape Data:**
    Run the `getgold.py` script to fetch the latest gold prices.

    ```bash
    python getgold.py
    ```

    This will create/update the `gold_prices.json` file.

2.  **Generate Video:**
    Run the `app.py` script to generate the video.

    ```bash
    python app.py
    ```

    The output video will be saved as `out/output.mp4`.

## File Structure

-   `app.py`: The main script for generating the video.
-   `getgold.py`: The script for scraping gold price data.
-   `gold_prices.json`: The JSON file where the scraped data is stored.
-   `assets/`: Folder containing background videos.
-   `out/`: Folder where the output video is saved.
-   `run_gold.bat`: Batch file to run the scripts.
