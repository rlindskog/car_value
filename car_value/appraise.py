import requests
from bs4 import BeautifulSoup
from cars import GetCars
import re

class AppraiseCar:
    def __init__(self, car):
        try:
            self.make = car['make']
            self.model = car['model']
            self.cl_price = car['price']
            self.year = car['year']
            self.miles = car['odometer']
            self.start_url = 'http://www.kbb.com/'
            self.cl_url = car['link']
            self.cl_condition = car['condition']
        except:
            pass
        try:
            if self.cl_condition == 'excellent':
                self.condition = 'very-good'
            elif self.cl_condition == 'like new':
                self.condition = 'excellent'
            else:
                self.condition = self.cl_condition
        except:
            self.cl_condition = 'Not Given.'
            self.condition = 'good'
        try:
            self.transmission = car['transmission']
        except:
            self.transmission = 'Not Given.'

    def __call__(self):
        return self.run()

    def run(self):
        kbb_url = self.get_url()
        if kbb_url:
            car_data = self.get_car_data(kbb_url)
            if car_data != None:
                return car_data

    def get_url(self):
        try:
            make_req = self.get_make_req(self.start_url)
            model_req = self.get_model_req(make_req)
            year_req = self.get_year_req(model_req)
            style_req = self.get_styles_req(year_req)
            type_url = self.get_type_url(style_req)
            final_url = self.get_final_url(type_url)
            return final_url
        except:
            pass

    def get_make_req(self, url):
        make_url = url + self.make
        req = requests.get(make_url)
        if req.status_code == 200:
            return req
        else:
            pass

    def get_model_req(self, req):
        model_url = req.url + '/' + self.model
        new_req = requests.get(model_url)
        if req.status_code == 200:
            return new_req
        else:
            pass

    def get_year_req(self, req):
        year_url = req.url + '/' + str(self.year)
        new_req = requests.get(year_url)
        if req.status_code == 200 and year_url != None:
            return new_req
        else:
            pass

    def get_styles_req(self, req):
        try:
            href = '/styles/?intent=trade-in-sell&mileage=%s' % self.miles
            styles_url = req.url + href
            new_req = requests.get(styles_url)
            if req.status_code == 200 and req is not None:
                return new_req
            else:
                pass
        except:
            pass

    def get_type_url(self, req):
        try:
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            options_div = soup.find('div', {'class': 'owners-styles-details'})
            option = options_div.find('div') # random first choice
            specific = option.find('div', {'class': 'style-container'})
            href = specific.find('label', {'class': 'style-radio-label js-style-option'}).get('data-href')
            type_url = 'http://www.kbb.com%s' % href
            return type_url
        except:
            pass

    def get_final_url(self, url):
        condition_param = '&pricetype=trade-in&condition=%s' % self.condition
        modal_stripped = re.sub('&modalview=false', '', url)
        options_stripped = re.sub('options/', '', modal_stripped)
        final_url = options_stripped + condition_param
        return final_url

    def get_car_data(self, kbb_url):
        html = requests.get(kbb_url).text
        soup = BeautifulSoup(html, 'html.parser')
        cash_offer = soup.find('a', {'id': 'instantCashOfferLink'}).get('href')
        kbb_price = int(cash_offer.split('kbbevalue=')[1].split('&kbbvgvalue')[0])
        data = {
            'year': self.year,
            'make': self.make,
            'model': self.model,
            'cl_url': self.cl_url,
            'cl_price': self.cl_price,
            'condition': self.cl_condition,
            'transmission': self.transmission,
            'miles': self.miles,
            'kbb_url': kbb_url,
            'kbb_price': kbb_price
        }
        return data

    def print_data(self):
        data = self.run()
        # print(data)
        if data:
            # print(data['condition'])
            return (
                '''
                ------------------------
                %s %s %s
                Craigslist Item:
                    URL: %s
                        Price: $%s
                        Condition: %s
                        Transmission: %s
                Kelly Blue Book:
                    URL: %s
                    Price: $%s

                Deal Rank: %s
                ------------------------
                '''
                % (
                    str(data['year']),
                    data['make'],
                    data['model'],
                    data['cl_url'],
                    str(data['cl_price']),
                    data['condition'],
                    data['transmission'],
                    data['kbb_url'],
                    str(data['kbb_price']),
                    str(data['kbb_price'] / data['cl_price'])
                )
            )
    def get_other_data(self, url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        kioskModal = soup.find('script', {'id': 'kioskModal'}).next_siblings
        script = list(kioskModal)[1].text
        return script


if __name__ == '__main__':
    query = {
        'region': 'sfbay',
        'make': 'honda',
        'model': 'accord'
    }
    car_appraisal = AppraseCar(query)
    car_appraisal.print_data()
