
import json
import pandas as pd
from filter.common_function import read_csv, dict2json
import os
import numpy as np





def extract_event(df_group,df_information):
    """
    get event information for each tgt_app
    :param df_completion: is a tgt_app group result for groundtruth_full_pair_add_result_test_case_search_delete_false_1007
    :param df_information: is a information csv for groundtruth_full_pair_add_result_test_case_09161849_all
    :return:
    """

    # add xpath for fit for fruiter
    df_call_graph_group = pd.DataFrame(columns=['tgt_app','function','predict_tgt_index','droidbot_type','resource_id','content_desc','input','direction','text','condition','xpath'],index=[])
    script_file_name = df_group.iloc[0].at['tgt_app']+"_"+df_group.iloc[0].at['function']
    for idx in range(len(df_group)):
        tgt_app = df_group.iloc[idx].at['tgt_app']
        function = df_group.iloc[idx].at['function']
        predict_tgt_index = df_group.iloc[idx].at['predict_tgt_index']
        df_lines = df_information.query("tgt_app==@tgt_app and function ==@function and tgt_index==@predict_tgt_index")
        resource_id = df_lines.iloc[0].at['tgt_add_id']
        event_type = df_lines.iloc[0].at['type']
        content_desc = df_lines.iloc[0].at['tgt_content']
        text = df_lines.iloc[0].at['tgt_text']
        xpath = df_lines.iloc[0].at['tgt_add_xpath']
        if text == text:
            text = text.replace(" ","\b")
        if event_type == "SYS_EVENT":
            continue
        if event_type == 'EMPTY_EVENT':
            continue
        droidbot_type = np.nan
        input = np.nan
        direction = np.nan
        condition = np.nan
        action = np.nan
        if event_type == "oracle":
            droidbot_type = 'oracle'
        if 'action' in df_lines and 'predict_action' not in df_lines:
            action = df_lines.iloc[0].at['action']
        if 'predict_action' in df_lines:
            action = df_lines.iloc[0].at['predict_action']
        if action =='click':
            droidbot_type = 'touch'
        if action == action and 'send' in action:
            droidbot_type = ''
            # add sendKeys fit for fruiter
            if 'enter' in action or 'Keys' in action:
                droidbot_type = 'set_text_and_enter'
            else:
                droidbot_type = 'set_text'
            if 'input' in df_lines:
                input = df_lines.iloc[0].at['input']
            elif 'predict_input' in df_lines:
                input = df_lines.iloc[0].at['predict_input']
        if action == 'swipe_right':
            droidbot_type = 'scroll'
            direction = 'RIGHT'
        if action == 'long_press':
            droidbot_type = 'long_touch'
        if action == 'wait_until_text_invisible':
            condition = 'disappear'
        df_information_line = pd.DataFrame(
            {
                'tgt_app':tgt_app,
                'function':function,
                'predict_tgt_index':predict_tgt_index,
                'droidbot_type':droidbot_type,
                'resource_id':resource_id,
                'content_desc':content_desc,
                'input':input,
                'direction':direction,
                'text':text,
                'condition':condition,
                'xpath':xpath,
            },index=[1]
        )
        # df_call_graph_group = df_call_graph_group.append(df_information_line,ignore_index=True)
        df_call_graph_group = pd.concat([df_call_graph_group,df_information_line],axis=0)
    df_call_graph_group = df_call_graph_group.sort_values("predict_tgt_index")
    return df_call_graph_group,script_file_name


