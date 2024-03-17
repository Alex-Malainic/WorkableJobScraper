# Workable Job Scraper

This Python script enables automated scraping of job listings from Workable-powered websites, facilitating efficient data collection related to job opportunities. It allows for both partial and full scraping functionalities, where partial scraping fetches basic job listing details such as job titles, types, locations, and URLs, and full scraping extends this by also gathering detailed job descriptions, requirements, and benefits. The script is capable of handling multiple websites in parallel, significantly reducing the time required for data collection.

## Features

- **Partial Scraping**: Quickly gathers basic job listing information.
- **Full Scraping**: Provides an in-depth collection of job data including descriptions, requirements, and benefits.
- **Concurrent Scraping**: Utilizes Python's `concurrent.futures.ThreadPoolExecutor` for efficient parallel data processing.
- **Customizable**: Easily extendable to add more websites or adapt to changes in website structure.
- **Clean Data Processing**: Automatically skips common introductory headings in job descriptions and requirements.

## Installation

Ensure you have Python installed on your system. This script was developed using Python 3.8+, and compatibility with earlier versions is not guaranteed.

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
