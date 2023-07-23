import requests

# The API endpoint
url_root = "http://127.0.0.1:8000/"

# A GET request to the API
response = requests.get(url_root)

# Print the response
response_json = response.json()
print(response_json)



url_interest_value = "http://127.0.0.1:8000/interest_value/"

# Adding a payload
payload = {"initial_value": 1000, "final_value": 1500}

response = requests.get(url_interest_value, params=payload)

# Print the response
response_json = response.json()
print(response_json)
