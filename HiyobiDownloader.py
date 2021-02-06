import sys


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import json
import requests
import urllib.request
import time

form_class = uic.loadUiType("HiyobiDownloader.ui")[0]


class Hiyobi:

    @staticmethod
    def tags_to_array(tags: str):
        return list(filter(None, tags.split(" ")))

    @staticmethod
    def make_body(tags: list, page=1):
        return json.dumps({
            "search": tags,
            "paging": page
        })

    @staticmethod
    def get_cover_image_url(number):
        return "https://cdn.hiyobi.me/tn/" + str(number) + ".jpg"

    @staticmethod
    def search(tags: list, page=1):
        url = "https://api.hiyobi.me/search"
        payload = Hiyobi.make_body(tags, page)
        headers = {'Content-Type': 'application/json', }
        response = requests.post(url, headers=headers, data=payload.encode('utf-8'))
        return json.loads(response.text)

    @staticmethod
    def get_image_urls(number):
        requestUrl = "https://cdn.hiyobi.me/data/json/" + str(number) + "_list.json"
        obj = json.loads(requests.get(requestUrl).text)
        return [("https://cdn.hiyobi.me/data/" + number + "/" + i["name"]) for i in obj]

    @staticmethod
    def get_image_file_names(number):
        requestUrl = "https://cdn.hiyobi.me/data/json/" + str(number) + "_list.json"
        obj = json.loads(requests.get(requestUrl).text)
        return [i["name"] for i in obj]

class ThreadClass(QThread): # 오직 이미지 데이터를 받아오기 위한 쓰레드
    finished = pyqtSignal(dict)
    progressbar = pyqtSignal(int)
    def __init__(self, sec=0, parent=None):
        super().__init__()
        self.main = parent

    def run(self):
        data ={}
        for i in range(len(self.loadedDatabase)):
            data.update({str(i): urllib.request.urlopen(
                urllib.request.Request(Hiyobi.get_cover_image_url(self.loadedDatabase[i]['id']),
                                        headers={'User-Agent': 'Mozilla/5.0'})).read()})
            self.progressbar.emit(i)

        self.finished.emit(data) # 받아온 이미지 데이터를 보냄
        self.stop() # 종료

    def stop(self):
        self.working = False
        self.quit()
        self.wait(5000)

    @pyqtSlot(list) # 검색을 위한 데이터를 받아옴
    def get_data(self, search_text):
        self.loadedDatabase = search_text


