from mynamedtuple import mynamedtuple


class DictTuple:
    def __init__(self, *args):
        if not args:
            raise AssertionError("No dictionaries provided.")

        self.dt = [arg for arg in args if arg]  # Filter out empty dictionaries
        if not self.dt:
            raise AssertionError("No non-empty dictionaries provided.")

        for arg in self.dt:
            if not isinstance(arg, dict):
                raise AssertionError(f"DictTuple init: {arg} is not a dictionary.")

    def __len__(self):
        # Number of distinct keys
        all_keys = set()
        for d in self.dt:
            all_keys.update(d.keys())
        return len(all_keys)

    def __bool__(self):
        # True if more than one dictionary, False otherwise
        return len(self.dt) > 1

    def __repr__(self):
        dict_reprs = ', '.join(f"{repr(d)}" for d in self.dt)
        return f"DictTuple({dict_reprs})"

    def __contains__(self, key):
        # Check if key is in any dictionary
        return any(key in d for d in self.dt)

    def __getitem__(self, key):
        # Get the value associated with key from the latest dictionary
        for d in reversed(self.dt):
            if key in d:
                return d[key]
        raise KeyError(f"Key {key} not found.")

    def __setitem__(self, key, value):
        # Update the latest dictionary or append a new one if key not found
        for d in reversed(self.dt):
            if key in d:
                d[key] = value
                return
        # Key not found, add a new dictionary with the key-value pair
        self.dt.append({key: value})

    def __delitem__(self, key):
        # Delete the key from all dictionaries
        found = False
        for d in self.dt:
            if key in d:
                del d[key]
                found = True

        if not found:
            raise KeyError(f"Key {key} not found.")

    def __call__(self, key):
        # Return a list of values associated with key
        return [d[key] for d in self.dt if key in d]

    def __iter__(self):
        latest_index = {}

        for i, d in enumerate(reversed(self.dt)):
            for key in d:
                latest_index[key] = len(self.dt) - 1 - i

        sorted_keys = sorted(latest_index.keys())
        return iter(sorted_keys)

    def __eq__(self, other):
        if isinstance(other, dict):
            # Collect all keys in this DictTuple
            all_keys = set()
            for d in self.dt:
                all_keys.update(d.keys())

            # Check if all keys in this DictTuple are in the other dictionary
            if not all_keys.issubset(other.keys()):
                return False

            # Compare values for each key
            for key in all_keys:
                try:
                    if self[key] != other[key]:
                        return False
                except KeyError:
                    return False

            return True

        if isinstance(other, DictTuple):
            # Collect all keys in both DictTuples
            all_keys = set()
            for d in self.dt:
                all_keys.update(d.keys())
            for d in other.dt:
                all_keys.update(d.keys())

            # Compare values for each key
            for key in all_keys:
                try:
                    if self[key] != other[key]:
                        return False
                except KeyError:
                    return False

            return True

        return False

    def __add__(self, other):
        if isinstance(other, dict):
            if not other:
                return self
            return DictTuple(*self.dt, other)
        if isinstance(other, DictTuple):
            combined_dicts = [d for d in self.dt] + [d for d in other.dt]
            return DictTuple(*combined_dicts)
        raise TypeError(f"Unsupported operand type(s) for +: 'DictTuple' and '{type(other).__name__}'")

    def __radd__(self, other):
        if isinstance(other, dict):
            if not other:
                return self
            return DictTuple(other, *self.dt)
        if isinstance(other, DictTuple):
            combined_dicts = [d for d in other.dt] + [d for d in self.dt]
            return DictTuple(*combined_dicts)
        raise TypeError(f"Unsupported operand type(s) for +: '{type(other).__name__}' and 'DictTuple'")

    def __setattr__(self, name, value):
        if name == 'dt':
            super().__setattr__(name, value)
        else:
            raise AssertionError(f"Cannot add attribute {name} to DictTuple")

    def __dict__(self):
        # Convert DictTuple to a single dictionary for easier comparison
        combined_dict = {}
        for d in self.dt:
            combined_dict.update(d)
        return combined_dict


