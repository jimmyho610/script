import math
import matplotlib.pyplot as plt
import cv2
from matplotlib import lines
import numpy as np
import os
import argparse
import xml.etree.ElementTree as ET

Color = [   
            # orange
            [255, 120, 0], # darkorange
            [255, 0, 0], # red
            [255, 200, 0], # gold
            
            # blue
            [0, 0, 139], # darkblue
            [0, 0, 255], # blue 
            [30, 144, 255], # dodgerblue
            [0, 191, 255], # deepskyblue
            
        ]

class_dict = {0: 'piglet', 1: 'head', 2: 'tail', 3: 'right_lying', 4: 'left_lying', 5: 'sitting', 6: 'standing'}
       

def rotate_xml(image_name, rotate_angle):
    rotated_boxes = {'piglet':[], 'other':[], 'right_lying':[], 'left_lying':[], 'sitting':[], 'standing':[]}
    img = plt.imread(os.path.join(args.image_path, image_name + '.jpg'))
    

    (h, w) = img.shape[:2]
    (cx, cy) = (w // 2, h // 2)
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cx, cy), rotate_angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cx
    M[1, 2] += (nH / 2) - cy
    # perform the actual rotation and return the image
    rotate_image = cv2.warpAffine(img, M, (nW, nH))
#    print(rotate_image.shape)
    cv2.imwrite('../Datasets/Augmentation/{}/Image/rotate_{}_{}.jpg'.format(args.xml_path.split('/')[-2], rotate_angle, image_name), rotate_image[:,:,::-1])
    
    tree = ET.parse(os.path.join(args.xml_path, image_name + '.xml'))
    root = tree.getroot()
    root.find('filename').text = "rotate_{}_{}".format(rotate_angle, image_name)
    root.find('size').find('height').text = str(rotate_image.shape[0])
    root.find('size').find('width').text = str(rotate_image.shape[1])
    
            
    for i, box in enumerate(root.iter('robndbox')):      
        cnt_x = float(box.find('cx').text)
        cnt_y = float(box.find('cy').text)
        wb = float(box.find('w').text)
        hb = float(box.find('h').text)
        theta = float(box.find('angle').text)
        c = math.cos(-theta)
        s = math.sin(-theta)
        rect = [(-wb / 2, hb / 2), (-wb / 2, -hb / 2), (wb / 2, -hb / 2), (wb / 2, hb / 2)]
        # x: left->right ; y: top->down
        rotated_rect = np.array([(s * yy + c * xx + cnt_x, c * yy - s * xx + cnt_y) for (xx, yy) in rect])
        rotated_rect = np.hstack((rotated_rect, np.ones((rotated_rect.shape[0],1), dtype = type(rotated_rect[0][0]))))
        rotated_rect = np.dot(M,rotated_rect.T).T
        
        cnt_x = (rotated_rect[1][0] + rotated_rect[3][0]) / 2
        cnt_y = (rotated_rect[1][1] + rotated_rect[3][1]) / 2
        angle = -theta * 180 / math.pi
        angle += rotate_angle
        angle = (angle + 180) % 360 - 180
        theta = -angle * math.pi / 180
        rotated_boxes[root[i+6][1].text].append([cnt_x, cnt_y, wb, hb, theta])
        
        box.find('cx').text = str(cnt_x)
        box.find('cy').text = str(cnt_y)
        box.find('w').text = str(wb)
        box.find('h').text = str(hb)
        box.find('angle').text = str(theta)
    tree.write('../Datasets/Augmentation/{}/Annotation/rotate_{}_{}.xml'.format(args.xml_path.split('/')[-2], rotate_angle, image_name))
        
    if args.show:
        show(rotate_image, rotated_boxes)       
        
                
def show(img, boxes):
    fig, ax = plt.subplots(1, figsize=(19.2,10.8))
    height, width = img.shape[:2]
    ax.set_ylim(height + 10, -10)
    ax.set_xlim(-10, width + 10)
    ax.axis('off')
    
    for i, cls in enumerate(boxes.keys()):
        for value in boxes[cls]:
            cnt_x, cnt_y, w, h, theta = value
            c = math.cos(-theta)
            s = math.sin(-theta)
            rect = [(-w / 2, h / 2), (-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2)]
            # x: left->right ; y: top->down
            rotated_rect = [(s * yy + c * xx + cnt_x, c * yy - s * xx + cnt_y) for (xx, yy) in rect]
            for k in range(4):
                j = (k + 1) % 4
                ax.add_line(
                    lines.Line2D(
                        [rotated_rect[k][0], rotated_rect[j][0]],
                        [rotated_rect[k][1], rotated_rect[j][1]],
                        color=[item/255 for item in Color[i]],
                        linestyle="-",
                        linewidth=2,
                    )
                )
            x, y = rotated_rect[1]
            angle = -theta * 180 / math.pi
            ax.text(x, y, cls, size=12, fontweight='bold',rotation=angle,rotation_mode='anchor',\
                    verticalalignment="top",horizontalalignment="left", color='w', \
                    bbox=dict(boxstyle='square', facecolor=[item/255 for item in Color[i]], 
                              edgecolor='None', pad=0)       
            )

    count_piglet = 'piglet count: {}'.format(len(boxes['piglet']) + len(boxes['other']))
    ax.text(width, height, count_piglet, fontweight = 'bold', color='w', size=30, 
           verticalalignment='bottom', horizontalalignment='right', 
           bbox=dict(boxstyle='square', facecolor=[0, 128/255, 0], edgecolor='None', pad = 0))
    ax.imshow(img)
    plt.show()
    plt.tight_layout()
    print('piglet count', len(boxes['piglet']) + len(boxes['other']))

    
def main():
    for img_file in sorted(os.listdir(args.xml_path)):
        if img_file.endswith('.xml'):
            image_name = os.path.splitext(img_file)[0] 
            for i in range(1,6):
                rotate_xml(image_name, 60 * i)

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Change file name')
    parser.add_argument('--image_path', default="../Crop images/rpi2/Day", type=str, help='image path')
    parser.add_argument('--xml_path', default="../Labeled image/piglet behavior/detection/rotated_roLabelImg/rpi2/Day", type=str, help='xml path')
    parser.add_argument('--show', default=False, action='store_false')
    args = parser.parse_args()
    main()
    