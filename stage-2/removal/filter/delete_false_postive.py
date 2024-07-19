
# delete the false positives
# the output is the input of add_execution_modification


from test_execution import ContactsAndroidTests

def delete_false_event(df_group,generation):
    # given the df_group
    # goal: whether the df_group is the sequence
    # if the sequence -> output: df_group
    # if not the sequence -> 1) if the same src-> 2 tgt; ->2) if not the same src-> 2 tgt
    df_src_app = df_group.groupby(['src_app'])
    consider_src_app = set()
    for group in df_src_app:
        src_group = group[1].sort_values('src_index')
        src_app_name = src_group.iloc[0].at['src_app']
        for idx in range(len(src_group)-1):
            ori_predict_label = src_group.iloc[idx].at['ori_predict_label']
            if ori_predict_label == 0:
                continue
            event_type = src_group.iloc[idx].at['type']
            # for empty event in craftdroid
            if event_type == 'EMPTY_EVENT':
                continue
            tgt_index = float(src_group.iloc[idx].at['tgt_index'])
            tgt_index_after = float(src_group.iloc[idx+1].at['tgt_index'])
            if tgt_index >= tgt_index_after:
                consider_src_app.add(src_app_name)
                break

        src_index_list = src_group['src_index']
        if len(set(src_index_list)) < len(src_index_list):
            consider_src_app.add(src_app_name)
            continue
        tgt_index_list = src_group['tgt_index']
        if len(set(tgt_index_list)) < len(tgt_index_list):
            consider_src_app.add(src_app_name)
            continue
    # # for test
    # consider_src_app = {'a33'}
    if len(consider_src_app)==0:
        return df_group
    else:
        # get the dumplicate src_app
        for src_app in consider_src_app:
            if src_app == 'a54':
                print("here")
            one_src_multiple_tgt = set()  # same src -> multiple tgt
            one_tgt_multiple_src = set()
            group = df_group.query("src_app == @src_app and ori_predict_label == 1").sort_values('src_index')
            for idx in range(len(group)):
                src_index = group.iloc[idx].at['src_index']
                df_src = df_group.query("src_app == @src_app and src_index == @src_index and ori_predict_label == 1")
                if len(df_src) > 1:
                    one_src_multiple_tgt.add(src_index)
                tgt_index = group.iloc[idx].at['tgt_index']
                df_tgt = df_group.query("src_app == @src_app and tgt_index == @tgt_index and ori_predict_label == 1")
                if len(df_tgt) > 1:
                    one_tgt_multiple_src.add(tgt_index)
            if len(one_src_multiple_tgt) == 0 and len(one_tgt_multiple_src) == 0:
                # 2) sequence different
                df_group = modify_sequence(src_app,df_group)
            else:
                # 1) same src different tgt
                # identify static or dynamic
                # if len(one_tgt_multiple_src)!= 0 :
                # a. static anlaysis
                # # for test
                # src_app = 'a24'
                if len(one_src_multiple_tgt)!=0 and len(one_tgt_multiple_src)!=0:
                    df_group = static_analysis_sequence(src_app, df_group)
                elif len(one_src_multiple_tgt)!=0:
                    # b. dynamic analysis
                    df_group = dynamic_analysis_sequence_src(src_app, df_group, one_src_multiple_tgt,generation)
                elif len(one_tgt_multiple_src)!=0:
                    # b. dynamic analysis
                    df_group = dynamic_analysis_sequence_tgt(src_app, df_group, one_tgt_multiple_src,generation)
        return df_group

