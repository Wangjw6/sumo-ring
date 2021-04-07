import argparse
import os
import sys
import configparser
from simulator import TrafficSimulator
def parse_args():
    parser = argparse.ArgumentParser()
    default_config_dir = 'G:\\mcgill\\sumo-ring\\config\\demo.ini'
    parser.add_argument('--config_dir', type=str, required=False,
                        default=default_config_dir, help="config dir")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    config = configparser.ConfigParser()
    config.read(args.config_dir)
    simluator = TrafficSimulator(config=config,is_record=True)
    simluator._simulate(num_step=3600)
    print('done')