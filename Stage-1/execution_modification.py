
import pandas as pd
import numpy as np
from test_execution import ContactsAndroidTests
# bisect is for insert an item in an ordered sequence
import bisect
import time
from datetime import datetime
from common_function import create_file
import copy

class Generation():

    def get_group(self,tgt_app_name,function_name,csv_file,csv_name):
        df = pd.read_csv(csv_file + csv_name)

        # fit for fruiter
        if 'tgt_index_manual' in df.columns.tolist():
            df = df.rename(columns={'tgt_index_manual':'tgt_index'})
        if 'appflow_new_id' in df.columns.tolist():
            df = df.rename(columns={'appflow_new_id':'tgt_add_id'})
        if 'appflow_new_appium_xpath' in df.columns.tolist():
            df = df.rename(columns={'appflow_new_appium_xpath':'tgt_add_xpath'})


        df_only_predict_true = df.query("ori_predict_label == 1") # only use the predict_true to generate test case

        groups = df_only_predict_true.groupby(['tgt_app', 'function']) # given a target app
        for group in groups:
            tgt_app = group[0][0]
            function = group[0][1]
            df_group = group[1]
            if tgt_app == tgt_app_name and function == function_name:
                # initial column:rev_predict_label
                df_group['rev_predict_label'] = df_group['ori_predict_label']
                # delete the same column (e.g., a34-a33-b32 fp==tp)
                if 'src_index' in df_group.columns.values.tolist():
                    df_duplicate_group =df_group.drop_duplicates(['src_app','tgt_app','function','src_index','tgt_index'])
                    return df_duplicate_group
                else:
                    df_duplicate_group = df_group.drop_duplicates(
                        ['src_app', 'tgt_app', 'function', 'tgt_index'])
                    return df_duplicate_group

    def combine_test_case(self,df_group, predict_true_threhold):
        tgt_indexs = df_group['tgt_index']
        tgt_candidate_test_case = list(set(tgt_indexs.values.tolist()))
        # for '-3' '-2'
        # tgt_candidate_test_case = list(map(int,tgt_candidate_test_case))
        tgt_candidate_test_case.sort()
        tgt_combine_true_test_case = []
        tgt_combine_consider_test_case = []
        for tgt_index in tgt_candidate_test_case:  # iter set
            df_tgt = df_group.query("tgt_index == @tgt_index")  # group the certain tgt_index in the same dataframe
            tgt_predict_true = 0
            for idx in range(len(df_tgt)):
                # if df_tgt.iloc[idx].at['ori_predict_label'] == 1:
                if df_tgt.iloc[idx].at['rev_predict_label']==1:
                    tgt_predict_true += 1
            if tgt_predict_true >= predict_true_threhold:
                tgt_combine_true_test_case.append(tgt_index)
            if tgt_predict_true > 0 and tgt_predict_true < predict_true_threhold:
                tgt_combine_consider_test_case.append(tgt_index)
        return tgt_combine_true_test_case,tgt_combine_consider_test_case

    def test_case_for_execution(self,df_group,tgt_index_list):
        test_case = []
        action_label = 0
        tgt_app = df_group.iloc[0].at['tgt_app']
        for tgt_index in tgt_index_list:
            df_tgt = df_group.query("tgt_index == @tgt_index and rev_predict_label == 1")
            event_checker = np.nan
            input = np.nan
            type = ""
            predict_actions = np.nan
            if df_tgt.iloc[0].at['tgt_add_id']==df_tgt.iloc[0].at['tgt_add_id']: # not nan for tgt_add_id
                event_checker = df_tgt.iloc[0].at['tgt_add_id']
            else:
                event_checker = df_tgt.iloc[0].at['tgt_add_xpath']
            type = df_tgt.iloc[0].at['type']
            predict_actions = set(df_tgt["predict_action"].values.tolist())
            if np.nan in predict_actions:
                predict_actions.remove(np.nan)
            if len(predict_actions) == 0:
                predict_actions = np.nan
            # for predict_actions but contains two actions
            predict_action_list = list()
            if type != 'SYS_EVENT' and type != 'EMPTY_EVENT':
                predict_action_list = list(predict_actions)
            if len(predict_action_list) == 1:
                predict_action = predict_action_list[0]
                input = np.nan
                if 'input' in df_tgt:
                    input = df_tgt.iloc[0].at['input']
                elif 'predict_input' in df_tgt:
                    input = df_tgt.iloc[0].at['predict_input']
                event = [tgt_index,event_checker,type,predict_action,input]
                test_case.append(event)
            elif len(predict_action_list) > 1:
                predict_actions = predict_action_list
                # input = df_tgt.iloc[0].at['input']
                # get inputs
                inputs = []
                for predict_action in predict_actions:
                    if 'predict_input' in df_tgt:
                        input = df_tgt[df_tgt['predict_action']==predict_action].iloc[0].at['predict_input']
                        inputs.append(input)
                    else:
                        input = df_tgt[df_tgt['predict_action'] == predict_action].iloc[0].at['input']
                        inputs.append(input)
                event = [tgt_index,event_checker,type,predict_actions,inputs]
                test_case.append(event)
                action_label = 1
            elif len(predict_action_list) == 0: # for SYS_Event
                print('SYS_EVENT')
                predict_action = ''
                input = ''
                event = [tgt_index,event_checker,type,predict_action,input]
                test_case.append(event)
        return test_case,tgt_app, action_label

    def test_case_for_execution_tgt(self,df_group,src_index_list):
        # for one tgt multiple src
        test_case = []
        action_label = 0
        tgt_app = df_group.iloc[0].at['tgt_app']
        for src_index in src_index_list:
            df_tgt = df_group.query("src_index == @src_index and rev_predict_label == 1")
            tgt_index = df_tgt.iloc[0].at['tgt_index']
            event_checker = np.nan
            input = np.nan
            type = ""
            predict_actions = np.nan
            if df_tgt.iloc[0].at['tgt_add_id']==df_tgt.iloc[0].at['tgt_add_id']: # not nan for tgt_add_id
                event_checker = df_tgt.iloc[0].at['tgt_add_id']
            else: # not nan for tgt_add_id
                event_checker = df_tgt.iloc[0].at['tgt_add_xpath']
            type = df_tgt.iloc[0].at['type']
            if type == 'SYS_EVENT' or type == 'EMPTY_EVENT':
                continue
            predict_actions = set(df_tgt["predict_action"].values.tolist())
            if np.nan in predict_actions:
                predict_actions.remove(np.nan)
            if len(predict_actions) == 0:
                prediction_actions = np.nan
            # for predict_actions but contains two actions
            predict_action_list = list(predict_actions)
            if len(predict_action_list) == 1:
                predict_action = predict_action_list[0]
                input = ''
                if 'predict_input' in df_tgt:
                    input = df_tgt.iloc[0].at['predict_input']
                elif 'input' in df_tgt:
                    input = df_tgt.iloc[0].at['input']
                event = [tgt_index,event_checker,type,predict_action,input]
                test_case.append(event)
            elif len(predict_action_list) > 1:
                predict_action = predict_action_list
                input = ''
                if 'predict_input' in df_tgt:
                    input = df_tgt.iloc[0].at['predict_input']
                elif 'input' in df_tgt:
                    input = df_tgt.iloc[0].at['input']
                event = [tgt_index,event_checker,type,predict_action,input]
                test_case.append(event)
                action_label = 1
            elif len(predict_action_list) == 0: # for SYS_Event
                predict_action = ''
                input = ''
                if 'predict_input' in df_tgt:
                    input = df_tgt.iloc[0].at['predict_input']
                elif 'input' in df_tgt:
                    input = df_tgt.iloc[0].at['input']
                event = [tgt_index,event_checker,type,predict_action,input]
                test_case.append(event)
        return test_case,tgt_app, action_label






    def execute_test_case(self,test_case,tgt_app,action_index,reset_label,end_label,android_test):
        # return a response result to guide search_test_case
        # add a reset label for setUp and tearDown
        # android_test = ContactsAndroidTests()
        if reset_label == 0:
            android_test.setUp(tgt_app)
            execution_label = android_test.test_function(test_case,action_index)
            reset_label = 1
            # android_test.tearDown()
        else:
            execution_label = android_test.test_function(test_case, action_index)
            reset_label = 1
        if end_label == 1:
            android_test.tearDown()
        return execution_label,reset_label





