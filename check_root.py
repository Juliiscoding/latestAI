import requests
import json

def authenticate():
    auth_url = "https://auth.prohandel.cloud/api/v4/token"
    auth_data = {
        "apiKey": "7e7c639358434c4fa215d4e3978739d0",
        "secret": "1cjnuux79d"
    }
    
    response = requests.post(auth_url, json=auth_data)
    response.raise_for_status()
    
    auth_response = response.json()
    return auth_response["token"]["token"]["value"]

def check_root_endpoints():
    token = authenticate()
    print(f"Successfully authenticated")
    
    # Base URLs to try
    base_urls = [
        "https://linde.prohandel.de/api",
        "https://linde.prohandel.de/api/v2",
        "https://linde.prohandel.de"
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    for base_url in base_urls:
        try:
            print(f"\nChecking root endpoint: {base_url}")
            response = requests.get(base_url, headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.content:
                try:
                    data = response.json()
                    print(f"Response data: {json.dumps(data, indent=2)}")
                except:
                    print(f"Response content: {response.content.decode()}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_root_endpoints()
