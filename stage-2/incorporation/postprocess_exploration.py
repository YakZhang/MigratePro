

import json
import os
import numpy as np
import Levenshtein

import pandas as pd
import parameter as para


def choose_droidbot_output(output_dirs_path):
    """
    get the output_file_path that has the minimize path and get the groundtruth
    if cannot get the output_file_path that has minimize path, then random analyze one output_file
    :param output_file:
    :return:
    """
    has_output = True
    have_file = False
    output_dir_names = os.listdir(output_dirs_path)
    action_count = 100
    choose_output_dir = ''
    choose_output_dirs = [] # all find results choose_output_dirs
    for output_dir_name in output_dir_names:
        if '.DS_Store' in output_dir_name:
            continue
        if 'script' in output_dir_name:
            continue
        # choose_output_dir = output_dirs_path + output_dir_name + "/"
        if os.path.isfile(output_dirs_path+output_dir_name):
            continue
        action_count_path = output_dirs_path + output_dir_name + "/"+'logger_info.txt'
        if os.path.exists(action_count_path):
            with open(action_count_path,'r') as f:
                data = f.read()
                current_output_dir = output_dirs_path + output_dir_name + "/"
                choose_output_dirs.append(current_output_dir)
                if 'Cannot' in data:
                    have_file = True
                    continue
                # current_output_dir = output_dirs_path + output_dir_name + "/"
                # choose_output_dirs.append(current_output_dir)
                row_current_action_count = data.replace("Have finish the search and the action number is ","")
                current_action_count = int(row_current_action_count.split("\n")[0])
                if current_action_count <= action_count:
                    action_count = current_action_count
                    choose_output_dir = output_dirs_path + output_dir_name + "/"
    if choose_output_dir == '':
        has_output = False
    return choose_output_dir,choose_output_dirs,has_output,have_file


def revise_screen_name(state_file_path):
    for file in os.listdir(state_file_path):
        file_path = os.path.join(state_file_path, file)
        if '.json' in file_path:
            # find json file
            with open (file_path,'r') as load_f:
                state_dict = json.load(load_f)
                state_tag = state_dict['tag']
                state_str = state_dict['state_str']
                screen_ori_name = "screen_" + state_tag + ".jpg"
                screen_rev_name = "state_" + state_tag+ "_"+ state_str + ".jpg"
                if os.path.exists(state_file_path + screen_ori_name):
                    os.rename(state_file_path + screen_ori_name, state_file_path + screen_rev_name)


