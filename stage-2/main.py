


import pandas as pd
import numpy as np
# bisect is for insert an item in an ordered sequence
import bisect
import time
import os
from removal.filter.add_execution_modification import Generation
from removal.filter.false_repair_and_completion import revise, add_true_generate_index, completion, completion_for_one_source, generate_explore_script, postprocess_explore
from incorporation.start import explore


if __name__ == "__main__":


    tgt_app_name = 'tgt_app'
    function = 'function'
    apk_path = 'apk_path'
    base_path = 'base_sequence_path'
    csv_name = 'base_sequence.csv'
    csv_save_name = 'explore'
    enhance_test_path = 'enhance_test_path'
    filter_path = enhance_test_path +'filter/'
    script_path = enhance_test_path +'connection/'
    generation = Generation()
    df_revised_group = revise(base_path, csv_name, tgt_app_name, function, generation)
    completion(df_revised_group,filter_path,csv_save_name,generation, 0.5)
    generate_explore_script(filter_path,base_path,csv_name,script_path,csv_save_name)
    explore(script_path,apk_path,enhance_test_path)

 





