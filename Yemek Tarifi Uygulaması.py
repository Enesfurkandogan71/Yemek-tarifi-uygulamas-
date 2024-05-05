import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTextEdit, QListWidget, QDialog, QDialogButtonBox, QSlider
import sqlite3

class TarifUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Yemek Tarifi Uygulaması")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.label = QLabel("Tarif Adı:")
        self.layout.addWidget(self.label)

        self.tarif_adi_input = QTextEdit()
        self.layout.addWidget(self.tarif_adi_input)

        self.label_malzemeler = QLabel("Malzemeler:")
        self.layout.addWidget(self.label_malzemeler)

        self.malzemeler_input = QTextEdit()
        self.layout.addWidget(self.malzemeler_input)

        self.label_tarif = QLabel("Tarif:")
        self.layout.addWidget(self.label_tarif)

        self.tarif_input = QTextEdit()
        self.layout.addWidget(self.tarif_input)

        self.button_kaydet = QPushButton("Tarifi Kaydet")
        self.button_kaydet.clicked.connect(self.tarif_kaydet)
        self.layout.addWidget(self.button_kaydet)

        self.button_ara = QPushButton("Tarif Ara")
        self.button_ara.clicked.connect(self.open_tarif_ara)
        self.layout.addWidget(self.button_ara)

        self.button_degerlendir = QPushButton("Tarifi Değerlendir")
        self.button_degerlendir.clicked.connect(self.open_tarif_degerlendir)
        self.layout.addWidget(self.button_degerlendir)

        self.central_widget.setLayout(self.layout)

        # SQLite veritabanı bağlantısı
        self.conn = sqlite3.connect('tarifler.db')
        self.c = self.conn.cursor()

        # Tarifler tablosunu oluştur
        self.c.execute('''CREATE TABLE IF NOT EXISTS tarifler
                          (tarif_adi TEXT, malzemeler TEXT, tarif TEXT, puan INTEGER)''')
        self.conn.commit()

    def tarif_kaydet(self):
        tarif_adi = self.tarif_adi_input.toPlainText()
        malzemeler = self.malzemeler_input.toPlainText()
        tarif = self.tarif_input.toPlainText()

        # Tarifi veritabanına ekle
        self.c.execute("INSERT INTO tarifler (tarif_adi, malzemeler, tarif, puan) VALUES (?, ?, ?, ?)",
                       (tarif_adi, malzemeler, tarif, 0))  # Başlangıçta puan 0 olacak
        self.conn.commit()

        print("Tarif kaydedildi!")
        self.clear_inputs()

    def open_tarif_ara(self):
        self.ara_window = TarifAramaWindow(self.conn)
        self.ara_window.show()

    def open_tarif_degerlendir(self):
        self.degerlendir_window = TarifDegerlendirWindow(self.conn)
        self.degerlendir_window.exec_()  # exec_() kullanarak pencerenin modal olarak açılmasını sağlayalım

    def clear_inputs(self):
        self.tarif_adi_input.clear()
        self.malzemeler_input.clear()
        self.tarif_input.clear()

class TarifAramaWindow(QDialog):
    def __init__(self, conn):
        super().__init__()

        self.setWindowTitle("Tarif Ara")
        self.setGeometry(200, 200, 400, 200)

        self.conn = conn
        self.c = self.conn.cursor()

        layout = QVBoxLayout()

        label = QLabel("Aranacak Tarif:")
        layout.addWidget(label)

        self.search_input = QTextEdit()
        layout.addWidget(self.search_input)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.puan_label = QLabel("")
        layout.addWidget(self.puan_label)

        button_ara = QPushButton("Ara")
        button_ara.clicked.connect(self.ara)
        layout.addWidget(button_ara)

        # Kaydedilen tariflerin listesi
        self.list_widget = QListWidget()
        self.update_recipe_list()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def ara(self):
        search_query = self.search_input.toPlainText()

        # Aranan tarifin listemizde olup olmadığını kontrol edelim
        self.c.execute("SELECT * FROM tarifler WHERE tarif_adi LIKE ?", ('%' + search_query + '%',))
        result = self.c.fetchone()

        if result:
            self.result_label.setText("Aranan Tarif: " + result[0])
            self.puan_label.setText("Değerlendirme Puanı: " + str(result[3]))
        else:
            self.result_label.setText("Aranan Tarif: Bulunamadı")
            self.puan_label.setText("Değerlendirme Puanı: -")

    def update_recipe_list(self):
        self.list_widget.clear()
        self.c.execute("SELECT tarif_adi FROM tarifler")
        recipes = self.c.fetchall()
        for recipe in recipes:
            self.list_widget.addItem(recipe[0])

class TarifDegerlendirWindow(QDialog):
    def __init__(self, conn):
        super().__init__()

        self.setWindowTitle("Tarifi Değerlendir")
        self.setGeometry(200, 200, 400, 200)

        self.conn = conn
        self.c = self.conn.cursor()

        layout = QVBoxLayout()

        label = QLabel("Değerlendirilecek Tarif:")
        layout.addWidget(label)

        self.degerlendir_input = QTextEdit()
        layout.addWidget(self.degerlendir_input)

        self.slider_label = QLabel("Puan: 5")
        layout.addWidget(self.slider_label)

        self.slider = QSlider()
        self.slider.setOrientation(1)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(5)
        self.slider.valueChanged.connect(self.slider_changed)
        layout.addWidget(self.slider)

        button_degerlendir = QPushButton("Değerlendir")
        button_degerlendir.clicked.connect(self.degerlendir)
        layout.addWidget(button_degerlendir)

        # Kaydedilen tariflerin listesi
        self.list_widget = QListWidget()
        self.update_recipe_list()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def slider_changed(self):
        value = self.slider.value()
        self.slider_label.setText("Puan: " + str(value))

    def degerlendir(self):
        degerlendirme = self.degerlendir_input.toPlainText()
        puan = self.slider.value()

        selected_recipe = self.list_widget.currentItem().text()

        # Tarifin puanını güncelle
        self.c.execute("UPDATE tarifler SET puan = ? WHERE tarif_adi = ?", (puan, selected_recipe))
        self.conn.commit()

        self.accept()  # Pencereyi kapat

    def update_recipe_list(self):
        self.list_widget.clear()
        self.c.execute("SELECT tarif_adi FROM tarifler")
        recipes = self.c.fetchall()
        for recipe in recipes:
            self.list_widget.addItem(recipe[0])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TarifUygulamasi()
    window.show()
    sys.exit(app.exec_())
