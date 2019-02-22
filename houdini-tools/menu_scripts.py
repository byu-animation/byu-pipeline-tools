import hou, sys, os, json, assemble_v2
from byuam import Project, Department, Element, Environment, Body, Asset, Shot, AssetType
from byugui import CheckoutWindow, message_gui


global WINDOW
global DEPARTMENT

def add_callback():
    global WINDOW
    global DEPARTMENT

    name=WINDOW.current_item
    print name
    assemble_v2.create_hda(name,DEPARTMENT)

def add_hda(department):
    global WINDOW
    global DEPARTMENT
    DEPARTMENT=department[0]
    WINDOW =CheckoutWindow(hou.ui.mainQtWindow(),department)

    WINDOW.finished.connect(add_callback)
