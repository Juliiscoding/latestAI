# ProHandel API Troubleshooting Guide

This guide provides solutions for common issues when connecting to the ProHandel API, based on our experience integrating with it for CloudStock functionality.

## Core Functionality Requirements

For CloudStock, we primarily need access to:

1. **Inventory data** (stock levels)
2. **Product data** (details, pricing)
3. **Sales data** (for historical analysis)

These core endpoints are essential for inventory management functionality.

## Common Authentication Issues

### Issue 1: Incorrect Authentication URL

The ProHandel API authentication endpoint can vary depending on your account:

```
https://auth.prohandel.cloud/api/v4/token
https://auth.prohandel.de/api/v4/token
https://linde.prohandel.de/auth/api/v4/token
```

**Solution:** Try each authentication URL until you find one that works with your credentials.

### Issue 2: API URL Variations

The base API URL can also vary:

```
https://linde.prohandel.de/api/v2/
https://api.prohandel.de/api/v2/
```

**Solution:** Our testing found that `https://linde.prohandel.de/api/v2/` works most reliably.

### Issue 3: Authentication Response Format

The authentication response format may vary:

```json
// Format 1
{
  "token": {
    "value": "your-token-here"
  }
}

// Format 2
{
  "token": {
    "token": {
      "value": "your-token-here"
    }
  }
}

// Format 3
{
  "access_token": "your-token-here"
}
```

**Solution:** Handle all possible response formats in your code.

## Working Authentication Example

```python
def authenticate(api_key, api_secret):
    """Authenticate with the ProHandel API"""
    auth_urls = [
        "https://auth.prohandel.cloud/api/v4",
        "https://auth.prohandel.de/api/v4",
        "https://linde.prohandel.de/auth/api/v4"
    ]
    
    auth_data = {
        "apiKey": api_key,
        "secret": api_secret
    }
    
    for auth_url in auth_urls:
        try:
            print(f"Trying authentication URL: {auth_url}")
            response = requests.post(f"{auth_url}/token", json=auth_data)
            
            if response.status_code == 200:
                auth_response = response.json()
                
                # Handle different response formats
                if "token" in auth_response and "value" in auth_response["token"]:
                    return auth_response["token"]["value"], auth_url
                elif "token" in auth_response and isinstance(auth_response["token"], dict) and "token" in auth_response["token"]:
                    return auth_response["token"]["token"]["value"], auth_url
                elif "access_token" in auth_response:
                    return auth_response["access_token"], auth_url
        except Exception as e:
            print(f"Error with {auth_url}: {str(e)}")
    
    raise Exception("Authentication failed with all URLs")
```

## API Request Best Practices

1. **Include proper headers:**
   ```python
   headers = {
       "Authorization": f"Bearer {access_token}",
       "Content-Type": "application/json",
       "Accept": "application/json",
       "X-API-Version": "v2.29.1"  # Include API version
   }
   ```

2. **Handle pagination correctly:**
   ```python
   params = {
       "page": page_number,
       "pagesize": items_per_page  # Usually 100 is optimal
   }
   ```

3. **Handle token expiration:**
   If you receive a 401 Unauthorized response, refresh your token and retry the request.

4. **Process different response formats:**
   The API may return data as a list or as a dictionary with a "data" key.

## Testing Core Endpoints

### Inventory Endpoint

```python
def test_inventory(api_url, access_token):
    """Test the inventory endpoint"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.get(
        f"{api_url}/inventory",
        headers=headers,
        params={"page": 1, "pagesize": 1}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully retrieved inventory data")
        return data
    else:
        print(f"Failed to retrieve inventory: {response.status_code}")
        print(response.text)
        return None
```

### Articles (Products) Endpoint

```python
def test_articles(api_url, access_token):
    """Test the articles endpoint"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.get(
        f"{api_url}/article",
        headers=headers,
        params={"page": 1, "pagesize": 1}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully retrieved article data")
        return data
    else:
        print(f"Failed to retrieve articles: {response.status_code}")
        print(response.text)
        return None
```

### Sales Endpoint

```python
def test_sales(api_url, access_token):
    """Test the sales endpoint"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.get(
        f"{api_url}/sale",
        headers=headers,
        params={"page": 1, "pagesize": 1}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully retrieved sales data")
        return data
    else:
        print(f"Failed to retrieve sales: {response.status_code}")
        print(response.text)
        return None
```

## Subscription Level Considerations

If you're having trouble accessing certain endpoints, it might be due to your subscription level:

1. **Basic Subscription**: May only include access to inventory and product data
2. **Standard Subscription**: May include sales data
3. **Premium Subscription**: May include all endpoints

Contact ProHandel support to confirm which endpoints are available with your subscription.

## Complete Testing Script

We've created a comprehensive testing script that tries multiple authentication and API URLs to find the working combination for your account:

```bash
python test_prohandel_direct.py
```

This script will:
1. Try multiple authentication URLs
2. Try multiple API base URLs
3. Test the core endpoints needed for CloudStock
4. Save the working configuration for future use

## Next Steps

If you're still experiencing issues:

1. Check your API credentials with ProHandel support
2. Confirm your subscription level includes the endpoints you need
3. Request specific documentation for your subscription level
4. Consider using our Lambda function which handles these edge cases automatically

## Working Configuration

Based on our testing, the following configuration works reliably:

```python
config = {
    "auth_url": "https://auth.prohandel.cloud/api/v4",
    "api_url": "https://linde.prohandel.de/api/v2",
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": "v2.29.1"
    }
}
```
