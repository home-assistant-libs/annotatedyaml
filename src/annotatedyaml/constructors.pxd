import cython

cdef object NodeDictClass
cdef object NodeStrClass

from .reference cimport _add_reference_to_node_class
