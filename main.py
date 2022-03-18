import sys, os
import sqlite3
from PyQt5.QtWidgets import QApplication ,QWidget,QDialog,QDialogButtonBox,QVBoxLayout,QLabel
from PyQt5.uic import loadUi
import string
import random


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('layout.ui',self)
        self.createButton.clicked.connect(self.create_password)
        self.deleteButton.clicked.connect(self.delete_user)
        self.dial.valueChanged.connect(lambda: self.dial_method())
        self.alert.hide()
        self.populate_services()
        self.buscaServicio.activated.connect(lambda: self.populate_users())
        self.buscaUsuario.activated.connect(lambda: self.select_password())

    def create_password(self):
        newService = self.newService.text()
        newUser = self.newUser.text()
        chars = set(string.ascii_lowercase)
        
        if self.checkBox_upper.isChecked():
            chars.update(set(string.ascii_uppercase))
        if self.checkBox_digit.isChecked():
            chars.update(set(string.digits))
        if self.checkBox_special.isChecked():
            chars.update(set(string.punctuation))
            chars.remove('\\')  #Removes character as may create conflicts in passwords 

        charLenght = self.get_lenght_chars_dial()
        chars = list(chars)
        psw = []
        for char in range(charLenght):
            psw.append(random.choice(chars))
        newpsw = "".join((psw))

        conn = self.connect_to_db()
        cur = conn.cursor()
        query = """INSERT INTO passwords(servicio,usuario,psw) VALUES (?,?,?)"""        
        cur.execute(query,(newService,newUser,newpsw))
        conn.commit()
        conn.close()
        self.alert.setText('Nueva contraseña: {}  para Usuario: {}'.format(newpsw,newUser))
        self.alert.show()
        self.populate_services()

    def get_lenght_chars_dial(self):
        value = self.dial.value()
        if value < 20:
           charLenght = 6
        if value >= 20 and value < 40:
            charLenght = 8
        if value >= 40 and value < 60:
            charLenght = 10
        if value >= 60 and value < 80:
            charLenght = 12
        if value >= 80 and value < 100:
            charLenght = 14
        return charLenght

    def dial_method(self):
            
            # getting dial value
            charLenght = self.get_lenght_chars_dial()
            # setting text to the label
            self.label_lenghtChar.setText("Largo: {} caract.".format(str(charLenght)))
            
    

    def connect_to_db(self):
        """Connect to database"""

        conn = sqlite3.connect("passwords.sqlite")
        
        cur = conn.cursor()

        cur.execute('''
        CREATE TABLE IF NOT EXISTS passwords(servicio TEXT,
                                         usuario TEXT,
                                         psw TEXT)''')

        
        return conn

    def populate_services(self):
        self.buscaServicio.clear()
        conn = self.connect_to_db()
        query = """SELECT servicio from passwords"""
        cur = conn.cursor()
        cur.execute(query)
        services = [x[0] for x in set(cur.fetchall())]
        self.buscaServicio.addItems(services)
        conn.close()

    def populate_users(self):
        self.buscaUsuario.clear()
        service = self.buscaServicio.currentText()
        query = "SELECT usuario from passwords WHERE servicio = ?"
        print(service)
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute(query,[service])
        users = [x[0] for x in cur.fetchall()]
        self.buscaUsuario.addItems(users)
        if len(users) == 1:
            self.select_password()
        conn.close()
        
    def select_password(self):
        service = self.buscaServicio.currentText()
        user = self.buscaUsuario.currentText()
        conn = self.connect_to_db()
        cur  = conn.cursor()
        query = "SELECT psw from passwords WHERE servicio = ? AND usuario = ?"
        cur.execute(query,(service,user))
        password = cur.fetchall()[0][0]
        self.alert.setText("Tu contraseña es: {}".format(password))
        self.alert.show()

    def delete_user(self):
        service = self.buscaServicio.currentText()
        user = self.buscaUsuario.currentText()
        query = "DELETE from passwords WHERE servicio = ? AND usuario = ?".format(service,user)
        conn = self.connect_to_db()
        cur = conn.cursor()
        
        dlg = CustomDialog()

        if dlg.exec():
            cur.execute(query,(service,user))
            conn.commit()
            conn.close()
            self.alert.setText("Usuario: {} borrado con exito".format(user))
        else:
            self.alert.setText("No se realizaron cambios".format(user))
        self.populate_services()

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Borrado de datos")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Estás seguro que deseas borrar el usuario y contraseña?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())

