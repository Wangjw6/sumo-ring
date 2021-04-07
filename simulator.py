import os
import sys
import configparser
from build_ring import gen
from sumolib import checkBinary
import pandas as pd
import  numpy as np
import glob
import matplotlib.pyplot as plt
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

class TrafficSimulator():
    def __init__(self, config, is_record,is_vis=False, port=88):
        self.config = config
        self.name = config.get('ENV_CONFIG', 'scenario')
        self.seed = config.getint('ENV_CONFIG', 'seed')
        self.port = port
        self.sim_thread = port
        self.data_path = config.get('ENV_CONFIG', 'data_path')+self.name
        self.output_path = self.data_path + '\\output\\'
        self.is_record = is_record
        self.is_vis = is_vis
        self.ring_length = config.getint('ENV_CONFIG', 'LENGTH')
        self.vehicle_record = {}
        self._init_sim(self.seed)



    def _init_sim(self, seed, gui=False):
        sumocfg_file = self._init_sim_config()
        if gui:
            app = 'sumo-gui'
        else:
            app = 'sumo'
        command = [checkBinary(app)+'.exe', '-c', sumocfg_file,  "--start"]
        # sumoCmd = [self.sumoBinary, "-c", self.sumoConfig, "--start"]
        print(command)
        print('Traci begin...')
        self.sim = traci
        self.sim.start(command,label='0')

    def _init_sim_config(self, ):
        print('Generate and Initialize...')
        sumo_config = gen(config=self.config,path = self.data_path)
        return sumo_config


    def _measure_traffic_state(self,step):
        cars = self.sim.vehicle.getIDList()
        for car in cars:
            dist = self.sim.vehicle.getDistance(car)
            speed = self.sim.vehicle.getSpeed(car)
            r = int(self.sim.vehicle.getDistance(car)/self.ring_length)
            pos = self.sim.vehicle.getDistance(car)-r*self.ring_length
            if car not in self.vehicle_record:
                self.vehicle_record[car] = {'step':[step],
                                            'dist':[dist],
                                            'pos': [pos],
                                            'speed':[speed],
                                            'round':[r]}
            else:
                self.vehicle_record[car]['step'].append(step)
                self.vehicle_record[car]['dist'].append(dist)
                self.vehicle_record[car]['speed'].append(speed)
                self.vehicle_record[car]['pos'].append(pos)
                self.vehicle_record[car]['round'].append(r)

    def output_record(self):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        for key,values in self.vehicle_record.items():
            df = pd.DataFrame.from_dict(values, orient="columns")
            df.to_csv('%s//%s.csv'%(self.output_path,key))
        print('save...')

    def vis_trajectory(self):
        vehicles = []
        for file in glob.glob(self.output_path+"\\*.csv"):
            vehicles.append(pd.DataFrame(pd.read_csv(file)))
        for v in vehicles:
            plt.plot(v['step'],v['pos'])
        plt.show()
        return

    def _simulate(self, num_step):
        for s in range(num_step):
            self.sim.simulationStep()
            if self.sim.vehicle.getIDCount()>0:
                print('Step: ',s, 'Running vehicles: ', self.sim.vehicle.getIDCount())
            if self.is_record:
                self._measure_traffic_state(step=s)

        if self.is_record:
            self.output_record()
        if self.is_vis:
            self.vis_trajectory()
        self.terminate()

    def terminate(self):
        self.sim.close()
