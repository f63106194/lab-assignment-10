import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_president_terms():
    url = "https://en.wikipedia.org/wiki/List_of_presidents_of_the_United_States"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception("Failed to open.")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})

    presidents_data = {}

    for row in table.find_all('tr')[1:]:  
        cells = row.find_all('td')
        
        president_name = cells[1].text.strip()
        president_name = re.sub(r'\[.*?\]', '', president_name) 
        president_name = re.sub(r'\(.*?\)', '', president_name).strip()  
        term_info = cells[2].text.strip()
        years = re.findall(r'\d{4}', term_info)  
        
        if len(years) >= 2:
            start_year, end_year = int(years[0]), int(years[1])
            total_years = end_year - start_year
        else:
            total_years = 4  
        
        terms_served = (total_years // 4) + (1 if total_years % 4 != 0 else 0)

        political_party = cells[-3].text.strip()
        political_party = re.sub(r'\[.*?\]', '', political_party)  

        presidents_data[president_name] = [political_party, terms_served]
        
    return presidents_data


def calculate_approval_changes():
    url = "https://dsci.isi.edu/slides/data/presidents"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to open.")
        return None

    data = response.json().get("presidents", [])

    approval_changes = {}

    for president in data:
        name = president.get("name")
        approval_ratings = president.get("approval_ratings", {})
        start = approval_ratings.get("start")
        end = approval_ratings.get("end")
        if name and start is not None and end is not None:
            approval_changes[name] = end - start
    
    return approval_changes


def generate_president_dataframe():
    terms_data = get_president_terms()
    approval_changes = calculate_approval_changes()

    terms_df = pd.DataFrame.from_dict(terms_data, orient="index", columns=["Party", "Terms"]).reset_index()
    terms_df = terms_df.rename(columns={"index": "President"})
    terms_df["Approval Change"] = terms_df["President"].map(approval_changes)

    return terms_df
