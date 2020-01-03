"""Host API required Work Files tool"""
import sys
import os
import ix
import avalon.api

def file_extensions():
    return [".project"]


def has_unsaved_changes():
    saver = ix.check_need_save()
    return 

def save_file(filepath):

    return ix.save_project(filepath)


def open_file(filepath):
    ix.load_project(str(filepath))
    return 


def current_file():
    current_filepath = ix.application.get_factory().get_vars().get("PNAME").get_string()+".project"
    #current_filepath = ix.application.get_current_project_filename()
    return current_filepath


def work_root():
    work_dir = avalon.api.Session.get("AVALON_WORKDIR")
    scene_dir = avalon.api.Session.get("AVALON_SCENEDIR")
    if scene_dir:
        return os.path.join(work_dir, scene_dir)
    else:
        return work_dir
