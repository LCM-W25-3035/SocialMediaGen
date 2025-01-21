import requests
from pymongo import MongoClient

# Function to fetch data from an API
def fetch_data_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Parse the JSON data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

# Function to load data into MongoDB
def load_data_to_mongo(db_name, collection_name, data):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI if using a remote database
        db = client[db_name]
        collection = db[collection_name]

        # Insert data into the collection
        if isinstance(data, list):  # If data is a list of records
            result = collection.insert_many(data)
            print(f"{len(result.inserted_ids)} records inserted into MongoDB collection '{collection_name}'.")
        elif isinstance(data, dict):  # If data is a single record
            result = collection.insert_one(data)
            print(f"1 record inserted into MongoDB collection '{collection_name}'.")
        else:
            print("Unsupported data format for MongoDB insertion.")
    except Exception as e:
        print(f"Error loading data into MongoDB: {e}")

# Main script
if __name__ == "__main__":
    # Define API URL
    api_url = "https://api.example.com/data"  # Replace with your API endpoint

    # Define MongoDB database and collection names
    database_name = "my_database"
    collection_name = "my_collection"

    # Fetch data from the API
    api_data = fetch_data_from_api(api_url)

    if api_data:
        # Load data into MongoDB
        load_data_to_mongo(database_name, collection_name, api_data)
