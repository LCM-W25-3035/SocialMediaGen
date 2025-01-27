import requests

# GDELT API Endpoint
url = "https://api.gdeltproject.org/api/v2/doc/doc"

# Parameters for the API request
params = {
    "format": "json",
    "Sourcelanguage": "ENGLISH",  # Request data in JSON format
    "maxrecords": 10,  # Limit to 10 records
    "query": "technology"  # Example query for testing
}

try:
    response = requests.get(url, params=params)

    # Check Status Code
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        # Check if Content-Type is JSON
        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            if data:
                print("Fetched Data:")
                print(data)
            else:
                print("No data found for the query.")
        else:
            print("Response is not in JSON format.")
            print(f"Raw Response: {response.text[:500]}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f"Error message: {response.text[:500]}")

except Exception as e:
    print(f"An error occurred: {e}")
