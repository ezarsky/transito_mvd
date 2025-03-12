import datetime
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from utils import round_time_5min

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


all_data = velocity_data.merge(volume_data, how='inner', 
                                 on=['timestamp', 'latitud', 'longitud', 
                                     'id_carril', 'cod_detector',
                                     'dsc_avenida', 'dsc_int_anterior',
                                     'dsc_int_siguiente'])

all_data['timeofday'] = all_data['timestamp'].dt.hour + all_data['timestamp'].dt.minute/60
all_data['date'] = all_data['timestamp'].dt.date

# number of radars/detectors
dates = pd.date_range(all_data['date'].min(), all_data['date'].max())
detector_counts = []
for date in dates:
    date_data = all_data[all_data['date'] == date.date()]
    detectors = date_data.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente', 'id_carril']).groups
    detector_counts.append(len(detectors))

detector_counts = np.array(detector_counts)


date_labels = [date.date() for date in dates if date.day % 5 == 0]
fig, ax = plt.subplots()
ax.plot(dates, detector_counts)
ax.tick_params(axis='x', rotation=90)
plt.show()


# TODO: correlation (do this by intersection/detector)
all_data[['velocidad', 'volume']].corr()
all_data[['velocidad', 'volumen_hora']].corr()

fig, ax = plt.subplots()
ax.scatter(all_data['velocidad'], all_data['volume'])
ax.set_xlabel('Velocity')
ax.set_ylabel('Volume (last 5 min)')
plt.show()

fig, ax = plt.subplots()
ax.scatter(all_data['velocidad'], all_data['volumen_hora'])
ax.set_xlabel('Velocity')
ax.set_ylabel('Volume (last hour)')
plt.show()


# weekdays vs weekends
weekday_data = all_data[all_data["timestamp"].dt.dayofweek < 5]
weekend_data = all_data[all_data["timestamp"].dt.dayofweek >= 5]

weekday_data[['velocidad', 'volume']].corr()
weekday_data[['velocidad', 'volumen_hora']].corr()

fig, ax = plt.subplots()
ax.scatter(weekday_data['velocidad'], weekday_data['volume'])
ax.set_xlabel('Velocity')
ax.set_ylabel('Volume (last 5 min)')
ax.set_title('Velocity vs. Volume (Weekdays)')
plt.show()

fig, ax = plt.subplots()
ax.scatter(weekday_data['velocidad'], weekday_data['volumen_hora'])
ax.set_xlabel('Velocity')
ax.set_ylabel('Volume (last hour)')
ax.set_title('Velocity vs. Volume (Weekdays)')
plt.show()

weekend_data[['velocidad', 'volume']].corr()
weekend_data[['velocidad', 'volumen_hora']].corr()

fig, ax = plt.subplots()
ax.scatter(weekend_data['velocidad'], weekend_data['volume'])
ax.set_xlabel('Velocity')
ax.set_ylabel('Volume (last 5 min)')
ax.set_title('Velocity vs. Volume (Weekends)')
plt.show()

fig, ax = plt.subplots()
ax.scatter(weekend_data['velocidad'], weekend_data['volumen_hora'])
ax.set_xlabel('Velocity')
ax.set_ylabel('Volume (last hour)')
ax.set_title('Velocity vs. Volume (Weekends)')
plt.show()


# velocity and volume vs hour by day of week
day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

