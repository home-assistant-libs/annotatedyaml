import cython


cdef class NodeListClass(list):

    cdef public object __config_file__
    cdef public object __line__

cdef class NodeStrClass(str):

    cdef public object __config_file__
    cdef public object __line__


cdef class NodeDictClass(dict):

    cdef public object __config_file__
    cdef public object __line__
