
# input original predict_result
# output the tgt_index for each event (for fp/ combine/ explore)
# goal: the tgt_index sequence can execute and each tgt_index represent one event

import string
import random

import pandas as pd

import networkx as nx

def initial_group(df_group):
    # input four test_case
    # output the partial_order
    # df_src_app = df_group.groupby(['src_app'])
    # for group in df_src_app:
    #     src_group = group[1].sort_values('src_index')
    #     src_app_name = src_group.iloc[0].at['src_app']
    tag = 0
    have_used_letters = set()
    for idx in range(len(df_group)):
        # ignore the empty event
        if df_group.iloc[idx].at['type'] == 'EMPTY_EVENT':
            continue
        # have label a letter for the tgt_index
        if df_group.iloc[idx].at['tgt_index'] == df_group.iloc[idx].at['tgt_index']:
            continue
        else:
            # label a letter for the tgt_index
            letter = string.ascii_lowercase[tag]
            tag += 1
            row_index = df_group.iloc[idx].at['index']
            df_group.loc[row_index,'tgt_index'] = letter
            have_used_letters.add(letter)
            event_dict = dict()
            if df_group.iloc[idx].at['tgt_add_id'] ==df_group.iloc[idx].at['tgt_add_id']:
                event_dict['tgt_add_id'] = df_group.iloc[idx].at['tgt_add_id']
            else:
                event_dict['tgt_add_id'] = ''
            if df_group.iloc[idx].at['tgt_add_xpath'] == df_group.iloc[idx].at['tgt_add_xpath']:
                event_dict['tgt_add_xpath'] = df_group.iloc[idx].at['tgt_add_xpath']
            else:
                event_dict['tgt_add_xpath'] = ''
            if df_group.iloc[idx].at['tgt_text'] == df_group.iloc[idx].at['tgt_text']:
                event_dict['tgt_text'] = df_group.iloc[idx].at['tgt_text'].split(".com")[0] # for a13 .com/?kao=-1&kak=-1 and /html same
            else:
                event_dict['tgt_text'] = ''
            if df_group.iloc[idx].at['tgt_content'] == df_group.iloc[idx].at['tgt_content']:
                event_dict['tgt_content'] = df_group.iloc[idx].at['tgt_content']
            else:
                event_dict['tgt_content'] = ''
            # todo: need to revise predict_action (send / wait)
            if df_group.iloc[idx].at['predict_action'] == df_group.iloc[idx].at['predict_action']:
                event_dict['predict_action'] = df_group.iloc[idx].at['predict_action']
            else:
                event_dict['predict_action'] = ''
            if df_group.iloc[idx].at['predict_input'] == df_group.iloc[idx].at['predict_input']:
                event_dict['predict_input'] = df_group.iloc[idx].at['predict_input']
            else:
                event_dict['predict_input'] = ''
            if df_group.iloc[idx].at['activity'] == df_group.iloc[idx].at['activity']:
                event_dict['activity'] = df_group.iloc[idx].at['activity']
            else:
                event_dict['activity'] = ''
            if df_group.iloc[idx].at['package'] == df_group.iloc[idx].at['package']:
                event_dict['package'] = df_group.iloc[idx].at['package']
            else:
                event_dict['package'] = ''

            set_index_for_group(df_group, letter, event_dict)

    # # for each group, should not contain same letter
    # df_src_app = df_group.groupby(['src_app'])
    # for group in df_src_app:
    #     group_used_letters = set()
    #     src_group = group[1].sort_values('src_index')
    #     for i in range(len(src_group) - 1):
    #         if src_group.iloc[i].at['tgt_index'] in group_used_letters:
    #             letter = string.ascii_lowercase[tag]
    #             tag += 1
    #             row_index = src_group.iloc[i].at['index']
    #             df_group.loc[row_index, 'tgt_index'] = letter
    #             group_used_letters.add(letter)
    #         else:
    #             group_used_letters.add(src_group.iloc[i].at['tgt_index'])
    return df_group


