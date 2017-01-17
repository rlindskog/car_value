import requests
from bs4 import BeautifulSoup
from threading import Thread
import json

class GetCars:
    def __init__(self, query):
        self.region = query['region']
        self.url = 'http://%s.craigslist.org' % self.region
        self.params = {}
        self.make_params(query)
    def __call__(self):
        return self.run()

    def run(self):
        for page in self.get_page_link():
            for car in page:
                yield car
        print('All done')
        
    def make_params(self, query):
        try:
            if query['make'] and not query['model']:
                self.params['auto_make_model'] = query['make']
            elif query['model'] and not query['make']:
                self.params['auto_make_model'] = query['model']
            elif query['make'] and query['model']:
                self.params['auto_make_model'] = query['make'] + ' ' + query['model']
        except:
            pass

    def get_page_link(self):
        page_num = 1
        while True:
            self.params['s'] = page_num * 100
            page_num += 1
            return self.get_car_link(self.params)

    def get_car_link(self, params):
        new_url = self.url + '/search/cta'
        html = requests.get(new_url, params=params).text
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find('ul', {'class': 'rows'})
        for result in rows.find_all('li', {'class': 'result-row'}):
            # image = result.find('img').get('src')
            info = result.find('p', {'class': 'result-info'})
            # title = info.find('a', {'class': 'result-title'}).text
            result_url = self.url + info.find('a', {'class': 'result-title'}).get('href')
            yield self.get_car_details(result_url)

    def get_car_details(self, url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        # title = soup.find('title').text
        postingtitle = soup.find('span', {'class': 'postingtitletext'})
        car_details = {'link': url}
        try:
            price = postingtitle.find('span', {'class': 'price'}).text.split('$')[1]
            car_details['price'] = int(price)
        except:
            pass
        try:
            location = postingtitle.find('small').text[2:-1]
            car_details['location'] = location
        except:
            pass
        try:
            mapAndAttrs = soup.find('div', {'class', 'mapAndAttrs'})
            title = mapAndAttrs.find('span').text
            try:
                car_details['title'] = title
                title_list = title.split(' ')
                year = int(title_list[0])
                make = title_list[1]
                model = title_list[2]
                car_details['year'] = year
                car_details['make'] = make
                car_details['model'] = model
            except Exception as e:
                pass
            for span in mapAndAttrs.find_all('span')[1:]:
                try:
                    kv = span.text.split(': ')
                    key = kv[0]
                    value = kv[1]
                    car_details[key] = value
                except:
                    continue
        except:
            pass
        yield car_details

    def get_continent(self):
        continent_url = self.url + '/#%s' % self.continent

    def get_available_regions(self):
        html = requests.get(self.url).text
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('section', {'class': 'body'})
        continent_list = body.find_all('h1')
        colmask_list = body.find_all('div', {'class': 'colmask'})
        continent_list_length = len(continent_list)

        available_regions = {}
        for i in range(continent_list_length):
            continent = continent_list[i].text
            available_regions[continent] = {}
            colmask = colmask_list[i]
            for box in colmask.find_all('div', {'class': 'box'}):
                state_list = box.find_all('h4')
                ul_list = box.find_all('ul')
                state_list_length = len(state_list)
                for i in range(state_list_length):
                    state = state_list[i].text
                    available_regions[continent][state] = {}
                    ul = ul_list[i]
                    for region in ul.find_all('li'):
                        link = str(region.find('a')['href'])
                        region = region.text
                        available_regions[continent][state][region] = link
        with open('regions.json', 'w') as f:
            f.write(json.dumps(available_regions))
        return available_regions

if __name__ == '__main__':
    query = {'region': 'sfbay', 'make': 'honda', 'model': 'accord'}
    myCar = GetCars(query)
    for car in myCar.run():
        print(car)
