"""Script used to demonstrate how to connect to the ECONIndexer API using the Requests module."""

import requests

# The API endpoint
url_root = "https://econindexer_api-1-k4103730.deta.app/"

# A GET request to the API
response = requests.get(url_root)

# Print the response
response_json = response.json()
print(response_json)



url_interest_value = "https://econindexer_api-1-k4103730.deta.app/interest_value/"

# Adding a payload
payload = {"initial_value": 1000, "final_value": 1500}

response = requests.get(url_interest_value, params=payload)

# Print the response
response_json = response.json()
print(response_json)
