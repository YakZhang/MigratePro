
# Goal: given four migrating test cases from four apps, we combine them into one test case for a target app
# coding=utf-8
import numpy as np
import pandas as pd


def combine_test_case(df_group):
    tgt_indexs= df_group['tgt_index']
    tgt_candidate_test_case = list(set(tgt_indexs.values.tolist()))
    tgt_combine_true_test_case = []
    tgt_combine_false_test_case = []
    for tgt_index in tgt_candidate_test_case: # iter set
        df_tgt = df_group.query("tgt_index == @tgt_index") # group the certain tgt_index in the same dataframe
        tgt_predict_true = 0
        for idx in range(len(df_tgt)):
            if df_tgt.iloc[idx].at['ori_predict_label'] == 1:
                tgt_predict_true += 1
        if tgt_predict_true >= 0.5:
            tgt_combine_true_test_case.append(tgt_index)
        elif tgt_index == tgt_index: # tgt_index !=nan
            tgt_combine_false_test_case.append(tgt_index)
    return tgt_combine_true_test_case,tgt_combine_false_test_case

def get_new_test_event(df_tgt,ori_predict_label,column_index):
    predict_actions = set(df_tgt["predict_action"].values.tolist())
    if np.nan in predict_actions:
        predict_actions.remove(np.nan)
    if len(predict_actions)==0:
        prediction_actions = np.nan
    src_combine = df_tgt["src_app"].values.tolist()
    df_line = pd.DataFrame(
        {
            'index':column_index,
            'tgt_app': df_tgt.iloc[0].at['tgt_app'],
            'function': df_tgt.iloc[0].at['function'],
            'tgt_ori_id': df_tgt.iloc[0].at['tgt_ori_id'],
            'tgt_ori_xpath': df_tgt.iloc[0].at['tgt_ori_xpath'],
            'tgt_add_id': df_tgt.iloc[0].at['tgt_add_id'],
            'tgt_add_xpath': df_tgt.iloc[0].at['tgt_add_xpath'],
            'tgt_text': df_tgt.iloc[0].at['tgt_text'],
            'tgt_content': df_tgt.iloc[0].at['tgt_content'],
            'tgt_state': df_tgt.iloc[0].at['tgt_state'],
            'tgt_index': df_tgt.iloc[0].at['tgt_index'],
            'type': df_tgt.iloc[0].at['type'],
            'label': df_tgt.iloc[0].at['label'],
            'ori_predict_label': ori_predict_label,
            'action': df_tgt.iloc[0].at['action'],
            'predict_action': str(predict_actions),
            'src_combine': str(src_combine),
        }, index=[1]
    )
    return df_line


def generate_test_cases(csv_file,csv_name):
    df = pd.read_csv(csv_file + csv_name)
    df_combine = pd.DataFrame(columns=['index','tgt_app','function','tgt_ori_id','tgt_ori_xpath','tgt_add_id','tgt_add_xpath','tgt_text','tgt_content',
                                       'tgt_state','tgt_index','type','label','ori_predict_label','action','predict_action','src_combine'])
    groups = df.groupby(['tgt_app', 'function']) # given a target app
    index = 0
    for group in groups:
        df_group = group[1]
        tgt_combine_true_test_case,tgt_combine_false_test_case = combine_test_case(df_group)
        # print(index)
        if len(tgt_combine_true_test_case) >0:
            for tgt_index in tgt_combine_true_test_case:
                df_tgt = df_group.query("tgt_index == @tgt_index and ori_predict_label == 1")
                df_line = get_new_test_event(df_tgt,1,index)
                df_combine = pd.concat([df_combine,df_line],ignore_index=True)
                index += 1
        if len(tgt_combine_false_test_case) >0:
            for tgt_index in tgt_combine_false_test_case:
                df_tgt = df_group.query("tgt_index == @tgt_index")

                df_line = get_new_test_event(df_tgt,0,index)
                df_combine = pd.concat([df_combine,df_line],ignore_index=True)
                index += 1

    # df_combine.to_csv(csv_save_file+csv_save_name)
    return df_combine

def modify_predict_action(df_combine):
    for idx in range(len(df_combine)):
        ori_predict_label = df_combine.loc[idx,'ori_predict_label']
        label = df_combine.loc[idx,'label']
        if ori_predict_label != 1: 
            df_combine.loc[idx,'predict_action'] = np.nan
        type = df_combine.loc[idx,'type']
        if ori_predict_label == 1 and type == 'SYS_EVENT':
            df_combine.loc[idx, 'predict_action'] = np.nan
        if label != 1:
            df_combine.loc[idx,'action'] = np.nan
        action = df_combine.loc[idx,'action']
        predict_action = df_combine.loc[idx,'predict_action']
        predict_event_true = 0
        if label == 1 and ori_predict_label == 1 and type == 'SYS_EVENT':
            predict_event_true = 1
        elif label == 1 and ori_predict_label == 1 and action in predict_action:
            predict_event_true = 1
        df_combine.loc[idx,'predict_event_true'] = predict_event_true
    # df_combine.to_csv(csv_save_file+csv_save_name)
    return df_combine

def get_true_test_case(df_combine,csv_save_file,csv_save_name,csv_false_save_name):
    groups = df_combine.groupby(['tgt_app','function'])
    df_false = pd.DataFrame(columns=df_combine.columns.tolist())
    group_index = 0
    migration_test_case_num = len(groups)
    migration_true_test_case_num = 0
    for group in groups:
        df_group = group[1]
        predict_test_true = 1
        for index in range(len(df_group)):
            predict_event_true = df_group.iloc[index].at['predict_event_true']
            if predict_event_true == 0:
                predict_test_true = 0
        for index in range(len(df_group)):
            column_num = df_group.iloc[index].at['index']
            df_group.loc[column_num, 'test_case'] = group_index
            df_group.loc[column_num, 'predict_test_true'] = predict_test_true
            df_combine.loc[column_num,'test_case'] = group_index
            df_combine.loc[column_num,'predict_test_true']=predict_test_true
        if predict_test_true == 1:
            migration_true_test_case_num += 1
        else:
             df_false = pd.concat([df_false, df_group], axis=0)
        group_index = group_index + 1
    print("migration_test_case_num", migration_test_case_num)
    print("migration_true_test_case_num", migration_true_test_case_num)
    df_combine.to_csv(csv_save_file+csv_save_name)
    df_false.to_csv(csv_save_file + csv_false_save_name)
    return df_combine


def update_src_tgt_test_case(df_combine,df_ori,csv_save_file,csv_save_name):
    # given df_combine, df_ori(ori src_tgt_test_case for test case migration)
    # output the migration true_test_case_num; predict_test_true for src-tgt pair
    for idx in range(len(df_combine)):
        tgt_app = df_combine.loc[idx,'tgt_app']
        function = df_combine.loc[idx,'function']
        tgt_index = df_combine.loc[idx,'tgt_index']
        predict_event_true = df_combine.loc[idx,'predict_event_true']
        predict_action = df_combine.loc[idx,'predict_action']
        df_lines = df_ori.query("tgt_app==@tgt_app and function == @function and tgt_index == @tgt_index")
        for idx in range(len(df_lines)):
            ori_column_index = df_lines.iloc[idx].at['index']
            df_ori.loc[ori_column_index,'predict_event_true'] = predict_event_true
            df_ori.loc[ori_column_index,'predict_action'] = predict_action
            df_ori.loc[ori_column_index,'ori_predict_label'] = predict_event_true
    df_ori.to_csv(csv_save_file+csv_save_name)

