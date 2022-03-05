from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
# from kivymd.uix.card import MDCard
# from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
# from kivymd.uix.filemanager import MDFileManager
# from kivymd.uix.label import MDLabel, MDIcon
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDGridBottomSheet, MDListBottomSheet
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineAvatarListItem
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from datetime import datetime

import time
import threading
import os
import cv2

# from db_server import load_files_from_server, download_file_content, delete_record, upload_file_content,search,create_cat

from utils import check_for_thumbnail, verify_video, create_merge_actions, create_file_action
KV = '''
MDScreen:
    ScreenManager:
        id:screen_manager
        Screen:
            name:"main-screen"
            id:main_screen
            MDBoxLayout:

                orientation:"vertical"
                MDToolbar:
                    md_bg_color:app.theme_cls.bg_dark
                    title:"Status Saver"
                    right_action_items:[["merge", lambda x:app.show_merge_dialog()], ["refresh", lambda x:app.refresh()]]

                ScrollView:
                    MDList:
                        id:box
                        cols:2
                        spacing:10

<ImageScreen>
    MDBoxLayout:
        orientation:"vertical"
        MDIconButton:
            id:back
            icon:"keyboard-backspace"
            on_release:app.back_to_homescreen()
        Image:
            id:image
            source:root.image_tb
        MDBoxLayout:
            size_hint_max_y:60
            padding:10
            MDIconButton:
                id:share
                icon:"share"
                on_release:app.play_video()
            MDSeparator:
            MDIconButton:
                id:save
                icon:"download"
                on_release:app.save_video()
            MDSeparator:
            MDIconButton:
                id:merge
                icon:"merge"
                on_release:app.add_to_mergelist()


<MergeItem>
    ImageLeftWidget:
        source:root.source
'''


file_clicked = None
file_clicked_thumbnail = None
merge_list = []
ongoing_merge = False
remove_merge_list = set()


class ImageScreen(Screen):
    image_tb = StringProperty()


class MergeItem(OneLineAvatarListItem):
    divider = None
    source = StringProperty()


class Files(SmartTileWithLabel):
    def __init__(self, datas, image, duration=None):
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
            self.file_name) < 31 else self.file_name[:31]+'...'
        duration = duration
        self.text = f"[size=18][color=#ffffff]{label_text}[/color][/size]"
        if duration:
            self.text += "\n[size=14]{}[/size]".format(duration)

        # icon = MDIcon(icon='file' if data_type ==
        #               'file' else 'folder', halign='center')
        # icon.font_size = 50
        # label = MDLabel(text=label_text)
        # label.padding_x = 30
        # label.font_style = 'Subtitle2'
        # self.add_widget(icon)
        # self.add_widget(label)

    def on_release(self):
        global file_clicked, file_clicked_thumbnail
        file_clicked = self.file_name+self.file_extension
        file_clicked_thumbnail = self.source
        app.show_list_menu()

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


