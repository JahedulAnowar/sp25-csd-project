import boto3, json, requests
from datetime import datetime
from decimal import Decimal

# AWS
dynamodb = boto3.resource("dynamodb")
data_table = dynamodb.Table("PovertyDataCache")
country_table = dynamodb.Table("CountryCodes")
secrets_client = boto3.client("secretsmanager")


def get_country_name(country_code):
    """Get full country name from DynamoDB country codes table"""
    try:
        response = country_table.get_item(Key={"country_code": country_code.upper()})
        if "Item" in response:
            return response["Item"]["country_name"]
        else:
            return country_code
    except Exception as e:
        print(f"Error fetching country name: {e}")
        return country_code


def get_secret():
    """Get API keys from AWS Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId="CHARITY_API_KEY")
        return json.loads(response["SecretString"])
    except Exception as e:
        print(f"Error fetching secrets: {e}")
        raise e


def convert_floats_to_decimal(obj):
    """Recursively convert floats to Decimal for DynamoDB compatibility"""
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def lambda_handler(event, context):
    all_results = []
    page = 1
    per_page = 100

    # Extract country code from API Gateway event
    country_code = event.get("queryStringParameters", {}).get("country", "BGD")
    country_name = get_country_name(country_code)

    # Get API keys from secrets
    secret = get_secret()
    api_key = secret["EVERYORG_API"]

    print(f"Processing request for {country_name} ({country_code})")

    # Check cache in DynamoDB
    try:
        response = data_table.get_item(Key={"country": country_code})
        if "Item" in response:
            cached = response["Item"]
            current_timestamp = int(datetime.now().timestamp())
            # If data is fresh (<1 day), return cached
            if (current_timestamp - cached["timestamp"]) < 86400:
                print("Returning cached data")
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": json.dumps(cached["data"], default=str),
                }
    except Exception as e:
        print(f"Error checking cache: {e}")

    # Retrieve Poverty Data
    pip_url = f"https://api.worldbank.org/pip/v1/pip?country={country_code}&year=all&povline=2.15&format=json"
    print(f"Fetching poverty data from: {pip_url}")

    try:
        pip_response = requests.get(pip_url, timeout=30)
        if pip_response.status_code == 200 and pip_response.text.strip():
            pip_resp = pip_response.json()
            print(
                f"Successfully fetched poverty data: {len(pip_resp) if isinstance(pip_resp, list) else 'single object'}"
            )
        else:
            print(f"No poverty data available (status: {pip_response.status_code})")
            pip_resp = []
    except Exception as e:
        print(f"Error fetching poverty data: {e}")
        pip_resp = []

    # Retrieve Non-profit organisation Data
    try:
        while True:
            non_profit_url = f"https://partners.every.org/v0.2/browse/poverty?apiKey={api_key}&take={per_page}&page={page}"
            response = requests.get(non_profit_url, timeout=30)

            if response.status_code != 200:
                print(f"Every.org API Error: {response.status_code} - {response.text}")
                break

            data = response.json()
            nonprofits = data.get("nonprofits", [])
            if not nonprofits:
                break

            all_results.extend(nonprofits)
            print(f"Fetched page {page}, total organizations: {len(all_results)}")

            # Stop if we've reached the last page
            pagination = data.get("pagination", {})
            if page >= pagination.get("pages", page):
                break

            page += 1

            if page > 50:
                print("Reached maximum page limit (50)")
                break

    except Exception as e:
        print(f"Error fetching nonprofit data: {e}")

    # Filter Nonprofits by country in location and description fields
    country_results = [
        org
        for org in all_results
        if country_name.lower() in str(org.get("description", "")).strip().lower()
        or country_name.lower() in str(org.get("location", "")).strip().lower()
    ]

    print(f"Found {len(country_results)} nonprofits for {country_name}")

    # Aggregate data for the response
    result = {
        "country": {"name": country_name, "code": country_code},
        "poverty_data": pip_resp,
        "nonprofits": [
            {
                "name": org.get("name"),
                "description": org.get("description"),
                "website": org.get("websiteUrl"),
                "location": org.get("location"),
                "tags": org.get("tags", []),
                "profileUrl": org.get("profileUrl"),
                "logoUrl": org.get("logoUrl"),
                "coverImageUrl": org.get("coverImageUrl"),
                "matchedByLocation": country_name.lower()
                in str(org.get("location", "")).strip().lower(),
                "matchedByDescription": country_name.lower()
                in str(org.get("description", "")).strip().lower(),
            }
            for org in country_results
        ],
        "summary": {
            "total_nonprofits_found": len(country_results),
            "total_poverty_data_years": (
                len(pip_resp) if isinstance(pip_resp, list) else 1
            ),
            "generated_at": datetime.now().isoformat(),
        },
    }

    # Save to DynamoDB cache
    try:
        dynamo_result = convert_floats_to_decimal(result)
        data_table.put_item(
            Item={
                "country": country_code,
                "timestamp": int(datetime.now().timestamp()),
                "data": dynamo_result,
            }
        )
        print("Successfully cached result in DynamoDB")
    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")

    # Return JSON response
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(result, default=str),
    }
