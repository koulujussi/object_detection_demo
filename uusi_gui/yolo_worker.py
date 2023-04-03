
from PySide6.QtCore import Slot, QThread, Signal
from PySide6.QtGui import QPixmap, QImage

from ultralytics import YOLO
import cv2
from misc import *

#https://www.pythonguis.com/tutorials/multithreading-pyside6-applications-qthreadpool/
class Worker(QThread):
    changePixmap = Signal(QPixmap)

    def __init__(self, model, parent=None):
        QThread.__init__(self, parent=parent)
        self.yolo_is_running = True
        self.model = model
        print(self.model)

    @Slot() 
    def run(self):
    # https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html
    # https://docs.ultralytics.com/usage/python/

        model = YOLO(self.model)

        #Choose capture device. 0 is the default for webcam.
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # if frame is not read correctly
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            
            # if frame is read correctly
            if ret :
                results = model.predict(frame)

                img = draw_boxes(frame, results[0])

                rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format.Format_RGB888)
                convertToQtFormat = QPixmap.fromImage(convertToQtFormat)

                p = convertToQtFormat.scaled(640, 480)
                self.changePixmap.emit(p)
                
                #to exit with q-key or Stop button
                if cv2.waitKey(25) & 0xFF == ord('q'): break
                if self.yolo_is_running == False: break
            else: break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

        img = QPixmap("./image.jpeg")
        p = img.scaled(640, 480)
        self.changePixmap.emit(p)
        self.yolo_is_running = True
    
    @Slot()
    def stop(self):
        print("täällä threadissa stoppia painettu")
        self.yolo_is_running = False
        self.wait()