# -*- coding: utf-8 -*-
"""
build *.xml files for a ring network

@author: Jiawei Wang
"""
import numpy as np
from numpy import pi, sin, cos, linspace
import os



def write_file(path, content):

    with open(path, 'w') as f:
        f.write(content)


def output_nodes_(node,length):
    str_nodes = '<nodes>\n'
    #nodes
    r = length / (2 * pi)
    nodes = [{
        "id": "bottom",
        "x": 0,
        "y": -r
    }, {
        "id": "right",
        "x": r,
        "y": 0
    }, {
        "id": "top",
        "x": 0,
        "y": r
    }, {
        "id": "left",
        "x": -r,
        "y": 0
    }]
    for n in nodes:
        str_nodes += node % (n['id'], n['x'], n['y'], 'priority')

    str_nodes += '</nodes>\n'
    print('Number of nodes: ',len(nodes))
    return str_nodes



def output_road_types(speed_limit):
    str_types = '<types>\n'
    str_types += '  <type id="a" priority="1" numLanes="1" speed="%.2f"/>\n' % speed_limit
    str_types += '  <type id="b" priority="1" numLanes="1" speed="%.2f"/>\n' % speed_limit
    str_types += '</types>\n'
    return str_types


def get_edge_str_(edge, id ,from_node, to_node, edge_type,shape):
    edge_id = '%s' % (id)
    return edge % (edge_id, from_node, to_node, edge_type,shape)

def output_edges_(edge,length,resolution):
    str_edges = '<edges>\n'

    r = length / (2 * pi)
    edgelen = length / 4.

    edges = [{
        "id":
            "bottom",
        "type":
            "edgeType",
        "from":
            "bottom",
        "to":
            "right",
        "length":
            edgelen,
        "shape":
            [
                (r * cos(t), r * sin(t))
                for t in linspace(-pi / 2, 0, resolution)
            ]
    },
        {
        "id":
            "right",
        "type":
            "edgeType",
        "from":
            "right",
        "to":
            "top",
        "length":
            edgelen,
        "shape":
            [
                (r * cos(t), r * sin(t))
                for t in linspace(0, pi / 2, resolution)
            ]
    },
        {
        "id":
            "top",
        "type":
            "edgeType",
        "from":
            "top",
        "to":
            "left",
        "length":
            edgelen,
        "shape":
            [
                (r * cos(t), r * sin(t))
                for t in linspace(pi / 2, pi, resolution)
            ]
    },
        {
        "id":
            "left",
        "type":
            "edgeType",
        "from":
            "left",
        "to":
            "bottom",
        "length":
            edgelen,
        "shape":
            [
                (r * cos(t), r * sin(t))
                for t in linspace(pi, 3 * pi / 2, resolution)
            ]
    }]
    for e in edges:
        shape = ""
        for t in range(len(e['shape'])):
            shape+='%s,%s'%(np.format_float_positional(e['shape'][t][0], trim='-'),np.format_float_positional(e['shape'][t][1], trim='-'))
            if t<len(e['shape'])-1:
                shape+=' '
        str_edges += get_edge_str_(edge,e['id'], e['from'], e['to'], 'a',shape)
    str_edges += '</edges>\n'
    print('Number of edges: ', len(edges))
    return str_edges



def get_con_str_(con, from_edge, to_edge, from_lane, to_lane):
    return con % (from_edge, to_edge, from_lane, to_lane)

def output_connections_(con):
    str_cons = '<connections>\n'
    # edge nodes
    connections = [['top','left'],['left','bottom'],['bottom','right'],['right','top']]
    for c in connections:
        str_cons += get_con_str_(con, c[0], c[1], 0, 0)
    str_cons += '</connections>\n'
    print('Nubmer of connections: ', len(connections))
    return str_cons


def output_netconfig(path):
    str_config = '<configuration>\n  <input>\n'
    str_config += '    <edge-files value="%s\\sim.edg.xml"/>\n'%path
    str_config += '    <node-files value="%s\\sim.nod.xml"/>\n'%path
    str_config += '    <type-files value="%s\\sim.typ.xml"/>\n'%path
    str_config += '    <connection-files value="%s\\sim.con.xml"/>\n'%path
    str_config += '  </input>\n  <output>\n'
    str_config += '    <output-file value="%s\\sim.net.xml"/>\n'%path
    str_config += '  </output>\n</configuration>\n'
    return str_config





