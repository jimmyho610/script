import os
import json
import xml.etree.ElementTree as ET
import glob
import math

START_BOUNDING_BOX_ID = 1

def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise ValueError("Can not find %s in %s." % (name, root.tag))
    if length > 0 and len(vars) != length:
        raise ValueError(
            "The size of %s is supposed to be %d, but is %d."
            % (name, length, len(vars))
        )
    if length == 1:
        vars = vars[0]
    return vars


#def get_filename_as_int(filename):
#    try:
#        filename = filename.replace("\\", "/")
#        filename = os.path.splitext(os.path.basename(filename))[0]
#        return int(filename)
#    except:
#        raise ValueError("Filename %s is supposed to be an integer." % (filename))


def get_categories():
    """Generate category name to id mapping from predifined_classes.txt
    
    Returns:
        dict -- category name to id mapping.
    """
    classes_names = []
    with open('../Labeled image/piglet behavior/detection/rolabelImg/data/predefined_classes.txt') as f:
        classes = f.readlines()
    for cls in classes:
        classes_names.append(cls.strip('\n'))
    return {name: i for i, name in enumerate(classes_names)}


def convert(xml_files, json_file):
    json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}
    categories = get_categories()
    bnd_id = START_BOUNDING_BOX_ID
    image_id = 0
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        filename = get(root, "filename")[0].text
        ## The filename must be a number
#        image_id = int(filename)
        size = get_and_check(root, "size", 1)
        width = int(get_and_check(size, "width", 1).text)
        height = int(get_and_check(size, "height", 1).text)
        image = {
            "file_name": filename+'.jpg',
            "height": height,
            "width": width,
            "id": image_id,
        }
        json_dict["images"].append(image)
        ## Currently we do not support segmentation.
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        for obj in get(root, "object"):
            category = get_and_check(obj, "name", 1).text
            if category not in categories:
#                new_id = len(categories)
#                categories[category] = new_id
                continue
            category_id = categories[category]
            robndbox = get_and_check(obj, "robndbox", 1)
            cx = float(get_and_check(robndbox, "cx", 1).text)
            cy = float(get_and_check(robndbox, "cy", 1).text)
            w = float(get_and_check(robndbox, "w", 1).text)
            h = float(get_and_check(robndbox, "h", 1).text)
            angle = float(get_and_check(robndbox, "angle", 1).text)
            angle = (angle * 180 / math.pi + 180) % 360 - 180
            ann = {
                "area": w * h,
                "iscrowd": 0,
                "image_id": image_id,
                "bbox": [float(item) for item in [cx, cy, w, h, angle]],
                "category_id": category_id,
                "id": bnd_id,
                "ignore": 0,
                "segmentation": [],
            }
            json_dict["annotations"].append(ann)
            bnd_id = bnd_id + 1
        image_id += 1

    for cate, cid in categories.items():
        cat = {"supercategory": "none", "id": cid, "name": cate}
        json_dict["categories"].append(cat)

    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    json_fp = open(json_file, "w")
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert Pascal VOC annotation to COCO format."
    )
    parser.add_argument("--xml_dir", default="../Labeled image/piglet behavior/detection/rotated_roLabelImg/rpi1/Day", help="Directory path to xml files.", type=str)
    parser.add_argument("--json_file", default="../Labeled image/piglet behavior/detection/rotated_roLabelImg/rpi1//Day/rpi1.json", help="Output COCO format json file.", type=str)
    args = parser.parse_args()
    xml_files = glob.glob(os.path.join(args.xml_dir, "*.xml"))

    # If you want to do train/test split, you can pass a subset of xml files to convert function.
    print("Number of xml files: {}".format(len(xml_files)))
    convert(xml_files, args.json_file)
    print("Success: {}".format(args.json_file))