import json
from multiprocessing import Pool
import random
import time

class Biba():
    
    x_min = 59.85115
    x_max = 60.02331

    y_min = 30.16413
    y_max = 30.50722

    t_min = 10
    t_max = 25

    @staticmethod
    def gaussian(min_, max_):
        return random.gauss(min_ + (max_-min_)/2,(max_-min_)*0.5)

    def __init__(self, biba_id):
        self.biba_id = biba_id
        self.x = random.uniform(Biba.x_min, Biba.x_max)
        self.y = random.uniform(Biba.y_min, Biba.y_max)
        self.t = round(self.gaussian(Biba.t_min, Biba.t_max), 2)

    def randomize_temp(self):
        self.t = self.t + random.uniform((Biba.t_min - (Biba.t_min - Biba.t_max)/2)*0.05,
                                        (Biba.t_max - (Biba.t_min - Biba.t_max)/2)*0.05)
        self.t = round(self.t, 2)

    def get_data(self):
        return {
            'biba_id':self.biba_id,
            'temperature':self.t,
            'y':self.y,
            'x':self.x
        }

def biba_sim(biba_id):
    
    work_time = 10
    sleep_time = 1

    start_time = time.time()
    biba = Biba(biba_id)

    while(time.time() - start_time<=work_time):
        biba.randomize_temp()
        print('request {}'.format(biba.get_data()))
        time.sleep(sleep_time)

if __name__ == '__main__':
    bibas_num = 10
    pool = Pool(bibas_num)
    pool.map(biba_sim, range(bibas_num))