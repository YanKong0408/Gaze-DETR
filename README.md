# Gaze-DETR: Using Expert Gaze to Reduce False Positives in Vulvovaginal Candidiasis Screening
**MICCAI 2024 early accept!!!** 

![Intro](./image/intro.png)

## Useful links

<div align="center">
    <a href="https://arxiv.org/pdf/2405.09463" class="button"><b>[Paper]</b></a> &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://pan.baidu.com/s/1bG1RB-wod8PIE0MJ3EhWJg?pwd=gaze" class="button"><b>[Checkpoint of Gaze-Dino-Res50]</b></a> &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://pan.baidu.com/s/1bG1RB-wod8PIE0MJ3EhWJg?pwd=gaze" class="button"><b>[Checkpoint of Gaze-Dino-Swin]</b></a> &nbsp;&nbsp;&nbsp;&nbsp;
</div>

## Method
![Intro](./image/method.png)

## Usage

### Install

```sh
# Clone this repo
git clone https://github.com/YanKong0408/Gaze-DETR.git
cd Gaze-DETR

# Install Pytorch and torchvision
# We test our models under 'python=3.7.3,pytorch=1.9.0,cuda=11.1'. Other versions might be available as well.
conda install -c pytorch pytorch torchvision

# Install other needed packages
pip install -r requirements.txt

# Compiling CUDA operators
cd models/Gaze-Dino/ops
python setup.py build install
# unit test (should see all checking is True)
python test.py
cd ../../..
```

### Gaze Processing

Gaze tracks were seamlessly obtained during the bounding box annotation process, utilizing software [Miceye](https://github.com/JamesQFreeman/MICEYE).

You can use the following code to process the folder containing the raw data from the above software into a coco-style json file.
``` sh
python gaze_processing.py \
    --output_dir  /path/to/your/output/dir \
    --raw_data_fold /path/to/your/raw/data/fold
```

The key function is in [util/gaze_process.py](https://github.com/YanKong0408/Gaze-DETR/blob/main/util/gaze_process.py) as follow. You can use this function to process other forms of Gaze data as JSON files.
``` Python
from util.gaze_process import gaze_box2json
gaze_box2json(images, gazes, boxes, json_file, gaze_only = True)
```

### Model
Our code is based on [DINO](https://github.com/IDEA-Research/DINO).

Data can be obtained from the json file split resulting from the above step and should be organized into the coco dataset format.
```
Your_Fold/
  └── annotations/
  	├── instances_train2017.json
  	└── instances_val2017.json
```

Train
``` sh
python main.py \
    --output_dir  /path/to/your/output/dir \
    -c config/Gaze-DINO/Gaze_DINO_swin.py \
    --options batch_size=1 \
    --coco_path /path/to/your/data/dir
    --resume path/to/your/pre-train/model.pth
```

Inference
``` sh
python mian.py \
    --output_dir  /path/to/your/output/dir \
    -c config/Gaze-DINO/Gaze_DINO_swin.py \
    --options batch_size=1 \
    --coco_path /path/to/your/data/dir
    --resume path/to/your/pre-train/model.pth
    --eval
```
## Performance
Our comprehensive tests confirm that Gaze-DETR surpasses existing leading methods, showcasing remarkable improvements in detection accuracy and generalizability.

| Method                   | backbone | AP<sub>0.2:0.5 | AP<sub>0.2 | AP<sub>0.5 |     AR    |
|--------------------------|----------|:--------------:|:----------:|:----------:|:---------:|
| RetinaNet (ICCV 2017)    | Resnet50 |      0.466     |    0.533   |    0.326   |   0.850   |
| YoloV8                   | Resnet50 |      0.482     |    0.587   |    0.333   |   0.866   |
| DN-DETR (CVPR 2022 Oral) | Resnet50 |      0.535     |    0.657   |    0.330   |   0.912   |
| DINO (ICLR 2023)         |  Swin-L  |      0.646     |    0.711   |    0.561   | **0.988** |
| Gaze-DN-DETR             | Resnet50 |      0.554     |    0.690   |    0.335   |   0.878   |
| Gaze-DINO                |  Swin-L  |    **0.687**   |  **0.755** |  **0.585** | **0.988** |

More experiment results are shown in [our paper](https://arxiv.org/pdf/2405.09463).

More test will come soon.

## Citation
Use this bibtex to cite this repository:
```
@misc{kong2024gazedetr,
      title={Gaze-DETR: Using Expert Gaze to Reduce False Positives in Vulvovaginal Candidiasis Screening}, 
      author={Yan Kong and Sheng Wang and Jiangdong Cai and Zihao Zhao and Zhenrong Shen and Yonghao Li and Manman Fei and Qian Wang},
      year={2024},
      eprint={2405.09463},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
