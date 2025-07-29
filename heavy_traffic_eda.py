from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from utils import round_time_5min

rng = np.random.default_rng(7)

velocity_path = "../data/velocidad_2022_12.csv"
volume_path = "../data/volumen_2022_12.csv"

velocity_data = pd.read_csv(velocity_path)
volume_data = pd.read_csv(volume_path)

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

velocity_sample = velocity_data.head(1500)
volume_sample = volume_data.head(1500)


all_data = pd.merge(velocity_data, volume_data, how='inner', 
                    on=['timestamp', 'latitud', 'longitud', 
                        'id_carril', 'cod_detector',
                        'dsc_avenida', 'dsc_int_anterior',
                        'dsc_int_siguiente'])

all_data['timeofday'] = all_data['timestamp'].dt.hour + all_data['timestamp'].dt.minute/60
all_data['date'] = all_data['timestamp'].dt.date

intersections_by_vol = all_data.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente'])['volume'].agg('sum')
intersections_by_vol = intersections_by_vol.sort_values(ascending=False)

top100 = intersections_by_vol.reset_index().iloc[:100]

foo = pd.merge(all_data, top100, how='inner', on=['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente'])
foo = foo.rename(columns={'volume_x': 'volume_5min'})


detectors = foo.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente']).groups
for detector in detectors.keys():
    road, prev_road, next_road = detector
    idxs = detectors[detector]
    detector_data = foo.loc[idxs, :]
    
    hour_stats = detector_data.groupby(['timeofday']).agg( 
        vel_10th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 10)),
        vel_25th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 25)),
        vel_50th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 50)),
        vel_75th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 75)),
        vel_90th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 90)),
        vol_10th=pd.NamedAgg(column = 'volume_5min', aggfunc=lambda x: np.percentile(x, 10)),
        vol_25th=pd.NamedAgg(column = 'volume_5min', aggfunc=lambda x: np.percentile(x, 25)),
        vol_50th=pd.NamedAgg(column = 'volume_5min', aggfunc=lambda x: np.percentile(x, 50)),
        vol_75th=pd.NamedAgg(column = 'volume_5min', aggfunc=lambda x: np.percentile(x, 75)),
        vol_90th=pd.NamedAgg(column = 'volume_5min', aggfunc=lambda x: np.percentile(x, 90))
        )

    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(hour_stats.index, hour_stats['vel_50th'], color = 'navy')
    axs[0].fill_between(hour_stats.index, hour_stats['vel_25th'], 
                        hour_stats['vel_75th'], color = 'navy', alpha = 0.5)
    axs[0].fill_between(hour_stats.index, hour_stats['vel_10th'], 
                        hour_stats['vel_90th'], color = 'navy', alpha = 0.2)
    axs[0].set_ylim(bottom=0, top=120)
    axs[0].set_ylabel('Velocity (km/h)')
    axs[0].set_title(f'Hourly Velocity {road} between {prev_road} and {next_road}')
    
    axs[1].plot(hour_stats.index, hour_stats['vol_50th'], color = 'maroon')
    axs[1].fill_between(hour_stats.index, hour_stats['vol_25th'], 
                        hour_stats['vol_75th'], color = 'maroon', alpha = 0.5)
    axs[1].fill_between(hour_stats.index, hour_stats['vol_10th'], 
                        hour_stats['vol_90th'], color = 'maroon', alpha = 0.2)
    axs[1].set_ylim(bottom=0, top=80)
    axs[1].set_ylabel('Time of Day')
    axs[1].set_ylabel('Number of cars \n(past 5 min)')
    axs[1].set_title(f'Hourly Volume {road} between {prev_road} and {next_road}')
    fig.subplots_adjust(hspace=0.4)
    plt.show()