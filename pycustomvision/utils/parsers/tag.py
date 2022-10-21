# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = tags_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Tag:
    id: str
    name: str
    type: str
    image_count: int
    description: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Tag':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        name = from_str(obj.get("name"))
        type = from_str(obj.get("type"))
        image_count = from_int(obj.get("imageCount"))
        description = from_union([from_none, from_str], obj.get("description"))
        return Tag(id, name, type, image_count, description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["name"] = from_str(self.name)
        result["type"] = from_str(self.type)
        result["imageCount"] = from_int(self.image_count)
        result["description"] = from_union(
            [from_none, from_str], self.description)
        return result


def tags_from_dict(s: Any) -> List[Tag]:
    return from_list(Tag.from_dict, s)


def tags_to_dict(x: List[Tag]) -> Any:
    return from_list(lambda x: to_class(Tag, x), x)