class WindowClass(QMainWindow, form_class):
    get_data = pyqtSignal(list) # 스레드에서 검색창에 정보를 스레드에 넘겨주기 위함
    def __init__(self):
        super().__init__()


        self.worker = ThreadClass(parent=self)
        self.worker.finished.connect(self.update_image)
        self.worker.progressbar.connect(self.progressing)
        self.get_data.connect(self.worker.get_data)

        self.selectedIndex = None
        self.loadedDatabase = None

        self.setupUi(self)

        self.progressBar.reset()
        self.progressBar.setRange(0,14)


        self.searchBar.returnPressed.connect(self.search)
        self.searchButton.clicked.connect(self.search)

        self.thumbnailViews = []
        temp = ""
        for i in range(1, 16):
            if i == 15:
                temp += "self.thumbnail_" + str(i)
            else:
                temp += "self.thumbnail_" + str(i) + " "
        print(temp)
        for i in eval("[" + ",".join(temp.split(" ")) + "]"):
            self.thumbnailViews.append(i)
        del temp

        self.selectButtons = []
        temp = ""
        for i in range(1, 16):
            if i == 15:
                temp += "self.pushButton_" + str(i)
            else:
                temp += "self.pushButton_" + str(i) + " "
        print(temp)
        for i in eval("[" + ",".join(temp.split(" ")) + "]"):
            self.selectButtons.append(i)
        del temp

        for i in range(15):
            print("self.selectButtons[%d].clicked.connect(lambda: self.set_selected_index(%d))" % (i, i))

        for i in range(15):
            self.selectButtons[i].clicked.connect(lambda: self.set_selected_index(i))

        self.selectButtons[0].clicked.connect(lambda: self.set_selected_index(0))
        self.selectButtons[1].clicked.connect(lambda: self.set_selected_index(1))
        self.selectButtons[2].clicked.connect(lambda: self.set_selected_index(2))
        self.selectButtons[3].clicked.connect(lambda: self.set_selected_index(3))
        self.selectButtons[4].clicked.connect(lambda: self.set_selected_index(4))
        self.selectButtons[5].clicked.connect(lambda: self.set_selected_index(5))
        self.selectButtons[6].clicked.connect(lambda: self.set_selected_index(6))
        self.selectButtons[7].clicked.connect(lambda: self.set_selected_index(7))
        self.selectButtons[8].clicked.connect(lambda: self.set_selected_index(8))
        self.selectButtons[9].clicked.connect(lambda: self.set_selected_index(9))
        self.selectButtons[10].clicked.connect(lambda: self.set_selected_index(10))
        self.selectButtons[11].clicked.connect(lambda: self.set_selected_index(11))
        self.selectButtons[12].clicked.connect(lambda: self.set_selected_index(12))
        self.selectButtons[13].clicked.connect(lambda: self.set_selected_index(13))
        self.selectButtons[14].clicked.connect(lambda: self.set_selected_index(14))

    def set_selected_index(self, index: int):
        self.selectedIndex = index
        # print(index)
        if self.loadedDatabase == None:
            self.textBrowser.clear()
            self.textBrowser.append("<b>[Error]</b>")
            self.textBrowser.append("There is no data to print.")
        else:
            selectedData = self.loadedDatabase[self.selectedIndex]
            self.textBrowser.clear()
            self.textBrowser.append("<b>[ID]</b>")
            self.textBrowser.append(str(selectedData["id"]))
            self.textBrowser.append("")
            self.textBrowser.append("<b>[Title]</b>")
            self.textBrowser.append(selectedData["title"])
            self.textBrowser.append("")
            self.textBrowser.append("<b>[artists]</b>")
            for artist in selectedData["artists"]:
                self.textBrowser.append(artist['display'])
            self.textBrowser.append("")
            self.textBrowser.append("<b>[groups]</b>")
            for group in selectedData["groups"]:
                self.textBrowser.append(group['display'])
            self.textBrowser.append("")
            self.textBrowser.append("<b>[parodys]</b>")
            for parody in selectedData["parodys"]:
                self.textBrowser.append(parody['display'])
            self.textBrowser.append("")
            self.textBrowser.append("<b>[characters]</b>")
            for character in selectedData["characters"]:
                self.textBrowser.append(character['display'])
            self.textBrowser.append("")
            self.textBrowser.append("<b>[tags]</b>")
            for tag in selectedData["tags"]:
                self.textBrowser.append(tag['display'])

    @pyqtSlot(int)
    def progressing(self, progress): # 진행바 설정
        self.progressBar.setValue(progress)


    @pyqtSlot(dict) # dict 타입의 인자를 받음, 스레드 처리를 위해서 추가
    def update_image(self, data):
        # print(type(self.loadedDatabase))
        for i in range(len(self.loadedDatabase)): # 당신은 len(self.thumbnailViews)를 사용했지만 그건 심각한 코드 오류이다. self.thumbnailViews는 IndexError를 만드는 주범이다.
            print(i)
            qPixmapVar = QPixmap()
            qPixmapVar.loadFromData(data[str(i)])  # 제너레이터 형식
            self.thumbnailViews[i].setPixmap(qPixmapVar.scaledToWidth(100))


    def search(self):
        try:
            # print(self.worker.isRunning())
            # print(self.worker.isFinished())
            if (self.worker.isRunning() == False and self.worker.isFinished() == True) or \
                    (self.worker.isRunning() == False and self.worker.isFinished() == False): # 스레드가 동작중일 때 중복 동작을 피하기 위해서
                self.loadedDatabase = Hiyobi.search(Hiyobi.tags_to_array(self.searchBar.text()))["list"]  # 검색어를 찾고
                self.get_data.emit(self.loadedDatabase)  # 찾은 데이터를 스레드에 보내고 (이미지 검색의 활용을 위해서)
                self.worker.start() # 스레드를 시작한다.

        except KeyError:
            self.loadedDatabase = None
            self.textBrowser.clear()
            self.textBrowser.append("<b>[Error]</b>")
            self.textBrowser.append("There is no result.")
            for i in range(len(self.thumbnailViews)):
                self.thumbnailViews[i].setPixmap(QPixmap())
        # except IndexError: #이런거 만들지 말고 왜 오류가 나왔는지 디버깅 하자 ㅠㅠㅠ
        #     self.loadedDatabase = None
        #     self.textBrowser.clear()
        #     self.textBrowser.append("<b>[Error]</b>")
        #     self.textBrowser.append("There is no result.")
        #     for i in range(len(self.thumbnailViews)):
        #         self.thumbnailViews[i].setPixmap(QPixmap())





if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