if __name__ == "__main__":
    Coordinate = mynamedtuple('Coordinate', 'x y')

    # Test creation and initialization
    print("Testing initialization...")
    try:
        d1 = DictTuple({'c1': Coordinate(1, 2)}, {'c1': Coordinate(3, 4)})
        print("Initialized DictTuple d1:", repr(d1))
    except AssertionError as e:
        print(f"Error during initialization: {e}")

    try:
        d2 = DictTuple({'c2': Coordinate(5, 6)})
        print("Initialized DictTuple d2:", repr(d2))
    except AssertionError as e:
        print(f"Error during initialization: {e}")

    try:
        d_invalid = DictTuple({})
    except AssertionError as e:
        print(f"Expected error: {e}")

    # Test len
    print("\nTesting len...")
    print("Number of distinct keys in d1:", len(d1))  # Expected: 1

    # Test bool
    print("\nTesting bool...")
    print("Boolean value of d1:", bool(d1))  # Expected: True

    # Test contains
    print("\nTesting contains...")
    print("'c1' in d1:", 'c1' in d1)  # Expected: True
    print("'c2' in d1:", 'c2' in d1)  # Expected: False

    # Test getitem
    print("\nTesting getitem...")
    try:
        print("d1['c1']:", d1['c1'])  # Expected: Coordinate(3, 4)
    except KeyError as e:
        print(f"Error: {e}")

    # Test setitem
    print("\nTesting setitem...")
    try:
        d1['c1'] = Coordinate(7, 8)
        print("After setting d1['c1']:",
              repr(d1))  # Expected: DictTuple({'c1': Coordinate(7, 8)}, {'c1': Coordinate(7, 8)})
    except KeyError as e:
        print(f"Error: {e}")

    # Test delitem
    print("\nTesting delitem...")
    try:
        del d1['c1']
        print("After deleting 'c1':", repr(d1))  # Expected: DictTuple({})
    except KeyError as e:
        print(f"Error: {e}")

    # Test call
    print("\nTesting call...")
    print("d1('c1'):", d1('c1'))  # Expected: []

    # Test iter
    print("\nTesting iter...")
    for key in d1:
        print("Key:", key)  # Expected: (No output as dict is empty)

    # Test equality
    print("\nTesting equality...")
    d3 = DictTuple({'c1': Coordinate(7, 8)}, {'c1': Coordinate(7, 8)})
    print("d1 == d3:", d1 == d3)  # Expected: True
    print("d1 == d2:", d1 == d2)  # Expected: False
    print("d1 == {'c1': Coordinate(7, 8)}:", d1 == {'c1': Coordinate(7, 8)})  # Expected: True

    # Test addition
    print("\nTesting addition...")
    try:
        d4 = d1 + d2
        print("d1 + d2:", repr(
            d4))  # Expected: DictTuple({'c1': Coordinate(7, 8)}, {'c1': Coordinate(7, 8)}, {'c2': Coordinate(5, 6)})
    except TypeError as e:
        print(f"Error: {e}")

    try:
        d5 = d2 + {'c3': Coordinate(9, 10)}
        print("d2 + {'c3': Coordinate(9, 10)}:",
              repr(d5))  # Expected: DictTuple({'c2': Coordinate(5, 6)}, {'c3': Coordinate(9, 10)})
    except TypeError as e:
        print(f"Error: {e}")

    try:
        d6 = {'c4': Coordinate(11, 12)} + d1
        print("{'c4': Coordinate(11, 12)} + d1:", repr(
            d6))  # Expected: DictTuple({'c4': Coordinate(11, 12)}, {'c1': Coordinate(7, 8)}, {'c1': Coordinate(7, 8)})
    except TypeError as e:
        print(f"Error: {e}")

    # Test setting an attribute (should raise an exception)
    print("\nTesting setting attribute...")
    try:
        d1.new_attr = "value"
    except AssertionError as e:
        print(f"Expected error: {e}")
