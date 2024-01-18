import pandas as pd
import numpy as np
import keyring
import requests
from urllib.parse import urlencode, quote_plus
from unidecode import unidecode 


# loading list of researchers from UNAM-IA
invest = pd.read_csv('IA_inves.csv', comment='#')
name1 = []
name2 = []
name3 = []

for i in range(len(invest['last_1'])):
    tmp = f"{invest['last_1'][i]}, {invest['name_1'][i]}"
    name1.append(tmp)
    tmp = f"{invest['last_1'][i]}, {invest['name_1'][i].strip()[0]}."
    name2.append(tmp)

    if invest['last_2'][i] != np.nan:
        tmp = f"{invest['last_1'][i]}-{invest['last_2'][i]}, {invest['name_1'][i].strip()[0]}."
        name3.append(tmp)

print('This is the list of authors to be run in  the query:')
print('----')
for i in range(len(invest['last_1'])):
    print(f"{name1[i]}, {name2[i]}, {name3[i]}")   



token="oWP5e2LVuUCxW9nxbynNEj0YPe2uEtDZCbgiZBej"

# query function
def query(query_field, query_value, fields):
    encoded_query = urlencode({"q": f"{query_field}:{query_value}","fl": f"{fields}","rows": 4000})
    results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query), headers={'Authorization': 'Bearer ' + token})
    r = results.json()    
    return(r)
    
bibliography = []
n_research = len(invest['last_1'])

# Here the query starts
for i in range(n_research):
    try:
        print(f" retirving data for author: {name1[i]} ... ")
        r = query('author', name1[i], "title, bibcode, year,aff, author")
        data = r['response']["docs"]
        n_data = len(data)
        print('number of entries:',n_data)
        for j in range(n_data):
            bibliography.append(data[j])

        print(f" retirving data for author: {name2[i]} ... ")
        r = query('author', name2[i], "title, bibcode, year,aff, author")
        data = r['response']["docs"]
        n_data = len(data)
        print('number of entries:',n_data)
        for j in range(n_data):
            bibliography.append(data[j])

        print(f" retirving data for author: {name3[i]} ... ")
        r = query('author', name3[i], "title, bibcode, year,aff, author")
        data = r['response']["docs"]
        n_data = len(data)
        print('number of entries:',n_data)
        for j in range(n_data):
            bibliography.append(data[j])

    except requests.JSONDecodeError:
        try:
            print(f" retirving data for author: {name2[i]} ... ")
            r = query('author', name2[i], "title, bibcode, year,aff, author")
            data = r['response']["docs"]
            n_data = len(data)
            print('number of entries:',n_data)
            for j in range(n_data):
                bibliography.append(data[j])

            print(f" retirving data for author: {name3[i]} ... ")
            r = query('author', name3[i], "title, bibcode, year,aff, author")
            data = r['response']["docs"]
            n_data = len(data)
            print('number of entries:',n_data)
            for j in range(n_data):
                bibliography.append(data[j])

        except requests.JSONDecodeError:
            print(f" retirving data for author: {name3[i]} ... ")
            r = query('author', name3[i], "title, bibcode, year,aff, author")
            data = r['response']["docs"]
            n_data = len(data)
            print('number of entries:',n_data)
            for j in range(n_data):
                bibliography.append(data[j])

# Cleaning the entries:
# - matching the query with the three types of author's names using in the query
# - TODO: clean by duplicates!
# - TODO: use orcid for the following names: lopez, jose; garcia, maria; perez maria; hernandez, jesus
# - TODO: use second name of carigi, leticia?

n_biblio = len(bibliography)
print('number of all retrive publications',n_biblio)

sel_biblio = []
for i in range(n_biblio):
    list = bibliography[i]['author']
    revi = []
    for author in list: 
        tmp = unidecode(author.lower())
        revi.append(tmp)
        
    for j in range(n_research):
        if (name1[j] in revi) == True:
            sel_biblio.append(bibliography[i])
        else:       
            if (name2[j] in revi) == True:
                sel_biblio.append(bibliography[i])
            else:
               if (name3[j] in revi) == True:
                    sel_biblio.append(bibliography[i])

print('number of selected articles',len(sel_biblio))

# write / read a jason file
import json

with open("bibliography.json", "w") as fp:
    json.dump(sel_biblio, fp)
    print("Done writing JSON data into .json file")
