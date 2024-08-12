import keyword


def mynamedtuple(type_name, field_names, mutable=False, defaults={}):
    # format field names
    if isinstance(field_names, str):
        field_names = [name.strip() for name in field_names.replace(',', ' ').split()]

    # Remove duplicates
    field_names = list(dict.fromkeys(field_names))

    # Validate field names
    if not all(name.isidentifier() and not keyword.iskeyword(name) for name in field_names):
        raise SyntaxError("Invalid field names: must be valid identifiers and not Python keywords.")

    # Validate type name
    if not type_name.isidentifier() or keyword.iskeyword(type_name):
        raise SyntaxError("Type name must be a valid identifier and not a Python keyword.")

    # Validate defaults
    if not all(name in field_names for name in defaults):
        raise SyntaxError("Defaults dictionary contains invalid field names.")

    # Define __init__ method
    init_params = ', '.join(f'{name}={defaults.get(name, None)}' for name in field_names)

    init_body = '\n        '.join(f'self.{name} = {name}' for name in field_names)

    init_method = f"""
    def __init__(self, {init_params}):
        self._fields = {field_names}
        self._mutable = {mutable}
        {init_body}
        self._initialized = True
        
    """

    repr_method = f"""
    def __repr__(self):
        field_representations = []
        for field in self._fields:
            value = getattr(self, field)
            field_representations.append(f"{{field}}={{value!r}}")
        fields_str = ', '.join(field_representations)
        return f"{{type(self).__name__}}({{fields_str}})"
    """

    # Define methods to get field values
    get_methods = '\n'.join(f"""
    def get_{name}(self):
        return self.{name}
    """ for name in field_names)

    # Define methods to handle indexing and replacement
    indexing_method = f"""
    def __getitem__(self, index):
        return getattr(self, {field_names}[index])
    """

    # Define __eq__ method
    eq_conditions = ' and '.join(f'self.{name} == other.{name}' for name in field_names)
    eq_method = f"""
    def __eq__(self, other):
        if not isinstance(other, {type_name}):
            return False
        return {eq_conditions}
    """

    asdict_method = f"""
    def _asdict(self):
        return {{name: getattr(self, name) for name in {field_names}}}
    """

    make_method = f"""
    @classmethod
    def _make(cls, values):
        if len(values) != len({field_names}):
            raise ValueError("The number of values does not match the number of fields.")
        return cls(*values)
    """

    replace_method = f"""
    def _replace(self, **kargs):
        if not self._mutable:
            new_values = {{k: kargs.get(k, getattr(self, k)) for k in {field_names}}}
            return {type_name}(**new_values)
        else:
            for k, v in kargs.items():
                if k in {field_names}:
                    setattr(self, k, v)
                else:
                    raise AttributeError(f'Invalid field name: {{k}}')
            return None
    """

    # Define __setattr__ method
    setattr_method = f"""
    def __setattr__(self, name, value):
        if not hasattr(self, '_initialized'):
            object.__setattr__(self, name, value)
        else:
            if not self._mutable and name in self._fields:
                raise AttributeError(f'Cannot modify field in immutable instance.')
            object.__setattr__(self, name, value)
    """

    # Define the class
    class_code = f"""
class {type_name}:
    
    {init_method}
    {repr_method}
    {get_methods}
    {indexing_method}
    {replace_method}
    {asdict_method}
    {make_method}
    {setattr_method}
    """
    # Execute the class string
    exec(class_code, globals())
    return globals()[type_name]


if __name__ == "__main__":

    coordinate = mynamedtuple('coordinate', 'x  age', mutable=False, defaults={'x': 10})
    p = coordinate(0, 0)

    try:
        # Test __repr__
        print("Representation:", repr(p))  # Should output: coordinate(x=0, age=0)

        # Test __getitem__
        print("Indexing:", p[0])  # Should output: 0

        # Test get methods
        print("Get x:", p.get_x())  # Should output: 0
        print("Get age:", p.get_age())  # Should output: 0

        # Test _asdict
        print("Asdict:", p._asdict())  # Should output: {'x': 0, 'age': 0}

        # Test _make
        p2 = coordinate._make([1, 2])
        print("Made from list:", repr(p2))  # Should output: coordinate(x=1, age=2)

        # Test _replace
        p3 = p._replace(x=5)
        print("Replaced x:", repr(p3))  # Should output: coordinate(x=5, age=0)

        # Test equality
        print("Equal to p2:", p == p2)  # Should output: False
        print("Equal to p3:", p == p3)  # Should output: False

        # Test error cases
        try:
            p[0] = 10  # Should raise an error as it's immutable
        except Exception as e:
            print("Indexing Error:", e)

        try:
            p.get_nonexistent()  # Should raise an error as method does not exist
        except Exception as e:
            print("Get Method Error:", e)

        try:
            p._replace(nonexistent=5)  # Should raise an error as field does not exist
        except Exception as e:
            print("Replace Method Error:", e)

        try:
            p._make([1])  # Should raise an error as values do not match fields
        except Exception as e:
            print("Make Method Error:", e)

        try:
            p.x = 20  # Should raise an error as it's immutable
        except Exception as e:
            print("Setattr Error:", e)

    except Exception as e:
        print("Error:", e)
