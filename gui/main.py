import os
import sys
import cv2
import pandas as pd

# PyQt
from PyQt5 import uic
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QHBoxLayout, QLabel, 
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QMessageBox, 
        QScrollArea, QTableView, QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange, QHeaderView, QAbstractItemView)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtCore import QDir, Qt, QUrl, QSize, QTimer, QThread, QAbstractTableModel
from PyQt5.QtGui import QIcon, QFont, QImage, QPixmap, QPalette, QPainter


class VideoThread(QThread):
    def __init__(self, videoFileName):
        super().__init__()
        self.videoFileName = videoFileName

    def run(self):
        self.cap = cv2.VideoCapture(self.videoFileName)
        (grabbed, frame) =  self.cap.read()
        fshape = frame.shape
        fheight = fshape[0]
        fwidth = fshape[1]
        outputFileName = self.videoFileName.replace('.mp4', '_result.avi')
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(outputFileName,fourcc , 20.0, (fwidth,fheight))

        while(self.cap.isOpened()):
            ret, frame = self.cap.read()
            if ret==True:
                frame = cv2.flip(frame,0)

                # write the flipped frame
                out.write(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        
        # Release everything if job is finished
        self.cap.release()
        

class MainGui(QMainWindow):
    def __init__(self):
            super(MainGui, self).__init__()
            uic.loadUi('main.ui', self)

            # IMAGE TAB
            openImageButton = self.findChild(QPushButton, 'openImageButton')
            openImageButton.setToolTip("Open Image File")
            openImageButton.setStatusTip("Open Image File")
            openImageButton.clicked.connect(self.openImageDialog)
            
            self.imageLabel = self.findChild(QLabel, 'viewImageLabel')
            self.imageLabel.setBackgroundRole(QPalette.Base)
            self.imageLabel.setScaledContents(True)

            
            # VIDEO TAB
            self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            videoWidget = self.findChild(QVideoWidget, 'videoWidget')

            openVideoButton = self.findChild(QPushButton, 'openVideoButton')  
            openVideoButton.setToolTip("Open Video File")
            openVideoButton.setStatusTip("Open Video File")
            openVideoButton.clicked.connect(self.openVideoDialog)

            self.playbutton = self.findChild(QPushButton, 'playButton')
            self.playButton.setEnabled(False)
            self.playButton.setFixedHeight(24)
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playButton.clicked.connect(self.play)

            self.positionSlider = self.findChild(QSlider, 'horizontalSlider')
            self.positionSlider.setRange(0, 0)
            self.positionSlider.sliderMoved.connect(self.setPosition)


            self.mediaPlayer.setVideoOutput(videoWidget)
            self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
            self.mediaPlayer.positionChanged.connect(self.positionChanged)
            self.mediaPlayer.durationChanged.connect(self.durationChanged)

            # Analyse Image
            self.analyseImageButton = self.findChild(QPushButton, 'analyseImageButton')
            self.analyseImageButton.setEnabled(False)
            self.analyseImageButton.clicked.connect(self.analyseImage)

            # Analyse Video
            self.analyseVideoButton = self.findChild(QPushButton, 'analyseVideoButton')
            self.analyseVideoButton.setEnabled(False)
            self.analyseVideoButton.clicked.connect(self.analyseVideo)

            # Metadata extraction
            openMetadataButton = self.findChild(QPushButton, 'openMetadataButton')
            openMetadataButton.setToolTip("Open Metadata File")
            openMetadataButton.setStatusTip("Open Metadata File")
            openMetadataButton.clicked.connect(self.openMetadataDialog)

            self.dataTableWidget = self.findChild(QTableWidget, 'dataTableWidget')
            self.dataTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.dataTableWidget.setRowCount(5)
            self.dataTableWidget.setColumnCount(2)
            self.dataTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.dataTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.dataTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
            self.dataTableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))

    # IMAGE FUNCTIONS
    def openImageDialog(self):
        options = QFileDialog.Options()
        # fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        self.imageFileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                  'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        if self.imageFileName:
            image = QImage(self.imageFileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % self.imageFileName)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0
            self.analyseImageButton.setEnabled(True)
        else:
            pass
    
    def analyseImage(self):
        self.image = cv2.imread(self.imageFileName)
        cv2.line(self.image, (0,0), (500, 1500), (0, 255, 0), thickness=10)
        qformat =QImage.Format_Indexed8
        if len(self.image.shape)==3:
            if self.image.shape[2] ==4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888
            img = QImage(self.image.data,
                self.image.shape[1],
                self.image.shape[0], 
                self.image.strides[0], # <--- +++
                qformat)
        self.image = QImage(self.image.data, self.image.shape[1], self.image.shape[0], QImage.Format_RGB888).rgbSwapped()
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))


    # VIDEO FUNCTIONS
    def openVideoDialog(self):
        self.videoFileName, _ = QFileDialog.getOpenFileName(self,"Select Media ",".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if self.videoFileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.videoFileName)))
            self.playButton.setEnabled(True)
            self.analyseVideoButton.setEnabled(True)
            self.play()
        else:
            pass


    def analyseVideo(self):
        self.analyseVideoButton.setEnabled(False)
        self.videoThread = VideoThread(self.videoFileName)
        self.videoThread.start()
        self.videoThread.finished.connect(self.onVideoThreadFinished)

    def onVideoThreadFinished(self):
        self.analyseVideoButton.setEnabled(True)
        self.resultVideoFileName = self.videoFileName.replace('.mp4', '_result.avi')
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.resultVideoFileName)))

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    # Metadata open dialog box
    def openMetadataDialog(self):
        self.csvFileName, _ = QFileDialog.getOpenFileName(self,"Select CSV ",".", "csv Files (*.csv)")

        if self.csvFileName != '':
            self.display_metadata(self.csvFileName)
        else:
            pass

    # Display extracted csv data
    def display_metadata(self, fileName):
        self.extract_metadata(fileName)
        
    
    # csv Metadata extraction
    def extract_metadata(self, fileName):
        self.data = pd.read_csv(fileName)
       


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainGui()
    window.show()
    app.exec_()