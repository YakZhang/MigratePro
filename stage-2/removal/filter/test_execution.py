
# Goal: generate the executed test cases according to test case sequences
# coding=utf-8

import os
import unittest
import time
from appium import webdriver
# from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction






def add_information_to_app_dictionary():
    app_dictionary = {}
    app_dictionary['a11'] = ['acr.browser.lightning','acr.browser.lightning.MainActivity','true']
    app_dictionary['a12'] = ['com.android.browser','com.android.browser.BrowserActivity','true']
    app_dictionary['a13'] = ['com.stoutner.privacybrowser.standard','com.stoutner.privacybrowser.activities.MainWebViewActivity','true'] #privicy_browser
    app_dictionary['a14'] = ['de.baumann.browser','de.baumann.browser.Activity.BrowserActivity','true'] #foss_browser
    app_dictionary['a15'] = ['org.mozilla.focus','org.mozilla.focus.activity.MainActivity','false'] # Firefox browser
    app_dictionary['a21'] = ['com.rubenroy.minimaltodo','com.rubenroy.minimaltodo.MainActivity','true'] #Minimal browser
    app_dictionary['a22'] = ['douzifly.list','douzifly.list.ui.home.MainActivity','true']#Clear List
    app_dictionary['a23'] = ['org.secuso.privacyfriendlytodolist','org.secuso.privacyfriendlytodolist.tutorial.TutorialActivity','true'] # Todo_list
    app_dictionary['a24'] = ['kdk.android.simplydo','kdk.android.simplydo.SimplyDoActivity','true'] # Simply do
    app_dictionary['a25'] = ['com.woefe.shoppinglist','com.woefe.shoppinglist.activity.MainActivity','true'] #Shopping List
    app_dictionary['a31'] = ['com.contextlogic.geek','com.contextlogic.wish.activity.login.LoginActivity','true'] # Geek
    app_dictionary['a32'] = ['com.contextlogic.wish','com.contextlogic.wish.activity.login.signin.SignInActivity','true'] # Wish
    app_dictionary['a33'] = ['com.rainbowshops','com.rainbowshops.activity.LaunchActivity','true'] #rainbow
    app_dictionary['a34'] = ['com.etsy.android','com.etsy.android.ui.homescreen.HomescreenTabsActivity','true']#etsy
    app_dictionary['a35'] = ['com.yelp.android','com.yelp.android.nearby.ui.ActivityNearby','true'] #yelp
    app_dictionary['a41'] = ['com.fsck.k9','com.fsck.k9.activity.setup.WelcomeMessage','true'] #k9
    app_dictionary['a43'] = ['ru.mail.mailapp','ru.mail.mailapp.SplashScreenActivity','true'] #mail.ru
    app_dictionary['a42'] = ['com.appple.app.email','com.fsck.k9.activity.Accounts','true'] # email box fast
    app_dictionary['a44'] = ['com.my.mail','ru.mail.mailapp.SplashScreenActivity','true'] #myMail
    app_dictionary['a45'] = ['park.outlook.sign.in.client','ru.mail.mailapp.SplashScreenActivity','true'] # emaulapp for any mail
    app_dictionary['a51'] = ['anti.tip','anti.tip.Tip','true'] #tip Calculator
    app_dictionary['a52'] = ['com.appsbyvir.tipcalculator','com.appsbyvir.tipcalculator.MainActivity','true']
    app_dictionary['a53'] = ['com.tleapps.simpletipcalculator','com.tleapps.simpletipcalculator.MainActivity','true'] # simple tip calculator
    app_dictionary['a54'] = ['com.zaidisoft.teninone','com.zaidisoft.teninone.Calculator','true']
    app_dictionary['a55'] = ['com.jpstudiosonline.tipcalculator','com.jpstudiosonline.tipcalculator.MainActivity','true'] #


    # add fruiter app_dictionary
    app_dictionary['abc'] = ['com.abc.abcnews','com.abc.abcnews.ui.navigation.MainNavigationActivity','true']
    app_dictionary['buzzfeed'] = ['com.buzzfeed.android','com.buzzfeed.android.activity.SplashActivity','true']
    app_dictionary['etsy'] = ['com.etsy.android','com.etsy.android.ui.homescreen.HomescreenTabsActivity','true']
    app_dictionary['fivemiles'] = ['com.thirdrock.fivemiles','com.insthub.fivemiles.Activity.WelcomeActivity','true']
    app_dictionary['fox'] = ['com.foxnews.android','com.foxnews.android.corenav.StartActivity','true']
    app_dictionary['geek'] = ['com.contextlogic.geek','com.contextlogic.wish.activity.login.LoginActivity','false']
    app_dictionary['home'] = ['com.contextlogic.home','com.contextlogic.wish.activity.login.signin.SignInActivity','false']
    app_dictionary['reuters'] = ['com.thomsonreuters.reuters', 'com.thomsonreuters.reuters.activities.SplashActivity', 'true']
    app_dictionary['smartnews'] = ['jp.gocro.smartnews.android','jp.gocro.smartnews.android.activity.SmartNewsActivity','true']
    app_dictionary['wish'] = ['com.contextlogic.wish','com.contextlogic.wish.activity.browse.BrowseActivity','true']
    return app_dictionary