def modify_sequence(src_app,df_group):
    # if one src has one tgt and one tgt has one src
    # static analysis the all the subsequence and revise them

    # get the intersection of tgt_index (above twice for a tgt_index)
    intersection = list()
    tgt_index_num_dict = dict() # key-- tgt_index; value -- number
    for idx in range(len(df_group)):
        if df_group.iloc[idx].at['type'] == 'EMPTY_EVENT':
            row_num = df_group.iloc[idx].at['index']
            df_group[row_num,'rev_predict_label'] = 0
            continue
        tgt_index = df_group.iloc[idx].at['tgt_index']
        if tgt_index in tgt_index_num_dict:
            tgt_index_num_dict[tgt_index] += 1
        else:
            tgt_index_num_dict[tgt_index] = 1
    for tgt_index in tgt_index_num_dict:
        if tgt_index_num_dict[tgt_index] >= 2:
            intersection.append(tgt_index)

    partial_order_dict = dict() 
    partial_order = set()
    for i in range(len(intersection)-1):
        for j in range(1,len(intersection)):
            start = intersection[i]
            end = intersection[j] # (0,2)
            get_partial_order(start,end,df_group,partial_order_dict)
            get_partial_order(end,start,df_group,partial_order_dict)
            key1 = str(start) + "-" + str(end)
            key2 = str(end) + "-" + str(start)
            if partial_order_dict[key1] > partial_order_dict[key2]:
                partial_order.add(key1)
            if partial_order_dict[key1] < partial_order_dict[key2]:
                partial_order.add(key2)

    df_src_app = df_group.query("src_app==@src_app").sort_values("src_index")
    for i in range(len(df_src_app)-1):
        for j in range(i+1,len(df_src_app)):
            current_tgt_index = df_src_app.iloc[i].at['tgt_index']
            after_tgt_index = df_src_app.iloc[j].at['tgt_index']
            pre_order= str(current_tgt_index)+"-"+str(after_tgt_index)
            post_order = str(after_tgt_index)+"-"+str(current_tgt_index)
            if pre_order in partial_order:
                continue
            if post_order in partial_order:
 
                current_row_index = df_src_app[df_src_app['tgt_index']==current_tgt_index].index.tolist()[0]
                after_row_index = df_src_app[df_src_app['tgt_index']==after_tgt_index].index.tolist()[0]
                df_group.loc[current_row_index,'tgt_index'] = after_tgt_index
                df_group.loc[after_row_index,'tgt_index'] = current_tgt_index
                df_src_app.loc[current_row_index,'tgt_index'] = after_tgt_index
                df_src_app.loc[after_row_index,'tgt_index'] = current_tgt_index
    return df_group








def get_partial_order(start,end,df_group,partial_order_dict):
    groups = df_group.groupby(['src_app'])
    num = 0 
    for group in groups:
        df_src_app = group[1]
        if start in df_src_app['tgt_index'].values and end in df_src_app['tgt_index'].values:
           
            start_index = df_src_app[(df_src_app['tgt_index'] == start) & (df_src_app['ori_predict_label'] == 1)].index.tolist()[0]
            end_index = df_src_app[(df_src_app['tgt_index'] == end) & (df_src_app['ori_predict_label'] == 1)].index.tolist()[0]
            if start_index < end_index:
                num += 1
    key = str(start)+"-"+str(end)
    partial_order_dict[key] = num