for i, day in enumerate(day_names):
    day_data = all_data[all_data['timestamp'].dt.dayofweek == i]

    hour_stats = day_data.groupby(['timeofday']).agg( 
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

    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(hour_stats.index, hour_stats['vel_50th'], color = 'navy')
    axs[0].fill_between(hour_stats.index, hour_stats['vel_25th'], 
                        hour_stats['vel_75th'], color = 'navy', alpha = 0.5)
    axs[0].fill_between(hour_stats.index, hour_stats['vel_10th'], 
                        hour_stats['vel_90th'], color = 'navy', alpha = 0.2)
    axs[0].set_ylim(bottom=0, top=60)
    axs[0].set_ylabel('Velocity (km/h)')
    axs[0].set_title(f'Hourly Velocity ({day})')
    
    axs[1].plot(hour_stats.index, hour_stats['vol_50th'], color = 'maroon')
    axs[1].fill_between(hour_stats.index, hour_stats['vol_25th'], 
                        hour_stats['vol_75th'], color = 'maroon', alpha = 0.5)
    axs[1].fill_between(hour_stats.index, hour_stats['vol_10th'], 
                        hour_stats['vol_90th'], color = 'maroon', alpha = 0.2)
    axs[1].set_ylim(bottom=0, top=80)
    axs[1].set_ylabel('Time of Day')
    axs[1].set_ylabel('Number of cars \n(past 5 min)')
    axs[1].set_title(f'Hourly Volume ({day})')
    fig.subplots_adjust(hspace=0.4)
    plt.show()


# velocity and volume vs hour by date
for day in range(1, 31+1):
    day_data = all_data[all_data['timestamp'].dt.day == day]

    if day_data.shape[0] != 0:
        hour_stats = day_data.groupby(['timeofday']).agg( 
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
    
        fig, axs = plt.subplots(2, 1, sharex=True)
        axs[0].plot(hour_stats.index, hour_stats['vel_50th'], color = 'navy')
        axs[0].fill_between(hour_stats.index, hour_stats['vel_25th'], 
                            hour_stats['vel_75th'], color = 'navy', alpha = 0.5)
        axs[0].fill_between(hour_stats.index, hour_stats['vel_10th'], 
                            hour_stats['vel_90th'], color = 'navy', alpha = 0.2)
        axs[0].set_ylim(bottom=0, top=60)
        axs[0].set_ylabel('Velocity (km/h)')
        axs[0].set_title(f'Hourly Velocity ({day} Dec)')
        
        axs[1].plot(hour_stats.index, hour_stats['vol_50th'], color = 'maroon')
        axs[1].fill_between(hour_stats.index, hour_stats['vol_25th'], 
                            hour_stats['vol_75th'], color = 'maroon', alpha = 0.5)
        axs[1].fill_between(hour_stats.index, hour_stats['vol_10th'], 
                            hour_stats['vol_90th'], color = 'maroon', alpha = 0.2)
        axs[1].set_ylim(bottom=0, top=80)
        axs[1].set_ylabel('Time of Day')
        axs[1].set_ylabel('Number of cars \n(past 5 min)')
        axs[1].set_title(f'Hourly Volume ({day} Dec)')
        fig.subplots_adjust(hspace=0.4)
        plt.show()

# velocity and volume vs hour by intersection
detectors = all_data.groupby(['dsc_avenida', 'dsc_int_anterior', 'dsc_int_siguiente', 'id_carril']).groups
for detector in detectors.keys():
    road, prev_road, next_road, lane = detector
    idxs = detectors[detector]
    detector_data = all_data.loc[idxs, :]
    
    hour_stats = detector_data.groupby(['timeofday']).agg( 
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

    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(hour_stats.index, hour_stats['vel_50th'], color = 'navy')
    axs[0].fill_between(hour_stats.index, hour_stats['vel_25th'], 
                        hour_stats['vel_75th'], color = 'navy', alpha = 0.5)
    axs[0].fill_between(hour_stats.index, hour_stats['vel_10th'], 
                        hour_stats['vel_90th'], color = 'navy', alpha = 0.2)
    axs[0].set_ylim(bottom=0, top=120)
    axs[0].set_ylabel('Velocity (km/h)')
    axs[0].set_title(f'Hourly Velocity {road} Entre {prev_road} Y {next_road} Carril {lane}')
    
    axs[1].plot(hour_stats.index, hour_stats['vol_50th'], color = 'maroon')
    axs[1].fill_between(hour_stats.index, hour_stats['vol_25th'], 
                        hour_stats['vol_75th'], color = 'maroon', alpha = 0.5)
    axs[1].fill_between(hour_stats.index, hour_stats['vol_10th'], 
                        hour_stats['vol_90th'], color = 'maroon', alpha = 0.2)
    axs[1].set_ylim(bottom=0, top=80)
    axs[1].set_ylabel('Time of Day')
    axs[1].set_ylabel('Number of cars \n(past 5 min)')
    axs[1].set_title(f'Hourly Volume {road} Entre {prev_road} Y {next_road} Carril {lane}')
    fig.subplots_adjust(hspace=0.4)
    plt.show()


all_data['latitud'].min()
all_data['latitud'].max()
all_data['longitud'].min()
all_data['longitud'].max()