def generate_test_case_sequence(events_path,df_info):
    # add used columns to describe whether the tgt_index has been used
    df_info['used'] = 'False'
    df_group =pd.DataFrame(columns=['tgt_app','function','tgt_add_id','tgt_text','tgt_content','start_state','end_state','view','tgt_index', 'analyze_path','type','action','predict_input'],index=[])
    file_paths = []
    for file in os.listdir(events_path):
        file_path = os.path.join(events_path,file)
        if '.json' in file_path:
            file_paths.append(file_path)
    file_paths.sort()
    tgt_app = file_paths[0].split("/")[6].split("_")[0]
    tgt_function = file_paths[0].split("/")[6].split("_")[1]
    for file_path in file_paths:
        with open(file_path,'r') as load_f:
            # initial
            tgt_add_id = np.nan
            tgt_content = np.nan
            tgt_text = np.nan
            tgt_add_xpath = np.nan
            tgt_view_str = np.nan
            type = np.nan
            action = np.nan
            input = np.nan
            event_dict = json.load(load_f)
            if event_dict['event']['event_type'] == "kill_app":
                continue
            if event_dict['event']['event_type'] == 'intent':
                continue
            if 'view' in event_dict['event']:
                tgt_add_id = event_dict['event']['view']['resource_id']
                tgt_content = event_dict['event']['view']['content_description']
                tgt_text = event_dict['event']['view']['text']
                tgt_view_str = event_dict['event']['view']['view_str']
                if 'xpath' in event_dict['event']['view']:
                    tgt_add_xpath = event_dict['event']['view']['xpath']
            start_state_str = event_dict['start_state']
            end_state_str = event_dict['stop_state']
            event_tag = event_dict['tag']
            if event_dict['event']['event_type'] == 'touch':
                action = 'click'
                type = 'gui'
            elif event_dict['event']['event_type'] == 'set_text':
                action = 'send'
                type = 'gui'
                input = event_dict['event']['text']
            elif event_dict['event']['event_type'] == 'scroll':
                action = 'swipe_right'
                type = 'gui'
            elif event_dict['event']['event_type'] == 'oracle':
                type = 'oracle'
                if event_dict['event']['condition'] == 'disappear':
                    action = 'invisible'
                else:
                    action = 'presence'
            elif event_dict['event']['event_type'] == 'key':
                type = 'droidbot_key'
                action = event_dict['event']['name']
            elif event_dict['event']['event_type'] == 'long_touch':
                type = 'gui'
                action = 'long_press'
            elif event_dict['event']['event_type'] == 'set_text_and_enter':
                type = 'gui'
                action = 'send_keys_and_enter' # for craftdroid

            tgt_index = -2
            if tgt_add_id == 'com.fsck.k9:id/to_wrapper':
                tgt_add_id = "com.fsck.k9:id/to"
            if tgt_add_id == 'com.appple.app.email:id/to_wrapper':
                tgt_add_id = 'com.appple.app.email:id/to'
            if tgt_add_id == 'com.appple.app.email:id/subject_wrapper':
                tgt_add_id = 'com.appple.app.email:id/subject'

            if tgt_add_id == 'com.contextlogic.geek:id/signin_fragement_password_text':
                print("here")

            # special for a13/b11
            if tgt_content == 'Donald Bren School of Information and Computer Sciences @ University of California, Irvine':
                tgt_content = 'Donald Bren School of Information and Computer Sciences'


            # since craftdroid has stepping type, we cannot use the type as the key, so we use the action as the key
            if tgt_add_id==tgt_add_id and tgt_add_id != None:
                df_tgt = df_info.query("tgt_app ==@tgt_app and function == @tgt_function and tgt_add_id ==@tgt_add_id and used == 'False' ")
                # tgt_index = find_tgt_index(df_info, tgt_app, tgt_function, type,tgt_add_id,df_tgt)
                if len(df_tgt)!=0:
                    # detect action
                    for idx in range(len(df_tgt)):
                        if action in df_tgt.iloc[idx].at['predict_action']:
                            tgt_index = df_tgt.iloc[idx].at['tgt_index']
                            break
                    # tgt_index = df_tgt.iloc[0].at['tgt_index']
                    for idx in range(len(df_tgt)):
                        if df_tgt.iloc[idx].at['tgt_index'] == tgt_index:
                            row_num = df_tgt.iloc[idx].at['index']
                            df_info.loc[row_num,'used'] = True

            # tgt_index == -2 means cannot find a corresponding widget, need other inforation to search (i.e., content, text, xpath)
            if tgt_index == -2 and tgt_content==tgt_content and tgt_content != None:
                df_tgt = df_info.query("tgt_app ==@tgt_app and function == @tgt_function and tgt_content ==@tgt_content and used == 'False' ")
                if len(df_tgt)!=0:
                    for idx in range(len(df_tgt)):
                        if action in df_tgt.iloc[idx].at['predict_action']:
                            tgt_index = df_tgt.iloc[idx].at['tgt_index']
                            break
                    # tgt_index = df_tgt.iloc[0].at['tgt_index']
                    for idx in range(len(df_tgt)):
                        if df_tgt.iloc[idx].at['tgt_index'] == tgt_index:
                            row_num = df_tgt.iloc[idx].at['index']
                            df_info.loc[row_num,'used'] = True
                # tgt_index = find_tgt_index(df_info, tgt_app, tgt_function, type, tgt_content)

            if tgt_index == -2 and tgt_text == tgt_text and tgt_text != None:
                tgt_text = tgt_text.replace("\b", " ")
                # tgt_index = find_tgt_index(df_info,tgt_app,tgt_function,type,tgt_content)
                df_tgt = df_info.query("tgt_app ==@tgt_app and function == @tgt_function and tgt_text ==@tgt_text and used == 'False' ")
                if len(df_tgt)!=0:
                    for idx in range(len(df_tgt)):
                        if action in df_tgt.iloc[idx].at['predict_action']:
                            tgt_index = df_tgt.iloc[idx].at['tgt_index']
                            break
                    # tgt_index = df_tgt.iloc[0].at['tgt_index']
                    for idx in range(len(df_tgt)):
                        if df_tgt.iloc[idx].at['tgt_index'] == tgt_index:
                            row_num = df_tgt.iloc[idx].at['index']
                            df_info.loc[row_num,'used'] = True

            # add for fruiter dataset
            if tgt_index == -2 and tgt_add_xpath == tgt_add_xpath and tgt_add_xpath != None:
                df_tgt = df_info.query("tgt_app ==@tgt_app and function == @tgt_function and tgt_add_xpath ==@tgt_add_xpath and used == 'False' ")
                if len(df_tgt)!=0:
                    for idx in range(len(df_tgt)):
                        if action in df_tgt.iloc[idx].at['predict_action']:
                            tgt_index = df_tgt.iloc[idx].at['tgt_index']
                            break
                    # tgt_index = df_tgt.iloc[0].at['tgt_index']
                    for idx in range(len(df_tgt)):
                        if df_tgt.iloc[idx].at['tgt_index'] == tgt_index:
                            row_num = df_tgt.iloc[idx].at['index']
                            df_info.loc[row_num,'used'] = True




            df_line= pd.DataFrame(
                {
                    'tgt_app':tgt_app,
                    'function':tgt_function,
                    'tgt_add_id':tgt_add_id,
                    'tgt_text':tgt_text,
                    'tgt_content':tgt_content,
                    'tgt_add_xpath':tgt_add_xpath,
                    'view':tgt_view_str,
                    'start_state':start_state_str,
                    'end_state':end_state_str,
                    'event_tag':event_tag,
                    'action':action,
                    'type': type,
                    'predict_input':input,
                    'tgt_index':tgt_index,
                    'analyze_path':file_path

                },index=[1]
            )
            df_group = pd.concat([df_group,df_line],axis=0,ignore_index=True)
            # df_group = df_group.append(df_line,ignore_index=True)
    return df_group,tgt_app,tgt_function

