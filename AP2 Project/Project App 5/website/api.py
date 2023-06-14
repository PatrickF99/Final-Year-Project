import requests

api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
query = 'Apple'
response = requests.get(api_url + query, headers={'X-Api-Key': 'hF5YxQt6y7hD8xXI8Zy1Ow==rrDStINNITeMcMMT'})
if response.status_code == requests.codes.ok:
    print(response.text)
else:
    print("Error:", response.status_code, response.text)