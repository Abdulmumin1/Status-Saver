from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDGridBottomSheet, MDListBottomSheet
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineAvatarListItem
from kivy.uix.screenmanager import Screen
import random
import threading
import os
import cv2

# from db_server import load_files_from_server, download_file_content, delete_record, upload_file_content,search,create_cat

KV = '''
MDScreen:
    Screen:
        id:main_screen
        MDBoxLayout:
            
            orientation:"vertical"
            MDToolbar:
                md_bg_color:app.theme_cls.bg_dark
                title:"Status Saver"
                right_action_items:[["merge", lambda x:app.show_merge_dialog()], ["refresh", lambda x:print('refresh')]]

            ScrollView:
                MDList:
                    id:box
                    cols:2
                    spacing:10

<ImageScreen>
    MDBoxLayout:
        MDLabel:
            text:"nice"
        FitImage:
            source:'/home/famira/Music/ed.png'
<MergeItem>
    ImageLeftWidget:
        source:root.source
'''


file_clicked = None
merge_list = []


class ImageScreen(Screen):
    ''


class MergeItem(OneLineAvatarListItem):
    divider = None
    source = StringProperty()


class Files(SmartTileWithLabel):
    def __init__(self, datas, image):
        super().__init__()
        self.orientation = 'vertical'
        self.size_hint_min_y = 200
        # self.md_bg_color = (.33, .33, .33, .3)
        self.radius = [6, 6, 6, 6]
        self.source = image
        # self.elevation = 10
        # self.background = '/home/famira/Music/ed.ed.png'
        # self.dialog = None
        # data_type = 'file'
        # self.file_id = datas['pk']
        self.file_name, self.file_extension = os.path.splitext(datas)
        label_text = self.file_name if len(
            self.file_name) < 11 else self.file_name[:11]+'...'
        self.text = label_text

        self.show_bottom_sheet = None
        # icon = MDIcon(icon='file' if data_type ==
        #               'file' else 'folder', halign='center')
        # icon.font_size = 50
        # label = MDLabel(text=label_text)
        # label.padding_x = 30
        # label.font_style = 'Subtitle2'
        # self.add_widget(icon)
        # self.add_widget(label)

    def on_release(self):
        global file_clicked
        file_clicked = self.file_name+self.file_extension
        app.show_list_menu()

    # def download_file(self,v=None):
    #     downloaded_text = f'{self.file_name}.{self.file_extension} downloaded'
    #     threadd = threading.Thread(target=download_file_content, args=(self.file_id, (self.file_name, self.file_extension, lambda:self.bar(downloaded_text)), self.error_f))
    #     threadd.start()
    # def error_f(self):
    #     self.bar('error downloading file. Retrying')
    #     event = Clock.schedule_once(self.download_file, 5)
    #     event()

    # def show_alert_dialog(self):
    #     if not self.dialog:
    #         self.dialog = MDDialog(
    #             title='Delete alert',
    #             text=f'do you want to delete {self.file_name}',
    #             buttons=[
    #             MDFlatButton(
    #             text="CANCEL", text_color=self.theme_cls.primary_color,on_release=self.dismiss_del_dial
    #             ),
    #             MDFlatButton(
    #             text="OK", text_color=self.theme_cls.primary_color,on_release=self.delete_file_ok
    #             ),
    #             ],
    #         )
    #         self.dialog.open()
    # def dismiss_del_dial(self,e):
    #     if self.dialog:
    #         self.dialog.dismiss()
    # def delete_file_ok(self,e):
    #     try:
    #         delete_record(self.file_id)
    #         toast('deleted')
    #         self.dialog.dismiss()
    #     except:
    #         self.dialog.dismiss()
    #         self.bar('error connecting with server')

    def bar(self, text):
        snackbar = Snackbar(
            text=text,
            snackbar_x="10dp",
            snackbar_y="10dp",)
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 2)
        ) / Window.width
        snackbar.open()