def generate_test_case_sequence_src(events_path,df_info):
    # add used columns to describe whether the tgt_index has been used
    df_info['used'] = 'False'
    df_group =pd.DataFrame(columns=['src_app','tgt_app','function','tgt_add_id','tgt_text','tgt_content','start_state','end_state','view','tgt_index', 'analyze_path','type','action','predict_input'],index=[])
    file_paths = []
    for file in os.listdir(events_path):
        file_path = os.path.join(events_path,file)
        if '.json' in file_path:
            file_paths.append(file_path)
    file_paths.sort()
    src_app = file_paths[0].split("/")[6].split("_")[0]
    tgt_app = file_paths[0].split("/")[6].split("_")[1]
    tgt_function = file_paths[0].split("/")[6].split("_")[2]
    for file_path in file_paths:
        with open(file_path,'r') as load_f:
            # initial
            tgt_add_id = np.nan
            tgt_content = np.nan
            tgt_text = np.nan
            tgt_view_str = np.nan
            type = np.nan
            action = np.nan
            input = np.nan
            event_dict = json.load(load_f)
            if event_dict['event']['event_type'] == "kill_app":
                continue
            if event_dict['event']['event_type'] == 'intent':
                continue
            if 'view' in event_dict['event']:
                tgt_add_id = event_dict['event']['view']['resource_id']
                tgt_content = event_dict['event']['view']['content_description']
                tgt_text = event_dict['event']['view']['text']
                tgt_view_str = event_dict['event']['view']['view_str']
            start_state_str = event_dict['start_state']
            end_state_str = event_dict['stop_state']
            event_tag = event_dict['tag']
            if event_dict['event']['event_type'] == 'touch':
                action = 'click'
                type = 'gui'
            elif event_dict['event']['event_type'] == 'set_text':
                action = 'send'
                type = 'gui'
                input = event_dict['event']['text']
            elif event_dict['event']['event_type'] == 'scroll':
                action = 'swipe_right'
                type = 'gui'
            elif event_dict['event']['event_type'] == 'oracle':
                type = 'oracle'
                if event_dict['event']['condition'] == 'disappear':
                    action = 'invisible'
                else:
                    action = 'presence'
            elif event_dict['event']['event_type'] == 'key':
                type = 'droidbot_key'
                action = event_dict['event']['name']
            elif event_dict['event']['event_type'] == 'long_touch':
                type = 'gui'
                action = 'long_press'
            elif event_dict['event']['event_type'] == 'set_text_and_enter':
                type = 'gui'
                action = 'send_keys_and_enter'

            tgt_index = -2
            if tgt_add_id == 'com.fsck.k9:id/to_wrapper':
                tgt_add_id = "com.fsck.k9:id/to"
            if tgt_add_id == 'com.appple.app.email:id/to_wrapper':
                tgt_add_id = 'com.appple.app.email:id/to'
            if tgt_add_id == 'com.appple.app.email:id/subject_wrapper':
                tgt_add_id = 'com.appple.app.email:id/subject'


            if tgt_content == 'Donald Bren School of Information and Computer Sciences @ University of California, Irvine':
                tgt_content = 'Donald Bren School of Information and Computer Sciences'


            # since craftdroid has stepping type, we cannot use the type as the key, so we use the action as the key
            if tgt_add_id==tgt_add_id and tgt_add_id != None:
                df_tgt = df_info.query("src_app == @src_app and tgt_app ==@tgt_app and function == @tgt_function and tgt_add_id ==@tgt_add_id and used == 'False' ")
                # tgt_index = find_tgt_index(df_info, tgt_app, tgt_function, type,tgt_add_id,df_tgt)
                if len(df_tgt)!=0:
                    # detect action
                    for idx in range(len(df_tgt)):
                        if action in df_tgt.iloc[idx].at['predict_action']:
                            tgt_index = df_tgt.iloc[idx].at['tgt_index']
                            break
                    #
                    # tgt_index = df_tgt.iloc[0].at['tgt_index']
                    for idx in range(len(df_tgt)):
                        if df_tgt.iloc[idx].at['tgt_index'] == tgt_index:
                            row_num = df_tgt.iloc[idx].at['index']
                            df_info.loc[row_num,'used'] = True


            if tgt_index == -2 and tgt_content==tgt_content and tgt_content != None:
                df_tgt = df_info.query("src_app == @src_app and tgt_app ==@tgt_app and function == @tgt_function and tgt_content ==@tgt_content and used == 'False' ")
                if len(df_tgt)!=0:
                    for idx in range(len(df_tgt)):
                        if action in df_tgt.iloc[idx].at['predict_action']:
                            tgt_index = df_tgt.iloc[idx].at['tgt_index']
                            break
                    # tgt_index = df_tgt.iloc[0].at['tgt_index']
                    for idx in range(len(df_tgt)):
                        if df_tgt.iloc[idx].at['tgt_index'] == tgt_index:
                            row_num = df_tgt.iloc[idx].at['index']
                            df_info.loc[row_num,'used'] = True
                # tgt_index = find_tgt_index(df_info, tgt_app, tgt_function, type, tgt_content)

            if tgt_index == -2 and tgt_text == tgt_text and tgt_text != None:
                tgt_text = tgt_text.replace("\b", " ")
                # tgt_index = find_tgt_index(df_info,tgt_app,tgt_function,type,tgt_content)
                df_tgt = df_info.query("src_app == @src_app and tgt_app ==@tgt_app and function == @tgt_function and tgt_text ==@tgt_text and used == 'False' ")
                if len(df_tgt)!=0:
                    for idx in range(len(df_tgt)):
                        if action in df_tgt.iloc[idx].at['predict_action']:
                            tgt_index = df_tgt.iloc[idx].at['tgt_index']
                            break
                    # tgt_index = df_tgt.iloc[0].at['tgt_index']
                    for idx in range(len(df_tgt)):
                        if df_tgt.iloc[idx].at['tgt_index'] == tgt_index:
                            row_num = df_tgt.iloc[idx].at['index']
                            df_info.loc[row_num,'used'] = True
            df_line= pd.DataFrame(
                {
                    'src_app':src_app,
                    'tgt_app':tgt_app,
                    'function':tgt_function,
                    'tgt_add_id':tgt_add_id,
                    'tgt_text':tgt_text,
                    'tgt_content':tgt_content,
                    'view':tgt_view_str,
                    'start_state':start_state_str,
                    'end_state':end_state_str,
                    'event_tag':event_tag,
                    'action':action,
                    'type': type,
                    'predict_input':input,
                    'tgt_index':tgt_index,
                    'analyze_path':file_path

                },index=[1]
            )
            df_group = pd.concat([df_group,df_line],axis=0,ignore_index=True)
            # df_group = df_group.append(df_line,ignore_index=True)
    return df_group,tgt_app,tgt_function,src_app