def extract_event_src(df_group,df_information):
    """
    get event information for each tgt_app
    :param df_completion: is a tgt_app group result for groundtruth_full_pair_add_result_test_case_search_delete_false_1007
    :param df_information: is a information csv for groundtruth_full_pair_add_result_test_case_09161849_all
    :return:
    """
    df_call_graph_group = pd.DataFrame(columns=['src_app','tgt_app','function','predict_tgt_index','droidbot_type','resource_id','content_desc','input'],index=[])
    script_file_name = df_group.iloc[0].at['src_app']+"_"+df_group.iloc[0].at['tgt_app']+"_"+df_group.iloc[0].at['function']
    for idx in range(len(df_group)):
        src_app = df_group.iloc[idx].at['src_app']
        tgt_app = df_group.iloc[idx].at['tgt_app']
        function = df_group.iloc[idx].at['function']
        predict_tgt_index = df_group.iloc[idx].at['predict_tgt_index']
        df_lines = df_information.query("src_app==@src_app and tgt_app==@tgt_app and function ==@function and tgt_index==@predict_tgt_index")
        resource_id = df_lines.iloc[0].at['tgt_add_id']
        event_type = df_lines.iloc[0].at['type']
        content_desc = df_lines.iloc[0].at['tgt_content']
        text = df_lines.iloc[0].at['tgt_text']
        if text == text:
            text = text.replace(" ","\b")
        if event_type == "SYS_EVENT":
            continue
        if event_type == 'EMPTY_EVENT':
            continue
        droidbot_type = np.nan
        input = np.nan
        direction = np.nan
        condition = np.nan
        action = np.nan
        if event_type == "oracle":
            droidbot_type = 'oracle'
        if 'action' in df_lines and 'predict_action' not in df_lines:
            action = df_lines.iloc[0].at['action']
        if 'predict_action' in df_lines:
            action = df_lines.iloc[0].at['predict_action']
        if action =='click':
            droidbot_type = 'touch'
        if action == action and 'send' in action:
            droidbot_type = ''
            if 'enter' in action:
                droidbot_type = 'set_text_and_enter'
            else:
                droidbot_type = 'set_text'
            if 'input' in df_lines:
                input = df_lines.iloc[0].at['input']
            elif 'predict_input' in df_lines:
                input = df_lines.iloc[0].at['predict_input']
        if action == 'swipe_right':
            droidbot_type = 'scroll'
            direction = 'RIGHT'
        if action == 'long_press':
            droidbot_type = 'long_touch'
        if action == 'wait_until_text_invisible':
            condition = 'disappear'
        df_information_line = pd.DataFrame(
            {
                'src_app':src_app,
                'tgt_app':tgt_app,
                'function':function,
                'predict_tgt_index':predict_tgt_index,
                'droidbot_type':droidbot_type,
                'resource_id':resource_id,
                'content_desc':content_desc,
                'input':input,
                'direction':direction,
                'text':text,
                'condition':condition

            },index=[1]
        )
        # df_call_graph_group = df_call_graph_group.append(df_information_line,ignore_index=True)
        df_call_graph_group = pd.concat([df_call_graph_group,df_information_line],axis=0)
    df_call_graph_group = df_call_graph_group.sort_values("predict_tgt_index")
    return df_call_graph_group,script_file_name


def get_call_graph_app(df_completion,style):
    """
    given the tgt_app_result for part 1 find the tgt_group for the result is not equal to the tgt groundtruth
    """
    if style == 'ablation_study':
        groups = df_completion.groupby(['tgt_app','function','src_app'])
        call_graph_groups = []
        for group in groups:
            df_group = group[1]
            completion_equation_groundtruth = df_group.iloc[0].at['whole_test_judge_result']
            if completion_equation_groundtruth == 'TRUE':
                continue
            call_graph_groups.append(df_group)
        return call_graph_groups
    else:
        groups = df_completion.groupby(['tgt_app','function'])
        call_graph_groups = []
        for group in groups:
            df_group = group[1]
            completion_equation_groundtruth = df_group.iloc[0].at['whole_test_judge_result']
            if completion_equation_groundtruth == 'TRUE':
                continue
            call_graph_groups.append(df_group)
        return call_graph_groups


def generate_droidbot_script(df_call_graph_group,script_file_name,script_path):
    # df_call_graph_group.sort_values("predict_tgt_index")
    group_dir = script_path + script_file_name +"/"
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
    script_dir = group_dir + 'script' + "/"
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)
    # output_dir = group_dir + 'output' + "/"
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # create views
    script = dict()
    view_key = "views"
    view_value = dict()
    for idx in range(len(df_call_graph_group)):
        tgt_idx = df_call_graph_group.iloc[idx].at['predict_tgt_index']
        key = script_file_name+"_"+str(tgt_idx)+"_"+"view"
        view_element = dict()
        sub_key1 = "resource_id"
        sub_value1 = df_call_graph_group.iloc[idx].at['resource_id']
        sub_key2 = "content_description"
        sub_value2 = df_call_graph_group.iloc[idx].at['content_desc']
        sub_key3 = 'text'
        sub_value3 = df_call_graph_group.iloc[idx].at['text']
        # add for fruiter dataset
        sub_key4 = 'xpath'
        sub_value4 = df_call_graph_group.iloc[idx].at['xpath']
        condition = df_call_graph_group.iloc[idx].at['condition']
        if sub_value1==sub_value1:
            view_element[sub_key1] = sub_value1
        elif sub_value2==sub_value2:
            view_element[sub_key2] = sub_value2
        elif sub_value3==sub_value3:
            view_element[sub_key3] = sub_value3
        elif sub_value4 == sub_value4:
            view_element[sub_key4] = sub_value4
        if condition == condition:
            view_element['condition'] = condition
        view_value[key] = view_element
    script[view_key] = view_value

    # creat states
    state_key = "states"
    state_value = dict()
    for idx in range(len(df_call_graph_group)):
        tgt_idx = df_call_graph_group.iloc[idx].at['predict_tgt_index']
        key = script_file_name+"_"+str(tgt_idx)+"_"+"state"
        state_element = dict()
        sub_key = "views"
        sub_value = [script_file_name+"_"+str(tgt_idx)+"_"+"view"]
        state_element[sub_key] = sub_value
        state_value[key] = state_element
    script[state_key] = state_value


    # create operations
    operation_key = "operations"
    operation_value = dict()
    for idx in range(len(df_call_graph_group)):
        tgt_idx = df_call_graph_group.iloc[idx].at['predict_tgt_index']
        key = script_file_name+"_"+str(tgt_idx)+"_"+"operation"
        operation_element = dict()
        sub_key1 = "event_type"
        sub_value1 = df_call_graph_group.iloc[idx].at['droidbot_type']
        operation_element[sub_key1]=sub_value1
        sub_key2 = "target_view"
        sub_value2 = script_file_name+"_"+str(tgt_idx)+"_"+"view"
        operation_element[sub_key2]=sub_value2

        if sub_value1 == "set_text" or sub_value1 == 'set_text_and_enter':
            sub_key3 = "text"
            input_text = df_call_graph_group.iloc[idx].at['input']
            # todo: for a3 and a4 need to revise the input
            if input_text!=input_text:
                continue
            sub_value3 = input_text.replace(" ","\b")
            operation_element[sub_key3]=sub_value3
        if sub_value1 == 'scroll':
            sub_key3 = 'direction'
            sub_value3= df_call_graph_group.iloc[idx].at['direction']
            operation_element[sub_key3]=sub_value3
        if sub_value1 == 'oracle':
            sub_key3 = 'condition'
            sub_value3 = df_call_graph_group.iloc[idx].at['condition']
            if sub_value3 == sub_value3:
                operation_element[sub_key3] = sub_value3
        operation_value[key] = [operation_element]
    script[operation_key] = operation_value

    # create main
    main_key = "main"
    main_value = dict()
    for idx in range(len(df_call_graph_group)):
        tgt_idx = df_call_graph_group.iloc[idx].at['predict_tgt_index']
        key = script_file_name + "_" + str(tgt_idx) + "_" + "state"
        value = [script_file_name + "_" + str(tgt_idx) + "_" + "operation"]
        main_value[key] = value
    script[main_key] = main_value

    # # write json file
    # json_str = json.dumps(script,indent=4)
    # json_path = script_dir + "script.json"
    # with open(json_path,'w') as json_file:
    #     json_file.write(json_str)
    # return script_dir

    # write json file
    json_path = script_dir + "script.json"
    dict2json(script, json_path)
    return script_dir


