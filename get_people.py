import requests

names = []

def get_person_names():
    global names
    response = requests.get('http://127.0.0.1:8000/person')
    if response.status_code == 200:
        data = response.json()
        print(data)
        names =  data.get('names', [])
    else:
        print(f"Error: {response.status_code}")
        return []

get_person_names()
print(names)