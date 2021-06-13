from datetime import datetime
from datetime import timedelta
from datetime import date
import requests
import json
import re
import os
import pickle

class Client():
    URL = 'https://enlighten.enphaseenergy.com'

    def __init__(self, utc_offset=-5, time_step=15,
            persist_session=False, session_file='enphase_cookie.p', 
            persist_config=False, config_file='enphase_config.p'):
        self.system_id = None
        self.csrf_token = ''
        self.cookies = None
        self.power_data = {}
        self.raw_data = {}
        
        self.persist_session = persist_session
        self.cookie_file = session_file
        self.persist_config = persist_config
        self.config_file = config_file
        
        # NOTE: our time axis should start at local solar midnight
        # and have units of minutes past UTC midnight
        self.utc_offset = utc_offset
        self.time_step = time_step
        self.minute_axis = _range(-utc_offset*60, (24-utc_offset)*60, time_step)
        
        if not self.load_session():
            return
        if not self.load_config():
            self.fetch_config()
    
    def login(self, username, password, force=False):
        if force:
          self.cookies = None
        if self.cookies is not None:
          return
        self.fetch_csrf()
        self.post_login(username, password)
        self.save_session()
        self.fetch_config()

    def fetch_csrf(self):
        resp = requests.get(self.URL)
        csrf_pattern = 'name="authenticity_token" value="(\S+)"'
        csrf_match = re.search(csrf_pattern, resp.text)
        if csrf_match is None:
            return
        self.csrf_token = csrf_match[1]

    def post_login(self, username, password):
        path = '/login/login'
        params = {
            'user[email]': username,
            'user[password]': password,
            'authenticity_token': self.csrf_token,
            'commit': 'Sign In',
            'utf8': '✓'
        }
        headers = {
            'origin': 'https://enlighten.enphaseenergy.com',
            'referer': 'https://enlighten.enphaseenergy.com/'
        }
        resp = requests.post(self.URL+path, data=params, headers=headers, allow_redirects=False)
        self.cookies = resp.cookies
    
    def save_session(self):
        if not self.persist_session:
            return
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        pickle.dump( self.cookies, open( self.cookie_file, "wb" ) )
    
    def load_session(self):
        if not os.path.exists(self.cookie_file):
            return False
        self.cookies = pickle.load(open( self.cookie_file, "rb" ))
        return self.cookies != None
    
    def fetch_config(self, force=False):
        if self.system_id is not None:
            return
        self.fetch_system_id()
        self.fetch_layout()
        self.save_config()

    def fetch_system_id(self):
        resp = requests.get(self.URL, cookies=self.cookies, allow_redirects=False)
        self.system_id = re.search('https://\S+/systems/(\S+)', resp.headers['location'])[1]

    def fetch_layout(self):
        path = f'/systems/{self.system_id}/site_array_layout_x'
        resp = requests.get(self.URL + path, cookies=self.cookies)
        arr = resp.json()
        # NOTE: sort by position along x
        self.modules = sorted(arr['arrays'][0]['modules'], key= lambda x: x['x'])
        self.device_index = [ m['inverter']['inverter_id'] for m in self.modules ]
    
    def save_config(self):
        if not self.persist_config:
            return
        c_data = {
            'system_id': self.system_id,
            'device_index': self.device_index
        }
        pickle.dump( c_data, open( self.config_file, "wb" ) )

    def load_config(self):
        if not os.path.exists(self.config_file):
            return False
        c_data = pickle.load(open( self.config_file, "rb" ))
        self.system_id = c_data['system_id']
        self.device_index = c_data['device_index']
        return True

    def time_axis(self, start):
        mins = self.minute_axis
        return [ start + timedelta(minutes=int(m)) for m in mins ]

    def get_day(self, date):
        date_str = date.strftime('%Y-%m-%d')
        path = f'/systems/{self.system_id}/inverter_data_x/time_series.json'
        params = {'date': date_str}
        return requests.get(self.URL + path, params=params, cookies=self.cookies).json()

    def fetch_day(self, date):
        date_key = date.strftime('%Y-%m-%d')
        self.power_data[date_key] = self.process_day(self.get_day(date))

    def inverter_details(self, date):
        # { "date": "...", "ch_id": ..., 
        #     "POWR":[[<time>, <power>, <???>],...],
        #     "DCV": [[<time>,<voltage>],...],
        #     "DCA": [[<time>,<current>,...]],
        #     "ACV": [[<time>,<voltage>],...],
        #     "ACHZ": [[<time>,<freq>],...],
        #     "TMPI": [[<time>,<temp_c>],...],
        #     "stat_info": {}
        # }
        pass

    def process_day(self, raw_data):
        raw_data.pop('haiku')
        date = raw_data.pop('date')
        start_ts = (
            datetime.strptime(date, '%Y-%m-%d')+
            timedelta(minutes=self.minute_axis[0])
            ).timestamp()
        
        # data -> { '<dev_id>': { 'POWR' [<time>, <power>, <max_pwr>] }, ... }
        self.device_index = list(raw_data.keys())
        data = []
        for i, p_id in enumerate(raw_data.keys()):
            panel_data = [0]*len(self.minute_axis)
            for sample in raw_data[p_id]['POWR']:    
                j = int((sample[0] - start_ts) / (self.time_step*60))
                panel_data[j]= sample[1]
            data.append(panel_data)
        return data

    def device_data(self, date, device_id):
        date_key = date.strftime('%Y-%m-%d')
        ds = datetime(date.year,date.month,date.day)
        if self.power_data.get(date_key, None) is None:
            self.fetch_day(ds)
        if device_id not in self.device_index:
            return None
        i = self.device_index.index(device_id)
        return self.time_axis(ds), self.data[date_key][i]
    
    def system_data(self, date, transpose=False):
        date_key = date.strftime('%Y-%m-%d')
        ds = datetime(date.year,date.month,date.day)
        if self.power_data.get(date_key, None) is None:
            self.fetch_day(ds)
        if transpose:
            return self.time_axis(ds), _transpose(self.power_data[date_key])
        else:
            return self.time_axis(ds), self.power_data[date_key]

    def array_power(self, time):
        times, powers = self.system_data(time, transpose=True)
        time_id = self.time_index(time)
        return times[time_id], powers[time_id]

    def system_totals_data(self, date):
        date_key = date.strftime('%Y-%m-%d')
        if self.power_data.get(date_key, None) is None:
            self.fetch_day(date)
        return self.time_axis(date), [sum(d) for d in self.power_data[date_key]]
    
    def time_index(self, time):
        ds = datetime(time.year,time.month,time.day)
        return round((time-ds).total_seconds() / (self.time_step*60))


