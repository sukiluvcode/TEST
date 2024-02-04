import json
import random
from typing import List
from collections import namedtuple

import streamlit as st
import pandas as pd
from pydantic import create_model, BaseModel, Field


DictWrapper = namedtuple("DictWrapper", ['name', 'type', 'description', 'is_array', 'field_of', 'depth'])
PrimalFieldWrapper = namedtuple("PrimalFieldWrapper", ['name', 'type', 'description', 'is_array'])

class DynamicPydantic:
    def __init__(self, base_model: BaseModel):
        self.base_model = base_model
        self.field_of = "Unit"
    
    def add_field(self, primal_field_wrapper: PrimalFieldWrapper, dict_wrappers: List[DictWrapper] = None):
        if primal_field_wrapper.type == "object":
            type_annoatation = self.build_block(dict_wrappers)
        else:
            type_annoatation = primal_field_wrapper.type
        if primal_field_wrapper.is_array:
            type_annoatation = List[type_annoatation]
    
        self.base_model = create_model(
            self.field_of,
            __base__=self.base_model,
            **{
                primal_field_wrapper.name: (type_annoatation, Field(None, description=primal_field_wrapper.description))
            }
        )

    def build_block(self, dict_wrappers: List[DictWrapper]) -> BaseModel:
        # TODO: can apply recursive logic to this, try it out!
        """only be called when user want to use nested structure"""
        annoatation_dict = {}
        #  dict_wrapper = [{"name": "unit", "type": "str", "description": "unit of property", "depth": 1}, {"name": "odd", "type": "object", "description": "odd", "depth": 1}, {"field_of": "odd", "name": "boo", "type": "str", "description": "boo", "depth": 2}]
        df = pd.DataFrame(dict_wrappers)
        grouped = df.groupby('field_of')
        df_for_each = [df for _, df in grouped] # collapse primal dataframe to small ones based on field_of
        df_sorted: List[pd.DataFrame] = sorted(df_for_each, key=lambda x: x.depth.iloc[0], reverse=True) # sort df by depth
        for df in df_sorted:
            field_of: str = df.field_of.iloc[0]
            field_definitions = {}
            for row in df.itertuples(index=False):
                if row.type == 'object':
                    type_ = annoatation_dict[row.name]
                else:
                    type_ = row.type
                if row.is_array:
                    type_ = List[type_]
                field_definitions.update(
                    {row.name: (type_, Field(None, description=row.description))}
                )
            annoatation_dict[field_of] = create_model(
                field_of.capitalize(),
                **field_definitions
            )
        field_of = df_sorted[-1]["field_of"].iloc[0] # the outermost field name
        return annoatation_dict[field_of]
    

# instantiate session variables
if "pydantic_model" not in st.session_state:
    st.session_state.pydantic_model = create_model("Unit")
if "field_definitions" not in st.session_state:
    st.session_state.field_definitions = {}
if "registry" not in st.session_state:
    st.session_state.registry = {}
if "node" not in st.session_state:
    st.session_state.node = {}
if "root_name" not in st.session_state:
    st.session_state.root_name = None
    st.session_state.node_name = None
    st.session_state.select_node = None

# basic config
st.set_page_config(page_title="Data Model", page_icon="📦")
st.title("Building :blue[Data] Model")
st.subheader("""supported by [pydantic](https://docs.pydantic.dev/latest/)"""
             , divider='rainbow')
with st.sidebar:
    st.write("")
    st.markdown("App created by soike Yuan 😊")

def id_gen():
    id_number = 0
    while True:
        yield id_number
        id_number += 1

id_gen = id_gen()
def input_schema(depth) -> PrimalFieldWrapper:
    if depth == 0:
        chunks = [8,2]
    elif depth == 1:
        chunks = [1, 15 ,4]
    elif depth == 2:
        chunks = [1,1,14,4]
    elif depth == 3:
        chunks = [1,1,1,13,4]

    *c, c1, c2 = st.columns(chunks)
    with c1:
        name = st.text_input("Name of the field", key=next(id_gen))
    with c2:
        type_ = st.selectbox(
            "Type of the field",
            options=["int", "float", "str", "bool", "object"],
            index=None,
            key=next(id_gen),
            help="the former 4 types is basic types, select object when needs nested model"
            )
    *c, c3, c4 = st.columns(chunks)
    with c3:
        description = st.text_input("Description of the field", key=next(id_gen))
    with c4:
        is_array = st.selectbox("Field is array", options=[True, False], index=None, key=next(id_gen))
    wrapper = PrimalFieldWrapper(name, type_, description, is_array)

    return wrapper

