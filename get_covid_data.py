import requests
import time
from datetime import datetime
import json
import eventlet

class CovidDataGetter:

    def __init__(self):
        self.all_data = dict()

    def get_data(self):
        try:
            summary_data_response = requests.get('https://api.covid19api.com/summary', timeout=(2, 3))
        except:
            return False
        json_summary_data = json.loads(summary_data_response.text)

        for number in json_summary_data['Countries']:
            if number['Slug'] == 'russia':
                self.all_data['total_cases'] = number['TotalConfirmed']
                self.all_data['total_deaths'] = number['TotalDeaths']
                self.all_data['total_recovered'] = number['TotalRecovered']

                self.all_data['new_confirmed'] = number['NewConfirmed']
                self.all_data['new_deaths'] = number['NewDeaths']
                self.all_data['new_recovered'] = number['NewRecovered']

                moscow_delta = 14400

                z_time_update = number['Date']
                z_time_update_timestamp = time.mktime(datetime.strptime(z_time_update, "%Y-%m-%dT%H:%M:%SZ").timetuple())
                moscow_update_timestamp = int(z_time_update_timestamp + moscow_delta)
                self.all_data['update_time'] = datetime.fromtimestamp(moscow_update_timestamp).strftime('%d.%m.%Y %H:%M:%S')

                return True

    def make_str(self):
        out_string = f'Информация о COVID-19 в России 🇷🇺:\n\n' \
                     f'🦠 Всего случаев: {self.all_data["total_cases"]} (+{self.all_data["new_confirmed"]})\n' \
                     f'💀 Смертей: {self.all_data["total_deaths"]} (+{self.all_data["new_deaths"]})\n' \
                     f'💊 Выздоровело: {self.all_data["total_recovered"]} (+{self.all_data["new_recovered"]})\n' \
                     f'⏳ Время последнего обновления по Москве: {self.all_data["update_time"]}'
        return out_string