def search_test_case(tgt_combine_true_test_case, tgt_combine_consider_test_case, df_group):

    time_start = time.time()
    if len(tgt_combine_consider_test_case) == 0: 
        print("all tgt_combine_true_test_case")
        time_end = time.time()
        search_time = time_end - time_start
        return tgt_combine_true_test_case, search_time
    all_test_events = copy.deepcopy(tgt_combine_true_test_case)
    all_test_events = insert_test_case(all_test_events, tgt_combine_consider_test_case)
    generation = Generation()
    execute_test_events = []
    reset_label = 0
    android_test = ContactsAndroidTests()

    for idx in range(len(all_test_events)):
        test_event = all_test_events[idx]
        print(test_event)
        execute_test_events.append(test_event)
        # for test
        # execute_test_events = [0.0,1.0,2.0,3.0,4.0,5.0]
        test_case,tgt_app,action_label = generation.test_case_for_execution(df_group, [test_event])
        execution_label = ""
        end_label = 0
        if idx == len(all_test_events) -1:
            end_label = 1
        if action_label == 0:
            execution_label, reset_label = generation.execute_test_case(test_case, tgt_app, 0,reset_label, end_label,android_test)
        else:
            # end_label = 0 for the first because the session cannot tear down
            execution_label_first, reset_label = generation.execute_test_case(test_case, tgt_app, 0,reset_label,0,android_test)
            execution_label_second, reset_label = generation.execute_test_case(test_case, tgt_app, 1,reset_label,end_label,android_test)
            if execution_label_first == 1 or execution_label_second == 1:
                execution_label = 1
        if execution_label == 0:
            execute_test_events.remove(test_event)
            combined_test_case = insert_test_case(execute_test_events, tgt_combine_true_test_case)
            time_end = time.time()
            search_time = time_end-time_start
            return combined_test_case,search_time
    combined_test_case = insert_test_case(execute_test_events, tgt_combine_true_test_case)
    time_end = time.time()
    search_time = time_end - time_start
    return combined_test_case, search_time









