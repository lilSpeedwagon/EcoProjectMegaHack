import json
from multiprocessing import Process
import random
import time
import requests
from pprint import pprint 
from datetime import datetime
import aiohttp
import asyncio
    
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

    def ones(self):
        r = random.uniform(0,1)
        if r > 0.95:
            return 1
        else:
            return 0 
        

    def __init__(self, biba_id):
        self.biba_id = biba_id
        self.x = random.uniform(Biba.x_min, Biba.x_max)
        self.y = random.uniform(Biba.y_min, Biba.y_max)
        self.t = round(self.gaussian(Biba.t_min, Biba.t_max), 2)
        self.h = round(self.gaussian(Biba.t_min, Biba.t_max), 2)
        self.n =  self.ones()
        self.g1 = self.ones()
        self.g2 = self.ones()

    def randomize(self):
        
        self.t = self.t + random.uniform((-(Biba.t_min - Biba.t_max)/2)*0.1,
                                        ((Biba.t_min - Biba.t_max)/2)*0.1)
        self.t = round(self.t, 2)
        self.t = self.clip(self.t, Biba.t_min, Biba.t_max)
        
        self.h = self.h + random.uniform((-(Biba.h_min - Biba.h_max)/2)*0.1,
                                        ((Biba.h_min - Biba.h_max)/2)*0.1)
        self.h = round(self.h, 2)
        self.h = self.clip(self.h, Biba.h_min, Biba.h_max)

        self.n = self.ones()
        self.g1 = self.ones()
        self.g2 = self.ones()

    def get_data(self):
        return {
            'biba_id':self.biba_id,
            'temperature':self.t,
            'y':self.y,
            'x':self.x,
            'n':self.n,
            'g1':self.g1,
            'g2':self.g2
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

async def biba_sim(biba_id,space_id,session,access_data,feature_table):
    
    work_time = 10000000
    sleep_time = 1

    start_time = time.time()
    biba = Biba(biba_id)

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
            "t_list":[{"val":biba.t,"time":current_time()}],
            "h_list":[{"val":biba.h,"time":current_time()}],
            "gas_1":biba.g1,
            "gas_2":biba.g2,
            "noise":biba.n
        }
    }

    flag = True
    if 'features' in feature_table: 
        for feature in feature_table['features']:
            if biba_id == feature['properties']['biba_id']:
                id_ = feature['id']
                flag = False
                break
    if flag:
        async with session.put('https://xyz.api.here.com/hub/spaces/{space_id}/features'.format(space_id = space_id), json = features_json, params={'access_token':access_data['token']}) as response:
            id_ = json.loads(await response.text())['features'][0]['id']

    while(time.time() - start_time<=work_time):
        
        #print('Hello from biba{biba}'.format(biba = biba_id))

        biba.randomize()
        
        async with session.get('https://xyz.api.here.com/hub/spaces/{space_id}/features/{feature_id}'.format(space_id = space_id, feature_id = id_), params={'access_token':access_data['token']}) as response:
            content = json.loads(await response.text())
            try:
                h_list = content['properties']['h_list']
                h_list.append({"val":biba.h, "time":current_time()})
                if len(h_list) > 100:
                    h_list.pop(0)
                t_list = content['properties']['t_list']
                t_list.append({"val":biba.t, "time":current_time()})
                if len(t_list) > 100:
                    t_list.pop(0)
            except Exception as e:
                print(e)
                h_list = [{"val":biba.h,"time":current_time()}]
                t_list = [{"val":biba.t,"time":current_time()}]    
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
                    "gas_1":biba.g1,
                    "gas_2":biba.g2,
                    "noise":biba.n        
                }
            }
            async with session.put('https://xyz.api.here.com/hub/spaces/{space_id}/features/{feature_id}'.format(space_id = space_id, feature_id = id_), json = features_json, params={'access_token':access_data['token']}) as response:
                print('Data of biba {bid} sent. Waiting {sleep_time} seconds...'.format(bid = biba_id, sleep_time = sleep_time))
                await asyncio.sleep(sleep_time)

async def simulate(biba_nums, space_id, access_data):

    response = requests.get('https://xyz.api.here.com/hub/spaces/{space_id}/iterate'.format(space_id = space_id), params={'access_token':access_data['token']})
    feature_table = json.loads(response.content)

    async with aiohttp.ClientSession() as session:
        task_list = []
        for i in biba_nums:
            task_list.append(asyncio.create_task(biba_sim(i,space_id,session,access_data,feature_table)))
        return await asyncio.gather(*task_list)

if __name__ == '__main__':
    
    with open('access_data.json') as f:
        access_data = json.load(fp = f)

    new_space ={
        'title':'hack_university_space',
        'description':'An array of map points made by simulation program'
    }

    try:
        space_id = access_data['space_id']
    except:    
        response = requests.post('https://xyz.api.here.com/hub/spaces', params={'access_token':access_data['token']}, json = new_space)
        space_id = json.loads(response.content)['id']
        with open('access_data.json','w') as f:
            new_json = {
                'token':access_data['token'],
                'space_id':space_id
            }
            json.dump(new_json, f, indent=2)

    asyncio.run(simulate(biba_nums = list(range(200)), space_id = space_id, access_data = access_data))
