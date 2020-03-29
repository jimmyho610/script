import os
import argparse
import glob

def rename(path, filetype, start):
    filelist = sorted(glob.glob(os.path.join(path, "*{}".format(filetype))))
    total_num = len(filelist)
    i = start
    for filename in filelist:
        filename = filename.replace("\\", "/")
        n = 6 - len(str(i))
        print(filename)
        src = os.path.join(filename)
        dst = os.path.join(os.path.abspath(path), str(0) * n + str(i) + filetype)
        try:
            os.rename(src, dst)
            print('converting %s to %s' % (src, dst))
            i += 1
        except:
            continue
    print('total %d to rename & converted %d %s' % (total_num, i-1, filetype))

            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Change file name')
    parser.add_argument("--path", default="../detectron2_repo/datasets/rpi3/train", help="Directory path to files.", type=str)
    args = parser.parse_args()
    parser.add_argument('--start', default=0, type=int, help='start')
    args = parser.parse_args()
    rename(args.path,'.jpg',args.start)
    rename(args.path,'.txt',args.start)
