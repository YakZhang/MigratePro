
from execution_modification import Generation
import pandas as pd
from sequence_generate import base_generation
import argparse
from exploration import input_manager
from exploration import input_policy
from exploration import env_manager
from exploration import DroidBot
from exploration.droidmaster import DroidMaster
from input import generate_script
from state_generation import explore_state

state_save_path = '/state_save_path/'

if __name__ == "__main__":

    tgt_app_name = 'tgt_app_name'
    function = 'function_name'
    apk_path = '/apk_path/'
    migrated_test_case = '/path/to/your.csv'
    execute_save_path = state_save_path+ 'execute/'
    unexecute_save_path = state_save_path + 'unexecute/'
    base_sequence_path = state_save_path + 'base/'
    generation = Generation()
    df = pd.read_csv(migrated_test_case)
    tgt_combine_true_test_case,tgt_combine_consider_test_case = generation.combine_test_case(df,0.5)
    generate_script(tgt_app_name,function,tgt_combine_true_test_case,df,execute_save_path,style='')
    generate_script(tgt_app_name,function,tgt_combine_consider_test_case,df,unexecute_save_path,style='')
    explore_state(execute_save_path,apk_path,state_save_path)
    explore_state(unexecute_save_path,apk_path,state_save_path)
    base_generation(migrated_test_case,base_sequence_path)


