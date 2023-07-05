from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from selenium import webdriver

class CrawlerThread(QThread):
    # 크롤링 작업이 완료되었을 때 신호를 보내기 위한 시그널
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        # 버튼 클릭 시 크롤링 작업 시작
        self.start_crawling()

    def start_crawling(self):
        # 크롤링 작업을 수행하는 스레드 생성 및 시작
        self.crawler_thread = CrawlerThread()
        self.crawler_thread.finished.connect(self.handle_crawling_finished)
        self.crawler_thread.start()

    def handle_crawling_finished(self, html):
        # 크롤링 작업이 완료되면 결과를 처리하는 코드를 여기에 작성
        pass

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
