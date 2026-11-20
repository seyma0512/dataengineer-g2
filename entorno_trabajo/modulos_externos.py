import requests

# Metodos disponibles: GET, POST, PUT, DELETE
response = requests.get("https://jsonplaceholder.typicode.com/users")
data = response.json()