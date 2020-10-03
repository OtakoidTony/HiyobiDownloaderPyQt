import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import json
import requests
import urllib.request

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


class WindowClass(QMainWindow, form_class):

    def __init__(self):
        super().__init__()

        self.selectedIndex = None
        self.loadedDatabase = None

        self.setupUi(self)

        self.progressBar.reset()

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

        # for i in range(15):
        #     print("self.selectButtons[%d].clicked.connect(lambda: self.set_selected_index(%d))" % (i, i))

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
        print(index)
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
            self.textBrowser.append("")
            self.textBrowser.append("<b>[groups]</b>")
            self.textBrowser.append("")
            self.textBrowser.append("<b>[parodys]</b>")
            self.textBrowser.append("")
            self.textBrowser.append("<b>[characters]</b>")
            self.textBrowser.append("")
            self.textBrowser.append("<b>[tags]</b>")


    def search(self):
        try:
            self.loadedDatabase = Hiyobi.search(Hiyobi.tags_to_array(self.searchBar.text()))["list"]
            for i in range(len(self.thumbnailViews)):
                print(i)
                qPixmapVar = QPixmap()
                qPixmapVar.loadFromData(urllib.request.urlopen(
                    urllib.request.Request(Hiyobi.get_cover_image_url(self.loadedDatabase[i]['id']),
                                           headers={'User-Agent': 'Mozilla/5.0'})).read())
                self.thumbnailViews[i].setPixmap(qPixmapVar.scaledToWidth(100))
            print(self.loadedDatabase)
        except KeyError:
            self.loadedDatabase = None
            self.textBrowser.clear()
            self.textBrowser.append("<b>[Error]</b>")
            self.textBrowser.append("There is no result.")
            for i in range(len(self.thumbnailViews)):
                self.thumbnailViews[i].setPixmap(QPixmap())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
