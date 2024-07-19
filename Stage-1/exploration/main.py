
import argparse
from droidbot import input_manager
from droidbot import input_policy
from droidbot import env_manager
from droidbot import DroidBot
from droidbot.droidmaster import DroidMaster
import time
from postprocess_droidbot import postprocess_explore_result,postprocess_explore_result_src



def parse_args():
    """
    parse command line input
    generate options including host name, port number
    """
    parser = argparse.ArgumentParser(description="Start DroidBot to test an Android app.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-d", action="store", dest="device_serial", required=False,
                        help="The serial number of target device (use `adb devices` to find)")
    parser.add_argument("-a", action="store", dest="apk_path", required=True,
                        help="The file path to target APK")
    parser.add_argument("-o", action="store", dest="output_dir",
                        help="directory of output")
    # parser.add_argument("-env", action="store", dest="env_policy",
    #                     help="policy to set up environment. Supported policies:\n"
    #                          "none\tno environment will be set. App will run in default environment of device; \n"
    #                          "dummy\tadd some fake contacts, SMS log, call log; \n"
    #                          "static\tset environment based on static analysis result; \n"
    #                          "<file>\tget environment policy from a json file.\n")
    parser.add_argument("-policy", action="store", dest="input_policy", default=input_manager.DEFAULT_POLICY,
                        help='Policy to use for test input generation. '
                             'Default: %s.\nSupported policies:\n' % input_manager.DEFAULT_POLICY +
                             '  \"%s\" -- No event will be sent, user should interact manually with device; \n'
                             '  \"%s\" -- Use "adb shell monkey" to send events; \n'
                             '  \"%s\" -- Explore UI using a naive depth-first strategy;\n'
                             '  \"%s\" -- Explore UI using a greedy depth-first strategy;\n'
                             '  \"%s\" -- Explore UI using a naive breadth-first strategy;\n'
                             '  \"%s\" -- Explore UI using a greedy breadth-first strategy;\n'
                             %
                             (
                                 input_policy.POLICY_NONE,
                                 input_policy.POLICY_MONKEY,
                                 input_policy.POLICY_NAIVE_DFS,
                                 input_policy.POLICY_GREEDY_DFS,
                                 input_policy.POLICY_NAIVE_BFS,
                                 input_policy.POLICY_GREEDY_BFS,
                             ))

    # for distributed DroidBot
    parser.add_argument("-distributed", action="store", dest="distributed", choices=["master", "worker"],
                        help="Start DroidBot in distributed mode.")
    parser.add_argument("-master", action="store", dest="master",
                        help="DroidMaster's RPC address")
    parser.add_argument("-qemu_hda", action="store", dest="qemu_hda",
                        help="The QEMU's hda image")
    parser.add_argument("-qemu_no_graphic", action="store_true", dest="qemu_no_graphic",
                        help="Run QEMU with -nograpihc parameter")

    parser.add_argument("-script", action="store", dest="script_path",
                        help="Use a script to customize input for certain states.")
    parser.add_argument("-count", action="store", dest="count", default=input_manager.DEFAULT_EVENT_COUNT, type=int,
                        help="Number of events to generate in total. Default: %d" % input_manager.DEFAULT_EVENT_COUNT)
    parser.add_argument("-interval", action="store", dest="interval", default=input_manager.DEFAULT_EVENT_INTERVAL,
                        type=int,
                        help="Interval in seconds between each two events. Default: %d" % input_manager.DEFAULT_EVENT_INTERVAL)
    parser.add_argument("-timeout", action="store", dest="timeout", default=input_manager.DEFAULT_TIMEOUT, type=int,
                        help="Timeout in seconds, -1 means unlimited. Default: %d" % input_manager.DEFAULT_TIMEOUT)
    parser.add_argument("-cv", action="store_true", dest="cv_mode",
                        help="Use OpenCV (instead of UIAutomator) to identify UI components. CV mode requires opencv-python installed.")
    parser.add_argument("-debug", action="store_true", dest="debug_mode",
                        help="Run in debug mode (dump debug messages).")
    parser.add_argument("-random", action="store_true", dest="random_input",
                        help="Add randomness to input events.")
    parser.add_argument("-keep_app", action="store_true", dest="keep_app",
                        help="Keep the app on the device after testing.")
    parser.add_argument("-keep_env", action="store_true", dest="keep_env",
                        help="Keep the test environment (eg. minicap and accessibility service) after testing.")
    parser.add_argument("-use_method_profiling", action="store", dest="profiling_method",
                        help="Record method trace for each event. can be \"full\" or a sampling rate.")
    parser.add_argument("-grant_perm", action="store_true", dest="grant_perm",
                        help="Grant all permissions while installing. Useful for Android 6.0+.")
    parser.add_argument("-is_emulator", action="store_true", dest="is_emulator",
                        help="Declare the target device to be an emulator, which would be treated specially by DroidBot.")
    parser.add_argument("-accessibility_auto", action="store_true", dest="enable_accessibility_hard",
                        help="Enable the accessibility service automatically even though it might require device restart\n(can be useful for Android API level < 23).")
    parser.add_argument("-humanoid", action="store", dest="humanoid",
                        help="Connect to a Humanoid service (addr:port) for more human-like behaviors.")
    parser.add_argument("-ignore_ad", action="store_true", dest="ignore_ad",
                        help="Ignore Ad views by checking resource_id.")
    parser.add_argument("-replay_output", action="store", dest="replay_output",
                        help="The droidbot output directory being replayed.")
    parser.add_argument("-script_target",action="store",dest="script_target_path",
                        help="Declare the target view that users want to stop the droidbot")
    options = parser.parse_args()

    # print options
    return options