def set_index_for_group(df_group,letter,event_dict):
    for idx in range(len(df_group)):
        if df_group.iloc[idx].at['tgt_index'] == df_group.iloc[idx].at['tgt_index']:
            continue
        test_event = dict()
        if df_group.iloc[idx].at['tgt_add_id'] == df_group.iloc[idx].at['tgt_add_id']:
            test_event['tgt_add_id'] = df_group.iloc[idx].at['tgt_add_id']
        else:
            test_event['tgt_add_id'] = ''
        if df_group.iloc[idx].at['tgt_add_xpath'] == df_group.iloc[idx].at['tgt_add_xpath']:
            test_event['tgt_add_xpath'] = df_group.iloc[idx].at['tgt_add_xpath']
        else:
            test_event['tgt_add_xpath'] = ''
        if df_group.iloc[idx].at['tgt_text'] == df_group.iloc[idx].at['tgt_text']:
            test_event['tgt_text'] = df_group.iloc[idx].at['tgt_text'].split(".com")[0]
        else:
            test_event['tgt_text'] = ''
        if df_group.iloc[idx].at['tgt_content'] == df_group.iloc[idx].at['tgt_content']:
            test_event['tgt_content']= df_group.iloc[idx].at['tgt_content']
        else:
            test_event['tgt_content'] = ''
        if df_group.iloc[idx].at['predict_action'] == df_group.iloc[idx].at['predict_action']:
            test_event['predict_action'] = df_group.iloc[idx].at['predict_action']
        else:
            test_event['predict_action'] = ''
        if df_group.iloc[idx].at['predict_input'] == df_group.iloc[idx].at['predict_input']:
            test_event['predict_input'] = df_group.iloc[idx].at['predict_input']
        else:
            test_event['predict_input'] = ''
        if df_group.iloc[idx].at['activity'] == df_group.iloc[idx].at['activity']:
            test_event['activity'] = df_group.iloc[idx].at['activity']
        else:
            test_event['activity'] = ''
        if df_group.iloc[idx].at['package'] == df_group.iloc[idx].at['package']:
            test_event['package'] = df_group.iloc[idx].at['package']
        else:
            test_event['package'] = ''
        tag = 1
        for key in test_event:
            if test_event[key] != event_dict[key]:
                tag = 0
                break
        if tag == 1:
            row_index = df_group.iloc[idx].at['index']
            df_group.loc[row_index,'tgt_index'] = letter
    return df_group

def get_partial_sequence(df_group,df_information):
    df_src_app = df_group.groupby(['src_app','function'])
    # mid_partial_dict to save all the a-b and b-a number
    mid_partial_dict = dict()
    for group in df_src_app:
        src_group = group[1].sort_values('src_index')
        src_app_name = src_group.iloc[0].at['src_app']
        for i in range(len(src_group)-1):
            for j in range(i+1, len(src_group)):
                # ignore empty_event
                if src_group.iloc[i].at['type']=='EMPTY_EVENT':
                    continue
                if src_group.iloc[j].at['type'] =='EMPTY_EVENT':
                    continue

                start = src_group.iloc[i].at['tgt_index']
                end = src_group.iloc[j].at['tgt_index']
                key = start + "-" + end
                if key in mid_partial_dict:
                    mid_partial_dict[key] += 1
                else:
                    mid_partial_dict[key] = 1
    # final partial_dict to save all the a-b number
    final_partial_sequence = set()
    for key in mid_partial_dict:
        start = key.split("-")[0]
        end = key.split("-")[1]
        opposite_key = end + "-" + start
        if opposite_key in mid_partial_dict:
            result = mid_partial_dict[key] - mid_partial_dict[opposite_key]
            if result > 0:
                final_partial_sequence.add(key)
            elif result < 0:
                final_partial_sequence.add(opposite_key)
        else:
            final_partial_sequence.add(key)
    # get graph
    G1 = nx.DiGraph()
    for partial_order in final_partial_sequence:
        start = partial_order.split("-")[0]
        end = partial_order.split("-")[1]
        G1.add_edge(start,end)
    # nx.draw(G1,with_labels=True)
    judge_graph =nx.is_directed_acyclic_graph(G1)
    print("graph is directed_acyclic_graph",judge_graph)

    # list_of_dangl = [node for node in G1.nodes if G1.in_degree(node)==0]
    sequences = []
    if judge_graph == True: #G1.in_degree(node)==0 exists
        while len(G1.nodes) > 0:

            list_of_0_in_degree = [node for node in G1.nodes if G1.in_degree(node) == 0]
            list_of_0_in_degree.sort() 
            sequences.append(list_of_0_in_degree)
            for node in list_of_0_in_degree:
                G1.remove_node(node)
    else: 
        while len(G1.nodes) > 0:
          
            pass

    # Number each label
    order = 0
    order_dict = dict()
    for seq in sequences:
        for label in seq:
            order_dict[label] = order
            order += 1

    # replace label by number
    for tgt_index_letter in order_dict:
        row_indexs = df_group[df_group['tgt_index'].isin([tgt_index_letter])].index.tolist()
        for row_index in row_indexs:
            df_information.loc[row_index,'tgt_index'] = order_dict[tgt_index_letter]
            df_group.loc[row_index,'tgt_index'] = order_dict[tgt_index_letter]

    # df_group['tgt_index'] = df_group.tgt_index.map(lambda x: order_dict[x])


    return df_group

