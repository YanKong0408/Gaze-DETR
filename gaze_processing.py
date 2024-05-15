import argparse
import cv2
import json
import os
import csv
from gaze_process_1 import *


def get_args_parser():
    ### raw_data_fold is the flod path contains collected data by the software Miceye v1(https://github.com/JamesQFreeman/MICEYE)
    ### or Miceye v2(https://github.com/YanKong0408/MicEye-v2.0)
    ### the formate of csv files is as follows:
    ### 
    parser = argparse.ArgumentParser('Gaze Processing', add_help=False)
    parser.add_argument('--raw_data_fold', type=str, required=True)
    parser.add_argument('--output_file', type=str, required=True)
    parser.add_argument('--gaze_only', type=bool, default=True)
    parser.add_argument('--miceye_version', type=int, default=1)
    return parser

def main(args):
    csv_files = []

    json_data = {
        "info": {},
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": [{"id": 1, "name": "object"}]
    }
    img_id = 1
    ann_id = 1

    if args.gaze_only:
        json_data['categories'].append({{"id": 2, "name": "gaze_only"}})
    else:
        json_data['categories'].append({{"id": 2, "name": "gaze"}})
    
    for file_name in os.listdir(args.raw_data_fold):
        if file_name.endswith('.csv'):
            csv_files.append(file_name)

    for file_name in csv_files:
        file_path = os.path.join(args.raw_data_fold, file_name)
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            print(f"Reading file: {file_name}")
            for line in csv_file:
                line = line.strip()
                if line:
                    imgName, _, gazeData, bboxs, _ = line.split(';')
                    gazeData, bboxs=eval(gazeData), eval(bboxs)
                    img=cv2.imread(imgName)

                    json_data["images"].append({
                        "id": img_id,
                        "file_name": imgName,
                        "width": img.shape[0],
                        "height": img.shape[1]
                    })

                    ### for MICEYE V2, gazeDate and bboxs need to be processed
                    if args.miceye_version == 2:
                        new_gazes=[]
                        new_bboxs=[]
                        for gaze in gazeData:
                            new_gazes.append([int(gaze[0][0]/gaze[1]),int(gaze[0][1]/gaze[1])])
                        for bbox in bboxs:
                            new_bboxs.append((int(bbox[0]/bbox[4]),int(bbox[1]/bbox[4]),int(bbox[2]/bbox[4]),int(bbox[3]/bbox[4])))
                        gazeData = new_gazes
                        bboxs=new_bboxs
                    ### end

                    for object_box in bboxs:
                        json_data["annotations"].append({
                            "id": ann_id,
                            "image_id": img_id,
                            "bbox": object_box,
                            "category_id": 1,
                            "area": object_box[2] * object_box[3],
                            "iscrowd": 0
                        })
                        ann_id += 1

                    gaze_boxs = gaze_process(gazeData, (img.shape[0],img.shape[1]),GuassKernal=(119,119),thre=0.1)
                    if args.gaze_only:
                        gaze_boxs = gaze_only(bboxs,gaze_boxs)
                    
                    for gaze_box in gaze_boxs:
                        json_data["annotations"].append({
                            "id": ann_id,
                            "image_id": img_id,
                            "bbox": gaze_box,
                            "category_id": 2,
                            "area": gaze_box[2] * gaze_box[3],
                            "iscrowd": 0
                        })
                        ann_id += 1
                    
    with open(args.output_file, 'w') as f:
        json.dump(json_data, f)
                        
                    

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Gaze Processing', parents=[get_args_parser()])
    args = parser.parse_args()
    main(args)
