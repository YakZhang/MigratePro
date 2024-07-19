# common useful function
import pandas as pd
import json
import os


def read_csv(csv_file, csv_name):
    df_csv = pd.read_csv(csv_file + csv_name)
    return df_csv

def read_json(jsonline_path):
    data = []
    with open(jsonline_path) as load_f:
        data = json.load(load_f)
    return data

def dict2json(dict,json_path):
    # write json file
    json_str = json.dumps(dict,indent=4)
    # json_path = script_dir + "script.json"
    with open(json_path,'w') as json_file:
        json_file.write(json_str)
    return json_path

def parse_file(file_path):
    # get all the file in the file_path
    result = []
    for maindir,subdir,file_name_list in os.walk(file_path):
        for filename in file_name_list:
            apath = os.path.join(maindir,filename)
            result.append(apath)
    return result

def create_file(file_path):
    # identify whether the file_path exist
    # if not create_file
    if not os.path.exists(file_path):
        os.system(r"touch{}".format(file_path))

def get_row_index_from_df(df_groundtruth_pair):

    index = df_groundtruth_pair.index.tolist()
    return index

def get_row_index_from_series(series):
    index = series.name
    return index