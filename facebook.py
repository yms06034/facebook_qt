import sys
import os
import facebook_crawling as fc
import asyncio

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QEventLoop
from ui import Ui_MainWindow

async def crawl_data(progress_callback):
    # 비동기 작업 수행
    for i in range(101):
        await asyncio.sleep(0.1)  # 임의의 작업 대기 시간
        progress_callback(i)

class CrawlThread(QThread):
    progress_update = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(crawl_data(self.update_progress))
        loop.close()

    def update_progress(self, progress):
        self.progress_update.emit(progress)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

main_ui = Ui_MainWindow()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        main_ui.setupUi(self)       

        self.show()
        
        self.browser = None
        window_ico = resource_path('facebook_logo.ico')
        self.setWindowIcon(QIcon(window_ico))

        print(window_ico)

        self.setWindowTitle("Facebook Crawling")
        
        main_ui.input_id.setText("miraemakers@naver.com")
        main_ui.input_pwd.setText("445566mmk@")
        
        # main_ui.btn_login.clicked.connect(self.btn_loginClicked)
        main_ui.btn_start.clicked.connect(self.start_crawling)
        
        self.crawl_thread = CrawlThread()
        self.crawl_thread.progress_update.connect(self.update_progress)
        
        
    def start_crawling(self):
        id = main_ui.input_id.text()
        pwd = main_ui.input_pwd.text()
        keyword = main_ui.input_kw.text()
        info_N = main_ui.input_num.text()

        line_edits = [keyword, pwd, id, info_N]

        if all(line_edit for line_edit in line_edits):
            if self.browser is None:
                self.browser = fc.open_browser()
                self.append_log("open facebook")

            login = fc.login(self.browser, id, pwd)
            if login:
                self.append_log("login success")
                self.append_log("로그인에 성공하였습니다.")
            else:
                self.append_log("login failed")
                self.append_log("로그인에 실패하였습니다.")

            self.append_log(f"{keyword} 검색시작")
            final_name = fc.search(self.browser, keyword, info_N)
            self.append_log(f"{keyword} 검색완료")
            self.append_log(final_name + ".csv")

            self.crawl_thread.start()
        else:
            self.append_log("모든 정보를 값을 입력하세요")

        
    def update_progress(self):
            def callback(progress):
                self.progress_bar.setValue(progress)
            return callback

    def btn_startClicked(self):
        id = main_ui.input_id.text()
        pwd = main_ui.input_pwd.text()
        keyword = main_ui.input_kw.text()
        info_N = main_ui.input_num.text()
        
        line_edits = [keyword, pwd, id, info_N]
        
        if all(line_edit for line_edit in line_edits):
            if self.browser is None:
                self.browser = fc.open_browser()
                self.append_log("open facebook")
            login = fc.login(self.browser, id, pwd)
            if login:
                self.append_log("login success")
                self.append_log("로그인에 성공하였습니다.")
            else:
                self.append_log("login failed")
                self.append_log("로그인에 실패하였습니다.")
                
                self.append_log(f"{keyword} 검색시작")
                final_name = fc.search(self.browser, keyword, info_N)
                self.append_log(f"{keyword} 검색완료")
                self.append_log(final_name+".csv")
                
        else:
            self.append_log("모든 정보를 값을 입력하세요")

    
    def append_log(self, msg = ""):
        main_ui.tb_log.append(self.timestamp()+ ": " +msg)

    
    def timestamp(self):
        return fc.datetime.datetime.now().strftime("%Y-%m-%d_%H/%M/%S")



if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())