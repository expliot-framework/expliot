"""Common helpers for EXPLIoT."""


def bstr(byts):
    """
    Converts a bytes or a bytearray object to a str (string) preserving the
    binary data as is.

    Args:
        byts(bytes or bytearray): A bytes/bytearray object that needs to be
            converted to binary string.
    Returns:
        str: The converted string that preserves the binary data as is.
    """
    if byts.__class__ == bytes or byts.__class__ == bytearray:
        return "".join([chr(i) for i in byts])
    raise TypeError("bytes or bytearray object expected, but passed {}".format(
        byts.__class__.__name__)
    )


def recurse_list_dict(obj, callback, cbdata, rlevel=0):
    """
    Iterate through a list or a dict recursively and call the callback method
    at three places while iterating:
    1. If the object is a dict, for each key, value pair
        1. If the value is a dict or a list - callback()
        2. If the value is not a dict or a list i.e. a leaf - callback()
    2. If the object is a list, for each value
        1. If the value is not a dict or a list i.e. a leaf - callback()

    Args:
        obj (list or dict): The list or dict object that has to be recursively iterated.
        callback (method): The callback method that has to be called.
        cbdata (opaque): This is passed to the callback and is opaque for this method
        rlevel (int): Recursion level of the method. Call MUST NOT pass any value to this
                      as it is initialized to zero by default.

    Returns:
        Nothing

    Callback method prototype:
    def mycallback(cbdata, robj, rlevel, key=None, value=None):

    Args:
        cbdata (defined by callback): This callback method's specific data.
        robj (list or dict): The list or dict object at the specified recursion level.
                             This object may be updated by the callback, which means
                             the original obj passed to recurse_list_dict() will be
                             eventually updated.
        rlevel (int): The current recursion level at which this callback instance is called.
        key (str): The key if the robj is a dict.
        value (can be any type): 1. The value of the key if robj is a dict or
                                 2. A value from the robj if it is a list
    Returns:
        Nothing
    """
    if obj.__class__ == dict:
        for key, value in obj.items():
            if (value.__class__ == dict) or (value.__class__ == list):
                callback(cbdata, obj, rlevel, key=key, value=value)
                recurse_list_dict(value, callback, cbdata, rlevel=(rlevel + 1))
            else:
                callback(cbdata, obj, rlevel, key=key, value=value)
    elif obj.__class__ == list:
        for value in obj:
            if (value.__class__ == dict) or (value.__class__ == list):
                recurse_list_dict(value, callback, cbdata, rlevel=(rlevel + 1))
            else:
                callback(cbdata, obj, rlevel, value=value)
