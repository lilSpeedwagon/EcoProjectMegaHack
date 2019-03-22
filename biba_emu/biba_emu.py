import json
from multiprocessing import Pool
import random
import time
import requests
from pprint import pprint 
from datetime import datetime


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
        
        self.t = self.t + random.uniform((-(Biba.t_min - Biba.t_max)/2)*0.05,
                                        ((Biba.t_min - Biba.t_max)/2)*0.05)
        self.t = round(self.t, 2)
        self.t = self.clip(self.t, Biba.t_min, Biba.t_max)
        
        self.h = self.h + random.uniform((-(Biba.h_min - Biba.h_max)/2)*0.05,
                                        ((Biba.h_min - Biba.h_max)/2)*0.05)
        self.h = round(self.h, 2)
        self.h = self.clip(self.h, Biba.h_min, Biba.h_max)


    def get_data(self):
        return {
            'biba_id':self.biba_id,
            'temperature':self.t,
            'y':self.y,
            'x':self.x
        }

def biba_sim(biba_id):
    
    access_data = {
        "token":"ALBEdMNS0iaTTOhfzju1sQk"
    }

    work_time = 20
    sleep_time = 1

    start_time = time.time()
    biba = Biba(biba_id)
    response = requests.get('https://xyz.api.here.com/hub/spaces/{space_id}/iterate'.format(space_id = '4WAJKc2S'), params={'access_token':access_data['token']})
    feature_table = json.loads(response.content)

    features_json = {
        "type": "Feature",
        "geometry":
        {
            "type": "Point",
            "coordinates":
            [
                biba.x,
                biba.y
            ]
        },
        "properties":
        {
            "biba_id":biba_id,
            "temperature":biba.t,
            "humidity":biba.h,
            "t_list":[{"val":biba.t,"time":datetime.today().strftime("%Y-%m-%d-%H.%M.%S")}],
            "h_list":[{"val":biba.h,"time":datetime.today().strftime("%Y-%m-%d-%H.%M.%S")}],
            "noise":0,
        }
    }
    flag = True
    for feature in feature_table['features']:
        if biba_id == feature['properties']['biba_id']:
            id_ = feature['id']
            flag = False
            break
    if flag:
        response = requests.put('https://xyz.api.here.com/hub/spaces/{space_id}/features'.format(space_id = '4WAJKc2S'), json = features_json, params={'access_token':access_data['token']})
        id_ = json.loads(response.content)['features'][0]['id']

    while(time.time() - start_time<=work_time):
        
        biba.randomize()
        
        response = requests.get('https://xyz.api.here.com/hub/spaces/{space_id}/features/{feature_id}'.format(space_id = '4WAJKc2S', feature_id = id_), params={'access_token':access_data['token']})
        content = json.loads(response.content)
        pprint(content)
        try:
            h_list = content['properties']['h_list']
            h_list.append({"val":biba.h, "time":datetime.today().strftime("%Y-%m-%d-%H.%M.%S")})
            if len(h_list) > 100:
                h_list.pop(0)
            t_list = content['properties']['t_list']
            t_list.append({"val":biba.t, "time":datetime.today().strftime("%Y-%m-%d-%H.%M.%S")})
            if len(t_list) > 100:
                t_list.pop(0)
        except Exception as e:
            print(e)
            h_list = [{"val":biba.h,"time":datetime.today().strftime("%Y-%m-%d-%H.%M.%S")}]
            t_list = [{"val":biba.t,"time":datetime.today().strftime("%Y-%m-%d-%H.%M.%S")}]    
        features_json = {
            "type": "Feature",
            "geometry":
            {
                "type": "Point",
                "coordinates":
                [
                    biba.x,
                    biba.y
                ]
            },
            "properties":
            {
                "biba_id":biba_id,
                "temperature":biba.t,
                "t_list":t_list,
                "h_list":h_list,
                "humidity":biba.h,
                "noise":0,
            }
        }
        response = requests.put('https://xyz.api.here.com/hub/spaces/{space_id}/features/{feature_id}'.format(space_id = '4WAJKc2S', feature_id = id_), json = features_json, params={'access_token':access_data['token']})
        time.sleep(sleep_time)

if __name__ == '__main__':
    
    with open('access_data.json') as f:
        access_data = json.load(fp = f)

    new_space ={
        'title':'demo',
        'description':'hello'
    }

    #response = requests.post('https://xyz.api.here.com/hub/spaces', params={'access_token':access_data['token']}, json = new_space)
    #print(response.content)


    #response = requests.get('https://xyz.api.here.com/hub/spaces/{space_id}/iterate'.format(space_id = '4WAJKc2S'), params={'access_token':access_data['token']})
    #pprint(json.loads(response.content))


    #response = requests.get('https://xyz.api.here.com/hub/spaces/{space_id}/features/aXe8SZzr44'.format(space_id = '4WAJKc2S'), params={'access_token':access_data['token']})
    #print(response.content)
    bibas_num = 80
    pool = Pool(bibas_num)
    pool.map(biba_sim, range(bibas_num))
    biba_sim(0)