def static_analysis_sequence(src_app,df_group):
    maxEvent = 10

    df_src_app = df_group.query("src_app==@src_app and ori_predict_label == 1").sort_values("src_index")

    line = [[False for i in range(maxEvent)] for j in range(maxEvent)] 
    left_set = set() 
    right_set = set()
    match_relation = {}

    for idx in range(len(df_src_app)):
        left = df_src_app.iloc[idx].at['src_index'].astype(int) #numpy.float64->int
        right = df_src_app.iloc[idx].at['tgt_index'].astype(int)
        line[left][right] = True

    tgt_index_mapping = [-1 for i in range(maxEvent)]

    for idx in range(len(df_src_app)):
        src_index = df_src_app.iloc[idx].at['src_index']
        tgt_index = df_src_app.iloc[idx].at['tgt_index']
        left_set.add(src_index.astype(int))
        right_set.add(tgt_index.astype(int))

    all = 0

    for left in left_set:
        used = [False for i in range(maxEvent)]
        if find_match_src_tgt(used, left,right_set,match_relation,line):
            all += 1

    max_match_bool_list = []
    for idx in range(len(df_src_app)):
        flag = False
        right = df_src_app.iloc[idx].at['tgt_index'].astype(int)
        if right in match_relation:
            left = match_relation[right]
            if df_src_app.iloc[idx].at['src_index'].astype(int) == left:
                flag = True
        max_match_bool_list.append(flag)
    # max_match_df = df_src_app[max_match_bool_list]
    # revise df_group
    for idx in range(len(df_src_app)):
        tgt_index = df_src_app.iloc[idx].at['tgt_index']
        src_index = df_src_app.iloc[idx].at['src_index']
        row_index = df_src_app[(df_src_app['tgt_index']==tgt_index)&(df_src_app['src_index']==src_index)].index.tolist()[0]
        df_group.loc[row_index,'rev_predict_label'] = int(max_match_bool_list[idx])
    return df_group

def find_match_src_tgt(used, left,right_set,match_relation,line):
    for right in right_set:
        if line[left][right] == True and used[right] == False:
            used[right] = 1
            if right not in match_relation or find_match_src_tgt(used,match_relation[right],right_set,match_relation,line):
                match_relation[right] = left
                return True
    return False




def dynamic_analysis_sequence_src(src_app,df_group,one_src_multiple_tgt,generation):

    one_src_multiple_tgt_list = list(one_src_multiple_tgt)
    one_src_multiple_tgt_list.sort()
    idx = 0
    src_group = df_group.query("src_app==@src_app and ori_predict_label == 1").sort_values('src_index')
    reset_label = 0 # need to revise
    android_test = ContactsAndroidTests()
    # todo: one_tgt_multiple_src_list need to add similar to one_src_multiple_tgt_list
    while len(one_src_multiple_tgt_list)-1 >= idx:
        src_index = one_src_multiple_tgt_list[idx]
        df_lines =src_group.query("src_index == @src_index")
        right_tgt_index = []
        wrong_tgt_index = []
        for index in range(len(df_lines)):
            tgt_index = df_lines.iloc[index].at['tgt_index']
            stepping_tgt_index = get_stepping_index(src_group,src_index)
            stepping_tgt_index.append(tgt_index)
            end_label = 1 # need to revise
            test_case, tgt_app, action_label = generation.test_case_for_execution(src_group, stepping_tgt_index)
            execution_label,_ = generation.execute_test_case(test_case, tgt_app, 0,reset_label, end_label,android_test)
            # todo: add code for multiple action / multiple condition
            if execution_label == 1:
                right_tgt_index.append(tgt_index)
            else:
                wrong_tgt_index.append(tgt_index)


        if len(right_tgt_index)!=0 and len(wrong_tgt_index)!=0: # find correct tgt_index
            for tgt_index in wrong_tgt_index:
                row_index = df_group[(df_group['tgt_index']==tgt_index)&(df_group['src_app']==src_app)&(df_group['ori_predict_label']==1)].index.tolist()
                df_group.loc[row_index[0],'rev_predict_label'] = 0
        idx += 1
    return df_group

