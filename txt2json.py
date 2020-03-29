import os
import json
import glob
import cv2

START_BOUNDING_BOX_ID = 1

def get_categories():
    """Generate category name to id mapping from predifined_classes.txt
    
    Returns:
        dict -- category name to id mapping.
    """
    classes_names = []
    with open('../Labeled image/piglet behavior/detection/labelImg_OBB/data/predefined_classes.txt') as f:
        classes = f.readlines()
    for cls in classes:
        classes_names.append(cls.strip('\n'))
    return {name: i for i, name in enumerate(classes_names)}

def get_filename_as_int(filename):
    try:
        filename = os.path.splitext(os.path.basename(filename))[0]
        return int(filename)
    except:
        raise ValueError("Filename %s is supposed to be an integer." % (filename))


def convert(txt_files, json_file):
    json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}
    categories = get_categories()
    bnd_id = START_BOUNDING_BOX_ID
    for filename in txt_files:
        filename = filename.replace("\\", "/")
        ## The filename must be a number
        image_id = get_filename_as_int(filename)
        height, width = cv2.imread(filename.replace('txt', 'jpg')).shape[:2]
        image = {
            "file_name": filename.replace('txt', 'jpg').split('/')[-1],
            "height": height,
            "width": width,
            "id": image_id,
        }
        json_dict["images"].append(image)

        # read bounding boxes
        with open(filename, 'r') as f:
            rows = f.read().splitlines()[1:]
            for row in rows:
                split = row.split(" ")
                category_id = int(split[0])
                ann = {
                "area": int(float(split[3]) * float(split[4])),
                "iscrowd": 0,
                "image_id": image_id,
                "bbox": [int(float(item)) for item in split[1:]],
                "category_id": category_id,
                "id": bnd_id,
                "ignore": 0,
                "segmentation": [],
                }
                json_dict["annotations"].append(ann)
                bnd_id = bnd_id + 1

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
    parser.add_argument("--txt_dir", default="../detectron2_repo/datasets/rpi3/train", help="Directory path to txt files.", type=str)
    parser.add_argument("--json_file", default="../detectron2_repo/datasets/rpi3/train/rpi3.json", help="Output COCO format json file.", type=str)
    args = parser.parse_args()
    txt_files = glob.glob(os.path.join(args.txt_dir, "*.txt"))

    # If you want to do train/test split, you can pass a subset of xml files to convert function.
    print("Number of xml files: {}".format(len(txt_files)))
    convert(txt_files, args.json_file)
    print("Success: {}".format(args.json_file))