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


all_data = velocity_data.merge(volume_data, how='inner', 
                                 on=['timestamp', 'latitud', 'longitud', 
                                     'id_carril', 'cod_detector',
                                     'dsc_avenida', 'dsc_int_anterior',
                                     'dsc_int_siguiente'])

all_data['timeofday'] = all_data['timestamp'].dt.hour + all_data['timestamp'].dt.minute/60
all_data['date'] = all_data['timestamp'].dt.date

foo = all_data.groupby(['dsc_avenida'])['volume'].agg('mean')
foo = foo.sort_values(ascending=False)
