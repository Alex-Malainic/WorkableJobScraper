from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
import re 

class WorkableJobScraper:
    """
    With the use of this class you can scrape Workable website and save the data locally.

    The initialization of the class should include a list of websites.

    This scraper has two main functionalities:
        1) scrape all job titles, location and URL's from a given website;
        2) access the individual jobs through their URL's and scrape the description, 
        requirements and benefits of the job in parallel;
    
    If a partial scraping is what you want, use the function 'partial_scrape'.
    For full scraping, use 'full_scrape'.
    """
    def __init__(self, website_list):
        self.scraped_jobs = [] # Initialize an empty list to store job details
        self.website_list = website_list
        self.partial_jobs = None # Initialize partial jobs object


    def initialize_webdriver(self):
        """
        Configures and initializes the Chrome webdriver.
        Returns the driver.

        If the initialization fails, raises an Exception.
    
        """
        # Configure webdriver options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--log-level=3")

        # Initialize driver
        try:
            driver = webdriver.Chrome(options = options)
            return driver
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
        

    def connect(self, driver, website):
        """
        Connects to target website.
        """
        
        # Get the name of the company from the URL
        company_name = re.search(r'\.com/([^/]+)', website)
        self.company_name = company_name.group(1).capitalize()

        print(f"Establishing connection to {self.company_name} career website...")

        # Connect to website
        driver.get(website)

        # Wait for the page to load dynamically loaded content
        time.sleep(5)


    # ------------------------ PARTIAL SCRAPE ---------------------
        
    def click_filter_button(self, driver):
        """ 
        Clicks the 'clear filter' button, if it exists.
        This particular filter appears on some websites and 
        filters the content based on geolocation, so in order to
        get all jobs it must be cleared.
        """
        try:
            filter_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@data-ui='clear-filters']")))
            
            # Scroll to the "clear filters" button
            driver.execute_script("arguments[0].scrollIntoView();", filter_button)
            time.sleep(2)
            try:
                filter_button.click()
            except Exception as e:
                driver.execute_script("arguments[0].click();", filter_button)
        except:
            pass


    def click_load_button(self, driver):
        """ 
        Clicks the 'load more' button, if it exists.
        If there are more buttons, they will be clicked
        until no more buttons exists (i.e. all jobs loaded)
        """
        while True:
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-ui='load-more-button']")))

                # Scroll to the "Show More" button
                driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                time.sleep(2)  # Wait for any potential overlay to disappear

                # Try clicking the button, or use JavaScript click if normal click fails
                try:
                    show_more_button.click()
                except Exception as e:
                    driver.execute_script("arguments[0].click();", show_more_button)

                time.sleep(3)  # Wait for the page to load more content
            except:
                break


    def scrape_jobs(self, driver, save = False):
        """
        Scrapes and stores jobs' information.
        Stores the title, job type, location and URL of the job.

        Returns a pandas dataframe containing the scraped data.
        """
        print("Searching job listings...")
        job_listings = driver.find_elements(By.XPATH, "//li[@data-ui='job']")

        for job in job_listings:
            title_element = job.find_element(By.XPATH, ".//h3[@data-ui='job-title']/span")
            job_type_element = job.find_element(By.XPATH, ".//span[@data-ui='job-workplace']/strong")
            location_element = job.find_element(By.XPATH, ".//span[@data-ui='job-location']")
            job_url_element = job.find_element(By.TAG_NAME, 'a')

            title = title_element.text if title_element.text else 'No Title Found'
            job_type = job_type_element.text if job_type_element.text else 'No Type Found'
            location = location_element.text if location_element.text else 'No Location Found'
            job_url = job_url_element.get_attribute('href') if job_url_element else 'No URL Found'

            self.scraped_jobs.append({
                'Company': self.company_name,
                'Title': title,
                'Type': job_type,
                'Location': location,
                'URL': job_url
            })

        # Close the connection to the website
        print('Closing the connection...')
        driver.quit()

        # Convert the list of dictionaries to a DataFrame
        job_listings_df = pd.DataFrame(self.scraped_jobs)

        # Save the jobs to a csv, if required
        if save:
            job_listings_df.to_csv("Workable_jobs.csv", index = False)

        return job_listings_df

                
    def partial_scrape(self, save = False):
        """
        Scrape each website for jobs. 
        Saves the jobs' title, type, location
        and URL in a dataframe.

        Optionally, you can set parameter 'save' to True
        in order to export scraped jobs to a CSV.
        """
        # Ensure the websites are in a list format
        if type(self.website_list) != list:
            self.website_list = [self.website_list]

        for website in self.website_list:
            # Initialize driver
            driver = self.initialize_webdriver()
            # Connect to websites
            self.connect(driver, website)
            # Clear filter button, if it exists
            self.click_filter_button(driver)
            # Click "Load more" buttons to reveal all jobs
            self.click_load_button(driver)

            # Save the scraped jobs information and print to the screen
            self.partial_jobs = self.scrape_jobs(driver, save)

        return self.partial_jobs

    # --------------------------- FULL SCRAPE ----------------------------------


    def find_heading_index(self, description, headings):
        """
        Function to find the heading and adjust the index
        in order to skip the heading text.
        """
        index = min([description.find(h) for h in headings if description.find(h) != -1], default=-1)
        if index != -1:
            # Adjust the index to skip over the heading text
            index += description[index:].find('\n') + 1
        return index


    def scrape_job_description(self, url):
        """
        Scrape each job's description.
        
        Returns a tuple consisting of the description, 
        requirements and  benefits of the job, if they exist.
        """

        # Initialize webdriver
        driver = self.initialize_webdriver()

        # Access job URL
        driver.get(url)

        # Wait for the page to load
        time.sleep(5)  

        # Initialize variables to store the extracted text
        job_description = job_requirements = job_benefits = ''


        # Scrape description, requirements and benefits of the job
        print(f"Scraping {url}")
        try:
            job_description_element = driver.find_element(By.XPATH, "//section[@data-ui='job-description']/div")
            job_description = job_description_element.text if job_description_element else ''

            # Find index of unwanted heading
            start_index = self.find_heading_index(job_description, ["Company Overview:\n"])

            # Slice the description from the starting index to skip the heading
            if start_index != -1:  # Only if a heading was found
                job_description = job_description[start_index:]


        except Exception:
            pass

        try:
            job_requirements_element = driver.find_element(By.XPATH, "//section[@data-ui='job-requirements']/div")
            job_requirements = job_requirements_element.text if job_requirements_element else ''

            # Find index of unwanted introductory description
            start_index = self.find_heading_index(job_requirements, ["The Role:\n", "Requirements:\n"])

            # Find index of unwanted heading
            if start_index != -1:  # Only if a heading was found
                job_requirements = job_requirements[start_index:]

        except Exception:
            pass

        try:
            job_benefits_element = driver.find_element(By.XPATH, "//section[@data-ui='job-benefits']/div")
            job_benefits = job_benefits_element.text if job_benefits_element else ''
        except Exception:
            pass

        
        # Destroy the connection
        driver.quit()

        return (job_description, job_requirements, job_benefits)


    def full_scrape(self, save = True):
        """
        Accesses each scraped job and extracts information
        related to it. The jobs are scraped in parallel in batches
        of 5, speeding up the process.

        Returns a dataframe containing full information about the jobs
        By default, it also saves the dataframe in a CSV.
        """
        # Scrape the websites for jobs if they have not been scraped already
        if self.partial_jobs is None:
            self.partial_jobs = self.partial_scrape()

        # Get URL list
        urls = self.partial_jobs['URL'].tolist()


        print("Scraping individual jobs...")

        # Use ThreadPoolExecutor to scrape in parallel
        with ThreadPoolExecutor(max_workers = 5) as executor:  
            descriptions = list(executor.map(self.scrape_job_description, urls))

        # Unzip the list of tuples into separate lists
        job_descriptions, job_requirements, job_benefits = zip(*descriptions)

        # Add the descriptions to DataFrame
        full_jobs = self.partial_jobs.copy()

        full_jobs['Job_Description'] = job_descriptions
        full_jobs['Job_Requirements'] = job_requirements
        full_jobs['Job_Benefits'] = job_benefits

        # Save the full dataframe, if needed
        if save:
            full_jobs.to_csv('Workable_Jobs_Full.csv', index = False)

       
        return full_jobs