def generate_test_case_sequence_false(output_dirs_path,policy_name,df_information,output_test_name):
    root_path = output_dirs_path.replace(policy_name,"")
    script_file = root_path + 'script/script.json'
    tgt_index_list = []
    df_group = pd.DataFrame(
        columns=['tgt_app', 'function', 'tgt_add_id', 'tgt_text', 'tgt_content', 'start_state', 'end_state', 'view',
                 'tgt_index', 'analyze_path', 'type', 'action', 'predict_input'], index=[])
    with open(script_file, 'r') as load_f:
        state_dict = json.load(load_f)
        tgt_indexs=state_dict['main'].keys()
        for tgt_index_ori in tgt_indexs:
            tgt_index = tgt_index_ori.split("_")[2]
            tgt_index_list.append(float(tgt_index))
    tgt_app = output_test_name.split("_")[0]
    function = output_test_name.split("_")[1].replace("/","")
    for tgt_index in tgt_index_list:
        # df_tgt_group = df_information.query("tgt_app == @tgt_app and function == @tgt_function and tgt_index == @tgt_index and label == 1")
        df_info_group = df_information.query("@tgt_app==tgt_app and @function==function and @tgt_index==tgt_index and ori_predict_label == 1")
        df_line = pd.DataFrame(
            {
                'tgt_app':df_info_group.iloc[0].at['tgt_app'],
                'function':df_info_group.iloc[0].at['function'],
                'tgt_add_id':df_info_group.iloc[0].at['tgt_add_id'],
                'tgt_text':df_info_group.iloc[0].at['tgt_text'],
                'tgt_content':df_info_group.iloc[0].at['tgt_content'],
                'start_state':np.nan,
                'end_state':np.nan,
                'view':np.nan,
                'tgt_index':tgt_index,
                'analyze_path':np.nan,
                'type':df_info_group.iloc[0].at['type'],
                'action':df_info_group.iloc[0].at['predict_action'],
                'predict_input':df_info_group.iloc[0].at['predict_input']
            },index=[1]
        )
        df_group = pd.concat([df_group,df_line],axis=0,ignore_index=True)
    return df_group,tgt_app,function








