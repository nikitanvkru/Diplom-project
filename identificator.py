import requests

if __name__ == '__main__':
  response = requests.get('http://localhost:50000')
  most_common_breed = response.json()['label']
  print(most_common_breed)
