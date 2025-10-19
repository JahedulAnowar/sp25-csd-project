# Backend API

## AWS API URL
Change _<country_code>_ to appropriate ISO code from json file _country-codes.json_.
```
https://lvuxh1wgz6.execute-api.us-east-1.amazonaws.com/prod?country=<country-code>
```

Add _x-api-key_ as a **Header** with the request.

### cURL command for testing
Windows:
```
curl.exe -i "https://lvuxh1wgz6.execute-api.us-east-1.amazonaws.com/prod?country=BGD" -H "x-api-key: ptBqdW6nzLavUqUPpEa5530vVQFWz8TKaoYFYthO" -H "Accept: application/json"
```

Linux:
```{bash}
curl -i "https://lvuxh1wgz6.execute-api.us-east-1.amazonaws.com/prod?country=BGD" \
  -H "x-api-key: ptBqdW6nzLavUqUPpEa5530vVQFWz8TKaoYFYthO" \
  -H "Accept: application/json"
```

### API Response for the user
_'api-response.json'_ file contains example reponse for Bangladesh(BGD).
```
json
{
    "country": {
        "name": "Bangladesh",
        "code": "BGD"
    },
    "poverty_data": [
        {},
        {}
    ],
    "nonprofits": [
        {},
        {}
    ],
    "summary": {
        "total_nonprofits_found": "5",
        "total_poverty_data_years": "10",
        "generated_at": "2025-10-03T18:59:19.847255"
    }
}
```

________________________________________________________________________________________________

## How to use test script for local testing
Create a virutal environment
```
python3 -m venv venv
```

Activate the environment
```
source venv/bin/activate         
```

Install dependencies
```
pip3 install requests python-dotenv
```

## Configure Environment
Change directory to 'backend-api' and copy `.env.example` to `.env` and fill in your API Key and country code.

Create _API key_ from https://www.every.org/developer.

Check _'country-codes.json'_ file for data fetching.

## Run the code
To test data aggregation locally:
```
python3 data-aggregator-test.py
```

## Update CountryCodes via CloudShell in Deployment

1. Upload files `country-codes.json` and `setup-dynamodb-countries-cs.py` cloudshell
2. Run command `python setup-dynamodb-countries-cs.py` to create and populate the _CountryCodes_ table.