import json
import os


class ValidationError(Exception):
    """raised when something is fundamentally wrong."""


def make_reduced_dict(schema, original):
    """return a new dict based on a schema and a payload.
    Only the properties from the schema are put in this new dict."""
    return _make_reduced_dict(
        dictify(schema),
        dictify(original)
    )


def _make_reduced_dict(schema, original):
    new_dict = {}
    if schema['type'] != 'object':
        raise ValidationError('JSON Schema needs to define an object')
    required = schema.get('required', [])
    for key, prop in schema['properties'].items():
        if prop.get('type') == 'object':
            # Need to recurse, but only if it exists.
            if key in original:
                new_dict[key] = _make_reduced_dict(
                    prop,
                    original[key]
                )
        else:
            if key in required or key in original:
                try:
                    value = original[key]
                except KeyError:
                    raise ValidationError('{} is required'.format(key))
                new_dict[key] = value
    return new_dict


def dictify(thing):
    if isinstance(thing, dict):
        return thing

    if hasattr(thing, 'read') and callable(thing.read):
        thing = json.load(thing)
    elif os.path.isfile(thing):
        thing = json.load(open(thing))
    else:
        thing = json.loads(thing)
    assert isinstance(thing, dict)
    return thing


def cli(args):
    if not args or '--help' in args:
        print('Usage: {} SCHEMAFILE.json SAMPLEFILE.json'.format(
            __file__
        ))
        return 0

    print(json.dumps(
        make_reduced_dict(
            args[0],
            args[1],
        ),
        indent=4,
        sort_keys=True,
    ))
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(cli(sys.argv[1:]))