def find_tgt_index(df_info, tgt_app, tgt_function, type,key,df_tgt):
    tgt_index = -2
    # df_tgt = df_info.query(
    #     "tgt_app ==@tgt_app and function == @tgt_function and key ==@key and type == @type and used == 'False' ")
    if len(df_tgt) != 0:
        tgt_indexs = set(df_tgt['tgt_index'])
        if len(tgt_indexs) == 1:
            tgt_index = tgt_indexs
            df_info[df_info['tgt_index'] == tgt_index and df_info['tgt_app'] == tgt_app and df_info['function'] == tgt_function and df_info['resource_id'] == key and df_info['type']==type] = 'True'
        else:
            tgt_index_list = list(tgt_indexs).sort()
            tgt_index = tgt_index_list[0]
            df_info[df_info['tgt_index'] == tgt_index and df_info['tgt_app'] == tgt_app and df_info['function'] == tgt_function and df_info[key] == key and df_info['type']==type] = 'True'
    return tgt_index




def save_call_graph_test_result(df_call_graph_test,save_csv_path,save_csv_name):
    if not os.path.exists(save_csv_path+save_csv_name):
        df_call_graph_test.to_csv(save_csv_path+save_csv_name)
    else:
        df_part_call_graph_test = pd.read_csv(save_csv_path+save_csv_name)
        df_part_call_graph_test = pd.concat([df_part_call_graph_test,df_call_graph_test],axis=0)
        df_part_call_graph_test.to_csv(save_csv_path+save_csv_name)