def insert_test_case(ori_test_case,after_test_case):
    # new_test_case = ori_test_case
    for idx in range(len(after_test_case)):
        if after_test_case[idx] in ori_test_case:
            continue
        bisect.insort(ori_test_case,after_test_case[idx])
    return ori_test_case

def record_search_result(combined_test_case, tgt_app_name,function_name,csv_save_file,csv_save_name,search_time,src_app_name):
    create_file(csv_save_file+csv_save_name)
    df = pd.read_csv(csv_save_file+csv_save_name)
    if src_app_name != '':
        for idx in range(len(combined_test_case)):
            predict_tgt_indx = combined_test_case[idx]
            record_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df_line = pd.DataFrame(
                {
                    'src_app':src_app_name,
                    'tgt_app': tgt_app_name,
                    'function': function_name,
                    'predict_tgt_index':predict_tgt_indx,
                    'search_time':search_time,
                    'time':record_time
                },index=[1]
            )
            df = pd.concat([df,df_line],axis=0,ignore_index=True)
    else:
        for idx in range(len(combined_test_case)):
            record_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            predict_tgt_indx = combined_test_case[idx]
            df_line = pd.DataFrame(
                {
                    'tgt_app': tgt_app_name,
                    'function': function_name,
                    'predict_tgt_index': predict_tgt_indx,
                    'search_time': search_time,
                    'time':record_time
                }, index=[1]
            )
            df = pd.concat([df, df_line], axis=0, ignore_index=True)
    df.to_csv(csv_save_file + csv_save_name)


def judge_the_combined_test_case(combined_test_case,tgt_app_name,function,csv_save_file,groundtruth_csv_name):

    df_groundtruth = pd.read_csv(groundtruth_csv_name)

    df_groundtruth = df_groundtruth.rename(columns={'app_name':'tgt_app'})
    df_tgt_app = df_groundtruth.query("tgt_app==@tgt_app_name and function == @function")
    groundtruth_tgt_indexs = df_tgt_app['tgt_index'].values.tolist()
    print("groundtruth_test_case",groundtruth_tgt_indexs)
    combined_test_case = list(map(int,combined_test_case))
    if groundtruth_tgt_indexs == combined_test_case:
        return True
    else:
        return False



















