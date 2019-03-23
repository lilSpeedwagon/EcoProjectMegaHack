import json
import random
import requests
from pprint import pprint 
from datetime import datetime
from bottle import route
import bottle    
class Biba():
    
    #magic numbers are corner coordinates of Saint-Petersburg
    y_min = 59.85115
    y_max = 60.02331

    x_min = 30.16413
    x_max = 30.50722

    t_min = 10
    t_max = 25

    h_min = 0
    h_max = 90
    

    @staticmethod
    def clip(val,min_, max_):
        if val>max_:
            return max_

        elif val<min_:
            return min_
        
        else:
            return val


    @staticmethod
    def gaussian(min_, max_):
        return random.gauss(min_ + (max_-min_)/2,(max_-min_)*0.5)

    def __init__(self, biba_id):
        self.biba_id = biba_id
        self.x = random.uniform(Biba.x_min, Biba.x_max)
        self.y = random.uniform(Biba.y_min, Biba.y_max)
        self.t = round(self.gaussian(Biba.t_min, Biba.t_max), 2)
        self.h = round(self.gaussian(Biba.t_min, Biba.t_max), 2)

    def randomize(self):
        
        self.t = self.t + random.uniform((-(Biba.t_min - Biba.t_max)/2)*0.1,
                                        ((Biba.t_min - Biba.t_max)/2)*0.1)
        self.t = round(self.t, 2)
        self.t = self.clip(self.t, Biba.t_min, Biba.t_max)
        
        self.h = self.h + random.uniform((-(Biba.h_min - Biba.h_max)/2)*0.1,
                                        ((Biba.h_min - Biba.h_max)/2)*0.1)
        self.h = round(self.h, 2)
        self.h = self.clip(self.h, Biba.h_min, Biba.h_max)


    def get_data(self):
        return {
            'biba_id':self.biba_id,
            'temperature':self.t,
            'y':self.y,
            'x':self.x
        }

def current_time():
    dt = datetime.now()
    t = {
        's':dt.second,
        'mi':dt.minute,
        'h':dt.hour,
        'd':dt.day,
        'mo':dt.month,
        'y':dt.year
    }
    return t

if __name__ == '__main__':

    with open('access_data_server.json') as f:
        access_data = json.load(fp = f)

    if not 'space_id' in access_data:
        features_json = {
                        "type": "Feature",
                        "geometry":
                        {
                            "type": "Point",
                            "coordinates":
                            [
                                0,
                                0
                            ]
                        },
                        "properties":
                        {
                            "biba_id":-1,
                            "temperature":None,
                            "t_list":[],
                            "h_list":[],
                            "humidity":None,
                            "noise":0,
                        }
                    }

        new_space ={
            'title':'hack_university_device',
            'description':'An array of map points made by simulation program'
        }

        response = requests.post('https://xyz.api.here.com/hub/spaces', params={'access_token':access_data['token']}, json = new_space)
        space_id = json.loads(response.content)['id']
        response = requests.put('https://xyz.api.here.com/hub/spaces/{space_id}/features'.format(space_id = space_id), json = features_json, params={'access_token':access_data['token']})
        pprint(json.loads(response.content))
        feature_id = json.loads(response.content)['features'][0]['id']

        with open('access_data_server.json','w') as f:
            access_data = {
                'token':access_data['token'],
                'space_id':space_id,
                'feature_id':feature_id
            }
            json.dump(access_data, f, indent=2)
 
    space_id = access_data['space_id']
    feature_id = access_data['feature_id']

    @route('/data/<data>')
    def index(data):
        dat = json.loads(data)

        response = requests.get('https://xyz.api.here.com/hub/spaces/{space_id}/features/{feature_id}'.format(space_id = space_id, feature_id = feature_id), params={'access_token':access_data['token']})
        content = json.loads(response.content)
        try:
            h_list = content['properties']['h_list']
            h_list.append({"val":dat['h'], "time":current_time()})
            if len(h_list) > 10:
                h_list.pop(0)
            t_list = content['properties']['t_list']
            t_list.append({"val":dat['t'], "time":current_time()})
            if len(t_list) > 10:
                t_list.pop(0)
        except Exception as e:
            print(e)
            h_list = [{"val":dat['h'],"time":current_time()}]
            t_list = [{"val":dat['t'],"time":current_time()}]    
        features_json = {
            "type": "Feature",
            "geometry":
            {
                "type": "Point",
                "coordinates":
                [
                    dat['x'],
                    dat['y']
                ]
            },
            "properties":
            {
                "biba_id":dat['id'],
                "temperature":dat['t'],
                "t_list":t_list,
                "h_list":h_list,
                "humidity":dat['h'],
                "noise":0,
            }
        }
        response = requests.put('https://xyz.api.here.com/hub/spaces/{space_id}/features/{feature_id}'.format(space_id = space_id, feature_id = feature_id), json = features_json, params={'access_token':access_data['token']})     
        return ('OK')

    bottle.run(host='192.168.184.1', port=8056)