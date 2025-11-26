#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pyautogui as pag
import time
from labauto.gui_control.gui_control_windows import GUIControlWindows

# memo
# - soft名: NETZSCH Measurement
# - input_parameterするとmain windowの名前が変わる. 途中でエラーになったときに困る. 毎回ソフトを起動しなおすのがよい?
#
class GUIControl_NETZSCH_Measurement(GUIControlWindows):
    def __init__(self):
        super().__init__(
            window_name='TMA 402 F3 Hyperion (1-414/6) ; 測定 - ExpertMode v. 8.0.3',
            exe_dir = 'C:\\Program Files (x86)\\NETZSCH\\Proteus80\\program',
            exe_cmd = 'start Tam.exe 52 1 4',  # Tam.exe InstrId ChnNo {BusId}            
            exe_sleep = 4  # 3 is sometimes not enough
        )

        # window name
        self.window_name_main     = self.window_name
        self.window_name_analysis = ''  # init with file name later
        self.methods_dir = 'C:\\NETZSCH\\Proteus80\\_Records\\Methods'

        # flag
        self.is_window_main = False
        self.is_window_ngb = False
        self.is_window_event_info = False
        self.is_window_analysis = False
        
        # path
        self.assets_dir = r'\\wsl$\Ubuntu\home\utokyo-user\catkin_ws\src\netzsch_ros\assets'  # raw文字
        self.img_path_method            = os.path.join(self.assets_dir, 'icon_method.png')
        self.img_path_select_method     = os.path.join(self.assets_dir, 'OpenMethod_selected_method_name.png')  # must take screenshot of the method to be used
        self.img_path_select            = os.path.join(self.assets_dir, 'Method_select.png')
        self.img_path_save              = os.path.join(self.assets_dir, 'MeasureFileNameSetting_save.png')
        self.img_path_overwrite_y       = os.path.join(self.assets_dir, 'NGB_overwrite_y.png')
        self.img_path_OK                = os.path.join(self.assets_dir, 'Method_OK.png')
        self.img_path_start_measure     = os.path.join(self.assets_dir, 'icon_start_measure.png')
        self.img_path_standby_TMAsoft   = os.path.join(self.assets_dir, 'Adjustment_standby_start.png')
        self.img_path_start_TMAsoft     = os.path.join(self.assets_dir, 'Adjustment_start.png')
        self.img_path_finish_measure_OK = os.path.join(self.assets_dir, 'NGB_OK.png')
        self.img_path_event_info_OK     = os.path.join(self.assets_dir, 'EventInfo_OK.png')
        self.img_path_analysis_window_close = os.path.join(self.assets_dir, 'analysis_window_close.png')
        self.img_path_NGB_No            = os.path.join(self.assets_dir, 'NGB_No.png')
        print('self.assets_dir:', self.assets_dir)

        # status
        self.TMA_measure_status = 'waiting'  # waiting, setting, measuring, completed

        
    def get_TMA_measure_status(self):
        return self.TMA_measure_status


    # 行程順
    # - soft起動
    # - 初期設定(メソッドを開く): メソッド -> メソッドを開く -> メソッドを選択(test.ngb-s-dilなど) -> 開く
    # - 設定定義を入力: ID, 名前,　長さ, 幅, 厚み, 試料の材質, ファイル名を入力 -> OK
    # - 測定(別window): 測定の開始(緑の三角アイコン) -> スタンバイの開始 -> 開始 -> 測定終了を待つ
    # 終わると, 測定データ(csvなど)は自動で保存される. 解析ソフトが起動する.        
    def start_software(self):
        self.execute_application()  # wait exe_sleep time
        self.is_window_main = True
        self.resize_window(self.window_name_main, width=600, height=800, x=0, y=0)  # resize window
        time.sleep(12)  # wait 
        
        # find セットポイントwindow and click 'いいえ' 
        self.click_by_pos_on_window('セットポイント', 370, 270, 1)
                 

    def set_method(self, method_file_name='test.ngb-s-dil'):
        # initial process
        self.TMA_measure_status = 'setting'
        self.make_window_active(self.window_name_main)
        self.click_by_img(self.img_path_method)   # click 'メソッド'
        self.click_by_pos(0, 100, relative=1)  # click 'メソッドを開く'
        str_open_method = 'メソッドを開く. ルート: ' + self.methods_dir
        self.make_window_active(str_open_method)
        self.click_by_img(self.img_path_select_method, clicks=2)
        window_name_method = 'メソッド '+ '\'' + method_file_name + '\'' + ' ベースの測定定義'
        self.make_window_active(window_name_method)


    def input_parameters(self,
                         lab              = 'room_A',
                         project          = 'sample_project',
                         measurer         = 'operator',
                         comment          = '',
                         sample_id        = 0,
                         sample_name      = 'test_material',
                         sample_length    = 20,   # [mm]
                         sample_width     = 5,    # [mm]
                         sample_thickness = 0.3,  # [mm]
                         sample_material  = 'polyethylene',
                         result_file_name = 'test_result'):
        
        # input parameters
        #前回の測定の有無で開始点が変わるので注意.
        #以下は, IDから始まる場合を想定.(基本的にはここから始まる)    
        # right top
        pag.write(str(sample_id))
        pag.press('tab')
        pag.write(sample_name)
        pag.press('tab', presses=3)
        # left top
        pag.write(lab)
        pag.press('tab')
        pag.write(project)
        pag.press('tab')
        pag.write(measurer)
        pag.press('tab')
        pag.write(comment)
        pag.press('tab', presses=4)
        # right middle
        pag.write(str(sample_length))
        pag.press('tab')
        pag.press('delete')
        pag.write(str(sample_width))
        pag.press('tab')
        pag.press('delete')
        pag.write(str(sample_thickness))
        pag.press('tab')
        pag.write(sample_material)
        pag.press('tab')
        # left bottom
        self.click_by_img(self.img_path_select)
        pag.write(result_file_name)
        time.sleep(1)  # wait tuning
        self.click_by_img(self.img_path_save)

        #上書き処理
        try:
            for i in range(3):
                self.make_window_active('NGB測定')
                time.sleep(1)
            self.click_by_img(self.img_path_overwrite_y)
        except:
            print('上書きしない')

        self.click_by_img(self.img_path_OK)

        # update name of main window
        self.window_name_main = self.window_name_main + ' - ' + result_file_name + '.ngb-sl8'
        self.window_name_analysis = 'NETZSCH Proteus Thermal Analysis (Automatic instance) 8.0.3 - [' + result_file_name + '.ngb-ol8]'
        print('window name updated to: %s'% self.window_name_main)


    def measure(self):
        self.TMA_measure_status = 'measuring'

        # 測定アイコンのクリック
        self.click_by_img(self.img_path_start_measure, sleep_time=3)  # must wait for a while (2s is short)

        #「スタンバイの開始」のクリック
        self.make_window_active('TMA 402 F3 Hyperion 調整 (1)')
        self.click_by_img(self.img_path_standby_TMAsoft)
        # memo:
        # - 装置にエラーがあると測定を開始できない
        # - 例としては,
        # - ガスの流量不足. 
        # - サンプルに負荷がかかっていない -> Delta L: UNF

        # 「開始」のクリック
        while True:
            try:
                self.click_by_img(self.img_path_start_TMAsoft)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                print('Image might not found. Check again in 10 seconds. ->', self.img_path_start_TMAsoft)
                time.sleep(10)
            else:
                print('TMA measurement has started')
                #測定完了後は, main画面に加えて, NGB測定, イベント情報, 分析ソフトのwindowが立ち上がる.
                self.is_window_ngb = True
                self.is_window_event_info = True
                self.is_window_analysis = True
                break

        # Todo:
        # - OCRで残り時間を抽出

        # NGB測定 windowで測定完了をチェック
        while True:
            try:
                self.make_window_active('NGB測定')
                time.sleep(3)
                self.click_by_img(self.img_path_finish_measure_OK)
                print('NGB window is closed')
                self.is_window_ngb = False
            except KeyboardInterrupt:
                break
            except:
                print('Under measurement. Check again in 10 seconds')
                time.sleep(10)
            else:
                print('TMA measurement has finished')
                time.sleep(1)
                break


        self.TMA_measure_status = 'completed'
        

    # 終了処理
    def close_software(self):
        # イベント情報window close
        while self.is_window_event_info:
            try:
                print('Closing event_info window')
                self.make_window_active('イベント情報')
                time.sleep(1)
                self.click_by_img(self.img_path_event_info_OK)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                print('event_info is not found. Check again in 2 seconds.')
                time.sleep(2)
            else:
                print('event_info windows is closed')
                self.is_window_event_info = False
                time.sleep(1)

        # main画面close
        while self.is_window_main:
            try:
                print('Closing main window')
                self.make_window_active(self.window_name_main)
                time.sleep(1)
                self.close_active_window()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                print('main window is not found. Check again in 2 seconds.')
                time.sleep(2)
            else:
                print('main windows is closed')
                self.is_window_main = False
                self.is_window_ngb = True  # main windowを閉じたときに NGB測定画面が出る
                time.sleep(1)

        # NGB測定 close
        while self.is_window_ngb:
            try:
                print('Closing NGB window')
                self.make_window_active('NGB測定')
                time.sleep(1)
                self.click_by_img(self.img_path_NGB_No)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                print('NGB window is not found. Check again in 2 seconds.')
                time.sleep(2)
            else:
                print('NGB window is closed')
                self.is_window_ngb = False
                time.sleep(1)

        # analysis soft close
        # memo & todo:
        # - window名が取得できればそこからcloseしたい.
        # - window名が既存のファイルがあると#nで増分していくのでどうするべきか.
        while self.is_window_analysis:
            try:
                print('Closing analysis window')
                self.click_by_img(self.img_path_analysis_window_close)  # このwindowを閉じるのが最後なのでこれでも問題ない.

                #self.make_window_active(self.window_name_analysis)
                #time.sleep(1)
                #self.close_active_window()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                print('Analysis window is not found. Check again in 2 seconds.')
                time.sleep(2)
            else:
                print('Analysis windows is closed')
                self.is_window_analysis = False
                time.sleep(1)

        print('End of this measurement')
        print('waiting for next measurement')


    def all_process(self):
        self.start_software()
        self.set_method()
        self.input_parameters()
        self.measure()
        self.close_software()


if __name__ == "__main__":
    tma_gui_controller = GUIControl_NETZSCH_Measurement()
    tma_gui_controller.start_software()
    #tma_gui_controller.all_process()

