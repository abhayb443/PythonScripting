import requests


# response = requests.get('https://places.ls.hereapi.com/places/v1/discover/explore?at=37.7942%2C-122.4070&apiKey=FGty7TOmcc_8z8-YEWrSV9OEQonoC0Ghd8mHO_RBJpw')
#
# print(response)
#
# print(response.headers)
#
# print(response.headers['content-type'])
#
# print(response.status_code)
#
# print(response.content)
#
# print(response.text)
#
# print(response.json())
#
# print(response.request.url)
#
# print(response.request.body)

from requests.auth import HTTPBasicAuth
from getpass import getpass

import timeit
from requests.adapters import HTTPAdapter

def with_func():
    with requests.session() as session:
        st = timeit.timeit()
        api_key = 'FGty7TOmcc_8z8-YEWrSV9OEQonoC0Ghd8mHO_RBJpw'
        response = session.get('https://places.ls.hereapi.com/places/v1/discover/explore?at=37.7942%2C-122.4070&apiKey={}'.format(api_key))
        ed = timeit.timeit()
        one = ed - st
        return one

def without_func():
    st1 = timeit.timeit()
    api_key = 'FGty7TOmcc_8z8-YEWrSV9OEQonoC0Ghd8mHO_RBJpw'
    response = requests.get('https://places.ls.hereapi.com/places/v1/discover/explore?at=37.7942%2C-122.4070&apiKey={}'.format(api_key))
    ed1 = timeit.timeit()
    two = ed1 - st1
    return two

def max_try():
    github_adapter = HTTPAdapter(max_retries=3)
    # Use `github_adapter` for all requests to endpoints that start with this URL
    session = requests.Session()
    session.mount('https://api.github.com', github_adapter)
    try:
        session.get('https://api.github.com')
    except ConnectionError as ce:
        print(ce)


if __name__=='__main__':
    print(with_func())
    print(without_func())
    print(max_try())