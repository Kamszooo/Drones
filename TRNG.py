import ctypes
from ctypes import wintypes

def generate_TRN(length):
    # Load the required Windows DLL
    bcrypt = ctypes.WinDLL('bcrypt.dll')

    # Define the BCryptGenRandom function signature
    bcrypt.BCryptGenRandom.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_uint8), wintypes.ULONG, wintypes.ULONG]
    bcrypt.BCryptGenRandom.restype = wintypes.BOOL

    provider = wintypes.HANDLE()
    buffer = (ctypes.c_uint8 * length)()

    try:
        # Open a handle to the default RNG algorithm provider
        bcrypt.BCryptOpenAlgorithmProvider(ctypes.byref(provider), 'RNG', None, 0)

        # Generate random bytes
        bcrypt.BCryptGenRandom(provider, buffer, length, 0)

        return int.from_bytes(bytes(buffer), byteorder='little')
    finally:
        # Close the handle to the provider
        if provider:
            bcrypt.BCryptCloseAlgorithmProvider(provider, 0)