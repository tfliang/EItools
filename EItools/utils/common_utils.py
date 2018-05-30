import requests


def iterate_pages(callback, payload, is_list=True, total=None, k_data="results", k_total="size", size=100):
    offset = 0
    if is_list:
        assert total is not None
    while True:
        data = callback(payload, offset, size)
        if not is_list:
            total = data[k_total]
            data = data[k_data]
        if total < offset:
            break
        offset += size
        for d in data:
            yield d


def rest_get(url):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    print(url)
    resp = requests.get(url, headers=user_agent)
    return resp


def rest_post(url, data=None):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    print(url)
    resp = requests.post(url, headers=user_agent, data=data)
    return resp


def exception_handler(iterator):
    while True:
        try:
            yield next(iterator)
        except StopIteration:
            raise
        except Exception as e:
            print(e)
            pass


def printf(f, *args):
    print(f.format(*args))
