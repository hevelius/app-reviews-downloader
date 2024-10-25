import jwt
import time
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Read environment variables
ISSUER_ID = os.getenv("ISSUER_ID")
KEY_ID = os.getenv("KEY_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
APP_ID = os.getenv("APP_ID")

# Generate JWT token
def generate_token():
    with open(PRIVATE_KEY_PATH, "r") as key_file:
        private_key = key_file.read()

    header = {
        "alg": "ES256",
        "kid": KEY_ID,
        "typ": "JWT"
    }

    payload = {
        "sub": "user", # this key only if you don't want to use ISSUER_ID
        "iat": int(time.time()),
        "exp": int(time.time()) + 20 * 60,  # Expiration time: 20 minutes
        "aud": "appstoreconnect-v1",
        "scope": [
            f"GET /v1/apps/{APP_ID}/customerReviews"
         ]
    }

    token = jwt.encode(payload, private_key, algorithm="ES256", headers=header)
    return token

'''
Get reviews from App Store Connect API:
- Get the JWT token
- Make a GET request to the API
- Get the reviews from the response
- Get the link to the next page
- Repeat the process until there are no more pages
- Return all reviews
'''
def get_reviews():
    token = generate_token()
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/customerReviews?sort=createdDate&limit=200"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    all_reviews = []
    next_url = url

    while next_url:
        response = requests.get(next_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Add reviews to the list
            if 'data' in data:
                all_reviews.extend(data['data'])
            
            # Get the link to the next page
            next_url = data.get("links", {}).get("next")
            
            # Print the number of reviews retrieved so far
            print(f"Reviews retrieved: {len(all_reviews)}")
        else:
            print(f"Request error: {response.status_code}")
            print(f"Error message: {response.text}")
            break  # Exit the loop if there is an error

    return all_reviews

# Save reviews to a JSON file
def save_to_json(reviews, filename="reviews.json"):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(reviews, json_file, ensure_ascii=False, indent=4)
    print(f"Reviews saved in {filename}")

if __name__ == "__main__":
    reviews = get_reviews()

    if reviews:
        save_to_json(reviews)
