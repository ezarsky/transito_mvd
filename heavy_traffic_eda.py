from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from utils import round_time_5min

rng = np.random.default_rng(7)

months = ['January', 'February', 'March',
          'April', 'May', 'June',
          'July', 'August', 'September',
          'October', 'November', 'December']

all_dfs = []
start_year = 2021
end_year = 2021

for y in range(start_year, end_year+1):
    year = str(y)
    for m in range(0, 12):
        print(f'Processing data from {months[m]} {year}...')
        month = str(m+1).zfill(2)
        velocity_path = f"../data/velocidad_{year}_{month}.csv"
        volume_path = f"../data/volumen_{year}_{month}.csv"
        
        try:
            velocity_data = pd.read_csv(velocity_path)
            volume_data = pd.read_csv(volume_path)
        
        except FileNotFoundError:
            continue
                
        velocity_data = velocity_data.drop_duplicates()
        volume_data = volume_data.drop_duplicates()
        
        
        velocity_data['timestamp'] = pd.to_datetime(velocity_data['fecha'] + ' ' + velocity_data['hora'], 
                                                    yearfirst=True)
        
        volume_data['timestamp'] = pd.to_datetime(volume_data['fecha'] + ' ' + volume_data['hora'],
                                                  yearfirst=True)
        
        velocity_data['timestamp'] = round_time_5min(velocity_data['timestamp']) 
        volume_data['timestamp'] = round_time_5min(volume_data['timestamp']) 
        
        velocity_data = velocity_data.drop(columns=['fecha', 'hora'])
        volume_data = volume_data.drop(columns=['fecha', 'hora'])
        
        
        all_data = pd.merge(velocity_data, volume_data, how='inner', 
                                         on=['timestamp', 'latitud', 'longitud', 
                                             'id_carril', 'cod_detector',
                                             'dsc_avenida', 'dsc_int_anterior',
                                             'dsc_int_siguiente'])
        

        all_data['timeofday'] = all_data['timestamp'].dt.hour + all_data['timestamp'].dt.minute/60
        all_data['date'] = all_data['timestamp'].dt.date
        
        all_dfs.append(all_data)

all_data = pd.concat(all_dfs)

intersections_by_vol = all_data.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente'])['volume'].agg('sum')
intersections_by_vol = intersections_by_vol.sort_values(ascending=False)

top100 = intersections_by_vol.reset_index().iloc[:100]

heavy_data = pd.merge(all_data, top100, how='inner', on=['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente'])
heavy_data = heavy_data.rename(columns={'volume_x': 'volume_5min'})
heavy_data = heavy_data.drop(columns=['volume_y'])

detectors = heavy_data.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente']).groups
for detector in detectors.keys():
    road, prev_road, next_road = detector
    idxs = detectors[detector]
    detector_data = heavy_data.loc[idxs, :]
    all_lanes = detector_data.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente', 'timestamp'])['volume_5min'].agg('mean')
    all_lanes = all_lanes.reset_index()
    all_lanes = all_lanes.rename(columns={'volume_5min': 'all_lanes_volume_5min'})
    
    detector_data = pd.merge(detector_data, all_lanes, how='inner', on=['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente', 'timestamp'])
    
    hour_stats = detector_data.groupby(['timeofday']).agg( 
        vel_10th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 10)),
        vel_25th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 25)),
        vel_50th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 50)),
        vel_75th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 75)),
        vel_90th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 90)),
        vol_10th=pd.NamedAgg(column = 'all_lanes_volume_5min', aggfunc=lambda x: np.percentile(x, 10)),
        vol_25th=pd.NamedAgg(column = 'all_lanes_volume_5min', aggfunc=lambda x: np.percentile(x, 25)),
        vol_50th=pd.NamedAgg(column = 'all_lanes_volume_5min', aggfunc=lambda x: np.percentile(x, 50)),
        vol_75th=pd.NamedAgg(column = 'all_lanes_volume_5min', aggfunc=lambda x: np.percentile(x, 75)),
        vol_90th=pd.NamedAgg(column = 'all_lanes_volume_5min', aggfunc=lambda x: np.percentile(x, 90))
        )

    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(hour_stats.index, hour_stats['vel_50th'], color = 'navy')
    axs[0].fill_between(hour_stats.index, hour_stats['vel_25th'], 
                        hour_stats['vel_75th'], color = 'navy', alpha = 0.5)
    axs[0].fill_between(hour_stats.index, hour_stats['vel_10th'], 
                        hour_stats['vel_90th'], color = 'navy', alpha = 0.2)
    axs[0].set_ylim(bottom=0, top=120)
    axs[0].set_ylabel('Avg speed (km/h) \n(over past 5 min)')

    
    axs[1].plot(hour_stats.index, hour_stats['vol_50th'], color = 'maroon')
    axs[1].fill_between(hour_stats.index, hour_stats['vol_25th'], 
                        hour_stats['vol_75th'], color = 'maroon', alpha = 0.5)
    axs[1].fill_between(hour_stats.index, hour_stats['vol_10th'], 
                        hour_stats['vol_90th'], color = 'maroon', alpha = 0.2)
    axs[1].set_ylim(bottom=0, top=100)
    axs[1].set_ylabel('Time of Day')
    axs[1].set_ylabel('Avg. cars per lane \n(over past 5 min)')
    fig.subplots_adjust(hspace=0.4)
    fig.suptitle(f'{road} between {prev_road} and {next_road}', fontsize=16)
    plt.show()
    

# TODO: investigate outliers

foo = heavy_data[heavy_data['dsc_avenida'] == 'Aramburu']

# TODO: map heavy traffic zones

# TODO: analyze daily volumes over year(s)

# TODO: analyze velocity distributions vs. posted limits