from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from utils import round_time_5min

months = ['January', 'February', 'March',
          'April', 'May', 'June',
          'July', 'August', 'September',
          'October', 'November', 'December']

day_stats_dfs = []
start_year = 2021
end_year = 2024

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
        
        velocity_sample = velocity_data.head(1500)
        volume_sample = volume_data.head(1500)
        
        
        all_data = velocity_data.merge(volume_data, how='inner', 
                                         on=['timestamp', 'latitud', 'longitud', 
                                             'id_carril', 'cod_detector',
                                             'dsc_avenida', 'dsc_int_anterior',
                                             'dsc_int_siguiente'])
        
        all_data['date'] = all_data['timestamp'].dt.date
        dates = all_data['date'].unique()
        detector_counts = []
        for date in dates:
            day_data = all_data[all_data['date'] == date]
            detectors = day_data.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente', 'id_carril']).groups
            detector_count = len(detectors)
            detector_counts.append(detector_count)
        
        detector_counts = pd.Series(detector_counts, dates)
        
        day_stats = all_data.groupby(['date']).agg( 
            vel_10th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 10)),
            vel_25th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 25)),
            vel_50th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 50)),
            vel_75th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 75)),
            vel_90th=pd.NamedAgg(column = 'velocidad', aggfunc=lambda x: np.percentile(x, 90)),
            vol_10th=pd.NamedAgg(column = 'volume', aggfunc=lambda x: np.percentile(x, 10)),
            vol_25th=pd.NamedAgg(column = 'volume', aggfunc=lambda x: np.percentile(x, 25)),
            vol_50th=pd.NamedAgg(column = 'volume', aggfunc=lambda x: np.percentile(x, 50)),
            vol_75th=pd.NamedAgg(column = 'volume', aggfunc=lambda x: np.percentile(x, 75)),
            vol_90th=pd.NamedAgg(column = 'volume', aggfunc=lambda x: np.percentile(x, 90))
            )

        day_stats['detector_counts'] = detector_counts
        day_stats_dfs.append(day_stats)    
        
total_stats = pd.concat(day_stats_dfs)

fig, axs = plt.subplots(2, 1, sharex=True)
axs[0].plot(total_stats.index, total_stats['vel_50th'], color = 'navy')
axs[0].fill_between(total_stats.index, total_stats['vel_25th'], 
                    total_stats['vel_75th'], color = 'navy', alpha = 0.5)
axs[0].fill_between(total_stats.index, total_stats['vel_10th'], 
                    total_stats['vel_90th'], color = 'navy', alpha = 0.2)
axs[0].set_ylim(bottom=0, top=60)
axs[0].set_ylabel('Velocity (km/h)')
axs[0].set_title('Velocity Over Time')

axs[1].plot(total_stats.index, total_stats['vol_50th'], color = 'maroon')
axs[1].fill_between(total_stats.index, total_stats['vol_25th'], 
                    total_stats['vol_75th'], color = 'maroon', alpha = 0.5)
axs[1].fill_between(total_stats.index, total_stats['vol_10th'], 
                    total_stats['vol_90th'], color = 'maroon', alpha = 0.2)
axs[1].set_ylim(bottom=0, top=80)
axs[1].set_xlabel('Date')
axs[1].set_ylabel('Number of cars \n(past 5 min)')
axs[1].set_title('Volume Over Time')
fig.subplots_adjust(hspace=0.4)
plt.show()

fig, ax = plt.subplots()
ax.plot(total_stats.index, total_stats['detector_counts'], color = 'purple')
ax.set_xlabel('Date')
ax.set_ylabel('Number of detectors active')
ax.set_title('Active Detectors Over Time')
plt.show()