def dynamic_analysis_sequence_tgt(src_app,df_group,one_tgt_multiple_src,generation):

    if src_app == 'a54':
        print("here")
    one_tgt_multiple_src_list = list(one_tgt_multiple_src)
    one_tgt_multiple_src_list.sort()
    idx = 0
    src_group = df_group.query("src_app==@src_app and ori_predict_label == 1").sort_values('src_index')
    reset_label = 0 # need to revise
    android_test = ContactsAndroidTests()
    while len(one_tgt_multiple_src_list)-1 >= idx:
        tgt_index = one_tgt_multiple_src_list[idx]
        df_lines =src_group.query("tgt_index == @tgt_index")
        right_src_index = []
        wrong_src_index = []
        for index in range(len(df_lines)):
            src_index = df_lines.iloc[index].at['src_index']
            row_index = df_lines.iloc[index].at['index']
            stepping_src_index = get_stepping_index_tgt(src_group,src_index,tgt_index)
            stepping_src_index.append(src_index)
            after_src_index = get_after_index(src_group,tgt_index,row_index)
            if after_src_index is not None:
                stepping_src_index.append(after_src_index)
            end_label = 1 # need to revise
            test_case, tgt_app, action_label = generation.test_case_for_execution_tgt(src_group, stepping_src_index)
            execution_label,_ = generation.execute_test_case(test_case, tgt_app, 0,reset_label, end_label,android_test)
            if execution_label == 1:
                right_src_index.append(src_index)
            else:
                wrong_src_index.append(src_index)

        if len(wrong_src_index)!=0: # find correct tgt_index
            for src_index in wrong_src_index:
                row_index = df_group[(df_group['src_index']==src_index)&(df_group['src_app']==src_app)&(df_group['ori_predict_label']==1)].index.tolist()
                df_group.loc[row_index[0],'rev_predict_label'] = 0
        elif len(right_src_index) !=0 and len(wrong_src_index)==0:#  
            for i in range(len(right_src_index)-1):
                src_index = right_src_index[i]
                row_index = df_group[(df_group['src_index']==src_index)&(df_group['src_app']==src_app)&(df_group['ori_predict_label']==1)].index.tolist()
                df_group.loc[row_index[0],'rev_predict_label'] = 0
        idx += 1
    return df_group


def get_stepping_index(src_group,target_src_index):
    # this is for one src multiple tgt
    # outpyt tgt_index (src_index is not unique but tgt_index is unique)
    stepping_index = []
    for idx in range(len(src_group)):
        src_index = src_group.iloc[idx].at['src_index']
        tgt_index = src_group.iloc[idx].at['tgt_index']
        if src_index != target_src_index:
            stepping_index.append(tgt_index)
        else:
            return stepping_index

def get_stepping_index_tgt(src_group,target_src_index,target_tgt_index):
    # this is for one target multiple src
    # delete the target index in the stepping index
    # output src_index (src_index is unique but tgt_index is not unique)
    stepping_index = []
    for idx in range(len(src_group)):
        src_index = src_group.iloc[idx].at['src_index']
        tgt_index = src_group.iloc[idx].at['tgt_index']
        if tgt_index != tgt_index: # tgt_index:nan
            continue
        if tgt_index == target_tgt_index:
            if src_index == target_src_index:
                return stepping_index
            else:
                continue
        else:
            stepping_index.append(src_index)



def get_after_index(src_group,target_tgt_index,row_index):
    for idx in range(len(src_group)):
        if src_group.iloc[idx].at['index'] > row_index and src_group.iloc[idx].at['tgt_index'] !=target_tgt_index:
            return src_group.iloc[idx].at['src_index']



def judge_false_positive(df_group,df_revised_group):
    df_fp = df_group.query("ori_predict_label==1 and label==0")
    if len(df_fp) >0:
        df_revised_fp = df_revised_group.query("rev_predict_label==1 and label ==0")
        if len(df_revised_fp) ==0:
            return 1,0

        else:
            revised_tag = True 
            for idx in range(len(df_revised_fp)):
                src_app = df_revised_fp.iloc[idx].at['src_app']
                df_src_app = df_revised_group.query("src_app == @src_app and rev_predict_label==1").sort_values("src_index")

                predict_tgt_index = df_src_app['tgt_index'].values.tolist()
                if predict_tgt_index == sorted(predict_tgt_index):
                    continue
                else:
                    revised_tag = False


            if revised_tag == False:
                return 1,1
            else:
                return 1,0
    else:
        return 0,0








