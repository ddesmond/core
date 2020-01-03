
import logging
import contextlib
import ix
import os.path

from .. import api, io


log = logging.getLogger(__name__)


def get_or_create_ctx(ctx_name, parent_ctx_path):
    """
    Create the context only if it  doesn't exist yet and return it.
    ctx_name        : name (only) of the new context
    parent_ctx_path : full path (with trailing slash) of the parent context
    """
    print("CREATING CONTEXT")
    full_path = parent_ctx_path + ctx_name
    if ix.item_exists(full_path) is None:
        # create it and return it
        return ix.cmds.CreateContext(ctx_name, "", parent_ctx_path)
    else:
        # already exists, return it
        return ix.get_item(full_path)

def refefenced_file_type(filename):
    extension = os.path.splitext(filename)[1]
    return extension

def ix_create_avalon_item(item_name):
    
    return 

def ix_actions_avalon_item(item_name,action,data):
    ''' accepts: read, write, update '''
    return

def ix_select(item_name):
    selection = ix.get_item(item_name)
    return selection

def ix_read_attribute(item_name,attribute):
    return

def ix_write_attribute(item_name,attribute,data):
    return

def ix_update_attribute(item_name,attribute,data):
    return

def ix_load_referenced_file(path):
    file_type = refefenced_file_type(path)
    if file_type == "abc" or "ABC":
        print "alembic"
        loader = ix.cmds.CreateFileReference("project://scene", ["/Users/des/Desktop/test_cam.abc"])
        #ix.cmds.RenameItem("project://scene/file1", "abc")
    if file_type == "usd" or "usdc" or "usda":
        print "usd"
        loader = ix.cmds.CreateFileReference("project://scene", ["/Users/des/Downloads/torus_sliced.red.usda"])
        #ix.cmds.RenameItem("project://scene/lol", "usd")

    if file_type == "obj":
        print "obj"
        loader = ix.cmds.CreateObject("polyfile", "GeometryPolyfile", "Global", "project://scene")
        #ix.cmds.RenameItem("project://scene/polyfile", "obj")
    if file_type == "vdb":
        print "volume"
        loader = ix.cmds.CreateObject("volume", "GeometryVolumeFile", "Global", "project://scene")
        #ix.cmds.RenameItem("project://scene/file", "volume")
    return 

def ix_update_geo(item_name,geo_type,data):
    return

def ix_delete_geo(item_name):
    return

def ix_set_item_path(item_name,path):
    return

def ix_render_preview_image():
    return

def ix_destroy_item(item_to_destroy):
    return




def reset_frame_range():
    """ Set timeine frame range.
    """
    
    fps = float(api.Session.get("AVALON_FPS", 25))
    ix.cmds.SetFps(fps)

    name = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": name, "type": "asset"})
    asset_data = asset["data"]
    frame_start = str(asset_data.get(
        "frameStart",
        asset_data.get("edit_in")))

    frame_end = str(asset_data.get(
        "frameEnd",
        asset_data.get("edit_out")))
    log.info(frame_start)
    log.info(frame_end)

    ix.begin_command_batch("Avalon: Frame range undo")
    ix.cmds.SetValues(["project://scene/image.background.first_frame"], [frame_start])
    ix.cmds.SetValues(["project://scene/image.background.last_frame"], [frame_end])
    ix.cmds.SetCurrentFrameRange(float(frame_start), float(frame_end))
    log.info("Frame range set")
    ix.end_command_batch()

def reset_resolution():
    """Set resolution to project resolution."""
    project = io.find_one({"type": "project"})
    p_data = project["data"]

    width = p_data.get("resolution_width",
                       p_data.get("resolutionWidth"))
    height = p_data.get("resolution_height",
                        p_data.get("resolutionHeight"))


    image = ix.get_item('project://scene/image')
    current_width = image.attrs.resolution[0]
    current_height = image.attrs.resolution[1]


    ix.begin_command_batch("Avalon: Resolution undo")
    if width != current_width or height != current_height:
        image.attrs.resolution_preset = "Custom"
        image.attrs.resolution[0] = width
        image.attrs.resolution[1] = height
        image.attrs.resolution_multiplier = "2"
    ix.end_command_batch()