class Main(MDApp):
    # data = {
    # 'Upload':'upload',
    # 'Create folder':'folder',
    # }
    # dialog = None
    # def bar(self, text):
    #     snackbar = Snackbar(
    #     text=text,
    #     snackbar_x="10dp",
    #     snackbar_y="10dp",)
    #     snackbar.size_hint_x = (
    #     Window.width - (snackbar.snackbar_x * 2)
    #     ) / Window.width
    #     snackbar.buttons = [
    #         MDFlatButton(
    #         text="CANCEL",
    #         text_color=(1, 1, 1, 1),
    #         on_release=snackbar.dismiss,
    #         ),
    #     ]
    #     snackbar.open()
    # def calls(self, but):
    #     if but.icon == 'upload':
    #         self.fileManager()
    #     else:
    #         self.show_confirmation_dialog()
    dialog = None

    def show_merge_dialog(self):
        if not self.dialog:
            # content = self.merge_contents()
            self.dialog = MDDialog(
                title="Videos to merge:",
                type="simple",
                items=[MergeItem(text=items, source=items+'_thumbnail.jpg')
                       for items in merge_list],
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color, on_release=self.close_dial
                    ),
                    MDFlatButton(
                        text="OK", text_color=self.theme_cls.primary_color, on_release=lambda x:print('merging============')
                    ),
                ],
            )
        # print(Window.height)
        # self.dialog.size_hint_min_y = Window.height - 50
        self.dialog.open()

    def close_dial(self, event):
        self.dialog.dismiss()
        self.dialog = None

    def show_list_menu(self):
        bottom_sheet_menu = MDListBottomSheet()
        bottom_sheet_menu.radius_from = "top"
        d = 'downloading..'
        data = {
            "Add to merge list": ['merge', 'merge'],
            "Share": ["share", 'link copied'],
            "Save": ["download", d],
        }
        for item in data.items():
            bottom_sheet_menu.add_item(
                item[0],
                lambda x, y=item[1][1]: self.callback_for_menu_items(y),
                icon=item[1][0],)
        bottom_sheet_menu.open()

    def save_video(self, file):
        with open(file, 'rb') as f:
            file2 = os.path.basename(file)
            with open(file2, 'wb') as nf:
                nf.write(f.read())

    def callback_for_menu_items(self, *args):
        global file_clicked
        if args[0] == 'downloading..':
            self.save_video(self.path+'/'+file_clicked)
            file_clicked = None
        elif args[0] == 'merge':
            global merge_list
            merge_list.append(file_clicked)
        # elif args[0] == 'deleted':
        #     self.show_alert_dialog()

    # def close_dial(self,e):
    #     if self.dialog:
    #         self.dialog.dismiss()
    # def search(self):
    #     self.root.ids.box.clear_widgets()
    #     res = None
    #     try:
    #         res = search(self.root.ids.text_searcher.text)
    #     except:
    #         self.bar('error connecting with server')
    #     if res:
    #         for xfile in res[::-1]:
    #             file_widget = Files(xfile)
    #             self.root.ids.box.add_widget(file_widget)

    # def fileManager(self):
    #     path = '/storage' # path to the directory that will be opened in the file manager
    #     self.file_manager = MDFileManager(
    #     # exit_manager=self.cl,
    #     select_path=self.select_path,
    #     )
    #     self.file_manager.show(path)

    # def upload_files_func(self, upload_files):
    #     if type(upload_files) == list:
    #         for file in upload_files:
    #             self.upload_def(file)
    #     else:
    #         self.upload_def(upload_files)

    # def select_path(self, path):
    #     upload_files  = path
    #     try:
    #         thread = threading.Thread(target=self.upload_files_func,args=(upload_files,))
    #         thread.start()
    #         self.file_manager.close()
    #     except:
    #         self.file_manager.close()
    #         self.bar('error connecting with server')

    # def upload_def(self, xfile):
    #     upload = upload_file_content(xfile,error=self.upload_error)
    #     if upload:
    #         file_card = Files(upload)
    #         self.root.id.box.addWidget(file_card)
    # def upload_error(self):
    #     self.bar('error connecting with server')
    # def create_collection(self, name):
    #     try:
    #         cat =create_cat(name)
    #     except:
    #         self.bar('error connecting with server')
    #     self.dialog.dismiss()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return Builder.load_string(KV)

    def load_files(self):
        self.path = '/home/famira/Music/dyk'
        file_path = os.listdir(self.path)
        for file in file_path:

            if os.path.isfile(self.path+'/'+file):
                _, ext = os.path.splitext(file)
                if ext in ['.mp4', '.webm', '.avi']:

                    vidcap = cv2.VideoCapture(self.path+'/'+file)
                    success, image = vidcap.read()
                    thmb = file + "_thumbnail.jpg"
                    cv2.imwrite(thmb, image)
                elif ext in ['.jpg', '.JPEG', '.JPG', '.png']:
                    thmb = file + "_thumbnail.jpg"
                    cv2.imwrite(thmb, image)
                else:
                    continue
                file_widget = Files(file, thmb)
                self.root.ids.box.add_widget(file_widget)
                # await self.load_files()

    # def load_files(self,e):
    #     files = load_files_from_server()
    #     if files != 'error':
    #         for i in files[::-1]:
    #             choice = ['file', 'folder']
    #             but = Files(i)
    #             self.root.ids.box.add_widget(but)
    #     else:
    #         self.bar('error connecting with server')

    def on_start(self):
        self.load_files()


app = Main()
app.run()
