"""Encrypt & Decrypt module for the TP-Link smart device plugins"""


import codecs
from struct import pack
from expliot.core.vendors.tplink import KEY


# Encryption and Decryption of TP-Link Smart Home Protocol
def encrypt(string):
    """
    Encryption of input string which is in JSON format.
    Uses XOR cypher to encrypt.

    Args:
        string(str): The JSON string to encrypt.

    Returns(bytes):
        Data to be sent to the TP-Link smart devices.
    """

    # Step 1 : Add length of message as header
    result = pack(">I", len(string))
    result = list(map(hex, result))
    key = KEY
    # Step 2 : Using XOR Autokey Cipher
    for iter_string in string:
        current_char = key ^ ord(iter_string)
        key = current_char
        result.append(hex(current_char))

    # Step 3 : Convert hex array to hex string
    # 0x prefix for Hex not required
    # Example: ["0x0","0x21"] => "0021"
    result = [iter_result[2:] for iter_result in result]
    result = [ir if len(ir) == 2 else "0" + ir for ir in result]
    result = "".join(result)

    # Step 3 : Convert hex string to bytes
    result = bytes(bytearray.fromhex(result))
    return result


def decrypt(string):
    """
    Decryption of the hex string which was encrypted using XOR cypher.

    Args:
        string(str): Hex string to be decrypted, without the 0x prefix. Ex. 2a3b4cddeeff11.

    Returns(str):
        Decrypted string which is in JSON format.

    """

    result = ""
    string = codecs.decode(string, "hex")
    key = KEY

    # Skipping initial 4 byte of message header
    string = string[4:]
    string = "".join(map(chr, string))

    # Using XOR Autokey Cipher to decrypt
    for iter_string in string:
        current_char = key ^ ord(iter_string)
        key = ord(iter_string)
        result += chr(current_char)

    return result
