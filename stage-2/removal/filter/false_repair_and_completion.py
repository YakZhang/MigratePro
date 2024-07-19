# the main function for the whole project
# coding=utf-8

import pandas as pd
import numpy as np
# bisect is for insert an item in an ordered sequence
import bisect
import time
import os
from delete_false_postive import delete_false_event,judge_false_positive
from add_execution_modification import Generation,search_test_case,judge_the_combined_test_case, record_search_result
from completion import choose_droidbot_output,revise_screen_name,generate_test_case_sequence,evaluate_test_case,save_call_graph_test_result, generate_test_case_sequence_false,evaluate_test_case_false
from filter import generate_script



def revise(csv_file,csv_name,tgt_app_name,function,generation):

    # generation = Generation()

    # # for test swipe right and long press
    # tgt_app_name = 'a22'
    # function = 'b22'

    df_group = generation.get_group(tgt_app_name, function,csv_file, csv_name)
    if df_group is None:
        # the tool cannot generate any widget in the tgt_app and functions:
        return df_group
    # change src_index, tgt_index as the np.float (not np.numercic because tgt_index has float)
    df_group['src_index'] = df_group['src_index'].astype(float)
    df_group['tgt_index'] = df_group['tgt_index'].astype(float)
    # # add_true_generate_index for comparison for Craftdroid
    # df_group = add_true_generate_index(df_group)
    # revise fp
    df_revised_group = delete_false_event(df_group, generation)
    ori_fp, revised_fp = judge_false_positive(df_group, df_revised_group)
    print("whether df_group has fp", ori_fp)
    print("whether df_revised_group revised fp",revised_fp)
    return df_revised_group

def add_true_generate_index(df_group):
    # get the gen_id which equals to the tgt_index
    hash_gen_tgt_index = dict()
    for idx in range(len(df_group)):
        ori_predict_label = df_group.iloc[idx].at['ori_predict_label']
        if ori_predict_label == 0:
            continue
        else:
            label = df_group.iloc[idx].at['label']
            if label == 1:
                gen_id_for_tgt = df_group.iloc[idx].at['tgt_index']
                column_index= df_group.iloc[idx].at['index']
                df_group.loc[column_index,'gen_id_for_tgt'] = gen_id_for_tgt
                hash_string = str(df_group.iloc[idx].at['class']) +str(df_group.iloc[idx].at['tgt_add_id']) + str(df_group.iloc[idx].at['tgt_text'])+ str(df_group.iloc[idx].at['tgt_content']) + str(df_group.iloc[idx].at['type']) + str(df_group.iloc[idx].at['predict_action']) + str(df_group.iloc[idx].at['input'])
                hash_code =hash(hash_string)
                hash_gen_tgt_index[hash_code] = gen_id_for_tgt
    for idx in range(len(df_group)):
        if df_group.iloc[idx].at['gen_id_for_tgt'] == df_group.iloc[idx].at['gen_id_for_tgt']:
            # have gen_id_for_tgt
            continue
        else:
            hash_string = str(df_group.iloc[idx].at['class']) +str(df_group.iloc[idx].at['tgt_add_id']) + str(df_group.iloc[idx].at['tgt_text'])+ str(df_group.iloc[idx].at['tgt_content']) + str(df_group.iloc[idx].at['type']) + str(df_group.iloc[idx].at['predict_action']) + str(df_group.iloc[idx].at['input'])
            if hash_string in hash_gen_tgt_index:
                column_index =df_group.iloc[idx].at['index']
                df_group.loc[column_index,'gen_id_for_tgt'] = hash_gen_tgt_index[hash_string]
    return df_group





def completion(df_revised_group,csv_save_file,csv_save_name,generation, groundtruth_csv_name, parameter_predict_true):
    # combine
    # generation = Generation()
    # groundtruth_csv_name = para.tgt_groundtruth_name
    tgt_combine_true_test_case,tgt_combine_consider_test_case = generation.combine_test_case(df_revised_group,parameter_predict_true)
    tgt_app_name = df_revised_group.iloc[0].at['tgt_app']
    function = df_revised_group.iloc[0].at['function']
    print("tgt_app_name",tgt_app_name)
    print("function",function)
    print("tgt_combine_true_test_case",tgt_combine_true_test_case)
    print("tgt_combine_consider_test_case",tgt_combine_consider_test_case)
    combined_test_case, search_time = search_test_case(tgt_combine_true_test_case, tgt_combine_consider_test_case, df_revised_group)
    # combined_test_case, search_time = search_test_case_ori(tgt_combine_true_test_case, tgt_combine_consider_test_case, df_group)
    print("combined_test_case" ,combined_test_case)

    judge_result = judge_the_combined_test_case(combined_test_case, tgt_app_name, function, csv_save_file, groundtruth_csv_name)
    print("whether predict test_case_result", judge_result)


    record_search_result(combined_test_case, tgt_app_name, function, csv_save_file, csv_save_name ,search_time
                         ,judge_result,'')


def generate_explore_script(tgt_app_name, function_name, completion_csv_path,information_csv_path,information_csv_name,script_path,completion_csv_name,style):

    generate_script(tgt_app_name, function_name, completion_csv_path,completion_csv_name,information_csv_path,information_csv_name,script_path,style)

