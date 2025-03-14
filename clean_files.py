import os
import pandas as pd

data_path = '../data/'
all_files = os.listdir(data_path)
for file in all_files:
    if file.startswith('autoscope'):
        _, month, year, ending = file.split('_')
        vol_vel, ext = ending.split('.')
        new_name = '_'.join([vol_vel, year, month+'.'+ext])
        try:
            os.rename(data_path+file, data_path+new_name)
        except FileExistsError:
            pass

all_files = os.listdir(data_path)
for file in all_files:
    file_path = data_path + file
    data = pd.read_csv(file_path)
    if data.shape[1] == 1:
        print(f'Issue with file: {file}')
        print(f'First line:{data.iloc[0,:]}')
        print('Converting to commas...')
        data = pd.read_csv(file_path, sep=';')
        data.to_csv(file_path, sep=',')
        print('Done\n')
        
            
all_files = os.listdir(data_path)
vel_cols = dict()
vol_cols = dict()
for file in all_files:
    print(f'File: {file}')
    data_category = file.split('_')[0] 
    file_path = data_path + file
    data = pd.read_csv(file_path)
    cols = tuple(data.columns.to_list())
    print(f'Columns: {cols}')
    if data_category == 'velocidad':
        current_files = vel_cols.get(cols, [])
        vel_cols[cols] = current_files
        vel_cols[cols].append(file)
    if data_category == 'volumen':
        current_files = vol_cols.get(cols, [])
        vol_cols[cols] = current_files
        vol_cols[cols].append(file)
        
        
file_list = ['velocidad_2021_01.csv', 'velocidad_2021_02.csv', 'velocidad_2021_03.csv']
for file in file_list:
    file_path = data_path + file
    data = pd.read_csv(file_path)
    data = data.rename(columns={'velocidad_promedio': 'velocidad'})
    data.to_csv(file_path, index=False)