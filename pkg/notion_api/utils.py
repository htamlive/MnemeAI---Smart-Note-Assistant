# from torch import Tensor
# from transformers import AutoTokenizer, AutoModel
# from torch import no_grad
from typing import List
from config import config
import requests

def generate_embeddings(prompt:str | List[str]) -> List[List[float]] | None:    
    # Set your API key
    api_key = config.OPENAI_API_KEY
    
    # Define the endpoint and headers
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Define the payload
    payload = {
        "input": prompt,
        "model": "text-embedding-ada-002"
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the embeddings from the response
        embeddings = [item['embedding'] for item in data['data']]
        
        return embeddings
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []