#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import os
import pyautogui as pag
import pytesseract
import re
import tempfile
import time
from pathlib import Path
from labautopy.gui_control_windows import GUIControlWindows

# tesseract OCRのpathを指定
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# memo
# - soft名: NETZSCH Measurement
# - input_parameterするとmain windowの名前が変わる. 途中でエラーになったときに困るので, 毎回ソフトを起動しなおす.
# - 行程順
#   - start_software(): soft起動
#   - set_method():
#     - メソッド -> メソッドを開く -> メソッドを選択(test.ngb-s-dilなど) -> 開く
#   - input_parameters():
#     - ID, 名前, 長さ, 幅, 厚み, 試料の材質, ファイル名を入力 -> OK
#   - measure():
#     - 測定の開始(緑の三角アイコン) -> スタンバイの開始 -> 開始 -> 測定終了を待つ
#     - 測定が終わると, データ(csvなど)が保存される. 解析ソフトが起動する.
#   - close_software():
#     - 各種windowを閉じる


class GUIControl_NETZSCH_Measurement(GUIControlWindows):
    def __init__(self):
        super().__init__(
            window_name='TMA 402 F3 Hyperion (1-414/6) ; 測定 - ExpertMode v. 8.0.3',
            exe_dir = 'C:\\Program Files (x86)\\NETZSCH\\Proteus80\\program',
            exe_cmd = 'start Tam.exe 52 1 4',  # Tam.exe InstrId ChnNo {BusId}
            exe_sleep = 5  # 4 is sometimes not enough
        )

        # window name
        self.window_name_main_org = self.window_name  # original name at execution
        self.window_name_main     = self.window_name  # for updated name
        self.window_name_analysis = ''  # init with file name later
        self.methods_dir = 'C:\\NETZSCH\\Proteus80\\_Records\\Methods'

        # flag
        self.is_window_main = False
        self.is_window_ngb = False
        self.is_window_event_info = False
        self.is_window_analysis = False

        # path
        self.tmp_dir = tempfile.gettempdir()  # screenshot img for OCR
        self.script_dir = Path(__file__).parent.resolve()
        self.assets_dir = os.path.join(self.script_dir, 'assets')
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
        self.NETZSCH_measurement_status = 'waiting'  # waiting, setting, measuring, completed


    def get_NETZSCH_measurement_status(self):
        return self.NETZSCH_measurement_status


    def start_software(self):
        self.execute_application()  # wait exe_sleep time
        self.is_window_main = True
        self.resize_window(self.window_name_main_org, width=600, height=800, x=0, y=0)  # resize window
        time.sleep(12)  # wait

        # find セットポイントwindow and click 'いいえ'
        self.click_by_pos_on_window('セットポイント', 370, 270, 1)


    def set_method(self, method_file_name='test.ngb-s-dil'):
        # initial process
        self.NETZSCH_measurement_status = 'setting'
        self.make_window_active(self.window_name_main_org)
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
        result_file_name_w_id = result_file_name + '_' + str(sample_id)

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
        pag.write(result_file_name_w_id)
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
        self.window_name_main = self.window_name_main_org + ' - ' + result_file_name_w_id + '.ngb-sl8'
        self.window_name_analysis = 'NETZSCH Proteus Thermal Analysis (Automatic instance) 8.0.3 - [' + result_file_name_w_id + '.ngb-ol8]'
        print('window name updated to: %s'% self.window_name_main)


    def measure(self):
        self.NETZSCH_measurement_status = 'measuring'

        # 測定アイコンのクリック
        self.click_by_img(self.img_path_start_measure, sleep_time=3)  # must wait for a while (2s is short)

        #「スタンバイの開始」のクリック
        self.make_window_active('TMA 402 F3 Hyperion 調整 (1)')
        self.click_by_img(self.img_path_standby_TMAsoft)
        # memo:
        # - 装置にエラーがあると測定を開始できない
        # - 例:
        #   - ガスの流量不足.
        #   - サンプルに負荷がかかっていない -> Delta L: UNF

        # 「開始」のクリック
        try:
            while True:
                try:
                    self.click_by_img(self.img_path_start_TMAsoft)
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
        except KeyboardInterrupt:
            print('Ctrl+c')

        # OCR setting
        ss_path = os.path.join(self.tmp_dir, 'tmp_ss.png')
        print('screenshot is saved to: %s'% ss_path)

        # OCR
        seconds = None
        try:
            while seconds is None:
                try:
                    self.screenshot_window('測定残り時間', ss_path)
                    seconds = self.extract_remaining_time(ss_path, debug=True)
                    time.sleep(2)
                except Exception as e:
                    print(e)
                    print('OCR is not succeeded. Check again in 2 seconds.')
                    time.sleep(2)
        except KeyboardInterrupt:
            print('Ctrl+c')

        print('OCR succeeded')
        print('Wait for %s [sec]'% seconds)
        time.sleep(seconds)

        # NGB測定 windowで測定完了をチェック
        try:
            while self.is_window_ngb:
                try:
                    self.make_window_active('NGB測定')
                    time.sleep(3)
                    self.click_by_img(self.img_path_finish_measure_OK)
                except:
                    print('Under measurement(NGB window is not found). Check again in 2 seconds.')
                    time.sleep(2)
                else:
                    print('NGB window is closed')
                    print('TMA measurement has finished')
                    self.is_window_ngb = False
                    time.sleep(1)
        except KeyboardInterrupt:
            print('Ctrl+c')

        self.NETZSCH_measurement_status = 'completed'


    # 終了処理
    def close_software(self):
        # イベント情報window close
        try:
            while self.is_window_event_info:
                try:
                    print('Closing event_info window')
                    self.make_window_active('イベント情報')
                    time.sleep(1)
                    self.click_by_img(self.img_path_event_info_OK)
                except Exception as e:
                    print(e)
                    print('event_info is not found. Check again in 2 seconds.')
                    time.sleep(2)
                else:
                    print('event_info windows is closed')
                    self.is_window_event_info = False
                    time.sleep(1)
        except KeyboardInterrupt:
            print('Ctrl+c')

        # main画面close
        try:
            while self.is_window_main:
                try:
                    print('Closing main window')
                    self.make_window_active(self.window_name_main)
                    time.sleep(1)
                    self.close_active_window()
                except Exception as e:
                    print(e)
                    print('main window is not found. Check again in 2 seconds.')
                    time.sleep(2)
                else:
                    print('main windows is closed')
                    self.is_window_main = False
                    self.is_window_ngb = True  # main windowを閉じたときに NGB測定画面が出る
                    time.sleep(1)
        except KeyboardInterrupt:
            print('Ctrl+c')

        # NGB測定 close
        try:
            while self.is_window_ngb:
                try:
                    print('Closing NGB window')
                    self.make_window_active('NGB測定')
                    time.sleep(1)
                    self.click_by_img(self.img_path_NGB_No)
                except Exception as e:
                    print(e)
                    print('NGB window is not found. Check again in 2 seconds.')
                    time.sleep(2)
                else:
                    print('NGB window is closed')
                    self.is_window_ngb = False
                    time.sleep(1)
        except KeyboardInterrupt:
            print('Ctrl+c')

        # analysis soft close
        try:
            while self.is_window_analysis:
                try:
                    print('Closing analysis window')
                    # memo & todo:
                    # - window名が既存のファイルがあると#nで増分していくのでどうするべきか.
                    # - imgからだと誤認識があるので, window名が取得できるなら,そこからcloseできたほうがよい.
                    #self.make_window_active(self.window_name_analysis)
                    #time.sleep(1)
                    #self.close_active_window()
                    self.click_by_img(self.img_path_analysis_window_close)  # このwindowを閉じるのが最後なのでimgからでも誤認識が起きにくく,ひとまず問題ない.
                except Exception as e:
                    print(e)
                    print('Analysis window is not found. Check again in 2 seconds.')
                    time.sleep(2)
                else:
                    print('Analysis windows is closed')
                    self.is_window_analysis = False
                    time.sleep(1)
        except KeyboardInterrupt:
            print('Ctrl+c')

        print('End of this measurement')


    def extract_remaining_time(self, img_org_path, debug=False):
        """
        Extract remaining time for measurement completion with HH:MM:SS format by OCR
        """
        img = cv2.imread(img_org_path)
        img_scaled = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)  # scale 3times larger
        img_gray = cv2.cvtColor(img_scaled, cv2.COLOR_BGR2GRAY)  # gray scale
        img_th = cv2.adaptiveThreshold(  # threshold
            img_gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 7
        )

        if debug:
            cv2.imshow("gray", img_gray)
            img_gray_path = os.path.join(self.tmp_dir, 'debug_gray.png')
            cv2.imwrite(img_gray_path, img_gray)

            cv2.imshow("th", img_th)
            img_th_path = os.path.join(self.tmp_dir, 'debug_th.png')
            cv2.imwrite(img_th_path, img_th)

            cv2.waitKey(3000)  # wait 3s
            cv2.destroyAllWindows()

        # OCR
        text = pytesseract.image_to_string(img_th, lang='jpn+eng')
        print("OCR result:")
        print(text)

        # extract sec
        match = re.search(r'(\d+):(\d+):(\d+)', text)
        if match:
            h, m, s = map(int, match.groups())
            seconds = h * 3600 + m * 60 + s
            print('seconds: %s'% seconds)
            return seconds

        return None


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