# class ContactsAndroidTests(unittest.TestCase):
class ContactsAndroidTests():

    def setUp(self,app_name):

        app_dictionary = add_information_to_app_dictionary()
        caps = {}
        caps["deviceName"] = "emulator-5554"
        caps["platformName"] = "Android"
        # caps["appPackage"] = "kdk.android.simplydo"
        # caps["appActivity"] = "kdk.android.simplydo.SimplyDoActivity"
        caps['appPackage'] = app_dictionary[app_name][0]
        caps['appActivity'] = app_dictionary[app_name][1]
        caps["noReset"] = app_dictionary[app_name][2]

        self.driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)
        time.sleep(5)

    def tearDown(self):
        self.driver.quit()

    def test_function(self,test,action_idx):
        time.sleep(5)
        label = 0
        test_index = 0
        while(test_index < len(test)):
            event_type = test[test_index][2]
            el = ""
            if event_type == 'gui':
                event_checker = test[test_index][1]
                actions = test[test_index][3]
                action = ""
                if isinstance(actions,str):
                    action = actions
                else:
                    action = actions[action_idx]
                print("action",action)
                inputs = test[test_index][4]
                input = ""
                if isinstance(inputs,list):
                    input = inputs[action_idx]
                else:
                    input = inputs
                if isinstance(event_checker,float):

                    test_index += 1
                    continue
                if 'id/' in event_checker:
                    # el = self.driver.find_element_by_id(event_checker)
                    try:
                        # el = self.driver.find_element(AppiumBy.ID,event_checker) # for 2.6 version
                        el = self.driver.find_element_by_id(event_checker)
                        time.sleep(5)
                    except:
                        return label
                else:
                    # el =self.driver.find_element_by_xpath(event_checker)
                    try:
                        # el = self.driver.find_element(AppiumBy.XPATH,event_checker) # for 2.6 version
                        el = self.driver.find_element_by_xpath(event_checker)
                        time.sleep(5)
                    except:
                        return label
                if action == 'click':
                    action = el.click
                    self.try_action(action)
                elif action == 'send_keys_and_hide_keyboard' or action == 'send_keys':
                    action = el.send_keys
                    self.try_input_action(action, input)
                    # el.send_keys(input)

                    self.driver.hide_keyboard()
                elif action == 'clear_and_send_keys':
                    el.clear()
                    action = el.send_keys
                    # el.send_keys(input)
                    self.try_input_action(action, input)
                    self.driver.hide_keyboard()
                elif action == 'clear_and_send_keys_and_hide_keyboard':
                    el.clear()
                    # el.send_keys(input)
                    self.try_input_action(action, input)
                    self.driver.hide_keyboard()
                elif action == 'long_press':
                    action = TouchAction(self.driver)
                    action.long_press(el)
                    action.perform()

                # add sendKeys for fit for fruiter
                elif action == 'send_keys_and_enter' or action == 'sendKeys':
                    # need to test before
                    # el.send_keys(input)
                    action = el.send_keys
                    self.try_input_action(action, input)
                    self.driver.press_keycode(66)  # enter
                elif action == 'swipe_right':
                    # need to test before
                    height = el.rect['height']
                    width = el.rect['width']
                    x = el.rect['x']
                    y = el.rect['y']
                    start_x = x + 0.2 * width
                    start_y = y + 0.5 * height
                    end_x = x + 0.8 * width
                    end_y = y + 0.5 * height
                    duration = 800
                    self.driver.swipe(start_x, start_y, end_x, end_y, duration)
                    # time.sleep(5)
                    # el.click()
                    # self.driver.swipe(start_x=300, start_y=500, end_x=300, end_y=700, duration=880)
                time.sleep(5)

            if event_type == 'oracle':
                event_checker = test[test_index][1]
                condition = test[test_index][3]
                print("condition",condition)
                value = test[test_index][4]
                if isinstance(event_checker,float):

                    test_index += 1
                    continue
                if condition == 'wait_until_element_present':
                    if 'id/' in value:
                        try:
                            # el = self.driver.find_element(AppiumBy.ID, value) # for 2.6 version
                            el = self.driver.find_element_by_id(value)
                            assert el.is_displayed()
                            time.sleep(10)
                        except:

                            return label
                    else:
                        print("start oracle")
                        try:
                            # el = self.driver.find_element(AppiumBy.XPATH,value)
                            el = self.driver.find_element_by_xpath(value)
                            assert el.is_displayed()
                            time.sleep(10)
                            print("end oracle")
                        except:
                            return label
                if condition == 'wait_until_text_present':
                    if 'id/' in event_checker:
                        # el = self.driver.find_element(AppiumBy.ID,event_checker)
                        try:
                            el = self.driver.find_element_by_id(event_checker)
                            assert el.get_attribute('text') == value
                            time.sleep(10)
                        except:
                            return label
                    else:
                        # el = self.driver.find_element(AppiumBy.XPATH, event_checker)
                        try:
                            el = self.driver.find_element_by_xpath(event_checker)
                            assert el.get_attribute('text') == value
                            time.sleep(10)
                        except:
                            return label
                if condition == 'wait_until_text_invisible':
                    # need to test before
                    if 'id/' in event_checker:
                        # el = self.driver.find_element(AppiumBy.ID,event_checker)
                        try:
                            el = self.driver.find_element_by_id(event_checker)
                            assert el.is_displayed() == False
                            time.sleep(10)
                        except:
                            return label
                    else:
                        # el=self.driver.find_element(AppiumBy.XPATH,event_checker)
                        try:
                            el = self.driver.find_element_by_xpath(event_checker)
                            assert el.is_displayed() == False
                            time.sleep(10)
                        except:
                            return label
            # if event_type == 'SYS_EVENT':
            #     continue
            test_index += 1
        # need to test before
        label = 1
        return label

    def try_action(self, action):
        while True:
            try:
                action()
                break
            except Exception as e:
                print(e)
    def try_input_action(self, action, input):
        while True:
            try:
                action(input)
                break
            except Exception as e:
                print(e)





