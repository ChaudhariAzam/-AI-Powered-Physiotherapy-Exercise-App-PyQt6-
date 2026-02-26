from PyQt6.QtCore import Qt, QSize, QUrl,QThread,QPropertyAnimation,QEasingCurve,QRect,QTimer
from PyQt6.QtGui import QPixmap,QColor,QIcon,QPainter
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow, QWidget,  QSizePolicy, QGridLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QMessageBox, QDialog, QGraphicsDropShadowEffect, QScrollArea, QGraphicsOpacityEffect
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
import os
# os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import sys
import requests
from modules import CaptureCameraFramesWorker 
from modules import LoginDialog
from modules import videoApi
from modules import CircularProgressBar
from modules import TextToSpeechThread
from modules import estimate_motion
from modules import exercise


class BackgroundWidget(QWidget):
    def __init__(self, imagePath, parent=None):
        super().__init__(parent)
        self.backgroundPixmap = QPixmap(imagePath)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.backgroundPixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding))

class SimplifiedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Final window setup
        self.setWindowTitle("Physiotherapy App")
        # self.setMinimumSize(800, 600)  # Adjust the size as needed  # Set the window title
        mainlogo_path=self.resource_path("media/mainLogo.png")
        self.setWindowIcon(QIcon(mainlogo_path))
        self.cam=0
        self.loading_running=False
        self.camerasignal_connected=False
        self.selected_video=""
        window_background=self.resource_path("media/background.png")
        # Styles
        widget_style = """
            QWidget {
                background-color: #B0CCB0;
                border: 1px solid #000;
                border-radius: 5px
            }
        """
        main_window_style = f"""
            QMainWindow {{
                background-color: #ebf2ed;
                background-image: url({window_background});
            }}
            QMainWindow QAbstractItemView {{
                
                }}
            QLabel {{
                font-size: 18px;
                color: #333333;
                margin-bottom: 5px;
            }}
            QPushButton {{
                padding: 5px 10px;
                color: #333333;
                background-color: #5dc267;
                border: 3px solid transparent;
                border-radius: 5px; /* approximating the corner size */
                outline: none;
            }}
            QPushButton:hover {{
                background-color: #0b6414;
            }}
            QLineEdit:focus {{
                border-color: #5dc267;
            }}
            QPushButton:pressed {{
                background-color: #156e1e;
            }}
        """
        button_style_a=f"""QPushButton {{
                padding: 5px 10px;
                color: #333333;
                background-color: #5dc267;
                border: 3px solid transparent;
                border-radius: 5px; /* approximating the corner size */
                outline: none;
            }}
            QPushButton:hover {{
                background-color: #0b6414;
            }}
            QLineEdit:focus {{
                border-color: #5dc267;
            }}
            QPushButton:pressed {{
                background-color: #156e1e;
            }}
        """
        # self.initialDropDown()
        self.player = QMediaPlayer()
        # self.player.setMuted(True)
        self.player.setPlaybackRate(0.8)

        # Initialize all your labels and controls first
        self.widget_init()
        
        # Apply styles
        self.apply_styles(widget_style, main_window_style)

        #QVideoPlayer widget initialization
        self.video_widget(widget_style)

        # Create and set layouts
        self.setup_layouts(button_style_a)
        
        self.tutorialSetup()

        self.setup_ui_elements()  # Assuming this is defined elsewhere

        self.page2()

        self.stackedWidgets.setCurrentIndex(1)


    def tutorialSetup(self):
        # Create a label for the image
        self.chat_label = QLabel(self)
        chatlabel_path=self.resource_path("media/chatBox.png")
        self.chat_label.setPixmap(QPixmap(chatlabel_path))
        self.chat_label.setScaledContents(True)
        self.chat_label.setMaximumSize(700,700)
        # self.chat_label.setGeometry(QRect(200, 300, 50, 50))
  
        # Create an opacity effect for the image_label and set initial opacity to 0
        self.opacity_effect_chat = QGraphicsOpacityEffect(self.chat_label)
        self.opacity_effect_chat.setOpacity(0.0)  # Initial opacity set to 0 (fully transparent)
        self.chat_label.setGraphicsEffect(self.opacity_effect_chat)

        # Create the fade-in animation
        self.fade_in_chat = QPropertyAnimation(self.opacity_effect_chat, b"opacity")
        self.fade_in_chat.setDuration(2000)  # Duration in milliseconds
        self.fade_in_chat.setStartValue(0.0)  # Start fully transparent
        self.fade_in_chat.setEndValue(1.0)  # End fully opaque
        self.fade_in_chat.setEasingCurve(QEasingCurve.Type.InOutQuad)
        # self.fade_in_chat.start()

        self.delay_timer_chat = QTimer(self)
        self.delay_timer_chat.setSingleShot(True)
        self.delay_timer_chat.timeout.connect(self.startGrowAni_chat)
        self.delay_timer_chat.start(2000)
        
        # Create a label for the image
        self.image_label = QLabel(self)
        imagelabel_path=self.resource_path("media/apple.png")
        self.image_label.setPixmap(QPixmap(imagelabel_path))
        # self.image_label.setScaledContents(True)

        # # Create an opacity effect for the image_label
        # self.opacity_effect = QGraphicsOpacityEffect(self.image_label)
        # self.image_label.setGraphicsEffect(self.opacity_effect)

        # Create an opacity effect for the image_label and set initial opacity to 0
        self.opacity_effect = QGraphicsOpacityEffect(self.image_label)
        self.opacity_effect.setOpacity(0.0)  # Initial opacity set to 0 (fully transparent)
        self.image_label.setGraphicsEffect(self.opacity_effect)
        
        # Set initial size to (0, 0)
        self.image_label.setGeometry(150, 150, 0, 0)

        # Set up the grow animation
        self.grow_animation = QPropertyAnimation(self.image_label, b"geometry")
        self.grow_animation.setDuration(1000)  # Duration in milliseconds (2000 ms = 2 seconds)
        self.grow_animation.setStartValue(QRect(0, 0, 0, 0))  # Start from a small size
        self.grow_animation.setEndValue(QRect(200, 300, 250, 250)) 

        # Create the fade-in animation
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(2000)  # Duration in milliseconds
        self.fade_in.setStartValue(0.0)  # Start fully transparent
        self.fade_in.setEndValue(1.0)  # End fully opaque
        self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
        # self.fade_in.start()


        self.delay_timer = QTimer(self)
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self.startGrowAni)
        self.delay_timer.start(1000)
        
        # Create ComboBox
        self.tut_combo_box = QComboBox()

        # Set size policy to expand
        self.tut_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.downarrow_path=self.resource_path("media/down_arrow_white.png")
        self.uparrow_path=self.resource_path("media/up_arrow_white.png")

        stylesheet1=f"""
            QComboBox {{
                color: white;
                background-color: rgba(34,36,31,0.7); /* Set background color */
                
                font-family: 'Sitka Text Semibold';
                border: 2px solid gray;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                font-size: 14pt;     /* Large font size */
                min-height: 100px;   /* Substantial height */
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            QComboBox::down-arrow {{
                
                image: url({self.downarrow_path});
                width: 40px;
                height: 30px;
            }}
                                        

            QComboBox::down-arrow:on {{ /* when the combo box is open */
            image: url({self.uparrow_path});
                                        }}
                                        
            QComboBox:hover {{
                border: 2px  solid teal;  
            }}
            QComboBox:focus {{
                border: 2px solid green;   
            }}
            QComboBox QAbstractItemView {{
                background-color: #171717;
                outline: none;
                border-radius: 10px;  /* Rounded corners for the drop-down */
                /* Other QAbstractItemView styles... */
            }}
            QComboBox QAbstractItemView::item {{
                
                padding: 10px;
                color: white;
                
                border-bottom: 1px solid gray; /* Add a border to the bottom of each item */
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: rgba(93, 194, 103, 0.7);
                
            }}
        """
        # Adjust font size and height of the combo box
        self.tut_combo_box.setStyleSheet(stylesheet1)

        self.init_populate_video_list()
        
        # Create Button
        button = QPushButton("READY!")
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)
        shadow_effect.setXOffset(3)
        shadow_effect.setYOffset(3)
        button.setGraphicsEffect(shadow_effect)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(93, 194, 103, 0.9); /* Semi-transparent version of #5dc267 */
                border: 1px solid #5dc267; /* Border with the shade #5dc267 */
                border-radius: 15px; /* Rounded corners */
                color: black; /* Text color */
                font-size: 16pt;
                min-height: 100px;
                min-width: 200px;
                
            }
            QPushButton:hover {
                background-color: rgba(93, 194, 103, 0.7); /* Darker on hover */
                
            }
            
        """)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.clicked.connect(self.widgetindexchanged)
        # Create horizontal layout for Button and add it
        hbox_button = QHBoxLayout()
        hbox_button.addWidget(self.tut_combo_box)
        hbox_button.addWidget(button)
        hbox_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        tutbackground_path=self.resource_path("media/background.png")
        # Create a background widget
        self.tutorial = BackgroundWidget(tutbackground_path)


        self.tutorial.setMinimumSize(1100, 800)
        # Create layout
        layout = QVBoxLayout(self.tutorial)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        
        # Add ComboBox to layout
        hbox_labels = QHBoxLayout()
        hbox_labels.addWidget(self.image_label)
        hbox_labels.addWidget(self.chat_label)
        hbox_labels.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # layout.addWidget(self.tut_combo_box)
        layout.addLayout(hbox_button)
        layout.addLayout(hbox_labels)

        # self.image_label.raise_()  # Ensure the label is on top
        # self.chat_label.raise_()

        self.stackedWidgets.addWidget(self.tutorial)
        
        # Set window size
        # self.resize(800, 600)  # Adjust window size as needed

    def startGrowAni(self):
        self.fade_in.start()
        self.grow_animation.start()
    def startGrowAni_chat(self):
        self.fade_in_chat.start()
        tut_text="WELCOME TO THE AI-SUPPORTED, EXERCISE APP, PLEASE SELECT AN EXERCISE YOU WOULD LIKE TO PERFORM"
        self.textToSpeech(tut_text)
        # self.grow_animation_chat.start()

    def init_populate_video_list(self):
        self.init_rs = videoApi._neutriApiCall(self)

        self.init_neutriPlayList=self.init_rs[0] #Gettung the exercise name
        self.init_playItemList = ['Select exercise']+ [f"{exercise}" for exercise in self.init_neutriPlayList.values()]
        # This list can be hardcoded, or you could retrieve it from a directory of video files.
        video_list = ['Select Exercise', 'Bhuj Bandh', 'Bhuja Valli Sakthi Vikasaka','Jaanu Shakti Kriya','Bhuja Shakti Yoga','Kartal Karprasth', 'Kaphoni Shakti']   # Example list
        self.tut_combo_box.addItems(video_list)
        print(self.init_playItemList)

    def widgetindexchanged(self):
        
        self.stackedWidgets.setCurrentIndex(2)
        self.page2widget.hide()
        self.image_label.deleteLater()
        self.chat_label.deleteLater()
        self.current_index_page1 = self.tut_combo_box.currentIndex()
        video=  self.resource_path(f"media/{self.tut_combo_box.itemText(self.current_index_page1)}.mp4")
        print(video)
        self.mediaPlayer_tut.setSource(QUrl.fromLocalFile(video))
        # self.mediaPlayer_tut.setPosition(0)
        self.mediaPlayer_tut.play()
        self.mediaPlayer_tut.mediaStatusChanged.connect(self.on_media_status_changed_tut)
        self.exercise_details_tut(self.tut_combo_box.itemText(self.current_index_page1))
        delay_timer = QTimer(self)
        delay_timer.setSingleShot(True)
        delay_timer.timeout.connect(self.page2widget.show)
        delay_timer.start(100)
        
        



#---------------------------------------------PAGE 2 NEXT TO TUTORIAL---------------------------------------------------------------------------

    def fvideo_widget_tut(self):
        # Create an instance of QMediaPlayer
        self.mediaPlayer_tut = QMediaPlayer()
        # self.mediaPlayer_tut.setMuted(bool muted)
        self.mediaPlayer_tut.setPlaybackRate(0.8)
        # Create an instance of QVideoWidget
        self.videoWidget_tut = QVideoWidget()
        # Set QVideoWidget as the video output for QMediaPlayer
        self.mediaPlayer_tut.setVideoOutput(self.videoWidget_tut)
        # self.videoWidget.hide()

        # Create a parent widget and layout
        self.page2videowidget = QWidget()
        min_widget_size = QSize(500, 200)
        self.page2videowidget.setMinimumSize(min_widget_size)
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.page2videowidget.setSizePolicy(size_policy)
        
        widget_style = """
            QWidget {
                background-color: rgba(130, 220, 140, 0.8);
                border: 1px solid #000;
                border-radius: 5px
            }
        """
        layout_video=QVBoxLayout()
        layout_video.addWidget(self.videoWidget_tut)
        self.page2videowidget.setStyleSheet(widget_style)
        # layout = QVBoxLayout(self.scroll_video_widget)
        self.page2videowidget.setLayout(layout_video)   # Add the QVideoWidget
        

    def page2(self):

        self.page2widget = QWidget()
        self.page2widget.setStyleSheet("""
            QWidget {
                background-color: #B0CCB0;
                border: 1px solid #000;
                border-radius: 5px
            }
        """)

        self.fvideo_widget_tut()

        page2_button = QPushButton("Start Doing Exercise!")
        page2_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(93, 194, 103, 0.9); /* Semi-transparent version of #5dc267 */
                border: 1px solid #5dc267; /* Border with the shade #5dc267 */
                border-radius: 15px; /* Rounded corners */
                color: black; /* Text color */
                font-size: 16pt;
                min-height: 100px;
                min-width: 200px;
                
            }
            QPushButton:hover {
                background-color: rgba(93, 194, 103, 0.7); /* Darker on hover */
                
            }
            
        """)
        self.text_display_tut = QLabel()
        self.text_display_tut.setWordWrap(True)
        self.text_display_1.setMinimumSize(500,200)
        self.text_display_tut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_display_tut.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        page2_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        page2_button.clicked.connect(self.page2indexchanged)

        self.setMinimumSize(1100,250)

        control_layout_page2 = QHBoxLayout()
        control_layout_page2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        control_layout_page2.addWidget(self.page2videowidget)
        control_layout_page2.addWidget(self.text_display_tut)

        main_layout_page2 = QVBoxLayout()
        main_layout_page2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout_p2=QHBoxLayout()
        button_layout_p2.addWidget(page2_button)
        button_layout_p2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout_page2.addLayout(control_layout_page2)
        main_layout_page2.addLayout(button_layout_p2)

        self.page2widget.setLayout(main_layout_page2)
        self.stackedWidgets.addWidget(self.page2widget)

    def exercise_details_tut(self,item):
        findindex=list(self.rs[0].values())
        itemindex = findindex.index(item)+1
        excerciseDetails =list(self.rs[1].values())
        self.text_display_tut.setText(f"Exercise: <h1>{self.playItemList[itemindex]}</h1><p><font size='5'>{excerciseDetails[(itemindex-1)]}</font></p>")
        self.text_display_tut.setStyleSheet("""
                                        background-color: #B0CCB0;
                                        border-radius: 5px;
                                        padding: 3px;
                                        color: black;
                                        font-family: Arial;
                                        font-size: 14px;
                                        font-weight: bold;
                                    """)
    def on_media_status_changed_tut(self,status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Seek to the beginning of the media
            self.mediaPlayer_tut.setPosition(0)
            # Start playing again
            self.mediaPlayer_tut.play()

    
    def page2indexchanged(self):
        # self.mediaPlayer_tut.mediaStatusChanged.disconnect(self.on_media_status_changed)
        # self.page2widget.deleteLater()
        self.stackedWidgets.setCurrentIndex(0)
        w_background=self.resource_path("media/background.png")
        stylesheet0 = f"""
            QMainWindow {{
                background-color: #ebf2ed;
                background-image: url({w_background});
            }}
            QMainWindow QAbstractItemView {{
                
                }}
            QLabel {{
                font-size: 18px;
                color: #333333;
                margin-bottom: 5px;
            }}
            QPushButton {{
                padding: 5px 10px;
                color: #333333;
                background-color: #5dc267;
                border: 3px solid transparent;
                border-radius: 5px; /* approximating the corner size */
                outline: none;
            }}
            QPushButton:hover {{
                background-color: #0b6414;
            }}
            QLineEdit:focus {{
                border-color: #5dc267;
            }}
            QPushButton:pressed {{
                background-color: #156e1e;
            }}
        """
        stylesheet0_b=f"""QPushButton {{
                padding: 5px 10px;
                color: #333333;
                background-color: #5dc267;
                border: 3px solid transparent;
                border-radius: 5px; /* approximating the corner size */
                outline: none;
            }}
            QPushButton:hover {{
                background-color: #0b6414;
            }}
            QLineEdit:focus {{
                border-color: #5dc267;
            }}
            QPushButton:pressed {{
                background-color: #156e1e;
            }}
        """
        self.setStyleSheet(stylesheet0)
        self.playButton.setStyleSheet(stylesheet0_b)
        self.restartButton.setStyleSheet(stylesheet0_b)
        self.camButton.setStyleSheet(stylesheet0_b)
        self.videoComboBox.setCurrentIndex(self.current_index_page1)
        # self.on_video_selection_changed(self.current_index_page1)
        
        
        
 
#--------------------------------------------INITIALIZATION AND STYLING OF WIDGETS--------------------------------------------------------------------------------
        
    def widget_init(self):
        # Initialize labels and controls
        self.video_feed_1_path=self.resource_path("media/select_exercise2.png")
        self.video_feed_2_path=self.resource_path("media/camera-view.png")
        self.video_feed_1 = QLabel()
        # Set the QPixmap on the QLabel
        self.video_feed_1.setPixmap(QPixmap(self.video_feed_1_path))
        self.video_feed_2 = QLabel()
        self.video_feed_2.setPixmap(QPixmap(self.video_feed_2_path))
        self.text_display_1_path=self.resource_path("media/instructions.png")
        self.text_display_2_path=self.resource_path("media/YourScore.png")
        self.text_display_1 = QLabel()
        self.text_display_1.setPixmap(QPixmap(self.text_display_1_path))
        self.text_display_2 = QLabel()
        self.text_display_2.setPixmap(QPixmap(self.text_display_2_path))
        self.videoComboBox = QComboBox(self)
        self.playButton = QPushButton('Play', self)
        self.restartButton = QPushButton('Restart', self)
        self.camButton=QPushButton('Cam On', self)

        # Populate the video list (if the method is ready and available)
        self.populate_video_list()

        # Set a minimum size for the video feed labels
        min_widget_size = QSize(500, 350)  # You can adjust the size as needed
        self.video_feed_1.setMinimumSize(min_widget_size)
        self.video_feed_2.setMinimumSize(min_widget_size)
        self.text_display_1.setMinimumSize(min_widget_size)
        self.text_display_2.setMinimumSize(min_widget_size)

        # Adjust size policy for the widgets
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_feed_1.setSizePolicy(size_policy)
        self.video_feed_2.setSizePolicy(size_policy)
        self.text_display_1.setSizePolicy(size_policy)
        self.text_display_2.setSizePolicy(size_policy)

        self.video_feed_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_feed_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_display_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_display_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # self.video_feed_1.setScaledContents(True)
        # self.video_feed_2.setScaledContents(True)

        # # Apply shadow effect
        # self.apply_shadow_effect(self.video_feed_1)
        # self.apply_shadow_effect(self.video_feed_2)
        # self.apply_shadow_effect(self.text_display_1)
        # self.apply_shadow_effect(self.text_display_2)

    def apply_styles(self, widget_style, main_window_style):
        # Apply widget style
        self.video_feed_1.setStyleSheet(widget_style)
        self.video_feed_2.setStyleSheet(widget_style)
        self.text_display_1.setStyleSheet(widget_style)
        self.text_display_2.setStyleSheet(widget_style)

        # Apply main window style
        self.setStyleSheet(main_window_style)

    def video_widget(self,widget_style):
        # Create an instance of QMediaPlayer
        self.mediaPlayer = QMediaPlayer()
        # self.mediaPlayer.setMuted(bool muted)
        self.mediaPlayer.setPlaybackRate(0.8)
        # Create an instance of QVideoWidget
        self.videoWidget = QVideoWidget()
        # Set QVideoWidget as the video output for QMediaPlayer
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        # self.videoWidget.hide()

        # Create a parent widget and layout
        self.scroll_video_widget = QStackedWidget()
        self.scroll_video_widget.setStyleSheet(widget_style)
        
        self.scroll_video_widget.addWidget(self.video_feed_1)  # Add the QLabel
        self.scroll_video_widget.addWidget(self.videoWidget)    # Add the QVideoWidget
        self.scroll_video_widget.setCurrentIndex(0)


    def setup_scroll_area(self):
        self.QScrollArea_1 = QScrollArea()
        self.QScrollArea_1.setWidgetResizable(True)
        self.QScrollArea_1.setWidget(self.scroll_video_widget)
        self.QScrollArea_2 = QScrollArea()
        self.QScrollArea_2.setWidgetResizable(True)
        self.QScrollArea_2.setWidget(self.video_feed_2)
        self.QScrollArea_3 = QScrollArea()
        self.QScrollArea_3.setWidgetResizable(True)
        self.QScrollArea_3.setWidget(self.text_display_1)
        self.QScrollArea_4 = QScrollArea()
        self.QScrollArea_4.setWidgetResizable(True)
        self.QScrollArea_4.setWidget(self.text_display_2)

    def setup_layouts(self,button_style):

        self.stackedWidgets = QStackedWidget()
        # Create central widget as a container for the layout
        main_central=self.resource_path("media/background.png")
        central_widget = BackgroundWidget(main_central)
        central_widget.setStyleSheet(button_style)

        # Create layouts
        self.grid_layout = QGridLayout()
        control_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

        # Configure grid layout with video feeds and text displays
        self.grid_layout.addWidget(self.scroll_video_widget, 0, 0)  # Top-left
        self.grid_layout.addWidget(self.video_feed_2, 0, 1)  # Top-right
        self.grid_layout.addWidget(self.text_display_1, 1, 0)  # Bottom-left
        self.grid_layout.addWidget(self.text_display_2, 1, 1)  # Bottom-right

        self.text_display_1.setWordWrap(True)
        self.text_display_2.setWordWrap(True)


        #Set stretch factors
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setRowStretch(0, 1)
        self.grid_layout.setRowStretch(1, 1)

        
        # Configure control layout with video controls
        control_layout.addWidget(self.videoComboBox)
        control_layout.addWidget(self.playButton)
        control_layout.addWidget(self.restartButton)
        control_layout.addWidget(self.camButton)

        main_layout.addLayout(control_layout)  # Add the controls at the top
        main_layout.addLayout(self.grid_layout)  # Add the grid layout below

        # Set the layout for the central widget
        central_widget.setLayout(main_layout)
        central_widget.setMinimumSize(1100,800)
        self.stackedWidgets.addWidget(central_widget)

        # Set the central widget of the window
        self.setCentralWidget(self.stackedWidgets)



    def setup_ui_elements(self):
        

        self.pose_label=""
        self.steps_wrong=0
        # Initialize the workers
        # self.video_frame_worker = CaptureVideoFramesWorker()
        self.camera_frame_worker = CaptureCameraFramesWorker()

        # Connect the workers' signals to slots that update the GUI
        # self.video_frame_worker.VideoImageUpdated.connect(self.update_video_feed)
        self.camera_frame_worker.ImageUpdated.connect(self.update_camera_feed)
        self.camera_frame_worker.counterUpdate.connect(self.exercise_details1)
        self.camera_frame_worker.wrongmotion.connect(self.pausevideo)
        self.camera_frame_worker.exercisedone.connect(self.popupForCompletion)
        self.camera_frame_worker.currentPose.connect(self.setcurremtPose)
        self.camera_frame_worker.wrongsteps.connect(self.update_wrongsteps)
        # self.camera_frame_worker.wrongmotion.connect(self.pausevideo)
        
        # self.camera_frame_worker.startVideo.connect(self.sync_video)

        # # Handle errors from the workers
        # self.camera_frame_worker.errorOccurred.connect(self.handle_error)  # Assuming you have a handle_error method defined

        # Start the workers
        # self.video_frame_worker.start()
        # self.camera_frame_worker.start()

        # Connect signals and slots for the controls
        self.playButton.clicked.connect(self.on_play_clicked)
        self.restartButton.clicked.connect(self.on_restart_clicked)
        self.camButton.clicked.connect(self.on_cam_clicked)
        self.videoComboBox.currentIndexChanged.connect(self.on_video_selection_changed)
        self.mediaPlayer.mediaStatusChanged.connect(self.on_media_status_changed)
        self.mediaPlayer.errorOccurred.connect(self.handle_video_error)
        


    def apply_shadow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 127))
        widget.setGraphicsEffect(shadow)









