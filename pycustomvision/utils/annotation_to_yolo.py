from typing import Dict, Tuple

from pycustomvision.utils.parsers.annotation import Annotation, Region


def key_from_value(d: Dict, value):
    return [k for k, v in d.items() if v == value][0]

# convert xywh to cxcywh
def yolo_bbox(bbox: Region) -> Tuple[str, str, str, str]:
    return map(str, (bbox.left + bbox.width / 2,
                     bbox.top + bbox.height / 2,
                     bbox.width,
                     bbox.height))


def annotation_to_yolo(annotation: Annotation, labels: Dict[int, str]) -> str:
    lines = [f'{key_from_value(labels, bbox.tag_name)} {" ".join(yolo_bbox(bbox))}'
             for bbox in annotation.regions]
    return '\n'.join(lines)
