import cv2
import numpy as np
import xml.etree.ElementTree as ET
import os
import argparse
import matplotlib.pyplot as plt


def apply_transformation(image_name, transformation):
    if not os.path.exists('{}/{}/image'.format(data_path,transformation)):
        os.makedirs('{}/{}/image'.format(data_path,transformation))
    if not os.path.exists('{}/{}/xml'.format(data_path,transformation)):
        os.makedirs('{}/{}/xml'.format(data_path,transformation))
    import random
    interval = f_dic[transformation]
    factor = random.uniform(interval[0], interval[1])
    t_dic[transformation](image_name, factor)

def rotate_image(image_name, angle):
    image = cv2.imread(os.path.join(args.jpg_path, image_name + '.jpg'))
    # get image dimension
    img_height, img_width = image.shape[:2]
    # get rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center = (img_width / 2, img_height / 2), angle = angle, scale = 1.0 )
    # apply transformation (ratate image) 
    rotated_image = cv2.warpAffine(image, rotation_matrix, (img_width, img_height) )
    # --- compute new bounding box ---
    # Apply same transformation to the four bounding box corners
    tree = ET.parse(os.path.join(args.xml_path, image_name + '.xml'))
    root = tree.getroot()
    boxes = []
    for box in root.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        rotated_point_A = np.matmul(rotation_matrix, np.array( [xmin, ymin, 1] ).T )
        rotated_point_B = np.matmul(rotation_matrix, np.array( [xmax, ymin, 1] ).T )
        rotated_point_C = np.matmul(rotation_matrix, np.array( [xmax, ymax, 1] ).T )
        rotated_point_D = np.matmul(rotation_matrix, np.array( [xmin, ymax, 1] ).T )
        # Compute new bounding box, that is, the bounding box for rotated object
        x = np.array( [ rotated_point_A[0], rotated_point_B[0], rotated_point_C[0], rotated_point_D[0] ] )
        y = np.array( [ rotated_point_A[1], rotated_point_B[1], rotated_point_C[1], rotated_point_D[1] ] )
        box.find('xmin').text = str(np.min(x).astype(int))
        box.find('ymin').text = str(np.min(y).astype(int))
        box.find('xmax').text = str(np.max(x).astype(int))
        box.find('ymax').text = str(np.max(y).astype(int))
        if args.show:
            boxes.append([(np.min(x).astype(int), np.min(y).astype(int)), (np.max(x).astype(int), np.max(y).astype(int))])
    cv2.imwrite(os.path.join(data_path, '{}/{}/image/rotate_{}.jpg'.format(data_path,transformation,image_name)), rotated_image)
    tree.write(os.path.join(data_path, '{}/{}/xml/rotate_{}.xml'.format(data_path,transformation,image_name)))
    if args.show:
        show_image(rotated_image, boxes)

def width_shift_image(image_name, width_shift_range):
    boxes = []
    image = cv2.imread(os.path.join(args.jpg_path, image_name + '.jpg'))
    img_height, img_width = image.shape[:2]
    factor = img_width * width_shift_range
    M = np.float32([[1,0,factor],[0,1,0]]) 
    shifted_image = cv2.warpAffine( image, M, (img_width, img_height) )
    # --- compute new bounding box ---
    # Apply same transformation to the four bounding box corners
    tree = ET.parse(os.path.join(args.xml_path, image_name + '.xml'))
    root = tree.getroot()
    for box in root.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        shifted_point_A = np.matmul( M, np.array([xmin, ymin, 1] ).T )   
        shifted_point_C = np.matmul( M, np.array([xmax, ymax, 1] ).T )   
        box.find('xmin').text = str(shifted_point_A[0].astype(int))
        box.find('ymin').text = str(shifted_point_A[1].astype(int))
        box.find('xmax').text = str(shifted_point_C[0].astype(int))
        box.find('ymax').text = str(shifted_point_C[1].astype(int))
        if args.show:
            boxes.append([(shifted_point_A[0].astype(int), shifted_point_A[1].astype(int)), (shifted_point_C[0].astype(int), shifted_point_C[1].astype(int))])
    cv2.imwrite(os.path.join(data_path, '{}/{}/image/width_shift_{}.jpg'.format(data_path,transformation,image_name)), shifted_image)
    tree.write(os.path.join(data_path, '{}/{}/xml/width_shift_{}.xml'.format(data_path,transformation,image_name)))
    if args.show:
        show_image(shifted_image, boxes)

def height_shift_image(image_name, height_shift_range):
    boxes = []
    image = cv2.imread(os.path.join(args.jpg_path, image_name + '.jpg'))
    img_height, img_width = image.shape[:2]
    factor = height_shift_range * img_height
    M = np.float32([[1,0,0],[0,1,factor]]) 
    shifted_image = cv2.warpAffine(image, M, (img_width, img_height))
    # --- compute new bounding box ---
    # Apply same transformation to the four bounding box corners
    tree = ET.parse(os.path.join(args.xml_path, image_name + '.xml'))
    root = tree.getroot()
    for box in root.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        shifted_point_A = np.matmul( M, np.array([xmin, ymin, 1] ).T )   
        shifted_point_C = np.matmul( M, np.array([xmax, ymax, 1] ).T )   
        box.find('xmin').text = str(shifted_point_A[0].astype(int))
        box.find('ymin').text = str(shifted_point_A[1].astype(int))
        box.find('xmax').text = str(shifted_point_C[0].astype(int))
        box.find('ymax').text = str(shifted_point_C[1].astype(int))
        if args.show:
            boxes.append([(shifted_point_A[0].astype(int), shifted_point_A[1].astype(int)), (shifted_point_C[0].astype(int), shifted_point_C[1].astype(int))])
    cv2.imwrite(os.path.join(data_path, '{}/{}/image/height_shift_{}.jpg'.format(data_path,transformation,image_name)), shifted_image)
    tree.write(os.path.join(data_path, '{}/{}/xml/height_shift_{}.xml'.format(data_path,transformation,image_name)))
    if args.show:
        show_image(shifted_image, boxes)

def show_image(image, bboxs):
    copied_image = image.copy()
    for box in bboxs:
        transform_image = cv2.rectangle(copied_image, box[0], box[1], (0, 0, 255), 3)
    plt.imshow(transform_image[:,:,::-1])
    plt.show()

def main():
    global data_path, t_dic, f_dic, transformation
    data_path = '/home/ubuntu/Training/datasets/piglet behavior/detection/'
    t_dic = { "rotation":rotate_image, "width_shift":width_shift_image, "height_shift":height_shift_image}
    f_dic = { "rotation":(-60, 60), "width_shift":(-0.3, 0.3), "height_shift":(-0.3, 0.3)}
    for transformation in t_dic.keys():
        for img_file in sorted(os.listdir(args.jpg_path)):
            image_name = os.path.splitext(img_file)[0]
            apply_transformation(image_name, transformation)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Change file name')
    parser.add_argument('--jpg_path', default='', type=str, help='image path')
    parser.add_argument('--xml_path', default='', type=str, help='xml path')
    parser.add_argument('--show', default=False, action='store_true')
    args = parser.parse_args()
    main()