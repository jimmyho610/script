import cv2
import argparse
import numpy as np
from skimage.measure import compare_ssim

ROIs = {'rpi1':[(192, 1), (70, 455), (815, 453), (721, 1)],
        'rpi2':[(178, 1), (2, 513), (730, 523), (664, 33)],
        'rpi3':[(192, 0), (75, 509), (818, 490), (684, 1)],
        'rpi4':[(350, 94), (233, 541), (958, 541), (798, 75)]
    }
index = 0

def main():
    
    if args.video_path.endswith('.avi'):
        cut_video(args.video_path)
    else:
        import glob
        video_list = glob.glob('{}/*.avi'.format(args.video_path))
        for video in video_list:
            cut_video(video)

def cut_video(video):
    global index
    crop_frames = 0
    start = args.start
    cap = cv2.VideoCapture(video)
    src = np.float32(ROIs[args.device])
    h, w = args.image_height, args.image_width
    dst = np.float32([(0, 0), (0, h), (w, h), (w, 0)])
    M = cv2.getPerspectiveTransform(src, dst)
    
    target_image = None
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        clone = frame.copy()
        processed = cv2.warpPerspective(clone, M, (w, h))
        cv2.namedWindow("",0);
        cv2.resizeWindow("", 500, 500);
        cv2.imshow("", processed)
        cv2.waitKey(1)

        if target_image is None:
            n = 6 - len(str(start + crop_frames + index))
            filename = str(0) * n + str(start + crop_frames + index)
            cv2.imwrite('../Crop images/{}/{}/{}.jpg'.format(args.device, args.time, filename), processed)
            print('save {}'.format(filename))
            target_image = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            crop_frames += 1
            continue

        s = compare_ssim(target_image, cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY))
        if s <= 0.8:
            n = 6 - len(str(start + crop_frames + index))
            filename = str(0) * n + str(start + crop_frames + index)
            cv2.imwrite('../Crop images/{}/{}/{}.jpg'.format(args.device, args.time, filename), processed)
            print('save {}'.format(filename))
            crop_frames += 1
            target_image = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

    video_name = video.split('/')[-1]
    print(video_name)
    index += crop_frames
    write_xlsx(video_name, crop_frames, cap.get(7), start + index, args.device)
    cap.release()

def write_xlsx(video_name, frames, total_frames, index, device):
    import pandas as pd
    from openpyxl import load_workbook
    xlsx_path = '../Crop images/video information.xlsx'
    # new dataframe with same columns
    df = pd.DataFrame({'video': [video_name],
                       'video total frames':[total_frames],
                       'crop frames': [frames],
                       'index': [index - 1],
                       })
    writer = pd.ExcelWriter(xlsx_path, engine='openpyxl')
    # try to open an existing workbook
    writer.book = load_workbook(xlsx_path)
    # copy existing sheets
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
    # read existing file
    reader = pd.read_excel(xlsx_path, sheet_name = device)
    # write out the new sheet
    df.to_excel(writer,index=False,header=False,startrow=len(reader)+1,sheet_name=device)
    writer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crop video to images')
    parser.add_argument('--video_path', default='../video/rpi3/2019-11-25/11', type=str, help='video path')
    parser.add_argument('--time', default='Day', type=str, help='day or night')
    parser.add_argument('--device', default='rpi3', type=str, help='which rpi')
    parser.add_argument('--start', default=234, type=int, help='which index to start')
    parser.add_argument('--image_height', default=1000, type=int, help='image height')
    parser.add_argument('--image_width', default=1000, type=int, help='image width')
    args = parser.parse_args()
    main()