# NOTE: basic list handling, allows us to swap in numpy later
def _transpose(l):
    tl = list(zip(*l))
    return tl #[list(tt) for tt in tl ]

def _zeros(a,b):
    return [[0]*a]*b

def _range(a,e,s):
    return range(a,e,s)

'''Standard API'''
class enlightenAPI:

    def __init__(self, config):
        '''
        Initialize the englightAPI class
            Parameters:
                The API configuration (as a dictionary). Must contain api_url, site_id, api_key, and user_id
        '''
        self.config = config

    def __log_time(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S') + ": "

    def __get_authenticated_url(self, route:str):
        '''
        Private class function to get the API url that includes all the authentication params from the local config
            Parameters:
                route (string): the intended route to run (e.g.: summary, stats, inventory, etc)
            Returns:
                The enlighten API expected API url including user/app authentication info
        '''

        # This url more or less looks like this: https://api.enphaseenergy.com/api/v2/systems/:SITE_ID/summary?key=:API_KEY&user_id=:USER_ID"
        return f'{self.config["api_url"]}/{self.config["site_id"]}/{route}?key={self.config["api_key"]}&user_id={self.config["user_id"]}'

    def energy_lifetime(self, start_date:str = None, end_date:str = None):
        '''
        Run the enlighten API energy_lifetime route (https://developer.enphase.com/docs#energy_lifetime). This route
        gets the energy produced for each day (?) over the life of the system.
            Parameters:
                start_date (string):    start date to get a specific energy summary, formatted as 2010-09-17.
                                        If no date is provided, get the summary for all time.
                end_date (string):      end date to get a specific energy summary, formatted as 2010-09-17.
                                        If no date is provided, get the summary for all time.
            Returns:
                The enlighten summary for the system
        '''
        date_range = ""
        if start_date is not None or end_date is not None:
            date_range = f'&start_date={start_date}&end_date={end_date}'

        url = f'{self.__get_authenticated_url("energy_lifetime")}{date_range}'
        result = requests.get(url)
        return json.loads(result.text)

    def inventory(self):
        '''
        Run the enlighten API inventory route (https://developer.enphase.com/docs#inventory). This route
        gets all envoys and inverters in the system.
            Returns:
                The enlighten system inventory summary of all assets
        '''
        url = f'{self.__get_authenticated_url("inventory")}'
        result = requests.get(url)
        return json.loads(result.text)

    def inverter_summary(self):
        '''
        Run the enlighten API inverters_summary_by_envoy_or_site route (https://developer.enphase.com/docs#inverters_summary_by_envoy_or_site).
        This route returns the detailed information for each inverter (including lifetime power produced). Note: if your Envoy is connected via low
        bandwidth Cellular, data only refreshes to Enlighten every 6 hours. So perform this route the next day in the early morning to ensure you get
        complete data.
            Returns:
                The enlighten summary for the system
        '''
        print(self.__log_time() + "Pulling EnlightenAPI inverter summary...")
        url = f'{self.config["api_url"]}/inverters_summary_by_envoy_or_site?key={self.config["api_key"]}&user_id={self.config["user_id"]}&site_id={self.config["site_id"]}'
        result = requests.get(url)
        return json.loads(result.text)

    def summary(self, summary_date:str = None):
        '''
        Run the enlighten API summary route (https://developer.enphase.com/docs#summary)
            Parameters:
                summary_date (string):  date to get a specific summary, formatted as 2010-09-17.
                                        If no date is provided, get the summary for the current day.
            Returns:
                The enlighten summary for the system
        '''
        if summary_date is None:
            summary_date = date.today().strftime("%Y-%m-%d")
        url = f'{self.__get_authenticated_url("summary")}&summary_date={summary_date}'
        result = requests.get(url)
        return json.loads(result.text)

    def stats(self):
        '''
        Run the enlighten API stats route (https://developer.enphase.com/docs#stats)
            Returns:
                The enlighten summary for the system
        '''
        url = f'{self.__get_authenticated_url("stats")}'
        result = requests.get(url)
        return json.loads(result.text)
