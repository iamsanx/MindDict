import json
from minddict import MindDict


def test_repr_and_init():
    d = MindDict(a=1, b=2)
    assert isinstance(d, MindDict)
    assert "a=1" in repr(d)
    assert "b=2" in repr(d)
    # dot-access attribute assignment check
    assert d.a == 1
    assert d["b"] == 2


def test_to_and_from_json():
    d = MindDict(a=1, b=2)
    json_str = d.to_json(indent=2)
    assert isinstance(json_str, str)
    assert json.loads(json_str) == {"a": 1, "b": 2}

    d2 = MindDict.from_json(json_str)
    assert isinstance(d2, MindDict)
    assert d2 == d


def test_filter_basic():
    d = MindDict(a=1, b=2, c=3)
    result = d.filter(lambda k, v: v > 1)
    assert result == {"b": 2, "c": 3}
    assert d == {"a": 1, "b": 2, "c": 3}


def test_filter_empty_result():
    d = MindDict(x=1, y=2)
    res = d.filter(lambda k, v: v > 10)
    assert res == {}


def test_map_transform():
    d = MindDict(a=1, b=2)
    result = d.map(lambda k, v: (k.upper(), v * 10))
    assert result == {"A": 10, "B": 20}
    assert "A" not in d


def test_map_conflicting_keys():
    d = MindDict(a=1, b=2)
    result = d.map(lambda k, v: ("X", v))
    assert result == {"X": 2}


def test_invert_basic():
    d = MindDict(a=1, b=2)
    inv = d.invert()
    assert inv == {1: "a", 2: "b"}


def test_invert_with_duplicate_values():
    d = MindDict(a=1, b=1)
    inv = d.invert()
    assert inv == {1: "b"}


def test_diff_non_strict():
    a = MindDict(a=1, b=2)
    b = MindDict(a=1, b=3, c=4)
    diff = a.diff(b)
    assert diff == {"b": (2, 3), "c": (None, 4)}


def test_diff_strict():
    a = MindDict(a=1, b=2)
    b = MindDict(a=1, b=3, c=4)
    diff = a.diff(b, strict=True)
    assert diff == {"b": (2, 3)}


def test_flatten_basic():
    d = MindDict({
        "user": {"name": "Alice", "info": {"age": 30}},
        "active": True,
    })
    flat = d.flatten()
    assert flat == {
        "user.name": "Alice",
        "user.info.age": 30,
        "active": True,
    }


def test_unflatten_basic():
    d = MindDict({
        "user.name": "Alice",
        "user.info.age": 30,
        "active": True,
    })
    nested = d.unflatten()
    assert nested["user"]["info"]["age"] == 30
    assert nested["active"] is True


def test_flatten_then_unflatten_roundtrip():
    original = MindDict({
        "user": {"name": "Bob", "info": {"city": "Paris"}},
        "active": True,
    })
    flat = original.flatten()
    rebuilt = flat.unflatten()
    assert rebuilt == original


def test_merge_basic():
    a = MindDict(a=1, b=2)
    b = MindDict(b=3, c=4)
    merged = a.merge(b)
    assert merged == {"a": 1, "b": 3, "c": 4}
    assert a == {"a": 1, "b": 2}


def test_merge_with_empty():
    a = MindDict(a=1)
    b = MindDict()
    merged = a.merge(b)
    assert merged == {"a": 1}


def test_empty_minddict_behavior():
    d = MindDict()
    assert d.filter(lambda k, v: True) == {}
    assert d.map(lambda k, v: (k, v)) == {}
    assert d.diff(MindDict()) == {}
    assert d.flatten() == {}
    assert d.unflatten() == {}
    assert d.merge(MindDict()) == {}
