import typer
import pandas as pd
from pathlib import Path
from utils_details import fetch_details
from utils_report import *
from utils_commute import calculate_commute, save_commutes, load_commutes
from datetime import datetime
import json
import httpx


app = typer.Typer(no_args_is_help=True)


@app.command()
def details() -> None:    
    """
    Scrapes detailed data from Fairfax county website.
    
    Input : The previously scraped links (links.txt)
    
    Output : Fetches camp details and saves in dataframe (camps.pkl)
             Also creates a places.txt containing the unique places.
    """
    
    links = Path('links.txt')
    if not links.exists():
        raise FileNotFoundError("Please complete step 1 first. See step1.ipynb to create links.txt.")
    camps = fetch_details(links)
    df = pd.DataFrame.from_records([c.to_dict() for c in camps])
    df.to_pickle('camps.pkl')
    print('Created camps.pkl.')
    
    places = df['place'].unique().tolist()
    with open('places.txt','w') as f:
        for p in places:
            f.write(f"{p}\n")

    print('Created places.txt.')
    return None

@app.command()
def commute(home_address: str = "4440 Miniature Ln, Fairfax, VA 22033") -> None:    
    """
    Calculates commutes from home to all places using Google Routes API (API token required)
    
    Input : The previously collected places (places.txt)
            Also Google API token (stored in environment variable MAP_API_TOKEN)
    
    Output : The total daily estimated commute from home to each location (commutes.json)
    """
    # load places
    places = Path('places.txt')
    if not places.exists():
        raise FileNotFoundError("Please call DETAILS command first.")
    
    with open(places, 'r') as f:
        camps = f.readlines()
    
    camps = list(map(lambda x: x.strip(), camps))

    commutes = {}

    with httpx.Client(verify=False) as client:
        for camp in camps:            
            commutes[camp] = calculate_commute(client, camp=camp)

    save_commutes(commutes)
    print('Created commutes.json.')
    return None

@app.command()
def report(first_day:str, 
           last_day:str, 
           min_age:int = 5,
           max_commute:int=120,
           remove_half_day:bool=True,
           remove_schools:bool=True,
           show_full:bool=False) -> None:    
    """
    Creates a printed report for the week summarizing camp options
    
    Input : The previously collected details (camps.pkl)
            Commute times (commutes.json)
            Filter options (see command options)
    
    Output : A summary table including the following info:
        - title
        - commute time (sorted by this)
        - swimming indicator
        - available indicator
        - link to camp
    """
    camps = Path('camps.pkl')
    if not camps.exists():
        raise FileNotFoundError("Please call DETAILS command first.")
    cj = Path('commutes.json')
    if not cj.exists():
        raise FileNotFoundError("Please call COMMUTES command first.")
        
    
    first_day = datetime.strptime(first_day,'%m/%d/%Y')
    first_day = first_day.date()
    
    last_day = datetime.strptime(last_day,'%m/%d/%Y')
    last_day = last_day.date()

    df = pd.read_pickle('camps.pkl')

    with open('commutes.json','r') as f:
        commutes = json.load(f)
    
    df=(
        df.pipe(add_commute, commutes)
        .pipe(add_num_days)
        .pipe(add_session)
        .pipe(filter_commute, max_commute)
        .pipe(filter_schools, remove_schools)    
        .pipe(filter_age, min_age)
        .pipe(filter_half_day, remove_half_day)
        .pipe(filter_full, show_full)
        .pipe(filter_first_day, first_day)
        .pipe(filter_last_day, last_day)
    )
    
    df = df.sort_values('commute')
    p = Path('reports')
    p.mkdir(exist_ok=True)   
    
    write_table(p.joinpath(f"{str(first_day)}.html"),df)

    print(f"Created {str(first_day)}.html.")
    
    return None

if __name__ == "__main__":
    app()