#------------------------------------------HANDLING SIGNALS AND SLOTS FOR WIDGET DETAILS----------------------------------

    def update_wrongsteps(self,steps_u):
        self.steps_wrong=steps_u
    
    def handle_error(self, error_message):
        # Here, handle the error, e.g., by showing a message box to the user
        QMessageBox.critical(self, "Error", error_message)

    def update_video_feed(self, image):
        # Slot to handle the new frame from the video
        pixmap = QPixmap.fromImage(image)
        # print(image)
        self.video_feed_1.setPixmap(pixmap.scaled(self.video_feed_1.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def update_camera_feed(self, image):
        # Slot to handle the new frame from the camera
        pixmap = QPixmap.fromImage(image)
        # print("image sent to widget")
        # if self.cam!=0:
        self.video_feed_2.setPixmap(pixmap.scaled(self.video_feed_2.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def exercise_details(self,item):
        findindex=list(self.rs[0].values())
        print("-----------------------------------------------",findindex)
        itemindex = findindex.index(item)+1
        try:
            key_index= list(self.rs[1].keys())
            print(key_index)
        except Exception as e:
            print(e,"-------------line 770")
        self.saveindex=key_index[itemindex-1]
        print("-----------------------------------------------//////////////////",itemindex)
        excerciseDetails =list(self.rs[1].values())
        self.text_display_1.setText(f"Exercise: <h1>{self.playItemList[itemindex]}</h1><p><font size='5'>{excerciseDetails[(itemindex-1)]}</font></p>")
        self.text_display_1.setStyleSheet("""
                                        background-color: rgba(176,204,176,1);
                                        border-radius: 5px;
                                        padding: 3px;
                                        color: black;
                                        font-family: Arial;
                                        font-size: 14px;
                                        font-weight: bold;
                                    """)
        
    def exercise_details1(self,counter):
        self.counter=counter
        self.currentText=f"<h1>Exercise:</h1> <div style='font-size: 65px; color: #2b2424;'>{counter}</div><p style = 'font-size: 40px; color: #2b2424;'>Complete Rep</font></p><p style = 'font-size: 40px; margin-top: 40px; color: #0062FF;'>{self.pose_label}</font></p>"
        self.text_display_2.setText(self.currentText)
        self.text_display_2.setStyleSheet("""
                                        background-color: #B0CCB0;
                                        border-radius: 5px;
                                        padding: 3px;
                                        color: black;
                                        font-family: Arial;
                                        font-size: 14px;
                                        font-weight: bold;
                                    """)

    def populate_video_list(self):
        self.rs = videoApi._neutriApiCall(self)
        self.neutriPlayList=self.rs[0] #Gettung the exercise name
        self.playItemList = ['Select exercise']+ [f"{exercise}" for exercise in self.neutriPlayList.values()]
        # This list can be hardcoded, or you could retrieve it from a directory of video files.
        video_list = ['Select Exercise', 'Bhuj Bandh', 'Bhuja Valli Sakthi Vikasaka','Jaanu Shakti Kriya','Bhuja Shakti Yoga', 'Kartal Karprasth', 'Kaphoni Shakti', 'Anguli Shakti']  # Example list
        self.videoComboBox.addItems(video_list)
        # fonts = QFontDatabase.families()
        # print(fonts)
        self.videoComboBox.setStyleSheet("""
                QComboBox {
                    font-family: 'Sitka Text Semibold';
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 1px 18px 1px 3px;
                    min-width: 8em;  /* Increased width */
                    min-height: 24px; /* Increased height */
                    font-size: 16px;  /* Larger font size */
                    background-color: #F1F6F1; /* Light green background */
                    
                }

                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 15px;
                    border-left-width: 1px;
                    border-left-color: darkgray;
                    border-left-style: solid;
                    border-top-right-radius: 3px;
                    border-bottom-right-radius: 3px;
                }
                QComboBox::down-arrow {
                    image: url({self.downarrow_path});
                    width: 15px;
                    height: 15px;
                }
                                         

                QComboBox::down-arrow:on { /* when the combo box is open */
                image: url({self.uparrow_path});
                                         }
                                         
                QComboBox:hover {
                    border: 2px  solid teal;  
                }
                QComboBox:focus {
                    border: 1px solid green;   
                }
                /*QComboBox QAbstractItemView {
                    background-color: #BFDA9F;  
                    selection-background-color: blue; 
                    selection-color: white;           
                                         }*/
                 QComboBox QAbstractItemView::item {
                    color: black;
                    background: white;
                    border-bottom: 1px solid gray; /* Add a border to the bottom of each item */
                }
                QComboBox QAbstractItemView::item:hover {
                    background: #BFDA9F; /* Change background on hover for better visibility */
                }
            """)
                #     QComboBox::down-arrow:on { /* when the combo box is open */
                #     top: 1px;
                #     left: 1px;
                # }

    def setcurremtPose(self,label_pose):
        self.pose_label=label_pose
        self.textToSpeech(label_pose)


#----------------------------------------HANDLING SIGNALS AND SLOTS FOR BUTTON AND ITS FUNCTIONING-------------------------------------------
    
    
    
    def on_restart_clicked(self):
        # Code to handle pause action
        print("Button clicked properly")
        self.camera_frame_worker.reset()
        self.restart_media()
        # self.video_frame_worker.reset()
        if self.playButton.text()=='Play':
            self.playButton.setText('Pause')
            # self.video_frame_worker.unpause()

    def on_play_clicked(self):
        if self.playButton.text() == 'Play':
            self.playButton.setText('Pause')
            self.mediaPlayer.play()
            # self.video_frame_worker.unpause()
        else:
            self.playButton.setText('Play')
            self.mediaPlayer.pause()
            # self.video_frame_worker.pause()

    def on_cam_clicked(self):
        try:
            if self.camButton.text()=='Cam On':
                self.camButton.setText('--')
                self.camButton.clicked.disconnect(self.on_cam_clicked)
                try:
                    self.camera_frame_worker.wrongmotion.disconnect(self.pausevideo)
                    self.camera_frame_worker.endd()
                    # self.camera_frame_worker.ImageUpdated.disconnect
                    self.camera_frame_worker.finishedvideo.connect(self.updateCameraWithImage)
                    self.camerasignal_connected=True
                    # self.camButton.clicked.connect(self.on_cam_clicked)
                except Exception as e:
                    print(e, "main line 455")
                self.camButton.setText('Cam Off')
                self.camButton.clicked.connect(self.on_cam_clicked)
            else:
                self.camButton.setText('--')
                self.camButton.clicked.disconnect(self.on_cam_clicked)
                try:
                    self.camera_frame_worker.wrongmotion.connect(self.pausevideo)
                    self.camera_frame_worker.reset()
                    # self.camera_frame_worker.ImageUpdated.connect(self.update_camera_feed)
                    self.camera_frame_worker.startt(self.selected_video)
                    # self.camButton.clicked.connect(self.on_cam_clicked)
                except Exception as e:
                    print(e,"main line 374")
                self.camButton.setText('Cam On')
                self.camButton.clicked.connect(self.on_cam_clicked)
        except Exception as e:
            print(e, " Main Line 376")
        
   
#-------------------------TEXT TO SPEECH HANDLER---------------------------------------------------
    def textToSpeech1(self,text):
        self.ttsworker = TextToSpeechThread(text)  # Create a Worker instance
        self.ttsworker.finishedVoice.connect(self.ttsworker.deleteLater)
        self.ttsworker.start()
        self.ttsworker.wait()

        # # Connect signals and slots
        # self.thread.started.connect(self.worker.process)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.error.connect(self.errorString)

        # self.thread.start()  # Start the thread

        # # Disable the button
        # self.button.setEnabled(False)

    def textToSpeech(self,text):
        # Stop and clean up existing thread and worker if they exist
        if hasattr(self, 'ttsthread') and self.ttsthread.isRunning():
            # self.worker.stopSpeech()  # Custom method to stop speech
            self.worker.text=text
            # self.worker.run()
        else:
            self.ttsthread = QThread()  # Create a QThread instance
            self.worker = TextToSpeechThread(text)   # Create a Worker instance
            self.worker.moveToThread(self.ttsthread)  # Move worker to ttsthread

        # Connect signals and slots
        self.ttsthread.started.connect(self.worker.run)
        self.worker.finishedVoice.connect(self.ttsthread.quit)
        # self.worker.finishedVoice.connect(self.worker.deleteLater)
        # self.ttsthread.finished.connect(self.ttsthread.deleteLater)
        self.worker.error.connect(self.errorString)

        self.ttsthread.start()  # Start the ttsthread

    def errorString(self, error):
        print(f"Error: {error}")






#------------------------HADNLING VIDEO STATUS UPDATES AND CHANGES/LOADING AND FUCNTIONALITIES----------------------

    def handle_video_error(self,error, errorString):
        self.scroll_video_widget.setCurrentIndex(0)
        self.scroll_video_widget.show()
        print("show video feed 1.,.,.,.,.,.,.")

    def on_media_status_end(self,status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.mediaPlayer.mediaStatusChanged.disconnect(self.on_media_status_end)
            self.scroll_video_widget.setCurrentIndex(0)
            self.scroll_video_widget.show()
            print("show video feed 1.,.,.,.,.,.,.")
    
    def on_media_status_changed(self,status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Seek to the beginning of the media
            self.mediaPlayer.setPosition(0)
            # Start playing again
            self.mediaPlayer.play()

    def restart_media(self):
        self.mediaPlayer.stop()
        self.mediaPlayer.setPosition(0)
        self.mediaPlayer.play()

    #pause video slot for wrong motion signal
    def pausevideo(self, bool):
        if bool:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def updateCameraWithImage(self):
        pixmap = QPixmap(self.video_feed_2_path)
        print("in logo 00000000000000000000000000000000000000000000000000000000000000000000000")
        self.video_feed_2.setPixmap(pixmap)
        self.text_display_2.setPixmap(QPixmap(self.text_display_2_path))
        if self.camerasignal_connected:
            self.camera_frame_worker.finishedvideo.disconnect(self.updateCameraWithImage)
            self.camerasignal_connected=False

    def updateCameraWithText(self):
        self.video_feed_2.setPixmap(QPixmap())
        self.video_feed_2.setText("<h1>Be Ready, Get in Position</h1>")
        if self.camerasignal_connected:
            self.camera_frame_worker.finishedvideo.disconnect(self.updateCameraWithText)
            self.camerasignal_connected=False

    def loading(self):
        self.video_feed_2.setStyleSheet("""
                                        background-color: rgba(176,204,176,1);
                                    """)
        self.loading_running=True
        if not self.camera_frame_worker.finishedvideo_emitted:
            self.camera_frame_worker.finishedvideo.connect(self.updateCameraWithText)
            self.camerasignal_connected=True
        else:
            self.updateCameraWithText()
        # self.video_feed_2.setPixmap(QPixmap())
        # self.video_feed_2.setText("<h1>Be Ready, Get in Position</h1>")
        # engine=TextToSpeechThread("Be Ready, Get in Position")
        # engine.finishedVoice.connect(engine.wait)
        # self.video_feed_1.setPixmap(QPixmap())
        self.circular_progress = CircularProgressBar()
        self.grid_layout.addWidget(self.circular_progress, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.circular_progress.reset()
        self.circular_progress.show()  # Show the progress bar
        self.circular_progress.finished.connect(self.on_circular_progress_finished)

    def on_circular_progress_finished(self):
        self.playButton.setText('Pause')
        # self.videoWidget.show()
        self.scroll_video_widget.setCurrentIndex(1)
        self.scroll_video_widget.show()
        # self.video_feed_1.hide()
        self.mediaPlayer.setPosition(0)
        self.mediaPlayer.play()
        # self.video_frame_worker.startt()
        self.camera_frame_worker.reset()
        self.camera_frame_worker.startt(self.selected_video)
        self.video_feed_2.setStyleSheet("""
                                        background-color: rgba(176,204,176,0);
                                    """)
        self.circular_progress.finished.disconnect(self.on_circular_progress_finished)
        self.save_startTime=0
        # Timer setup
        self.ex_svae_timer = QTimer(self)
        self.ex_svae_timer.timeout.connect(self.save_updateTime)
        self.ex_svae_timer.start(1000)
        if hasattr(self, 'circular_progress'):
            self.grid_layout.removeWidget(self.circular_progress)
            self.circular_progress.deleteLater()
            self.loading_running=False
        
    def save_updateTime(self):
        self.save_startTime += 1

    def on_video_selection_changed(self, index):
        self.mediaPlayer.pause()
        # self.videoWidget.hide()
        self.scroll_video_widget.hide()
        # self.video_feed_1.hide()
        self.playButton.setText('Play')
        self.pose_label=""
        # self.video_frame_worker.pause()
        self.camera_frame_worker.reset()
        self.camera_frame_worker.endd()
        self.selected_video = self.videoComboBox.itemText(index)
        print(self.selected_video)
        dir = r'C:\Users\ADMIN\Desktop\Without Voice and text'
        self.video=  self.resource_path(f"media/{self.selected_video}.mp4") #{self.playItemList[itemindex].split('.mp4')[0]}|or|{self.playItemList[itemindex].replace('.mp4', '')}"                                                     
        if os.path.exists(self.video):
            try:
                self.exercise_details(self.selected_video)
                self.exercise_details1(self)
            except Exception as e:
                print(e)
            self.mediaPlayer.setSource(QUrl.fromLocalFile(self.video))
            # self.video_frame_worker.change_video_source_and_restart(self.video)
            if not self.loading_running:
                self.loading()
            else:
                self.circular_progress.hide()
                self.circular_progress.reset()
                self.circular_progress.show()
                # self.loading()
            self.textToSpeech(f"You have selected {self.selected_video}, take position")   

        else:
            self.textToSpeech("This Exercise is under Development. Update your NutriAnalyser App")
            if self.loading_running:
                self.circular_progress.hide()
                self.circular_progress.finished.disconnect(self.on_circular_progress_finished)
                self.grid_layout.removeWidget(self.circular_progress)
                self.circular_progress.deleteLater()
                self.loading_running=False
            if not self.camera_frame_worker.finishedvideo_emitted:
                self.camera_frame_worker.finishedvideo.connect(self.updateCameraWithImage)
                self.camerasignal_connected=True
            else:
                self.updateCameraWithImage()
            self.text_display_1.setPixmap(QPixmap(self.text_display_1_path))
            # self.text_display_2.setPixmap(QPixmap('./media/criteriontechofficial_logo.jpeg'))
            self.scroll_video_widget.setCurrentIndex(0)
            self.scroll_video_widget.show()
            # print("show video feed 1.,.,.,.,.,.,.")
            QMessageBox.warning(self, "Video Error, Update Required", "This Exercise is under Development, Update your NutriAnalyser App to The Latest Version.")   


    def popupForCompletion(self):
        self.mediaPlayer.pause()
        try:
            self.saveExerciseDetails(self.counter)
        except:
            pass
        # Create a message box
        msgBox = QMessageBox()
        msgBox.setText("<b>The exercise is complete.<b>")
        msgBox.setInformativeText("<b>What would you like to do next?<b>")
        # Create custom buttons
        doneButton = msgBox.addButton("Done", QMessageBox.ButtonRole.YesRole)
        repeatButton = msgBox.addButton("Repeat", QMessageBox.ButtonRole.NoRole)
        nextExerciseButton = msgBox.addButton("Next Exercise", QMessageBox.ButtonRole.AcceptRole)
        msgBox.setStyleSheet("QLabel{min-width: 200px; font-size: 18px; color: black;} QPushButton{ width:100px; font-size: 16px; }")
        msgBox_path=self.resource_path("media/exercise_complete.png")
        msgBox.setWindowIcon(QIcon(msgBox_path))
        msgBox.setWindowTitle("Exercise Complete")
        # Set the default button
        msgBox.setDefaultButton(doneButton)
        # msgBox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Track if a button was clicked
        self.buttonClicked = False
        msgBox.buttonClicked.connect(lambda _: setattr(self, 'buttonClicked', True))

        # Loop through the message box's children to find the QLabel
        for child in msgBox.findChildren(QLabel):
            # Center align the text of QLabel
            child.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # Display the message box and capture the response
        ret = msgBox.exec()
        # Get the role of the clicked button
        clickedButtonRole = msgBox.buttonRole(msgBox.clickedButton())
        # Handle the response based on the button role
        if not self.buttonClicked:
            self.done_exercise()
            print("No button selected, treating as 'Done'")
        else:
            clickedButtonRole = msgBox.buttonRole(msgBox.clickedButton())
            if clickedButtonRole == QMessageBox.ButtonRole.YesRole:
                self.done_exercise()
                print("Done selected")
            elif clickedButtonRole == QMessageBox.ButtonRole.NoRole:
                self.restart_exercise()
                print("Repeat selected")
            elif clickedButtonRole == QMessageBox.ButtonRole.AcceptRole:
                self.next_exercise()
                print("Next Exercise selected")
            else:
                print("Unexpected option selected")

        # if ret == QMessageBox.StandardButton.NoButton:
        #     self.done_exercise()
        #     print("Message box closed without selection, treating as 'Done'")
        #     return

        # # Handle the response based on the button role
        # if clickedButtonRole == QMessageBox.ButtonRole.YesRole:
        #     self.done_exercise()
        #     print("Done selected")
        # elif clickedButtonRole == QMessageBox.ButtonRole.NoRole:
        #     self.restart_exercise()
        #     # self.loading()
        #     print("Repeat selected")
        # elif clickedButtonRole == QMessageBox.ButtonRole.AcceptRole:
        #     self.next_exercise()
        #     print("Next Exercise selected")
        # else:
        #     # This should not be reached
        #     print("Unexpected option selected")
                
    def saveExerciseDetails(self,progress_value):
        self.progress_value = progress_value
        print("enetered save details,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
        if self.save_startTime>60:
            self.save_startTime=int(self.save_startTime/60)
        else:
            self.save_startTime=1
        
        totalsteps= 10+self.steps_wrong
        print("lllllllllllllllllllllllllllll",self.steps_wrong)

        saveExercise= 'https://nutrianalyser.com:313/api/Exercise/SaveUserExerciseDetails'

        payload= {

        "id":self.saveindex,

        "userLoginID":14,

        "totalStep":totalsteps,

        "currectStep":10,

        "totalTimeInMinute":self.save_startTime

        }
        try:

            token = '42556BE4B72B4ACDAFEDC59CCCE12A49U2113'
            test_response = requests.post(saveExercise, json=payload,headers={'token':token})
            print("done api hit")
        except Exception as e:
            print(e)
        # self.exercise_saved = True
    
    def restart_exercise(self):
        current_index = self.videoComboBox.currentIndex()
        self.on_video_selection_changed(current_index)

    def next_exercise(self):
        next_index = self.videoComboBox.currentIndex()+1
        self.videoComboBox.setCurrentIndex(next_index)
        # self.on_video_selection_changed(next_index)

    def done_exercise(self):
        self.scroll_video_widget.setCurrentIndex(0)
        self.scroll_video_widget.show()
        if not self.camera_frame_worker.finishedvideo_emitted:
            self.camera_frame_worker.finishedvideo.connect(self.updateCameraWithImage)
            self.camerasignal_connected=True
        else:
            self.updateCameraWithImage()
        self.text_display_1.setPixmap(QPixmap(self.text_display_1_path))



#---------------------ENDING THE MAIN WINDOW----------------------------------------------------------------------------------------------------------------
    
    
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # if hasattr(self, 'video_frame_worker'):
                # self.video_frame_worker.stop()
                # self.video_frame_worker.wait()

            if hasattr(self, 'camera_frame_worker'):
                self.camera_frame_worker.endd()
                self.camera_frame_worker.deleteLater()
                self.camera_frame_worker.wait()
            event.accept() 
        else:
            event.ignore()  



    
    def resource_path(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


#-------------------------------------MAIN TO RUN THE APPLICATION--------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    print("Starting application...")   

    login_dialog = LoginDialog()
    # result = login_dialog.exec()
    print(f"Login dialog result: {login_dialog.result()}")
    # if result == QDialog.DialogCode.Accepted:  # User successfully logged in
    print("Login successful. Showing main window...")
    main_window = SimplifiedMainWindow()
    main_window.show()
    # else:
    #     # Handle unsuccessful login if needed (e.g., retry, show error, etc.)
    #     print("Login failed or canceled.")
    sys.exit(app.exec())
    # sys.exit()

if __name__ == "__main__":
    main()