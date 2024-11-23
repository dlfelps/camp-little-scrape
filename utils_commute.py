import os
from datetime import date, datetime, timedelta, timezone
import httpx
import json

def dt_to_seconds(dt: datetime) -> int:
    return int((dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())

def get_commute_params(camp: str, home = "4440 Miniature Ln, Fairfax, VA 22033") :
    # returns 4 commute params:
    # morning commute (there and back)
    # afternoon commute (there and back)
    # based on next available weekday
    def defaults():
        params = {}
        params['avoid']='tolls'
        params['key'] = os.getenv("MAP_API_KEY")
        return params

    all_params = []
    tomorrow = date.today() + timedelta(days=1)
    if tomorrow.weekday() >= 5: # 5 is Saturday, 6 is Sunday
        tomorrow = tomorrow + timedelta(days=2)

    morning_commute = dt_to_seconds(datetime(tomorrow.year,tomorrow.month,tomorrow.day,hour=9,tzinfo=timezone.utc)) # 9 AM
    afternoon_commute = dt_to_seconds(datetime(tomorrow.year,tomorrow.month,tomorrow.day,hour=16,tzinfo=timezone.utc)) # 4 PM

    # morning commute
    temp = defaults()
    temp['destinations']=camp
    temp['origins']=home
    temp['arrival_time']=morning_commute
    all_params.append(temp)

    temp = defaults()
    temp['destinations']=home
    temp['origins']=camp
    temp['departure_time']=morning_commute    
    all_params.append(temp)

    # afternoon commute
    temp = defaults()
    temp['destinations']=camp
    temp['origins']=home
    temp['arrival_time']=afternoon_commute
    all_params.append(temp)

    temp = defaults()
    temp['destinations']=home
    temp['origins']=camp
    temp['departure_time']=afternoon_commute    
    all_params.append(temp)

    return all_params

def calculate_commute(client: httpx.Client, camp: str, home = "4440 Miniature Ln, Fairfax, VA 22033") :
    # returns estimated daily commute (in minutes)
    all_params = get_commute_params(camp=camp, home=home)

    total_time = 0

    for params in all_params:
        r = client.get('https://maps.googleapis.com/maps/api/distancematrix/json', params = params)
        if r.json()['rows'][0]['elements'][0]['status'] == 'OK':
            total_time += r.json()['rows'][0]['elements'][0]['duration']['value']
        else:
            return None

    return total_time // 60
    
        
def save_commutes(commutes: dict) -> None:
    # save commutes
    with open('commutes.json', 'w') as f:
        json.dump(commutes, f, ensure_ascii=True, indent=4)

    return None

def load_commutes() -> dict:
    # load commutes
    with open('commutes.json', 'r') as f:
        commutes = json.load(f)

    for k,v in commutes.items():
        if not v:
            raise ValueError(f'Commute not found for "{k}"')

    return commutes