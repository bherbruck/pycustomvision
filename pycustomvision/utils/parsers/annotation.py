# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = annotations_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Any, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Region:
    region_id: str
    tag_name: str
    created: str
    tag_id: str
    left: float
    top: float
    width: float
    height: float

    @staticmethod
    def from_dict(obj: Any) -> 'Region':
        assert isinstance(obj, dict)
        region_id = from_str(obj.get("regionId"))
        tag_name = from_str(obj.get("tagName"))
        created = from_str(obj.get("created"))
        tag_id = from_str(obj.get("tagId"))
        left = from_float(obj.get("left"))
        top = from_float(obj.get("top"))
        width = from_float(obj.get("width"))
        height = from_float(obj.get("height"))
        return Region(region_id, tag_name, created, tag_id, left, top, width, height)

    def to_dict(self) -> dict:
        result: dict = {}
        result["regionId"] = from_str(self.region_id)
        result["tagName"] = from_str(self.tag_name)
        result["created"] = from_str(self.created)
        result["tagId"] = from_str(self.tag_id)
        result["left"] = to_float(self.left)
        result["top"] = to_float(self.top)
        result["width"] = to_float(self.width)
        result["height"] = to_float(self.height)
        return result


@dataclass
class Tag:
    tag_id: str
    tag_name: str
    created: str

    @staticmethod
    def from_dict(obj: Any) -> 'Tag':
        assert isinstance(obj, dict)
        tag_id = from_str(obj.get("tagId"))
        tag_name = from_str(obj.get("tagName"))
        created = from_str(obj.get("created"))
        return Tag(tag_id, tag_name, created)

    def to_dict(self) -> dict:
        result: dict = {}
        result["tagId"] = from_str(self.tag_id)
        result["tagName"] = from_str(self.tag_name)
        result["created"] = from_str(self.created)
        return result


@dataclass
class Annotation:
    id: str
    created: str
    width: int
    height: int
    resized_image_uri: str
    thumbnail_uri: str
    original_image_uri: str
    tags: List[Tag]
    regions: List[Region]

    @staticmethod
    def from_dict(obj: Any) -> 'Annotation':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        created = from_str(obj.get("created"))
        width = from_int(obj.get("width"))
        height = from_int(obj.get("height"))
        resized_image_uri = from_str(obj.get("resizedImageUri"))
        thumbnail_uri = from_str(obj.get("thumbnailUri"))
        original_image_uri = from_str(obj.get("originalImageUri"))
        tags = from_list(Tag.from_dict, obj.get("tags"))
        regions = from_list(Region.from_dict, obj.get("regions"))
        return Annotation(id, created, width, height, resized_image_uri, thumbnail_uri, original_image_uri, tags, regions)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["created"] = from_str(self.created)
        result["width"] = from_int(self.width)
        result["height"] = from_int(self.height)
        result["resizedImageUri"] = from_str(self.resized_image_uri)
        result["thumbnailUri"] = from_str(self.thumbnail_uri)
        result["originalImageUri"] = from_str(self.original_image_uri)
        result["tags"] = from_list(lambda x: to_class(Tag, x), self.tags)
        result["regions"] = from_list(
            lambda x: to_class(Region, x), self.regions)
        return result


def annotations_from_dict(s: Any) -> List[Annotation]:
    return from_list(Annotation.from_dict, s)


def annotations_to_dict(x: List[Annotation]) -> Any:
    return from_list(lambda x: to_class(Annotation, x), x)