def generate_droidbot_stop_script(df_call_graph_group,script_dir,script_file_name):
    # generate the stop script json file
    stop_idx = len(df_call_graph_group)-1
    resource_id = df_call_graph_group.iloc[stop_idx].at['resource_id']
    content_desc =df_call_graph_group.iloc[stop_idx].at['content_desc']
    text = df_call_graph_group.iloc[stop_idx].at['text']
    condition = df_call_graph_group.iloc[stop_idx].at['condition']
    predict_tgt_index = df_call_graph_group.iloc[stop_idx].at['predict_tgt_index']
    sub_key1 = "resource_id"
    sub_value1 = resource_id
    sub_key2 = "content_description"
    sub_value2 = content_desc
    sub_key3 = "text"
    sub_value3 = text
    sub_key4 = "condition"
    sub_value4 = condition
    value = dict()
    if sub_value1==sub_value1:
        value[sub_key1] = sub_value1
    if sub_value2==sub_value2:
        value[sub_key2] = sub_value2
    if sub_value3 == sub_value3:
        value[sub_key3] = sub_value3
    if sub_value4 == sub_value4:
        value[sub_key4] = sub_value4
    key = script_file_name+ "_"+ str(predict_tgt_index)+"_"+"view"
    stop_script = dict()
    stop_script[key] = value

    # json_str = json.dumps(stop_script,indent=4)
    # json_path = script_dir + "stop_script.json"
    # with open(json_path,'w') as json_file:
    #     json_file.write(json_str)
    json_path = script_dir + "stop_script.json"
    dict2json(stop_script,json_path)









def generate_script(tgt_app_name, function_name, completion_csv_path, completion_csv_name, information_csv_path, information_csv_name,script_path,style):
    df_completion = read_csv(completion_csv_path,completion_csv_name)
    df_information = read_csv(information_csv_path,information_csv_name)

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

    if tgt_app_name != '' and function_name != '':
        # tgt_app_name is not none and function is not none
        df_information = df_information.query("tgt_app == @tgt_app_name and function == @function_name")
        df_completion = df_completion.query("tgt_app == @tgt_app_name and function == @function_name")


    # change the string to float
    df_information['tgt_index'] = df_information['tgt_index'].astype(float)
    call_graph_groups = get_call_graph_app(df_completion, style)
    idx = 0
    for df_group in call_graph_groups:
        if 'a13' in df_group['tgt_app'].values.tolist() and 'b11' in df_group['function'].values.tolist():
            print("here")
        df_call_graph_group = ''
        if style == 'ablation_study':
            df_call_graph_group, script_file_name = extract_event_src(df_group, df_information)
        else:
            df_call_graph_group, script_file_name = extract_event(df_group, df_information)
        script_dir = generate_droidbot_script(df_call_graph_group, script_file_name, script_path)
        generate_droidbot_stop_script(df_call_graph_group, script_dir, script_file_name)
        idx += 1