def output_trips(vehicle_num, depart_interval=60):
    str_trip = '<routes>\n'
    str_trip += '  <vType id="type1" length="5" accel="5" decel="10" maxSpeed="70"/>\n'
    str_trip += '  <route id="r0" edges="top left bottom right top"/>\n'
    begin = 0
    for v in range(vehicle_num):
        str_trip += '       <vehicle id="%s" depart="%s" departPos="%s" type="type1" route="%s" color="1,1,0"/>\n '%(v,str(begin+v*depart_interval),'base','r0')
    str_trip += '</routes>'
    print('Number of vehicles: ',vehicle_num)
    return str_trip

def gen_rou_file_(path, vehicle_num, seed=None):
    flow_file = 'sim.rou.xml'
    write_file(path + flow_file, output_trips(vehicle_num = config.getint('ENV_CONFIG', 'LENGTH'),depart_interval=config.getint('ENV_CONFIG', 'DEP_INTERVAL')))


def output_config(config):
    path =  config.get('ENV_CONFIG', 'data_path')+config.get('ENV_CONFIG', 'scenario')
    rou_file = path + '\\sim.rou.xml'
    net_file = path + '\\sim.net.xml'
    add_file = path + '\\sim.add.xml'
    str_config = '<configuration>\n  <input>\n'
    str_config += '    <net-file value="%s"/>\n' % net_file
    str_config += '    <route-files value="%s"/>\n' % rou_file
    str_config += '    <additional-files value="%s"/>\n'% add_file
    str_config += '  </input>\n  <time>\n'
    str_config += '    <begin value="0"/>\n    <end value="%s"/>\n' % str( config.getint('ENV_CONFIG', 'DURATION'))
    str_config += '  </time>\n</configuration>\n'
    return str_config


def gen(config,path):
    # nod.xml file

    node = '  <node id="%s" x="%.2f" y="%.2f" type="%s"/>\n'
    write_file(path+'\\sim.nod.xml', output_nodes_(node,length=config.getint('ENV_CONFIG', 'LENGTH')))

    # typ.xml file
    write_file(path+'\\sim.typ.xml', output_road_types(speed_limit = config.getint('ENV_CONFIG', 'SPEED_LIMIT')))

    # edg.xml file
    edge = '  <edge id="%s" from="%s" to="%s" type="%s" shape="%s"/>\n'
    write_file(path+'\\sim.edg.xml', output_edges_(edge,length=config.getint('ENV_CONFIG', 'LENGTH'),resolution=config.getint('ENV_CONFIG', 'RESOLUTION')))

    # con.xml file
    con = '  <connection from="%s" to="%s" fromLane="%d" toLane="%d"/>\n'
    write_file(path+'\\sim.con.xml', output_connections_(con))

    # tls.xml file
    # tls = '  <tlLogic id="%s" programID="0" offset="0" type="static">\n'
    # phase = '    <phase duration="%d" state="%s"/>\n'
    # write_file(path+'\\sim.tll.xml', output_tls(tls, phase))

    # net config file
    write_file(path+'\\sim.netccfg', output_netconfig(path))

    # generate net.xml file
    os.system('netconvert -c %s\\sim.netccfg'%path)

    # raw.rou.xml file
    write_file(path+'\\sim.rou.xml', output_trips(vehicle_num=config.getint('ENV_CONFIG', 'VEHICLE_NUM')))

    # generate rou.xml file
    # os.system('jtrrouter -n sim.net.xml -r sim.raw.rou.xml -o sim.rou.xml')

    # add.xml file
    rr = '<additionals>\n<rerouter id="%s" edges="%s"><interval end="1e9"><destProbReroute id="%s"/></interval></rerouter>' \
         '<rerouter id="%s" edges="%s"><interval end="1e9"><destProbReroute id="%s"/></interval></rerouter>\n</additionals>'
    write_file(path+'\\sim.add.xml', rr%(0,'right','top',1,'top','right'))

    # config file
    sumocfg_file = path + '\\sim.sumocfg'
    write_file(sumocfg_file, output_config(config=config))
    return sumocfg_file

    return path+'\\sim.sumocfg'

if __name__ == '__main__':
    gen(config)
