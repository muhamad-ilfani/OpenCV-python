import cv2
import argparse
import numpy as np
from imutils import paths
import os

ap = argparse.ArgumentParser()
#ap.add_argument('-i', '--image', required=True,
#                help = 'path to input image')
ap.add_argument('-c', '--config', required=True,
                help = 'path to yolo config file')
ap.add_argument('-w', '--weights', required=True,
                help = 'path to yolo pre-trained weights')
ap.add_argument('-cl', '--classes', required=True,
                help = 'path to text file containing class names')
args = ap.parse_args()


def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    #color = COLORS[class_id]
    if class_id == 0:
        color=(0, 0, 255)   #color BGR
    else:
        color=(0,0,0)
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

imagePaths=paths.list_images("frames")
banyak_orang=[]
for image in imagePaths:
    images = cv2.imread(image)
    Width = images.shape[1]
    Height = images.shape[0]
    scale = 0.00392

    classes = None

    with open(args.classes, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    #COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
    net = cv2.dnn.readNet(args.weights, args.config)
    blob = cv2.dnn.blobFromImage(images, scale, (416,416), (0,0,0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
        #print(class_ids)
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    #print((indices))
    hasil=0
    dst_folder = 'images'
    
    for i in range(len(image)):
        fname = image[i]
    
        dst_path = os.path.join(dst_folder, str(image))
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        dst_path = os.path.join(dst_path, fname)
    
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        if class_ids[i]==0:
            hasil=hasil+1
            draw_prediction(images, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
        cv2.imshow("object detection", images)
    ch = cv2.waitKey(1)
    if ch == 27:
        break
    elif ch == 32:
        while True:
            #cv2.waitKey(10)
            ch = cv2.waitKey(1)
            if ch == 32:
                break
    print(str(image), "terdapat", hasil, "orang")
    cv2.waitKey(200)
    #cv2.imwrite(dst_path + ".jpg", images)
    banyak_orang.append(hasil)
#    cv2.imwrite("object-detection.jpg", images)
jumlah_orang=pd.DataFrame(banyak_orang)
cv2.destroyAllWindows()