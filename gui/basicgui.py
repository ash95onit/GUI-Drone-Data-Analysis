# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'basicgui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(972, 653)
        Dialog.setFocusPolicy(QtCore.Qt.NoFocus)
        self.bLoadMedia = QtWidgets.QPushButton(Dialog)
        self.bLoadMedia.setGeometry(QtCore.QRect(20, 570, 201, 71))
        self.bLoadMedia.setObjectName("bLoadMedia")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 661, 531))
        self.label.setFrameShape(QtWidgets.QFrame.Box)
        self.label.setText("")
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setPixmap(QtGui.QPixmap("../res/audi_r8_9-wide.jpg"))
        self.label.setScaledContents(True)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.bLoadMedia.setText(_translate("Dialog", "Load Media"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
