from typing import Dict

from pycustomvision.utils.parsers.annotation import Annotation


def key_from_value(d: Dict, value):
    return [k for k, v in d.items() if v == value][0]


def annotation_to_yolo(annotation: Annotation, labels: Dict[int, str]) -> str:
    lines = [f'{key_from_value(labels, bbox.tag_name)} {bbox.left} {bbox.top} {bbox.width} {bbox.height}'
             for bbox in annotation.regions]
    return '\n'.join(lines)
