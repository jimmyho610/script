import cv2
import numpy as np

# grab references to the global variables 
pts = [] 
       
def click_and_crop(event, x, y, flags, param):
    
    global pts
	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append((x, y))
        cv2.circle(image, (x,y), 5, (0, 255, 0), -1)
        cv2.imshow("image", image)


def crop():
    ROIs = {'rpi1':[], 'rpi2':[], 'rpi3':[], 'rpi4':[]}
    for i in range(1,5):
        # load the image, clone it, and setup the mouse callback function
        global image, pts, clone
        image = cv2.imread('../Crop images/demo/rpi{}/0.jpg'.format(i))
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_crop)
         
        # keep looping until the 'q' key is pressed
        while True:
        	# display the image and wait for a keypress
            cv2.imshow("image", image)
            key = cv2.waitKey(1) & 0xFF
         
        	# if the 'r' key is pressed, reset the cropping region
            if key == ord("r"):
                image = clone.copy()
                pts = []
         
        	# if the 'c' key is pressed, break from the loop
            elif key == ord("c"):
                if len(pts) != 4:
                    print('Only 4 points are acceptable')
                else:
                    break
            
            elif key == ord("p"):
                cv2.drawContours(image, [np.array(pts)], -1, (0, 255, 0), 3, cv2.LINE_AA)
                
            
                
        print(pts)
        pts = np.array(pts)
        rect = cv2.boundingRect(pts)
        x,y,w,h = rect
        crop_rect = clone[y:y+h, x:x+w].copy()
        
        ## (2) make mask
        pts = pts - pts.min(axis=0)
        
        mask = np.zeros(crop_rect.shape[:2], np.uint8)
        cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
        
        ## (3) do bit-op
        dst = cv2.bitwise_and(crop_rect, crop_rect, mask = mask)
        
        ## (4) add the white background
        bg = np.ones_like(crop_rect, np.uint8)*255
        cv2.bitwise_not(bg,bg, mask=mask)
        dst2 = bg + dst
        
        cv2.imwrite("Crop images/demo/rpi{}/crop_rect.png".format(i), crop_rect)
        cv2.imwrite("Crop images/demo/rpi{}/mask.png".format(i), mask)
        cv2.imwrite("Crop images/demo/rpi{}/dst.png".format(i), dst)
        cv2.imwrite("Crop images/demo/rpi{}/dst2.png".format(i), dst2)
        ROIs['rpi{}'.format(i)] = pts.tolist()
        cv2.imshow("crop", dst)

        pts = []
    # close all open windows
    cv2.destroyAllWindows()

               
if __name__ == '__main__':
    crop()