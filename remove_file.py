import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Change file name')
    parser.add_argument('--jpg_path', default='', type=str, help='image path')
    parser.add_argument('--xml_path', default='', type=str, help='xml path')
    args = parser.parse_args()
    state = {k: v for k, v in args._get_kwargs()}
    filelist1 = os.listdir(args.jpg_path)
    filelist1.sort()
    filelist2 = os.listdir(arg.xml_path)
    filelist2.sort()
    name1 = [item.replace(".jpg", "") for item in filelist1 if item.endswith('.jpg')]
    name2 = [item.replace(".xml", "") for item in filelist2 if item.endswith('.xml')]
    diff = list(set(name1) - set(name2))
    # li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    for item in diff:
        os.remove(path_to_jpg + item + '.jpg')