class Main(MDApp):
    # data = {
    # 'Upload':'upload',
    # 'Create folder':'folder',
    # }
    # dialog = None
    def bar(self, text):
        snackbar = Snackbar(
            text=text,
            snackbar_x="10dp",
            snackbar_y="10dp",)
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 2)
        ) / Window.width
        # snackbar.buttons = [
        #     MDFlatButton(
        #         text="CANCEL",
        #         text_color=(1, 1, 1, 1),
        #         on_release=snackbar.dismiss,
        #     ),
        # ]
        snackbar.open()
    # def calls(self, but):
    #     if but.icon == 'upload':
    #         self.fileManager()
    #     else:
    #         self.show_confirmation_dialog()
    dialog = None

    def show_merge_dialog(self):
        # if there is an ongoing merge reject other merge
        if not merge_list:
            self.bar('Please select videos to merge')
            return
        if ongoing_merge:
            self.bar('There is an ongoing merge. Please wait')
            return

        # if the merge list is empty don't show dialog

        if not self.dialog:
            # content = self.merge_contents()
            self.dialog = MDDialog(
                title="Videos to merge:",
                type="simple",
                items=[MergeItem(text=items, source=os.path.join(self.thumbnail_path, items+'_thumbnail.jpg'))
                       for items in merge_list],
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color, on_release=self.close_dial
                    ),
                    MDFlatButton(
                        text="OK", text_color=self.theme_cls.primary_color, on_release=lambda x:self.merge_action()
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
        _, ext = os.path.splitext(file_clicked)
        merge_action = create_merge_actions(merge_list, file_clicked)
        # either play video or view image
        file_actions = create_file_action(file_clicked)

        data = {
            file_actions[0]: [file_actions[1], file_actions[2]],
            merge_action[0]: [merge_action[1], merge_action[2]],
            "Share": ["share", 'link copied'],
            "Save": ["download", d],
        }

        for item in data.items():
            bottom_sheet_menu.add_item(
                item[0],
                lambda x, y=item[1][1]: self.callback_for_menu_items(y),
                icon=item[1][0],)
        bottom_sheet_menu.open()

    def save_video(self):
        file = os.path.join(self.path, file_clicked)
        with open(file, 'rb') as f:
            _, ext = os.path.splitext(os.path.basename(file))
            with open(os.path.join(self.my_parent_folder, "VID-"+str(datetime.now())+ext), 'wb') as nf:
                nf.write(f.read())
            self.bar('File saved')

    def callback_for_menu_items(self, *args):
        global file_clicked
        if args[0] == 'downloading..':
            self.save_video()
            file_clicked = None
        elif args[0] == 'merge':
            self.add_to_mergelist()
        elif args[0] == 'remove':
            merge_list.remove(file_clicked)
        elif args[0] in ('play-video', 'view-image'):
            self.change_screen()

    def add_to_mergelist(self):
        global merge_list
        # file, ext = os.path.splitext(file_clicked)
        if not verify_video(file_clicked):
            toast('Please select a video file')
            return
        if file_clicked not in merge_list:
            merge_list.append(file_clicked) if len(
                merge_list) < 11 else toast('max reached')

    def merge_action(self):
        if len(merge_list) < 2:
            self.close_dial('event')
            toast('requires two or more videos')
            return
        files = [os.path.join(self.path, f) for f in merge_list]
        thread = threading.Thread(target=self.merge_thread, args=(files,))
        thread.start()
        self.close_dial('event')
        self.bar('merging in progress..')
        global ongoing_merge
        ongoing_merge = True

    def merge_thread(self, files):

        from utils import merge_videos
        merge_videos(files, 'VID_'+str(datetime.now()) +
                     '.mp4', "compose", self.bar)
        # set the flag for ongoing merge to False to allow other merges
        global ongoing_merge, merge_list
        ongoing_merge = False
        merge_list = []

        # merge_videos(files, )

        # elif args[0] == 'deleted':
        #     self.show_alert_dialog()

    def load_files(self):
        self.path = '/home/famira/Music/test_datas'
        self.thumbnail_path = 'thumbnails'
        if platform == "android":
            pass
        file_path = os.listdir(self.path)
        for file in file_path:

            if os.path.isfile(self.path+'/'+file):

                # check if thumbnail already created
                thmb = check_for_thumbnail(file, self.thumbnail_path)
                if not thmb:
                    # create thumbnail if it not available
                    thmb = self.create_thumbnail(file)
                if not thmb:
                    continue
                duration = None
                if verify_video(file):
                    duration = self.get_vid_duration(file)
                file_widget = Files(file, thmb, duration)
                self.root.ids.box.add_widget(file_widget)

    def create_thumbnail(self, file):
        _, ext = os.path.splitext(file)
        if verify_video(file):
            vidcap = cv2.VideoCapture(os.path.join(self.path, file))
            success, image = vidcap.read()
            thmb = os.path.join(self.thumbnail_path, file + "_thumbnail.jpg")
            cv2.imwrite(thmb, image)

            # return duration and thumbnail for video

            return thmb
        elif ext in ['.jpg', '.JPEG', '.JPG', '.png']:
            # thmb = file + "_thumbnail"+ext
            # with open(thmb, 'wb') as new:
            #     with open(os.path.join(self.path, file), 'rb') as old:
            #         new.write(old.read())
            thmb = os.path.join(self.path, file)
            return thmb

        return False

    def get_vid_duration(self, vid):
        vidcap = cv2.VideoCapture(os.path.join(self.path, vid))
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        frame_count = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = str(frame_count/fps)
        l = duration.split('.')
        duration = f'{l[0]}:{l[1][:2]}'
        return duration

        # await self.load_files()

    def load_video(self, image, *args):

        _, frame = self.capture.read(self.count)
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        image.texture = texture
        self.count += 1
        print(self.count)

    def change_screen(self):
        if verify_video(file_clicked):
            toast("Can't play video at the moment")
            return
        s = ImageScreen()
        s.image_tb = file_clicked_thumbnail
        s.name = "image"
        sm = self.root.ids.screen_manager
        sm.add_widget(s)
        sm.current = 'image'
        # if verify_video(file_clicked):
        # self.capture = cv2.VideoCapture(
        #     os.path.join(self.path, file_clicked))
        # self.count = 0
        # Clock.schedule_interval(
        #     lambda x: self.load_video(s), 1.0/30.0)

    def back_to_homescreen(self):
        sm = self.root.ids.screen_manager
        sm.remove_widget(sm.get_screen('image'))
        sm.current = "main-screen"

    def refresh(self):
        self.root.ids.box.clear_widgets()
        self.on_start()

    def load_ui(self):
        time.sleep(1)
        self.load_files()

    def on_start(self):

        thread = threading.Thread(target=self.load_ui)
        thread.start()

    def build(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permissions
            from android.storage import primary_external_storage_path
            request_permissions(
                [Permissions.READ_EXTERNAL_STORAGE, Permissions.WRITE_EXTERNAL_STORAGE])
            sdcard = primary_external_storage_path()
            self.path = os.path.join(sdcard, "WhatsApp/Media/.Statuses")
            self.my_parent_folder = os.path.join(sdcard, "Status-Saver")
            os.path.mkdirs(self.my_parent_folder)
            self.thumbnail_path = os.path.join(
                self.my_parent_folder, '.thumbnails')
            os.path.mkdirs(self.thumbnail_path)

        self.theme_cls.theme_style = 'Dark'
        return Builder.load_string(KV)


# Window.size = (400, 1280)
app = Main()
# asyncio.run(app.on_start())
app.run()
