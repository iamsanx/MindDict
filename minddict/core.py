import json
from typing import Callable, Any, Self, Tuple

class MindDict(dict):
    """
    A smarter dictionary class that extends Python's built-in dict with
    convenient transformation, filtering, and comparison utilities.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a MindDict instance, optionally from positional and keyword arguments.

        Parameters
        ----------
        *args : Any
            Positional arguments passed to the standard `dict` constructor.
        **kwargs : Any
            Keyword arguments used to populate the MindDict.
            Each key becomes both a dictionary key and an attribute of the instance.

        Returns
        -------
        None

        Behavior
        --------
        - All key/value pairs are stored as in a normal dict.
        - Each key is also set as an attribute on the object for dot-access (`obj.key`).
        - Non-string keys are supported as in `dict`, but are not exposed as attributes.
        - Existing attributes of the class (like methods) are not overwritten.

        Examples
        --------
        >>> d = MindDict(a=1, b=2)
        >>> d.a
        1
        >>> d['b']
        2
        >>> MindDict({'x': 10}, y=20)
        MindDict(x=10, y=20)
        """
        super().__init__(*args, **kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the MindDict.

        Returns
        -------
        str
            A formatted string showing all key/value pairs.

        Behavior
        --------
        - Displays items as `MindDict(key=value, ...)`.
        - Uses `repr()` for each value to show its literal form.
        - The output is concise and intended for debugging, not serialization.

        Examples
        --------
        >>> MindDict(a=1, b='test')
        MindDict(a=1, b='test')
        >>> MindDict(x=[1, 2]).__repr__()
        "MindDict(x=[1, 2])"
        """
        items = ', '.join(f"{k}={v!r}" for k, v in self.items())
        return f"MindDict({items})"
    
    def to_json(self, indent: int = 0) -> dict:
        return json.dumps(self, indent=indent)
    
    @classmethod
    def from_json(cls, data: str) -> Self:
        return cls(json.loads(data))

    
    def filter(self, fn: Callable[[Any, Any], bool]) -> Self:
        """
        Return a new MindDict containing only key/value pairs where
        the given function returns True.

        Parameters
        ----------
        fn : Callable[[Any, Any], bool]
            A predicate function that takes (key, value) and returns True
            if the pair should be included in the result.

        Returns
        -------
        Self
            A new MindDict instance containing only the items that
            satisfy the given condition.

        Behavior
        --------
        - Iterates over each key/value pair in order.
        - Keeps only items where `fn(key, value)` evaluates to True.
        - The order of elements is preserved from the original dictionary.
        - Exceptions raised by `fn` are propagated.

        Examples
        --------
        >>> d = MindDict(a=1, b=2, c=3)
        >>> d.filter(lambda k, v: v > 1)
        MindDict({'b': 2, 'c': 3})
        """
        return MindDict({k: v for k, v in self.items() if fn(k, v)})
    
    def map(self, fn: Callable[[Any, Any], Tuple[Any, Any]]) -> Self:
        """
        Transform each key/value pair using the provided function and return a new MindDict.

        Parameters
        ----------
        fn : Callable[[Any, Any], Tuple[Any, Any]]
            A function that receives (key, value) for each item in this mapping and
            returns a tuple (new_key, new_value). The returned pairs are used to
            construct the resulting MindDict.
            
        Returns
        -------
        Self
            A new MindDict instance containing the transformed key/value pairs.

        Behavior
        --------
        - The transformation is applied to every item in iteration order.
        - If multiple input items produce the same new_key, the last transformed
          pair encountered will determine the final value for that key.
        - Exceptions raised by `fn` are propagated to the caller.

        Examples
        --------
        >>> d = MindDict({'a': 1, 'b': 2})
        >>> d.map(lambda k, v: (k.upper(), v * 10))
        MindDict({'A': 10, 'B': 20})
        """
        result = {}
        for k, v in self.items():
            new_key, new_value = fn(k, v)
            result[new_key] = new_value
        return MindDict(result)
    
    def invert(self) -> Self:
        """
        Return a new MindDict with keys and values swapped.

        Returns
        -------
        Self
            A new MindDict where each key becomes its corresponding value,
            and each value becomes its corresponding key.

        Behavior
        --------
        - Only works correctly if all values in the original MindDict are hashable.
        - If multiple keys share the same value, the last encountered key
          will overwrite previous ones.
        - The method does not modify the original MindDict.

        Examples
        --------
        >>> d = MindDict(a=1, b=2)
        >>> d.invert()
        MindDict({1: 'a', 2: 'b'})
        """
        return MindDict({v: k for k, v in self.items()})
    
    def diff(self, other: Self, strict: bool = False) -> Self:
        """
        Compare two MindDict objects and return their differences.

        Parameters
        ----------
        other : Self
            Another MindDict (or dict) to compare against the current instance.
        strict : bool, optional
            If True, only include keys present in both MindDicts with different values.
            If False (default), include all differing keys (including missing ones).

        Returns
        -------
        Self
            A new MindDict where each key maps to a tuple (value_in_self, value_in_other)
            representing the detected difference.

        Behavior
        --------
        - A key is included if its value differs between the two mappings.
        - In non-strict mode, keys missing from either side are also included.
        - The comparison is shallow (values are compared directly).

        Examples
        --------
        >>> a = MindDict(a=1, b=2)
        >>> b = MindDict(a=1, b=3, c=4)
        >>> a.diff(b)
        MindDict({'b': (2, 3), 'c': (None, 4)})
        >>> a.diff(b, strict=True)
        MindDict({'b': (2, 3)})
        """
        result = {}
        keys = self.keys() | other.keys()
        
        for k in keys:
            v1, v2 = self.get(k), other.get(k)
            if v1 != v2:
                if strict and v1 and v2:
                    result[k] = (v1, v2)
                if not strict:
                    result[k] = (v1, v2)
            
        return MindDict(result)
    
    def flatten(self, separator: str = ".") -> Self:
        """
        Flatten nested dictionaries into a single-level MindDict
        with keys representing the hierarchy joined by a separator.

        Parameters
        ----------
        separator : str, optional
            String used to join nested key names.
            Defaults to "." (dot notation).

        Returns
        -------
        Self
            A new MindDict instance containing flattened key/value pairs.

        Behavior
        --------
        - Iteratively traverses nested dictionaries and flattens them into one level.
        - The resulting keys are concatenated using the given separator.
        - Deeply nested structures are processed until no nested dict remains.
        - Mutates a temporary copy internally, but the returned MindDict is new.
        - Nested non-dict objects (lists, sets, etc.) are left unchanged.

        Examples
        --------
        >>> d = MindDict({
        ...     'user': {'name': 'Fabio', 'info': {'age': 24, 'city': 'Nice'}},
        ...     'active': True
        ... })
        >>> d.flatten()
        MindDict({
        ...     'user.name': 'Fabio',
        ...     'user.info.age': 24,
        ...     'user.info.city': 'Nice',
        ...     'active': True
        ... })
        """
        result = {}
        
        def _flatten_dict(d: dict, parent_key: str = "") -> dict:
            items = {}
            for k, v in d.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.update(_flatten_dict(v, new_key))
                else:
                    items[new_key] = v
            return items

        return MindDict(_flatten_dict(self))

    def unflatten(self, separator: str = ".") -> Self:
        """
        Convert a flattened MindDict back into a nested structure
        based on the specified separator in the keys.

        Parameters
        ----------
        separator : str, optional
            String used to split keys into nested levels.
            Defaults to "." (dot notation).

        Returns
        -------
        Self
            A new MindDict instance with nested dictionaries reconstructed.

        Behavior
        --------
        - Iterates over each key/value pair in the flattened MindDict.
        - Splits keys by the specified separator to determine nesting.
        - Constructs nested dictionaries accordingly.
        - The original flattened MindDict remains unchanged.

        Examples
        --------
        >>> d = MindDict({
        ...     'user.name': 'Fabio',
        ...     'user.info.age': 24,
        ...     'user.info.city': 'Nice',
        ...     'active': True
        ... })
        >>> d.unflatten()
        MindDict({
        ...     'user': {
        ...         'name': 'Fabio',
        ...         'info': {'age': 24, 'city': 'Nice'}
        ...     },
        ...     'active': True
        ... })
        """
        result = {}
        
        for k, v in self.items():
            parts = k.split(separator)
            current = result
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = v
        
        return MindDict(result)
    
    def merge(self, other: Self) -> Self:
        """
        Merge another MindDict into this one, returning a new MindDict
        with combined key/value pairs.

        Parameters
        ----------
        other : Self
            Another MindDict (or dict) to merge with the current instance.

        Returns
        -------
        Self
            A new MindDict containing all key/value pairs from both
            MindDicts. In case of key conflicts, values from `other`
            will overwrite those in the current instance.

        Behavior
        --------
        - Combines all items from both MindDicts.
        - The order of items is preserved, with `other`'s items coming last.
        - The original MindDicts remain unchanged.

        Examples
        --------
        >>> a = MindDict(a=1, b=2)
        >>> b = MindDict(b=3, c=4)
        >>> a.merge(b)
        MindDict({'a': 1, 'b': 3, 'c': 4})
        """
        merged = MindDict(self)
        merged.update(other)
        return merged