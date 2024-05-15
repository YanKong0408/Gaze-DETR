import cv2
import numpy as np

def gaze_process(gaze_seqs,img_name, image_shape, min_w= 128, min_h=128, GuassKernal=(159,159), thre=0.1):
    ### process gaze from gaze sequences to gaze boxes
    # input: 
    #   gaze_seqs:[[x, y], [x, y], ...]
    #   image: (w,h) the shape of image
    #   min_w: the min width of gaze_box, the gaze_box with (w < min_w and h < min_h) will be deleted
    #   min_h: the min height of gaze_box, the gaze_box with (w < min_w and h < min_h) will be deleted
    #   GuassKernal: (x, y) the size of GuassKernal, which represnets the focal area of a gaze_points, is 
    #       related to the distance from the eye to the screen and the resolution of the image
    #   thre: the threshould of gaze heatmap for gaze mask

    # output: 
    #   gaze_boxes:[[x, y, w, h], [x, y, w, h], ...]

    canvas = np.zeros((image_shape[0],image_shape[1]))
    for gaze in gaze_seqs:
        if gaze[0] < image_shape[0] and gaze[1] < image_shape[1]:
            canvas[gaze[0]][gaze[1]] += 1
    g = cv2.GaussianBlur(canvas, GuassKernal, 0, 0)
    g = cv2.normalize(g, None, alpha=0, beta=1,
                    norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    g_expend=cv2.applyColorMap((g*255).astype(np.uint8), cv2.COLORMAP_JET)
    img=cv2.imread(img_name)
    print(img.shape,g_expend.shape)
    heapmapimage = cv2.addWeighted(img,0.7,g_expend,0.3,0)
    print('d:\INbreast_det\ALL-Gaze-Heatmap\\'+img_name.rsplit("\\")[-1])
    cv2.imwrite('d:\\INbreast_det\\ALL-Gaze-Heatmap\\'+img_name.rsplit("\\")[-1],heapmapimage)
    _, thresholded_map = cv2.threshold(g.T, thre, 1, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(np.uint8(thresholded_map), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    gaze_boxs=[]
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > min_w or h > min_h:
            gaze_boxs.append([x,y,w,h])

    return gaze_boxs
    
    
def gaze_only(object_boxs, gaze_boxs, gaze_only_IoU=0.5):
    ### get gaze_only boxes
    # input:
    #   object_boxs: mouse bounded boxes
    #   gaze_boxs: gaze boxes before processed, represneted regions gazed
    #   gaze_only_IoU: float of (0,1), if gaze_only, gaze_boxes of smaller IoU with every mouse_bboxs will be remained

    # output:
    #   gaze_only_boxs: represent regions reviewed but not annotated
    gaze_only_boxs = []
    for gaze_box in gaze_boxs:
        discard_box = False
        for object_box in object_boxs:
            iou = calculate_iou(object_box, gaze_box)
            if iou > gaze_only_IoU:
                discard_box = True
                break
        if not discard_box:
            gaze_only_boxs.append(gaze_box)

    return gaze_only_boxs


def calculate_iou(box_a, box_b):
    x1_a, y1_a, w_a, h_a = box_a
    x1_b, y1_b, w_b, h_b = box_b

    x2_a = x1_a + w_a
    y2_a = y1_a + h_a
    x2_b = x1_b + w_b
    y2_b = y1_b + h_b

    x1_intersect = max(x1_a, x1_b)
    y1_intersect = max(y1_a, y1_b)
    x2_intersect = min(x2_a, x2_b)
    y2_intersect = min(y2_a, y2_b)

    intersection_area = max(0, x2_intersect - x1_intersect) * max(0, y2_intersect - y1_intersect)

    area_a = w_a * h_a
    area_b = w_b * h_b
    iou = intersection_area / (area_a + area_b - intersection_area)

    return iou