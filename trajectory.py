from __future__ import division

import numpy as np



from matplotlib import pyplot as plt 
import xml.etree.cElementTree as ET
import seaborn as sns

rand = np.random.RandomState(0)

def load_trajectory(T_scale = 30, D_scale = 100, RoadLength = 10000, f_ratio = 0.05):
    
    xml_tree = ET.parse('trajectories.xml')
    xml_root = xml_tree.getroot()
    trajectory_data = []
    
    for timestep in xml_root.iter('timestep'):
        time = timestep.get('time')
        for lanelist in timestep.iter('edge'):
            lane = lanelist.get('id')
            for veh in lanelist.iter('vehicle'):
                veh_id = veh.get('id')
                veh_pos = float(veh.get('pos'))
                if lane == 'left':
                    veh_pos = float(veh_pos) + 2500
                elif lane == 'bottom':
                    veh_pos = float(veh_pos) + 5000
                elif lane == 'right':
                    veh_pos = float(veh_pos) + 7500
                veh_speed = veh.get('speed')
                trajectory_data.append([veh_id,time,veh_pos,veh_speed]) # id,time,pos
    
    trajectory_data = np.array(trajectory_data)
    trajectory_data = trajectory_data.astype(np.float32)
    np.save('trajectory_data.npy',trajectory_data)
    
    trajectory_data = np.load('trajectory_data.npy')
    
    TotalVehicle = np.unique(trajectory_data[:,0])
    n_u = round(f_ratio*TotalVehicle.shape[0])
    unknow_set = rand.choice(list(range(0,TotalVehicle.shape[0])),n_u,replace=False)
    FloatVehicle = TotalVehicle[unknow_set]
    MinTime = np.min(trajectory_data[:,1])
    TotalStep = np.max(trajectory_data[:,1]) - MinTime
    
    delta_t = T_scale
    delta_d = D_scale

    num_grid_row = np.ceil(RoadLength/delta_d).astype(int)
    num_grid_col = np.ceil(TotalStep/delta_t).astype(int)
    print(num_grid_row,num_grid_col)
    grid_line_d = np.arange(0,RoadLength,delta_d)
    grid_line_t = np.arange(0,TotalStep,delta_t)
    grid_line_d = np.append(grid_line_d,RoadLength-1)
    grid_line_t = np.append(grid_line_t,TotalStep-1)
    
    Q = np.zeros((num_grid_row,num_grid_col))
    V = np.zeros_like(Q)
    sum_of_d = np.zeros_like(Q)
    sum_of_t = np.zeros_like(Q)
    sum_of_v = np.zeros_like(Q)
    count_veh = np.zeros_like(Q)
    V[:, :] = np.nan
    
    veh_trajectory = []
    
    for veh_i in FloatVehicle:

    # Obtain available TimeStep-Location Trajectory from the data, exclude those exceed the limits of RoadLenth and TotalTimestep
        Trajectory = trajectory_data[trajectory_data[:,0]==veh_i,1:]
    
        Trajectory[Trajectory[:,1]<0,:] = np.nan
        Trajectory[Trajectory[:,1]>RoadLength,:] = np.nan
        mask = np.all(np.isnan(Trajectory), axis=1)
        Trajectory = Trajectory[~mask]
    
        veh_trajectory.append(Trajectory)
    
        # Locate which grids the trajectory belongs to
        # 1. Split trajectory by grid_line_t
        grid_t = Trajectory[:,0] // delta_t
        grid_d = Trajectory[:,1] // delta_d
        grid_d_t = np.zeros_like(Trajectory)
        
        # 2. Find grids that this trajectory has passed
        grid_d_t[:,0] = grid_d
        grid_d_t[:,1] = grid_t
        grid_d_t_unique = np.unique(grid_d_t,axis=0)
        
        # 3. Calculate required values in each passed grid
        for grid in grid_d_t_unique:
            d = int(grid[0])
            t = int(grid[1])
            
            # traj_passed = grid_d_t[(grid_d_t==grid).all(axis=1),:] # This does not consider the border
            left_border = t*delta_t
            right_border = (t+1)*delta_t
            top_border = (d+1)*delta_d
            bottom_border = d*delta_d
            idx = (Trajectory[:,0]>=left_border) & (Trajectory[:,0]<=right_border) & (Trajectory[:,1]>=bottom_border) & (Trajectory[:,1]<=top_border)
            traj_passed = Trajectory[idx,:]
    
            # Assumption: one-lane simulation, trajectory only goes from bottom left to upper right
            dt = np.max(traj_passed[:,0]) - np.min(traj_passed[:,0])
            dd = np.max(traj_passed[:,1]) - np.min(traj_passed[:,1])
            
            sum_of_d[d,t] += dd
            sum_of_t[d,t] += dt
            sum_of_v[d,t] += np.sum(traj_passed[:, 2])
            count_veh[d, t] += traj_passed.shape[0]
    
    V = sum_of_v/count_veh
    if f_ratio == 1:
        V[np.isnan(V)] = 0
        
    fig, ax = plt.subplots(figsize=(5,2.5))
    v_plot = sns.heatmap(V,ax=ax,cmap='Spectral')
    v_plot.invert_yaxis()
    ax.set_xlabel('Time division')
    ax.set_ylabel('Location division')
    return V 

V = load_trajectory(f_ratio = 1)
V_05 = load_trajectory(f_ratio = 0.05)
V_03 = load_trajectory(f_ratio = 0.03)
V_01 = load_trajectory(f_ratio = 0.01)
