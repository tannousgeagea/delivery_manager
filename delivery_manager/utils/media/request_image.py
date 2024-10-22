
import logging
import requests

def send_request(url:str, params:dict):
    try:    
        headers = {
            'accept': 'application/json'
        }
        
        response = requests.post(url, headers=headers, params=params, data={})
        return response.json()
    
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP Error start video generation: {err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An error occurred: {req_err}")
        return None
    except Exception as err:
        logging.error(f"Error start video generation: {err}")
        return None