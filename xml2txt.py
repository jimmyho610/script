import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Change file name')
    parser.add_argument('--txt_path', default='', type=str, help='txt path')
    parser.add_argument('--xml_path', default='', type=str, help='xml path')
    args = parser.parse_args()
    state = {k: v for k, v in args._get_kwargs()}
    if not os.path.exists(args.txt_path):
        os.mkdir(args.txt_path)
    for dataset in ['train', 'test']:
        f = open(os.path.join(args.txt_path,dataset+'.txt'),"w")
        for item in os.listdir(os.path.join(args.xml_path,dataset)):
            item = item.replace(".xml","")
            f.write(item)
            f.write('\n')
        f.close()