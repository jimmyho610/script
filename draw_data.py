import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib import lines
import math

def draw_xml(xml_file, img_path):
    boxes = {'piglet':[], 'right_lying':[], 'left_lying':[], 'sitting':[], 'standing':[]}
    Color = [   
                # orange
                [255, 120, 0], # darkorange
                
                # blue
                [0, 0, 139], # darkblue
                [0, 0, 255], # blue 
                [30, 144, 255], # dodgerblue
                [0, 191, 255], # deepskyblue
                
            ]
    
    # read bounding boxes
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for i in range(6, len(root)):
        bbox = []
        for j in range(5):
            bbox.append(float(root[i][5][j].text))
        boxes[root[i][1].text].append(bbox)
    
    # draw bounding boxes
    img = plt.imread(img_path)
    fig, ax = plt.subplots(1, figsize=(10.0,10.0))
    height, width = img.shape[:2]
    ax.set_ylim(height + 10, -10)
    ax.set_xlim(-10, width + 10)
    ax.axis('off')
    ax.set_title('Detection Result', fontsize = 30)
    for i, cls in enumerate(boxes.keys()):
        for value in boxes[cls]:
            cnt_x, cnt_y, w, h, theta = value
            c = math.cos(-theta)
            s = math.sin(-theta)
            rect = [(-w / 2, h / 2), (-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2)]
            # x: left->right ; y: top->down
            rotated_rect = [(s * yy + c * xx + cnt_x, c * yy - s * xx + cnt_y) for (xx, yy) in rect]
            print(rotated_rect)
            for k in range(4):
                j = (k + 1) % 4
                ax.add_line(
                    lines.Line2D(
                        [rotated_rect[k][0], rotated_rect[j][0]],
                        [rotated_rect[k][1], rotated_rect[j][1]],
                        color=[item/255 for item in Color[i]],
                        linestyle="-",
                        linewidth=3,
                    )
                )
            ax.plot(rotated_rect[0][0], rotated_rect[0][1], marker='o', color=[1,1,0], markersize=10)
            
#            x, y = rotated_rect[1]
#            angle = -theta * 180 / math.pi
#            ax.text(x, y, cls, size=12, fontweight='bold',rotation=angle,rotation_mode='anchor',\
#                    verticalalignment="top",horizontalalignment="right", color='w', \
#                    bbox=dict(boxstyle='square', facecolor=[item/255 for item in Color[i]], 
#                              edgecolor='None', pad=0)       
#            )
            import numpy as np
            import cv2
            rect = cv2.minAreaRect(np.array(rotated_rect, dtype=np.float32))
            box = np.int0(cv2.boxPoints(rect))
            for k in range(4):
                j = (k + 1) % 4
                ax.add_line(
                    lines.Line2D(
                        [box[k][0], box[j][0]],
                        [box[k][1], box[j][1]],
                        color=(1,0,0),
                        linestyle="-",
                        linewidth=2,
                    )
                )
            ax.plot(box[1][0], box[1][1], marker='o', color=[0,0,1])
            
#            
#    count_piglet = 'piglet count: {}'.format(len(boxes['piglet']))
#    ax.text(width, height, count_piglet, fontweight = 'bold', color='w', size=30, 
#           verticalalignment='bottom', horizontalalignment='right', 
#           bbox=dict(boxstyle='square', facecolor=[0, 128/255, 0], edgecolor='None', pad = 0))
    ax.imshow(img)
#    plt.show()
    plt.tight_layout()
#    plt.savefig(xml_path.replace('xml','png'))
    print('piglet count', len(boxes['piglet']))
    
if __name__ == "__main__":
    index = 0
    frame = str(0) * (6 - len(str(index))) + str(index)
    xml_path = '../Labeled image/piglet behavior/detection/rotated_roLabelImg/rpi1/Day/{}.xml'.format(frame)
    img_path = '../Crop images/rpi1/Day/{}.jpg'.format(frame)
    draw_xml(xml_path, img_path)

    
#    import os 
#    imglist = [item[-10:-4] for item  in os.listdir('../Labeled image/piglet behavior/detection/rotated_roLabelImg/rpi1/Day/') if item.endswith('.xml')]
#    for frame in imglist:
#        xml_path = '../Labeled image/piglet behavior/detection/rotated_roLabelImg/rpi1/Day/{}.xml'.format(frame)
#        img_path = '../Crop images/rpi1/Day/{}.jpg'.format(frame)
#        draw_xml(xml_path, img_path)