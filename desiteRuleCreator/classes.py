from PySide6.QtWidgets import QTreeWidget,QTreeWidgetItem,QAbstractItemView
from PySide6.QtGui import QDropEvent
from uuid import uuid4


def attributes_to_psetdict(attributes):
    pset_dict = {}
    for el in attributes:
        pset = el.propertySet
        if pset in pset_dict.keys():
            list = pset_dict[pset]
            list.append(el)
        else:
            pset_dict[pset] = [el]

    return pset_dict

def inherited_attributes(obj):
    def recursion(attribute_dict,obj):
        attributes = obj.attributes

        if attributes:
            attribute_dict[obj] = attributes

        parent = obj.parent
        if parent is not None:
            attribute_dict = recursion(attribute_dict, parent)
        return attribute_dict

    attribute_dict = dict()
    if obj.parent is not None:
        attribute_dict = recursion(attribute_dict,obj.parent)
    return attribute_dict

class PropertySet:
    def __init__(self, name:str):
        self._name = name
        self._attributes = list()  # attribute_name:value
        self._object = None

    @property
    def object(self):
        return self._object

    @object.setter
    def object(self, value):
        self._object = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value:str):
        self._name = value

    @property
    def attributes(self) -> list:
        return self._attributes

    @attributes.setter
    def attributes(self, value: dict):
        self._attributes = value

    def add_attribute(self, value):
        self._attributes.append(value)

    def remove_attribute(self, value):
        self._attributes.pop(self._attributes.index(value))


class Attribute:
    def __init__(self,propertySet:PropertySet, name:str, value,value_type, data_type = "xs:string"):
        self._name = name
        self._value = value
        self._propertySet = propertySet
        self._value_type = value_type
        self._data_type = data_type
        self._object = None
        propertySet.add_attribute(self)
        self._is_shared = False

    def __str__(self):
        text = f"{self.propertySet.name} : {self.name} = {self.value}"
        return text

    @property
    def is_shared(self):
        return self._is_shared

    @is_shared.setter
    def is_shared(self,value:bool):
        self._is_shared = value

    @property
    def object(self):
        return self._object

    @object.setter
    def object(self,value):
        self._object = value
        self.propertySet.object = self._object


    @property
    def name(self)->str:
        return self._name

    @name.setter
    def name(self, value:str):
        self._name = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        new_value = []
        for el in value:
            el:str = el
            if "|" in el:
                el = el.split("|")
                for item in el:
                    new_value.append(item)
            else:
                new_value.append(el)
        print(new_value)
        self._value = new_value

    @property
    def value_type(self)-> int :
        return self._value_type

    @value_type.setter
    def value_type(self, value: int):
        self._value_type = value

    @property
    def data_type(self) -> int:
        return self._data_type

    @data_type.setter
    def data_type(self, value: int):
        self._data_type = value

    @property
    def propertySet(self)->PropertySet:
        return self._propertySet

    @propertySet.setter
    def propertySet(self, value:PropertySet):
        self.propertySet.remove_attribute(self)
        value.add_attribute(self)
        self._propertySet = value

    def is_equal(self,attribute):
        equal = True

        if self.name != attribute.name:
            equal = False

        if self.value != attribute.value:
            equal = False

        if self.propertySet.name != attribute.propertySet.name:
            equal = False

        if equal:
            return True

    def delete(self):
        self.object.remove_attribute(self)
        self.propertySet.remove_attribute(self)

# class Group:
#     iter = dict()
#     def __init__(self,name):
#         self._name = name
#         self._objects = []
#         self._parent = None
#         self._attributes = list()
#         self.identifier = uuid4()
#         self._inherited_attributes = None
#         self.iter[self.identifier] = self
#
#     @property
#     def inherited_attributes(self) -> list:
#         self._inherited_attributes = inherited_attributes(self)
#         return self._inherited_attributes
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, value):
#         self._name = value
#
#     def add_child(self,object):
#         self._objects.append(object)
#         object.parent = self
#
#     def remove_child(self,object):
#         self._objects.remove(object)
#         object.parent= None
#
#     @property
#     def parent(self):
#         return self._parent
#
#     @parent.setter
#     def parent(self, value):
#         self._parent = value
#
#     @property
#     def attributes(self) -> list[Attribute]:
#         return self._attributes
#
#     def add_attribute(self, attribute):
#         self._attributes.append(attribute)
#         attribute.object = self
#
#     def remove_attribute(self, attribute):
#         self._attributes.remove(attribute)
#
#     def delete(self):
#         self.iter.pop(self.identifier)
#         pass

class Object:
    iter = dict()

    def __init__(self, name, ident: Attribute,parent = None, is_concept = False):

        self._name = name
        self._identifier = ident
        self.iter[ident] = self
        self._parent = parent
        self._attributes = list()
        self._parent = None
        self._inherited_attributes = None
        self._is_concept = is_concept
        self._children = list()
    @property
    def is_concept(self):
        return  self._is_concept

    @is_concept.setter
    def is_concept(self,value:bool):
        self._is_concept = value

    @property
    def inherited_attributes(self) -> list:
        self._inherited_attributes = inherited_attributes(self)
        return self._inherited_attributes

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self,value):
        self._parent = value
        value.add_child(self)
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def identifier(self) -> Attribute:
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def attributes(self)->list[Attribute]:
        return self._attributes

    def add_attribute(self,attribute):
        self._attributes.append(attribute)
        attribute.object = self

    def remove_attribute(self,attribute):
        self._attributes.remove(attribute)

    @property
    def children(self):
        return self._children

    def add_child(self, object):
        self._children.append(object)

    def remove_child(self,object):
        self._children.remove(object)


    @property
    def psetNameDict(self):
        p_set_dict = attributes_to_psetdict(self._attributes)
        new_dict = {}
        for key in p_set_dict.keys():
            new_dict[key.name]=key

        return new_dict

    def delete(self):
        self.iter.pop(self.identifier)


class CustomTree(QTreeWidget):
    def __init__(self, layout):
        super(CustomTree, self).__init__(layout)

    def dropEvent(self, event:QDropEvent) -> None:

        selected_items = self.selectedItems()

        if self.dropIndicatorPosition() == QAbstractItemView.DropIndicatorPosition.OnItem:
            droped_on_item = self.itemFromIndex(self.indexAt(event.pos()))
            object = droped_on_item.object

            if isinstance(object, Group):
                super(CustomTree, self).dropEvent(event)

        else:
            super(CustomTree, self).dropEvent(event)

        for el in selected_items:
            object = el.object
            parent = el.parent()
            if parent is not None:
                object.parent = parent.object
            else:
                object.parent = None


class CustomTreeItem(QTreeWidgetItem):
    def __init__(self, tree, object):
        super(CustomTreeItem, self).__init__(tree)
        self._object = object

    def addChild(self, child: QTreeWidgetItem) -> None:
        super(CustomTreeItem, self).addChild(child)
        self._object.add_child(child.object)

    @property
    def object(self):
        return self._object






