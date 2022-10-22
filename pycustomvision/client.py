from dataclasses import dataclass
from math import ceil
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Dict, List

import requests
import yaml

from pycustomvision.utils.annotation_to_yolo import annotation_to_yolo
from pycustomvision.utils.parsers.annotation import Annotation, annotations_from_dict
from pycustomvision.utils.parsers.tag import Tag, tags_from_dict


# dont't emit yaml tags
yaml.emitter.Emitter.process_tag = lambda self, *args, **kw: None


@dataclass
class YoloDatasetConfig:
    names: Dict[int, str]
    path: str
    train: str = 'train'
    val: str = 'val'
    test: str = 'test'


@dataclass
class CustomVisionClient:
    resource_name: str
    project_id: str
    subscription_key: str
    version: str = 'v3.3'
    annotation_chunk_size: int = 256

    @property
    def url(self):
        return f'https://{self.resource_name}.cognitiveservices.azure.com/customvision/{self.version}/Training/projects/{self.project_id}'

    @property
    def headers(self):
        return {'training-key': self.subscription_key}

    @property
    def config(self):
        return YoloDatasetConfig(names=[tag.name for tag in self.get_labels()])

    def get_image_count(self):
        res = requests.get(
            f'{self.url}/images/tagged/count', headers=self.headers)
        if res.status_code != 200:
            raise Exception(res.text)
        return int(res.text)

    def get_annotations(self, take=annotation_chunk_size, skip=0) -> List[Annotation]:
        res = requests.get(f'{self.url}/images/tagged',
                           headers=self.headers,
                           params={'take': take, 'skip': skip})
        if res.status_code != 200:
            raise Exception(res.text)
        data = res.json()
        annotations = annotations_from_dict(data)
        return annotations

    # for unpacking args
    def get_annotations_task(self, args):
        return self.get_annotations(*args)

    def get_all_annotations(self, chunk_size=annotation_chunk_size):
        image_count = self.get_image_count()
        threads = ceil(image_count / chunk_size)
        pool = ThreadPool(processes=threads)
        # get all annotations in parallel, hopefully don't hit rate limit
        args = [(chunk_size, i * chunk_size) for i in range(threads)]
        annotation_chunks = pool.map(self.get_annotations_task, args)
        all_annotations = [annotation for annotations in annotation_chunks
                           for annotation in annotations]
        assert len(all_annotations) == image_count
        return all_annotations

    def get_labels(self) -> List[Tag]:
        res = requests.get(f'{self.url}/tags', headers=self.headers)
        if res.status_code != 200:
            raise Exception(res.text)
        data = res.json()
        tags = tags_from_dict(data)
        return tags

    def get_image(self, url: str) -> bytes:
        res = requests.get(
            url,
            headers={
                'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
            },
            stream=True
        )
        if res.status_code != 200:
            raise Exception(res.text)
        return res.content

    def write_annotation(self, annotation: Annotation, path: str, names: Dict[int, str]):
        yolo_labels = annotation_to_yolo(
            annotation, labels=names)
        image = self.get_image(annotation.resized_image_uri)

        yolo_label_path = f'{path}/labels/{annotation.id}.txt'
        image_path = f'{path}/images/{annotation.id}.jpg'

        with open(yolo_label_path, 'w') as f:
            f.write(yolo_labels)

        with open(image_path, 'wb') as f:
            f.write(image)

    # for unpacking args
    def write_annotation_task(self, args):
        return self.write_annotation(*args)

    def export_dataset(self,
                       path: str = './dataset',
                       train: float = 0.8,
                       val: float = 0.1):
        labels = self.get_labels()
        config_path = f'{path}/data.yaml'

        Path(f'{path}').mkdir(parents=True, exist_ok=True)

        config = YoloDatasetConfig(
            names={i: tag.name for i, tag in enumerate(labels)}, path=path)

        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        annotations = self.get_all_annotations()

        # split into train, val, test
        total = len(annotations)
        train_count = ceil(total * train)
        val_count = ceil(total * val)

        train_annotations = annotations[:train_count]
        val_annotations = annotations[train_count:train_count + val_count]
        test_annotations = annotations[train_count + val_count:]

        # write annotations to files
        for annotations, annotation_path in zip(
            [train_annotations, val_annotations, test_annotations],
            [config.train, config.val, config.test]
        ):
            base_path = f'{path}/{annotation_path}'
            labels_path = f'{base_path}/labels'
            images_path = f'{base_path}/images'

            Path(labels_path).mkdir(parents=True, exist_ok=True)
            Path(images_path).mkdir(parents=True, exist_ok=True)

            pool = ThreadPool(processes=len(annotations))

            args = [(annotation, base_path, config.names)
                    for annotation in annotations]

            pool.map(self.write_annotation_task, args)
