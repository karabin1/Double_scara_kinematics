#!/usr/bin/python3

from math import sqrt, atan2, acos, sin, cos, pi
import cv2
import numpy as np

class DoubleScara:
    def __init__ (self):

        self.image_h = 1000
        self.image_w = 1000

        self.image_size = (self.image_h, self.image_w)
        self.image = np.ones(self.image_size) * 255

        self.c  = 0           # between shoulders
        self.l1 = 170           # shoulder to ecow
        self.l2 = 250           # ecow to hand
        self.l3 = 0             # hand to tool

        self.X_OFF = int((self.image_w - self.c) / 2)
        self.Y_OFF = 500

        self.x = 500          # start x
        self.y = 800          # start y

        self.work = 0
        self.filename = 'workspace.png'

        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', self.image_w, self.image_h)

        cv2.createTrackbar('X: ','image', self.x, 1000, self.x_callback)
        cv2.createTrackbar('Y: ','image', self.y, 1000, self.y_callback)

        cv2.createTrackbar('c:  ','image', self.c,  500, self.c_callback)
        cv2.createTrackbar('l1: ','image', self.l1, 500, self.l1_callback)
        cv2.createTrackbar('l2: ','image', self.l2, 500, self.l2_callback)

        self.x = 0
        self.y = 300

        self.workspace()
        self.callback()
        self.loop()
        
    def inverse(self, x, y):

        l4  = sqrt(self.l2**2 + self.l3**2 - 2 * self.l2 * self.l3 * cos(pi - pi / 4))    
        d3  = sqrt((self.c - x)**2 + y**2)

        theta2c = atan2(y, (self.c - x))
        theta2d = acos((d3**2 + self.l1**2 - l4**2) / (2 * self.l1 * d3))
        theta2  = theta2c + theta2d
        
        x4 = self.c + self.l1 * cos(pi - theta2)
        y4 = self.l1 * sin(pi - theta2)
        
        delta = atan2(x4 - x, y - y4)

        if self.l3 != 0:
            epsil = acos((self.l3**2 + l4**2 - self.l2**2) / (2 * self.l3 * l4))    
        else:
            epsil = 0

        x1 = x + self.l3 * sin(delta - epsil)
        y1 = y - self.l3 * cos(delta - epsil)

        d1 = sqrt(x1**2 + y1**2)

        theta1a = atan2(y1, x1)
        theta1b = acos((d1**2 + self.l1**2 - self.l2**2) / (2 * self.l1 * d1))
        theta1  = theta1a + theta1b

        return (theta1, theta2)

    def forward(self, theta1, theta2):

        theta1rev = theta1
        theta2rev = pi - theta2

        x1 = self.l1 * cos(theta1rev)
        y1 = sin(theta1rev) * self.l1
        x2 = self.c + self.l1 * cos(theta2rev)
        y2 = sin(theta2rev) * self.l1

        gaa = atan2((y1 - y2), (x1 - x2))
        l = sqrt((x1 - x2)**2 + (y1 - y2)**2)
        h = sqrt(self.l2**2 - (l / 2)**2)

        x3 = (x1 + x2) / 2 + (h * sin(gaa))
        y3 = (y1 + y2) / 2 + abs(h * cos(gaa))

        psichk = atan2((y3 - y2),(x2 - x3))
        x = x3 - self.l3 * cos(psichk + pi / 4)
        y = y3 + self.l3 * sin(psichk + pi / 4)    
                
        return (x1, y1, x2, y2, x3, y3, x, y)

    def draw (self, x1, y1, x2, y2, x3, y3, x, y):    

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        x3 = int(x3)
        y3 = int(y3)
        x  = int(x)
        y  = int(y)

        self.image = cv2.imread(self.filename) 

        arm1_base = [self.X_OFF,            self.Y_OFF     ]
        arm1_ecow = [self.X_OFF + x1,       self.Y_OFF + y1]
        #arm1_hand = [self.X_OFF + x3,       self.Y_OFF + y3]
        arm1_tool = [self.X_OFF + x,        self.Y_OFF + y ]

        arm2_base = [self.X_OFF + self.c,   self.Y_OFF     ]
        arm2_ecow = [self.X_OFF + x2,       self.Y_OFF + y2]
        #arm2_hand = [self.X_OFF + x3,       self.Y_OFF + y3]


        cv2.line(self.image, (arm1_base[0], arm1_base[1]), (arm1_ecow[0], arm1_ecow[1]), (0,255,0), 3)
        #cv2.line(self.image, (arm1_ecow[0], arm1_ecow[1]), (arm1_hand[0], arm1_hand[1]), (0,255,0), 3)
        #cv2.line(self.image, (arm1_hand[0], arm1_hand[1]), (arm1_tool[0], arm1_tool[1]), (0,255,0), 3)
        cv2.line(self.image, (arm1_ecow[0], arm1_ecow[1]), (arm1_tool[0], arm1_tool[1]), (0,255,0), 3)

        cv2.line(self.image, (arm2_base[0], arm2_base[1]), (arm2_ecow[0], arm2_ecow[1]), (0,255,0), 3)
        #cv2.line(self.image, (arm2_ecow[0], arm2_ecow[1]), (arm2_hand[0], arm2_hand[1]), (0,255,0), 3)
        cv2.line(self.image, (arm2_ecow[0], arm2_ecow[1]), (arm1_tool[0], arm1_tool[1]), (0,255,0), 3)

    def callback(self):
        try:  
            t1, t2 = self.inverse(self.x,self.y)
            x1, y1, x2, y2, x3, y3, x, y = self.forward(t1, t2)
            self.draw(x1, y1, x2, y2, x3, y3, self.x, self.y)  

            cv2.putText(self.image, 'x', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            cv2.putText(self.image, str(self.x), (180, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            cv2.putText(self.image, 'y', (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            cv2.putText(self.image, str(self.y), (180, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            cv2.putText(self.image, 'theta1', (50, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            cv2.putText(self.image, str(round(np.rad2deg(t1),4)), (180, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            cv2.putText(self.image, 'theta2', (50, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            cv2.putText(self.image, str(round(np.rad2deg(t2),4)), (180, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)


        except ValueError as e:
            print ("error", e)
            cv2.putText(self.image, 'OUT OF RANGE', (50, 400), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 3)

    def x_callback(self, x_call):
        self.x = x_call - 500
        self.callback()

    def y_callback(self, y_call):
        self.y = y_call - 500
        self.callback()

    def c_callback(self, c_call):
        self.c = c_call
        self.workspace()
        self.callback()
        
    def l1_callback(self, l1_call):
        self.l1 = l1_call
        self.workspace()
        self.callback()

    def l2_callback(self, l2_call):
        self.l2 = l2_call
        self.workspace()
        self.callback()

    def workspace(self):
        self.image = np.ones(self.image_size) * 255
        for x in range(-500, 500):
            if (x % 16) == 0:
                for y in range(-500, 500):
                    if (y % 16) == 0:
                        try:
                            self.inverse(x, y)
                            cv2.circle(self.image,(x + self.X_OFF, y + self.Y_OFF), 2, (0 ,255,0) , 1)
                        except:
                            pass

        cv2.imwrite(self.filename, self.image) 

    def loop(self):
     
        while(1):
            cv2.imshow('image',self.image)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()

if __name__ == "__main__":
    DoubleScara()

