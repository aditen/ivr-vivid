export type YoloClassName =
    'person'
    | 'bicycle'
    | 'car'
    | 'motorcycle'
    | 'airplane'
    | 'bus'
    | 'train'
    | 'truck'
    | 'boat'
    | 'traffic light'
    |
    'fire hydrant'
    | 'stop sign'
    | 'parking meter'
    | 'bench'
    | 'bird'
    | 'cat'
    | 'dog'
    | 'horse'
    | 'sheep'
    | 'cow'
    |
    'elephant'
    | 'bear'
    | 'zebra'
    | 'giraffe'
    | 'backpack'
    | 'umbrella'
    | 'handbag'
    | 'tie'
    | 'suitcase'
    | 'frisbee'
    |
    'skis'
    | 'snowboard'
    | 'sports ball'
    | 'kite'
    | 'baseball bat'
    | 'baseball glove'
    | 'skateboard'
    | 'surfboard'
    |
    'tennis racket'
    | 'bottle'
    | 'wine glass'
    | 'cup'
    | 'fork'
    | 'knife'
    | 'spoon'
    | 'bowl'
    | 'banana'
    | 'apple'
    |
    'sandwich'
    | 'orange'
    | 'broccoli'
    | 'carrot'
    | 'hot dog'
    | 'pizza'
    | 'donut'
    | 'cake'
    | 'chair'
    | 'couch'
    |
    'potted plant'
    | 'bed'
    | 'dining table'
    | 'toilet'
    | 'tv'
    | 'laptop'
    | 'mouse'
    | 'remote'
    | 'keyboard'
    | 'cell phone'
    |
    'microwave'
    | 'oven'
    | 'toaster'
    | 'sink'
    | 'refrigerator'
    | 'book'
    | 'clock'
    | 'vase'
    | 'scissors'
    | 'teddy bear'
    |
    'hair drier'
    | 'toothbrush';

export const YoloTypesAsArray = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'];

export const YoloClassImages = {
    "person": "https://image.spreadshirtmedia.net/image-server/v1/mp/products/T1302A1MPA3321PT24X0Y0D170309227FS1911/views/1,width=378,height=378,appearanceId=1,backgroundColor=F2F2F2/strichmaennchen-design-stickman-trend-geschenkidee-poster.jpg",
    "apple": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1200px-Apple_logo_black.svg.png",
    'car': "https://upload.wikimedia.org/wikipedia/commons/0/0b/Fernando_Alonso_2006_Canada.jpg",
    'boat': "https://www.electrive.net/wp-content/uploads/2019/08/wider-165-mega-yacht-nidec.jpg",
    'bird': "data:image/jpeg;base64,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"
};
