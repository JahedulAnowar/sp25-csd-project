# Backend API

## How to use
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

```
python3 data-aggregator-test.py
```


## API Response for the user
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
    ]
}
```