# st.markdown("### Add a new field or Modify existed")
# placeholder = st.empty()
# with placeholder.container():
#     field_definitions = {}
#     nested_field_definitions = []
#     depth = 0
#     primal_field_wrapper = input_schema(0)
#     field_definitions.update({"primal_field_wrapper": primal_field_wrapper})
#     type_ = primal_field_wrapper.type
#     name = primal_field_wrapper.name
#     # nested model
#     if type_ == "object":
#         st.markdown(f"- __Field of {name}__")
#         depth += 1
#         field_wrapper = input_schema(1)
#         nested_field_definitions.append(DictWrapper(**field_wrapper._asdict(), field_of=name, depth=depth))

#         c1, c2 = st.columns([8, 2])
#         with c2:
#             button_placeholder = st.empty()
#             add_sibling_button = button_placeholder.button("add_sibling", key=next(id_gen))

class PydanticNode:
    def __init__(self, name, parent_node: "PydanticNode"):
        self.name = name
        self.parent_node = parent_node
        self.display_tool = input_schema

class Nested(PydanticNode):
    def __init__(self, name, parent_node):
        super().__init__(name, parent_node)
        self.child_node = []

    def add_child(self, node):
        self.child_node.append(node)
    
    def diagram(self, indent=0):
        st.markdown(f"{self.name}")
        for node in self.child_node:
            node.diagram()


class Root(Nested):
    def __init__(self, name):
        super().__init__(name, parent_node=None)
        self.child_node = []

def update_depth(registry, node):
    depth_of_parent = registry.get(node.parent_node.name)
    depth = depth_of_parent + 1
    registry[node.name] = depth # update
    return depth

def trigger_function():
    
    if not st.session_state.node:
        name = st.session_state.root_name
        st.session_state.node[name] = Root(name)
        st.session_state.registry[name] = 0
    else:
        name = st.session_state.node_name
        parent_node = st.session_state.node[st.session_state.select_node] # None
        node = Nested(name=name, parent_node=parent_node)
        parent_node.add_child(node)
        st.session_state.node[name] = node
        update_depth(registry=st.session_state.registry, node=node)
    st.session_state.node[st.session_state.root_name].diagram()

# create node
with st.form("Create node", clear_on_submit=True):
    
    if not st.session_state.node:
        st.markdown("root definition")
        # init_wrapper = input_schema(depth=0)
        # name = init_wrapper.name
        name = st.text_input("inuput name", key="root_name")
    
    else:
        select_node = st.selectbox(
            "create nested field of",
            options=[node_name for node_name in st.session_state.node],
            key="select_node",
            index=None)
        # wrapper = input_schema(depth=0)
        # name = wrapper.name
        name = st.text_input("inuput name", key="node_name")

    button = st.form_submit_button("create", on_click=trigger_function)



    
    



# init_wrapper = input_schema(0)
# root = PydanticNode(name="root", parent_node=None)
# first_node = PydanticNode(name=init_wrapper.name, parent_node=root)





st.markdown("---")
st.markdown("show schema here")


# # streamlit construct flow
# dp = DynamicPydantic(base_model=st.session_state.pydantic_model)
# # user input logic
# #######
# name, type_, description, is_array, dict_wrappers = 1, 2,3 ,4, 5
# #######
# dp.add_field(name, type_, description, is_array, dict_wrappers) # add field to base model
# st.session_state.pydantic_model = dp.base_model # update
# st.json(
#     json.dumps(dp.base_model.model_json_schema())
# )


# dict_wrapper = [{"field_of": "test", "name": "unit", "type": "str", "description": "unit of property", "is_array": False, "depth": 1}, {"field_of": "test", "name": "odd", "type": "object", "description": "odd","is_array": True, "depth": 1}, {"field_of": "odd", "name": "boo", "type": "object","is_array": False, "description": "boofoo", "depth": 2}, {"field_of": "boo", "name": "lol", "type": "str", "description": "lolol","is_array": False, "depth":3}]
# dp = DynamicPydantic(base_model=st.session_state.pydantic_model)
# annoatation = dp.build_block(dict_wrappers=dict_wrapper)
# Model = create_model("Model", test=(annoatation, ...))
