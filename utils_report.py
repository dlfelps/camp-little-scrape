from datetime import timedelta
from pathlib import Path
from pandas import DataFrame
from yattag import Doc
from re import Pattern
import re

def add_commute(df, commutes):
    df['commute']=df.apply(lambda x: commutes[x.place], axis=1)
    return df

def add_num_days(df):
    df['num_days'] = df.apply(lambda x: x.last_day - x.first_day + timedelta(days=1), axis=1)
    df['num_days'] = df.apply(lambda x: x.num_days.days, axis=1)
    return df

def parse_session(pattern: Pattern, url: str) -> str:
    return pattern.search(url).group(1)

def add_session(df: DataFrame) -> DataFrame:
    pattern = re.compile(r'session_id=(\d+)')
    df['session'] = df.apply(lambda x: parse_session(pattern, x['url']), axis=1)
    return df

def filter_commute(df, max_commute=120):
    return df[df['commute'] <= max_commute]

def filter_schools(df, remove_schools=True):
    if remove_schools:
        return df[df['school'] == False]
    else:
        return df

def filter_full(df, show_full=False):
    if show_full:
        return df
    else:
        return df[df['available'] == True]

def filter_age(df, min_age=5):
    return df[df['min_age'] <= min_age]

def filter_half_day(df, remove_half_day=True):
    if remove_half_day:
        return df[df['full_day'] == True]
    else:
        return df

def filter_first_day(df, first_day):
    return df[df['first_day'] == first_day]

def filter_last_day(df, last_day):
    return df[df['last_day'] == last_day]



def write_table(file: Path, df: DataFrame) -> None:
    doc, tag, text = Doc().tagtext()
    
    # Start the HTML document
    with tag('html'):
        with tag('body'):
            with tag('table', border="1"):
                # Create table header
                with tag('tr'):
                    with tag('th'):
                        text('First day')
                    with tag('th'):
                        text('Num days')
                    with tag('th'):
                        text('Commute')
                    with tag('th'):
                        text('Swim')
                    with tag('th'):
                        text('Place')
                    with tag('th'):
                        text('Title')
                    with tag('th'):
                        text('URL')                        
                
                # Create table rows
                for row in df.itertuples(index=False):
                    with tag('tr'):
                        with tag('td'):
                            text(str(row.first_day))
                        with tag('td'):
                            text(str(row.num_days))
                        with tag('td'):
                            text(str(row.commute))
                        with tag('td'):
                            if row.swim:
                                doc.asis('&#127946')
                            else:
                                text('')
                        with tag('td'):
                            text(row.place)
                        with tag('td'):
                            text(row.title)
                        with tag('td'):
                            with tag('a', href=row.url):
                                text(row.session)

    with open(file,'w') as f:
        f.write(doc.getvalue())

    return None