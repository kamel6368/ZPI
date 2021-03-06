''' Prosze mi tego pliku nie zmieniac ~ Kucu, 2017 '''

import cv2
import Agent.database as db
import Agent.ImageProcessing.pictures_transformations as pt
from Agent.ImageProcessing.objects_detection import ObjectDetector
from Agent.enums import Color
from Agent.enums import ColorSpace
from Agent.object import Shape



cam = cv2.VideoCapture(0)
od = ObjectDetector()
for i in range(20):
    cam.read()

while True:
    images = []
    _, im = cam.read()
    #for i in range(1,10):
        #_, im = cam.read()
        #images.append(im)
    #im = pt.merge_pictures(images, ColorSpace.BGR, True)

    x = od.detect_objects(im, None, False)

    for obj in x:
        print obj.to_string()

    print ' '
    print ' '
    for single_contour in od.detected_contours:
        draw_color = (0, 0, 0)
        if single_contour[0] is Color.RED:
            draw_color = (0, 0, 255)
        elif single_contour[0] is Color.YELLOW:
            draw_color = (40, 244, 255)
        elif single_contour[0] is Color.GREEN:
            draw_color = (0, 255, 0)
        elif single_contour[0] is Color.BLUE:
            draw_color = (255, 0, 0)
        elif single_contour[0] is Color.VIOLET:
            draw_color = (188, 0, 105)
        cv2.drawContours(im, [single_contour[1]], -1, draw_color, 2)
    od.clear_contours()
    cv2.imshow('detected_objects', im)
    cv2.waitKey(1)

    for obj in x:
        if isinstance(obj, Shape):
            db.insert(obj)