def save_call_graph_test_result_src(df_call_graph_test,save_csv_path,save_csv_name,src_app_name):
    df_call_graph_test['src_app'] = src_app_name
    if not os.path.exists(save_csv_path+save_csv_name):
        df_call_graph_test.to_csv(save_csv_path+save_csv_name)
    else:
        df_part_call_graph_test = pd.read_csv(save_csv_path+save_csv_name)
        df_part_call_graph_test = pd.concat([df_part_call_graph_test,df_call_graph_test],axis=0)
        df_part_call_graph_test.to_csv(save_csv_path+save_csv_name)


def postprocess_explore_result(save_csv_path,save_csv_name,output_test_name,policy_name,pre_test_name, tool_result_name):


    output_dirs_path = "/path/" + pre_test_name + output_test_name + policy_name
    choose_output_dir, choose_output_dirs, has_output,have_file = choose_droidbot_output(output_dirs_path)
    print("choose_output_dir", choose_output_dir)
    tgt_event_path = save_csv_path + tool_result_name
    df_information = pd.read_csv(tgt_event_path)

    # revise column names for fit for fruiter
    # fit for fruiter
    if 'tgt_index_manual' in df_information.columns.tolist():
        df_information = df_information.rename(columns={'tgt_index_manual': 'tgt_index'})
    if 'appflow_new_id' in df_information.columns.tolist():
        df_information = df_information.rename(columns={'appflow_new_id':'tgt_add_id'})
    if 'appflow_new_appium_xpath' in df_information.columns.tolist():
        df_information = df_information.rename(columns={'appflow_new_appium_xpath':'tgt_add_xpath'})
    if 'appflow_content' in df_information.columns.tolist():
        df_information = df_information.rename(columns={'appflow_content':'tgt_content'})
    if 'appflow_text' in df_information.columns.tolist():
        df_information = df_information.rename(columns={'appflow_text':'tgt_text'})


    if has_output == True:
        print("======if has_output == True:========")
        state_file_path = choose_output_dir + "states/"
        revise_screen_name(state_file_path)
        events_path = choose_output_dir + 'events/'

        df_call_graph_test, tgt_app, tgt_function = generate_test_case_sequence(events_path, df_information)
        save_call_graph_test_result(df_call_graph_test, save_csv_path, save_csv_name)
    else:
        # for has_output= False
        df_call_graph_test, tgt_app, tgt_function = generate_test_case_sequence_false(output_dirs_path, policy_name,
                                                                                      df_information, output_test_name)
        save_call_graph_test_result(df_call_graph_test,, save_csv_path, save_csv_name)