def main():
    """
    the main function
    it starts a droidbot according to the arguments given in cmd line
    """
    opts = parse_args()
    import os
    if not os.path.exists(opts.apk_path):
        print("APK does not exist.")
        return
    if not opts.output_dir and opts.cv_mode:
        print("To run in CV mode, you need to specify an output dir (using -o option).")

    if opts.distributed:
        if opts.distributed == "master":
            start_mode = "master"
        else:
            start_mode = "worker"
    else:
        start_mode = "normal"

    if start_mode == "master":
        droidmaster = DroidMaster(
            app_path=opts.apk_path,
            is_emulator=opts.is_emulator,
            output_dir=opts.output_dir,
            # env_policy=opts.env_policy,
            env_policy=env_manager.POLICY_NONE,
            policy_name=opts.input_policy,
            random_input=opts.random_input,
            script_path=opts.script_path,
            event_interval=opts.interval,
            timeout=opts.timeout,
            event_count=opts.count,
            cv_mode=opts.cv_mode,
            debug_mode=opts.debug_mode,
            keep_app=opts.keep_app,
            keep_env=opts.keep_env,
            profiling_method=opts.profiling_method,
            grant_perm=opts.grant_perm,
            enable_accessibility_hard=opts.enable_accessibility_hard,
            qemu_hda=opts.qemu_hda,
            qemu_no_graphic=opts.qemu_no_graphic,
            humanoid=opts.humanoid,
            ignore_ad=opts.ignore_ad,
            replay_output=opts.replay_output,
            script_target_path = opts.script_target_path
        )
        droidmaster.start()
    else:
        droidbot = DroidBot(
            app_path=opts.apk_path,
            device_serial=opts.device_serial,
            is_emulator=opts.is_emulator,
            output_dir=opts.output_dir,
            # env_policy=opts.env_policy,
            env_policy=env_manager.POLICY_NONE,
            policy_name=opts.input_policy,
            random_input=opts.random_input,
            script_path=opts.script_path,
            event_interval=opts.interval,
            timeout=opts.timeout,
            event_count=opts.count,
            cv_mode=opts.cv_mode,
            debug_mode=opts.debug_mode,
            keep_app=opts.keep_app,
            keep_env=opts.keep_env,
            profiling_method=opts.profiling_method,
            grant_perm=opts.grant_perm,
            enable_accessibility_hard=opts.enable_accessibility_hard,
            master=opts.master,
            humanoid=opts.humanoid,
            ignore_ad=opts.ignore_ad,
            replay_output=opts.replay_output,
            script_target_path=opts.script_target_path
        )
        droidbot.start()
    return



def my_main_bfs():
    script_path = '/path/to/scripts/'
    apk_name = 'your_apk_name.apk'
    enhanced_test_path = '/path/to/new_test/'
    # for craftdroid droidbot BFS
    test_name_list = [script_path]
    apk_name_list = [apk_name]
    save_csv_path = enhanced_test_path
    save_csv_name = 'new_test.csv'
    type = 'experiment'
    tool_result_name = 'migrated_test.csv'

    for idx in range(len(test_name_list)):
        test_name = test_name_list[idx]
        apk_name = apk_name_list[idx]
        max_round_num = 1
        policy_file_name = 'bfs/'
        start_time = time.time()
        for round in range(max_round_num):
            print("test_name:",test_name)
            print("round_num:",round)
            apk_path = apk_name
            output_dir = test_name+policy_file_name+'output_'+str(round)
            log_filename = output_dir + "/log.txt"
            script_path = test_name+'script/script.json'
            script_target_path = test_name+'script/stop_script.json'
            droidbot_policy = input_policy.POLICY_GREEDY_BFS

            import os
            if not os.path.exists(apk_path):
                print("APK does not exist.")
                return
            if not output_dir:
                print("To run in CV mode, you need to specify an output dir (using -o option).")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            droidbot = DroidBot(
                app_path=apk_path,
                device_serial=None,
                is_emulator=False,
                output_dir=output_dir,
                env_policy=env_manager.POLICY_NONE,
                policy_name = droidbot_policy,
                random_input = True,
                script_path=script_path,
                event_interval=1,
                timeout=input_manager.DEFAULT_TIMEOUT,
                event_count=input_manager.DEFAULT_EVENT_COUNT,
                cv_mode=False,
                debug_mode=False,
                keep_app=False,  
                keep_env=False,
                profiling_method=None,
                grant_perm=False,
                enable_accessibility_hard=False,
                master=None,
                humanoid=None,
                ignore_ad=False,
                replay_output=None,
                script_target_path=script_target_path,
                log_filename=log_filename,
                target_path=None,
                watch_path=None
            )
            droidbot.start()

        # postprocess droidbot
        postprocess_explore_result(save_csv_path, save_csv_name, test_name, policy_file_name, pre_test_name,
                                       tool_result_name)

        end_time = time.time()
        import pandas as pd
        df = pd.read_csv(save_csv_path + save_csv_name)
        if df.loc[df.index[-1], 'time_cost'] == '':
            df.loc[df.index[-1], 'time_cost'] = end_time - start_time
            df.to_csv(save_csv_path + save_csv_name, index=False)
            print("save to csv ok!")
        else:
            print("final time cost:", end_time - start_time)



if __name__ == "__main__":
    my_main_bfs()
