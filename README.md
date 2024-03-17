# Workable Job Scraper

This Python script enables automated scraping of job listings from Workable-powered websites, facilitating efficient data collection related to job opportunities. It allows for both partial and full scraping functionalities, where partial scraping fetches basic job listing details such as job titles, types, locations, and URLs, and full scraping extends this by also gathering detailed job descriptions, requirements, and benefits. The script is capable of handling multiple websites in parallel, significantly reducing the time required for data collection.

## Features

- **Partial Scraping**: Quickly gathers basic job listing information.
- **Full Scraping**: Provides an in-depth collection of job data including descriptions, requirements, and benefits.
- **Concurrent Scraping**: Utilizes Python's `concurrent.futures.ThreadPoolExecutor` for efficient parallel data processing.
- **Customizable**: Easily extendable to add more websites or adapt to changes in website structure.
- **Clean Data Processing**: Automatically skips common introductory headings in job descriptions and requirements.

## Example Usage

To use the script, follow these steps:

1. **Initialization**: Create an instance of the `ScrapeWorkable` class by passing a list of Workable website URLs you wish to scrape.

    ```python
    scraper = WorkableJobScraper(['https://apply.workable.com/caxton/', 'https://apply.workable.com/twinkl-ltd'])
    ```
2. **Partial Scraping**: To perform a partial scrape, which collects basic job listing information, call the `partial_scrape` method.

    ```python
    partial_jobs = scraper.partial_scrape()
    ```
3. **Full Scraping**: For a comprehensive data collection that includes job descriptions, requirements, and benefits, call the `full_scrape` method. This method performs partial scraping if not already done and then proceeds with the detailed scraping.
   
    ```python
    full_jobs_df = scraper.full_scrape()
    ```
    Optionally, you can set `save=True` to export the collected data to a CSV file.

## Customization

You can customize the scraping process by modifying the `headings` list in the `find_heading_index` method to skip over any additional common introductory headings you encounter.

## Contributing

Contributions to enhance the functionality, improve efficiency, or extend compatibility are welcome. Please feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is open-source and available under the MIT License. See the LICENSE file for more details.
