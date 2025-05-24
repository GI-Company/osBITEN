import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QAction, QMessageBox
from PyQt5.QtGui import QFont

class BITEIDE(QMainWindow):
    def __init__(self, filename=None):
        super().__init__()
        self.setWindowTitle("BITE IDE")
        self.text = QTextEdit()
        self.text.setFont(QFont("Fira Mono", 13))
        self.setCentralWidget(self.text)
        self.filename = filename
        self._init_menu()
        if filename:
            self._load_file(filename)

    def _init_menu(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self._open_file)
        filemenu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self._save_file)
        filemenu.addAction(save_action)

        run_action = QAction("Run", self)
        run_action.triggered.connect(self._run_file)
        filemenu.addAction(run_action)

    def _open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Code Files (*.b *.c *.py);;All Files (*)")
        if fname:
            self.filename = fname
            self._load_file(fname)

    def _load_file(self, fname):
        with open(fname) as f:
            self.text.setPlainText(f.read())
        self.setWindowTitle(f"BITE IDE - {fname}")

    def _save_file(self):
        if not self.filename:
            fname, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Code Files (*.b *.c *.py);;All Files (*)")
            if not fname:
                return
            self.filename = fname
        with open(self.filename, "w") as f:
            f.write(self.text.toPlainText())
        QMessageBox.information(self, "Saved", "File saved successfully.")

    def _run_file(self):
        from bite_compiler import run_bite
        if self.filename:
            self._save_file()
            run_bite(self.filename)
        else:
            QMessageBox.warning(self, "Error", "Save the file first.")

def launch_ide(filename=None):
    app = QApplication(sys.argv)
    ide = BITEIDE(filename)
    ide.show()
    sys.exit(app.exec_())