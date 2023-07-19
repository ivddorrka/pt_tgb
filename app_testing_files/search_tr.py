import requests

url = 'http://127.0.0.1:5000/search_posts_by_tags'  # Replace with the URL of your Flask app's endpoint
search_query = 'tag1'
params = {'query': search_query}

response = requests.get(url, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.content)
    
    
    
    
# url2 = 'http://127.0.0.1:5000/search_posts_by_descs'  # Replace with the URL of your Flask app's endpoint
# search_query = 'Description'
# params = {'query': search_query}

# response = requests.get(url2, params=params)

# if response.status_code == 200:
#     print(response.json())
# else:
#     print(f"Request failed with status code: {response.status_code}")
#     print(response.content)
    
    