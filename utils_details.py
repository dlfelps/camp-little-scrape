import httpx
from httpx import Client
from bs4 import BeautifulSoup, SoupStrainer
import re
from re import Pattern
from dataclasses import dataclass
from datetime import date, datetime
import pandas as pd
from pathlib import Path
from tqdm import tqdm

@dataclass
class Camp():
    title: str 
    desc: str 
    min_age: int     
    place: str 
    school: bool
    first_day: date 
    last_day: date 
    swim: bool
    available: bool 
    full_day: bool
    url: str 

    def to_dict(self) -> dict:
        return {'title': self.title,                
                'desc': self.desc,     
                'min_age': self.min_age,  
                'place': self.place,
                'school': self.school,
                'first_day': self.first_day,
                'last_day': self.last_day,
                'swim': self.swim,    
                'available': self.available,
                'full_day': self.full_day,
                'url': self.url}

def is_class_available(soup: BeautifulSoup) -> bool:
    if soup.find("a", class_="btn btn-default1 logde"):
        return True
    else: # waitlist button has class "btn btn-default logde"
        return False

def try_place(soup: BeautifulSoup) -> str | None:
    result = soup.find(class_='panel-heading detail-title')
    if result:
        return result.text
    else:
        return None

def get_title(soup: BeautifulSoup) -> str:
    return soup.find("h2", class_='climb-hed').text

def get_description(soup: BeautifulSoup) -> str:
    return soup.find("p", class_="top-content").text

def get_min_age(soup: BeautifulSoup) -> int:
    
    text = soup.find("span", id="mainContent_spanThisactivity").text
    age_pattern = re.compile(r'This activity is Ages (\d+)')
    match = age_pattern.search(text)
    return int(match.group(1))

def get_dates(soup: BeautifulSoup) -> (date,date):
    def foo(date_str: str) -> date:
        dt = datetime.strptime(date_str,'%m/%d/%Y')
        return dt.date()
    panels = soup.find_all("div", class_="panel-body")
    date_pattern = re.compile(r'(\d\d/\d\d/202\d)')
    match = date_pattern.findall(panels[1].text)
    return (foo(match[0]), foo(match[1]))

def is_full_day(soup: BeautifulSoup) -> bool:
    panels = soup.find_all("div", class_="panel-body")
    time_pattern = re.compile(r'9:00 AM - 4:00 PM')
    if time_pattern.search(panels[1].text):
        return True
    else:
        return False

def get_swim(desc: str) -> bool:
    swim_pattern = re.compile(r'swim') 
    if swim_pattern.search(desc):
        return True
    else:
        return False

def is_school(place: str) -> bool:
    school_pattern = re.compile(r'school', re.IGNORECASE) 
    if school_pattern.search(place):
        return True
    else:
        return False
        
def try_parse_url(url: str, client: Client) -> Camp | None:

    r = client.get(url) 

    soup = BeautifulSoup(r.text, features="html.parser")
    place = try_place(soup)
    if not place: # shortcurcuit bad url to return None
        return None
    school = is_school(place)

    available = is_class_available(soup)

    title = get_title(soup) 
    min_age = get_min_age(soup)        
    desc = get_description(soup)   
    swim = get_swim(desc)
    first_day, last_day = get_dates(soup)
    full_day = is_full_day(soup)
    return Camp(url=url, 
                available=available, 
                place=place,
                school=school,
                title=title,
                min_age=min_age,
                desc=desc,
                swim=swim,
                first_day=first_day,
                last_day=last_day,
                full_day=full_day)
    
def fetch_details(link_file: Path):
    df = pd.read_csv(link_file, names=['urls'])
    camps = []
    with httpx.Client(verify=False) as client:
        for url in tqdm(df['urls'].tolist()):
            temp = try_parse_url(url, client)
            if temp:
                camps.append(temp)
    return camps        

