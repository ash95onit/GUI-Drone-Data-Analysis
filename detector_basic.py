import cv2
import numpy as np

# Parameters
max_car_ratio = 3.0
min_car_ratio = 2.0
min_car_area = 5000
max_car_area = 400000


def draw_lines(img, lines):
    try:
        for line in lines:
            coords = line[0]
            cv2.line(img, (coords[0],coords[1]), (coords[2],coords[3]), [0,0,255], 3)
    except:
        pass


def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked


def work_model(img):
    # HSV - blue channel extract
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_blue = img_hsv[:,:,0]
    _, img_blue_bin = cv2.threshold(img_blue,75,255, cv2.THRESH_BINARY)

    _, img_blue_bin_inv = cv2.threshold(img_blue,75,255, cv2.THRESH_BINARY_INV)

    # HSV - green channel extract
    img_green = img_hsv[:,:,1]
    _, img_green_bin = cv2.threshold(img_green,50,255, cv2.THRESH_BINARY)

    _, img_green_bin_inv = cv2.threshold(img_green,50,255, cv2.THRESH_BINARY_INV)

    # HSV - red channel extract
    img_red = img_hsv[:,:,2]
    _, img_red_bin = cv2.threshold(img_red,50,255, cv2.THRESH_BINARY)

    _, img_red_bin_inv = cv2.threshold(img_red,50,255, cv2.THRESH_BINARY_INV)

    # Gray - eliminate shadow
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, gray_bin_inv = cv2.threshold(gray,50,255, cv2.THRESH_BINARY_INV)

    _, gray_bin = cv2.threshold(gray,50,255, cv2.THRESH_BINARY)


    # subtract
    blue_gray_bin = img_blue_bin - gray_bin_inv



    rev_blue_gray_bin = gray_bin_inv - img_blue_bin

    # XOR
    temp1 = cv2.bitwise_and(img_blue_bin, gray_bin_inv) # shadow
    temp2 = cv2.bitwise_and(img_blue_bin_inv, gray_bin)
    xor_bin = cv2.bitwise_or(temp1, temp2)

    xor_bin_inv = cv2.bitwise_not(xor_bin)

    # shadow
    shadow = temp1 - blue_gray_bin

    return blue_gray_bin



#img = cv2.imread('./images/Situation_5_nah.JPG')
img = cv2.imread('./images/test4.JPG')

#img_bright= cv2.add(img,np.array([50.0]))
#img = cv2.resize(img, (600,600), interpolation = cv2.INTER_AREA)
res = img.copy()


blue_gray_bin = work_model(img)

# Denoise
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
morph = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))

# take morphological gradient
gradient_image = cv2.morphologyEx(morph, cv2.MORPH_GRADIENT, kernel)

# split the gradient image into channels
image_channels = np.split(np.asarray(gradient_image), 3, axis=2)

channel_height, channel_width, _ = image_channels[0].shape

# apply Otsu threshold to each channel
for i in range(0, 3):
    _, image_channels[i] = cv2.threshold(~image_channels[i], 0, 50, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    image_channels[i] = np.reshape(image_channels[i], newshape=(channel_height, channel_width, 1))

# merge the channels
denoise = np.concatenate((image_channels[0], image_channels[1], image_channels[2]), axis=2)

_, denoise_bin = cv2.threshold(denoise, 0, 255, cv2.THRESH_BINARY)

#hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#lower = np.array([71,3,120], dtype=np.uint8)
#upper = np.array([116,185,255], dtype=np.uint8)
#mask = cv2.inRange(hsv, lower, upper)
#croped = cv2.bitwise_and(img, img, mask=mask)
#croped_bgr = cv2.cvtColor(croped, cv2.COLOR_HSV2BGR)
#croped_gray = cv2.cvtColor(croped, cv2.COLOR_BGR2GRAY
#_, binary1= cv2.threshold(gray,200,255,cv2.THRESH_BINARY)
#canny = cv2.Canny(blue_gray_bin, threshold1=100, threshold2=300)
blur = cv2.GaussianBlur(blue_gray_bin, (13,13), 0 )
_, binary1= cv2.threshold(blur,175,255,cv2.THRESH_BINARY)
#canny = cv2.Canny(binary1, threshold1=300, threshold2=500)

#lines = cv2.HoughLinesP(blur, rho=1, theta=np.pi/180, threshold=180, minLineLength=500, maxLineGap=50)
#draw_lines(img,lines)
_, contours, hierarchy = cv2.findContours(binary1,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

# Iterate through contours and draw a slightly bigger white rectangle
# over the contours that are not big enough (the text) on the copy of the image.
for i in contours:
    cnt = cv2.contourArea(i)
    if cnt > min_car_area: # and cnt < max_car_area:
        cv2.drawContours(res, i, -1, (0, 255, 0), 5) 
        x,y,w,h = cv2.boundingRect(i)
        if w > h:
            size_ratio = w/h
        else:
            size_ratio = h/w
        if (size_ratio < max_car_ratio) and (size_ratio > min_car_ratio):
            print(size_ratio)
            cv2.line(res,(x-1,y-1),(x+w+1,y+h+1),(0,0,255),3)




cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 1200,800)
cv2.namedWindow('image2',cv2.WINDOW_NORMAL)
cv2.resizeWindow('image2', 1200,800)
cv2.namedWindow('image3',cv2.WINDOW_NORMAL)
cv2.resizeWindow('image3', 1200,800)



cv2.imshow('image', res)
cv2.imshow('image2', blue_gray_bin)
cv2.imshow('image3', binary1)
  
cv2.waitKey(0)
cv2.destroyAllWindows()