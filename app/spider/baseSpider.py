import requests


class BaseSpider:
    def __init__(self):

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
        }

        with requests.session() as session:
            self.session = session
            self.cookie = session.cookies

    def build_headers(self, headers):
        for key, value in headers.items():
            self.headers[key] = value

    def get_html(self, url, method, data=None, **kwargs):
        response = None
        # print('request url: %s with cookie:%s' % (url, dict(self.session.cookies)))

        if method == 'GET':
            response = self.session.get(url, headers=self.headers, **kwargs)
        elif method == 'POST':
            # print('post data: %s' % data)
            response = self.session.post(url, data=data, headers=self.headers, **kwargs)

        return response


if __name__ == '__main__':
    spider = BaseSpider()
    spider.get_html('http://www.baidu.com', 'GET')
    print(spider.headers)
    spider.get_html('http://www.baidu.com', 'GET', cookies={})
