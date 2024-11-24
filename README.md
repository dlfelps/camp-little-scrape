# Website scraper & report builder

This project provides improved ability to search and register for camps hosted by the [Fairfax County Park Authority](https://fairfax.usedirect.com/FairfaxFCPAWeb/Default.aspx) (FCPA). The final result is a Python command line tool to assist with creating a report to list camps meeting the filter criteria.

### Goals
The goals of this project are to:
- Improve user experience registering for camps hosted by FCPA
- Demonstrate the use of developing a command line tool
- Demonstrate the 3rd party API (Google MAP API)
- Demonstrate report creation

### FCPA site limitations
Why is this tool needed? Because FCPA offers hundreds of potential camps to register for and their filter options are rather limited. Here is a screenshot of the FCPA camp search site:

![](https://github.com/dlfelps/camp-little-scrape/blob/521b0cc1c8ef6089643608997fc7358f82ee5f9d/screenshots/fcpa_search.jpeg)

At first glance it the fields look reasonable. We should be able to narrow down the list of available camps and register for one. Let's see what happens if I try to find a camp for my 6 year old son for the two days after New Years Day (Jan 2-3).

![](https://github.com/dlfelps/camp-little-scrape/blob/cb453b1a43840bc5f3bebcaf8e4ae50c8552d4a8/screenshots/fcpa_results.jpeg)

Due to the broad age range filter (6-12 yrs old), only one of the first six camps listed in the results are appropriate for a 6 year old. And the one camp that is appropriate is for January 20 because the filter only allows you to specify the date "starting on or after". So the best I can do is limit results from a starting date to the end of that month. This is especially frustrating when trying to book camps over the summer break. Typically I want to book one camp per week for the entire summer. To do this on the FCPA website I can change the "starting on or after" date, but for the first week in a month I get all camps in that month (which could be more than 100 sessions!). 

### Desired capabilities

I would like to build a tool that can output a tailored report to facilitate selecting and registring for camps. Ideally I would be able to quickly update the data based on the current openings as classes can fill up quickly. So I need a way to:
1. Automatically scrape the camp data from the FCPA website
2. Select camps by various criteria
3. Generate a custom report


### Installation
1. Clone the repo (git clone https://github.com/dlfelps/camp-little-scrape.git)
2. Install dependencies (pip install -r requirements.txt)
3. Install Chrome (https://www.google.com/chrome/)
4. Sign up for a Google Maps API key (https://developers.google.com/maps)

### Usage

#### Process overview

![](https://github.com/dlfelps/camp-little-scrape/blob/cb453b1a43840bc5f3bebcaf8e4ae50c8552d4a8/screenshots/camp%20scraper-2024-11-21-162211.svg)

The overall process is described in the flowchart above. I will demonstrate each step below in detail, but at a high level, the tool completes a series of steps to:
1. Scrape camp links
2. Scrape camp details
3. (optional) Calculate commute times to each camp
4. Filter camps and generate report

##### Step 1 - Scrape camp links
The first step in the process uses [Selenium](https://selenium-python.readthedocs.io/) to semi-automatically scrape the camp session links from the FCPA website. 
1. launch jupyter lab
2. open step1.ipynb
3. Follow instructions in step1.ipynb to open remote Chrome browser
4. Go to FCPA website and search for ALL camps
5. Follow instructions in step1.ipynb to scrape each page

This step produces a ```links.txt``` file containing all the camp session links.

##### Step 2 - Scrape camp details
Steps 2-4 all use the command line gui provided by the camp.py file. It is built using [Typer](https://typer.tiangolo.com/). View the list of possible commands by calling ```python camp.py --help``` 

![](https://github.com/dlfelps/camp-little-scrape/blob/cb453b1a43840bc5f3bebcaf8e4ae50c8552d4a8/screenshots/gui_help.PNG)

Step 2 is initiated by calling ```python camp.py details```. This step scrapes the camp details (e.g. location, dates, times) for each camp found in the ```links.txt```.

##### Step 3 - (optional) Calculate commutes

The third step uses Google Maps API to calculate the typical daily commute to each camp. This calculation is the sum of the following distances between home (user specified) and camp location:
- morning dropoff (arriving by 9 AM)
- morning return (departing at 9 AM)
- afternoon pickup (arriving by 4 PM)
- afternooon return (departing at 4 PM)

Commute time is one of the most important factors when selecting camps. Since full day camps are only 7 hours, it would not be time efficient to spend 2 hours in the car, which is shockingly easy to do even staying with Fairfax county (where all FCPA camps are located). This step does require a Google Map API key, which can be created at https://developers.google.com/maps. The code retrieves your individial key from the environment variable ```MAP_API_KEY```. Here is a [guide](https://lazyprogrammer.me/how-to-set-environment-variables-permanently-in-windows-linux-and-mac/) if you need help.

##### Step 4 - Filter camps and generate report

The final step filters the available camps to generate a report. We can see the full list of available options by looking at the report help command ```python camp.py report --help```.

![](https://github.com/dlfelps/camp-little-scrape/blob/cb453b1a43840bc5f3bebcaf8e4ae50c8552d4a8/screenshots/gui_report_help.PNG)

The filtering options for this step are as follows:

|    Parameter    | Required? | Default value |                                    Description                                   |      Example      |
|:---------------:|:---------:|:-------------:|:--------------------------------------------------------------------------------:|:-----------------:|
|    first_day    |     Y     |      N/A      |                         The camp must start on this date                         |    "01/02/2025"   |
|     last_day    |     Y     |      N/A      |                          The camp must end on this date                          |    "01/03/2025"   |
|     min_age     |     N     |   5 (years)   |                       The camp must accept kids of this age                      |    --min-age=5    |
|   max_commute   |     N     | 120 (minutes) | The camp must not have an estimated daily commute greater than this many minutes | --max-commute=120 |
| remove_half_day |     N     |      True     |                    Half day camps (from 9-noon) are not shown                    | --remove-half-day |
|  remove_schools |     N     |      True     |                      Camps located at schools are not shown                      |  --remove-schools |
|    show_full    |     N     |     False     |               Camps that are already fully registered are not shown              |   --no-show-full  |

If your desired parameters are different from default, then change them when you call the report command, e.g. ```python camp.py report "01/02/2025" "01/03/2025" --min-age=7```. 

This will produce an HTML file in the reports directory with all matching camps:

![](https://github.com/dlfelps/camp-little-scrape/blob/cb453b1a43840bc5f3bebcaf8e4ae50c8552d4a8/screenshots/report.PNG)

The report is generated using the [yattag](https://www.yattag.org/) library to procedurally generate the HTML report from python code.
A few highlights of the report:
- The camps are sorted by shortest commute first
- The report highlights which camps include a swimming break
- Each camp includes a session link for easy registration

## Conclusion

Overall I found this side project to be quite rewarding. I learned how to:
- scrape data from websites (selenium and httpx)
- parse structured data from websites (beautifulsoup)
- keep API keys secret using environment variables
- use 3rd party APIs
- generate HTML from Python

Finally I found the tool to actually make finding and registering my son for camp much easier! 

## Possible improvements

I was not able to find a way for [Typer](https://typer.tiangolo.com/) to hide commands that were not yet applicable. Ideally, only the ```details``` command would be initially available (taking in the links.txt that was produced during the semi-manual scraping step). Then after creating "camps.pkl" and "places.txt" the ```commute``` command would be available. Finally the ```report``` command could be used.
