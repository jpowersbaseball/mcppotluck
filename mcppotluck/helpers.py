# 3rd-party imports
import requests
from requests.exceptions import HTTPError

mlbstatsapipref = 'http://statsapi.mlb.com/api/v1/'

def get_mlb_stats(
    endpoint: str
):
    """
    Request JSON from an MLB statsapi endpoint, return the JSON
    
    Args:
        endpoint (str): The endpoint to request, assumed to include all parts of the URL
    
    Returns:
        dict: The results of parsing the JSON response
    """
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
        return jsonResponse

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