def revise_tgt_index_according_correct_tgt_index(df_group,df_information):
    df_group['have_revised'] = False
    for idx in range(len(df_group)):
        ori_predict_label = df_group.iloc[idx].at['ori_predict_label']
        label = df_group.iloc[idx].at['label']
        correct_tgt_index = df_group.iloc[idx].at['correct_tgt_index']
        tgt_index = df_group.iloc[idx].at['tgt_index']
        if ori_predict_label == 1 and label == 1 and correct_tgt_index != tgt_index:
            need_revise_tgt_index_dict = need_revise_tgt_index(df_group, correct_tgt_index, tgt_index)
            for tgt_index in need_revise_tgt_index_dict:
                revised_tgt_index = need_revise_tgt_index_dict[tgt_index]
                row_indexs = df_group[df_group['tgt_index'].isin([tgt_index])].index.tolist()
                for row_index in row_indexs:
                    if df_group.loc[row_index,'have_revised'] == False:
                        df_information.loc[row_index,'tgt_index'] = revised_tgt_index
                        df_group.loc[row_index,'tgt_index'] = revised_tgt_index
                        df_group.loc[row_index,'have_revised'] = True





def need_revise_tgt_index(df_group,correct_tgt_index,tgt_index):
    need_revise_tgt_index_dict = dict()
    tgt_index_list = df_group['tgt_index'].tolist()
    tgt_index_set = set(tgt_index_list)
    if correct_tgt_index > tgt_index:
        for candidate_tgt_index in tgt_index_set:
            if candidate_tgt_index >= tgt_index:
                candidate_tgt_index_new = candidate_tgt_index + correct_tgt_index - tgt_index
                need_revise_tgt_index_dict[candidate_tgt_index] = candidate_tgt_index_new
    elif correct_tgt_index < tgt_index:
        for candidate_tgt_index in tgt_index_set:
            if candidate_tgt_index <= tgt_index:
                candidate_tgt_index_new = candidate_tgt_index + correct_tgt_index - tgt_index
                need_revise_tgt_index_dict[candidate_tgt_index] = candidate_tgt_index_new
    return need_revise_tgt_index_dict


def get_group(tgt_app_name,function_name, csv_file,csv_name):
    df = pd.read_csv(csv_file + csv_name)
    df_only_predict_true = df.query("ori_predict_label == 1") # only use the predict_true to generate test case
    groups = None
    if function_name == '':
        groups = df_only_predict_true.groupby(['tgt_app']) # given a target app
    else:
        groups = df_only_predict_true.groupby(['tgt_app','function']) # given a target app
    for group in groups:
        tgt_app = None
        function = None
        if function_name == '':
            tgt_app = group[0]
        else:
            tgt_app = group[0][0]
            function = group[0][1]
        df_group = group[1]
        if (function_name == '' and tgt_app == tgt_app_name) or (function_name != '' and function == function_name and tgt_app == tgt_app_name):
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










