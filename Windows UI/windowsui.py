from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QStackedWidget, QMessageBox, QListWidget, QHBoxLayout, QInputDialog
from PyQt6.QtCore import Qt
import requests
import json
import time
import os
import threading
import sys
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        
        if 'token' in self.config and self.validate_token(self.config['token']):
            self.switch_to_home()
        else:
            self.token_input = QLineEdit()
            self.token_input.setPlaceholderText("Enter your token")
            
            self.token_button = QPushButton("Submit")
            self.token_button.clicked.connect(self.validate_token)
            
            self.layout = QVBoxLayout()
            self.layout.addWidget(self.token_input)
            self.layout.addWidget(self.token_button)
            
            self.container = QWidget()
            self.container.setLayout(self.layout)
            
            self.setCentralWidget(self.container)
    
    def validate_token(self, token=None):
        if token is None:
            self.token = self.token_input.text().strip()
        else:
            self.token = token

        response = requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': self.token})
        if response.status_code == 200:
            self.config['token'] = self.token
            self.save_config()
            self.switch_to_home()
            return True
        else:
            if token is not None:
                QMessageBox.critical(self, "Invalid Token", "The token in the configuration file is incorrect.")
            else:
                QMessageBox.critical(self, "Invalid Token", "The token you entered is incorrect.")
            return False
    
    def switch_to_home(self):
        self.home_page = HomePage(self.config, self.save_config)
        self.setCentralWidget(self.home_page)
    
    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json') as f:
                return json.load(f)
        else:
            return {}
    
    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

class HomePage(QWidget):
    def __init__(self, config, save_config_callback):
        super().__init__()
        self.config = config
        self.save_config = save_config_callback

        self.pages = QStackedWidget()
        self.pages.addWidget(QLabel("Home Page"))
        
        self.advertiser_page = AdvertiserPage(self.config, self.save_config)
        self.pages.addWidget(self.advertiser_page)
        
        self.nav = QListWidget()
        self.nav.insertItem(0, "Home")
        self.nav.insertItem(1, "Advertiser")
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        
        self.nav.setFixedWidth(100)
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.nav)
        self.layout.addWidget(self.pages)
        
        self.setLayout(self.layout)

class AdvertiserPage(QWidget):
    def __init__(self, config, save_config_callback):
        super().__init__()
        self.config = config
        self.save_config = save_config_callback

        self.layout = QVBoxLayout()
        
        self.start_button = QPushButton("Start Advertising")
        self.start_button.clicked.connect(self.start_advertising)
        self.layout.addWidget(self.start_button)
        
        self.add_channel_button = QPushButton("Add Channel")
        self.add_channel_button.clicked.connect(lambda: self.modify_channels('add'))
        self.layout.addWidget(self.add_channel_button)
        
        self.remove_channel_button = QPushButton("Remove Channel")
        self.remove_channel_button.clicked.connect(lambda: self.modify_channels('remove'))
        self.layout.addWidget(self.remove_channel_button)
        
        self.change_message_button = QPushButton("Change Message")
        self.change_message_button.clicked.connect(self.change_message)
        self.layout.addWidget(self.change_message_button)
        
        self.change_delay_button = QPushButton("Change Delay")
        self.change_delay_button.clicked.connect(self.change_delay)
        self.layout.addWidget(self.change_delay_button)
        
        self.setLayout(self.layout)
    
    def start_advertising(self):
        threading.Thread(target=self.send_message).start()
    
    def send_message(self):
        while True:
            channels = self.config.get('channels', [])
            for channel in channels:
                if self.config.get('repeatBypass') == 'y':
                    repeatBypass = str(random.randint(752491546761342621526, 7834345876325483756245232875362457316274977135724691581387))
                    requests.post(f'https://discord.com/api/v10/channels/{channel}/messages', headers={'Authorization': self.config['token']}, json={'content': self.config['message']+'\n\n'+repeatBypass})
                else:
                    requests.post(f'https://discord.com/api/v10/channels/{channel}/messages', headers={'Authorization': self.config['token']}, json={'content': self.config['message']})
                time.sleep(int(self.config['delay']))
            time.sleep(int(self.config['delay']))
    
    def modify_channels(self, operation):
        channel, ok = QInputDialog.getText(self, "Channel ID", "Enter channel ID:")
        if ok and channel:
            if operation == 'add':
                self.config['channels'].append(channel)
            elif operation == 'remove' and channel in self.config['channels']:
                self.config['channels'].remove(channel)
            self.save_config()
    
    def change_message(self):
        message, ok = QInputDialog.getText(self, "Message", "Enter your message:")
        if ok:
            self.config['message'] = message
            self.save_config()
    
    def change_delay(self):
        delay, ok = QInputDialog.getInt(self, "Delay", "Enter your delay (in seconds):")
        if ok:
            self.config['delay'] = str(delay)
            self.save_config()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()