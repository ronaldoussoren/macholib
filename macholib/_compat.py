"""
2to3 compatibility routines
"""
import sys

def B(value):
    """
    Usage B("literal"), use this instead of b"literal" to ensure
    python <= 2.5 compatibility.
    """
    return value.encode("latin")

try:
    from __builtin__ import bytes
except ImportError:
    # Python 2.5 or earlier
    bytes = str
