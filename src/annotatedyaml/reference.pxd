from .objects cimport NodeDictClass, NodeListClass, NodeStrClass

cpdef _add_reference_to_node_dict_class(
    NodeDictClass obj,
    object loader,
    object node
)

cpdef _add_reference_to_node_list_class(
    NodeListClass obj,
    object loader,
    object node
)

cpdef _add_reference_to_node_str_class(
    NodeStrClass obj,
    object loader,
    object node
)
