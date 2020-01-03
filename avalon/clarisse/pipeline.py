import sys
import contextlib
import importlib
import logging
from pyblish import api as pyblish
from avalon import api as avalon

from ..pipeline import AVALON_CONTAINER_ID
import ix
from . import command

class clarisse_project_fileLogHandler(logging.Handler):
    def emit(self, record):
        entry = self.format(record)
        clarisse_project_file = get_current_clarisseproject()
        if clarisse_project_file:
            clarisse_project_file.Print(entry)


def ls():
    '''references only'''
    contexts = ix.api.OfContextSet()
    ix.application.get_factory().get_root().resolve_all_contexts(contexts)
    for context in contexts:
        #print(context)
        if context.is_reference() and not context.is_disabled():
            try:
                id = context.get_attribute("id").get_string()
                name = context.get_attribute("name").get_string()
                #ix.log_info("{}: {}".format(context.get_name(), name))
                # yielding only referenced files ""
                print(id, name, context)
                yield context
            except:
                pass

def find_host_config(config):
    config_name = config.__name__
    try:
        config = importlib.import_module(config_name + ".clarisse")
    except ImportError:
        pass
    return config


def install(config):
    """Install clarisse-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(clarisse)`.

    """
    #pyblish.register_host("clarisse")
    _install_menu()

    # Trigger install on the config's "clarisse" package
    config = find_host_config(config)
    if hasattr(config, "install"):
        config.install()

def _install_menu():
    ###install menu
    ix.application.get_main_menu().add_command("Avalon>")
    ix.application.get_main_menu().add_command("Avalon>Create")
    ix.application.get_main_menu().add_command("Avalon>Load")
    ix.application.get_main_menu().add_command("Avalon>Publish")
    ix.application.get_main_menu().add_command("Avalon>Manage")
    ix.application.get_main_menu().add_command("Avalon>Work file")
    ix.application.get_main_menu().add_command("Avalon>Project manager")
    ix.application.get_main_menu().add_command("Avalon>Reset resolution")
    ix.application.get_main_menu().add_command("Avalon>Reset frame range")



def _uninstall_menu():
    remove_command
    ix.application.get_main_menu().remove_command("Avalon>Create")
    ix.application.get_main_menu().remove_command("Avalon>Load")
    ix.application.get_main_menu().remove_command("Avalon>Publish")
    ix.application.get_main_menu().remove_command("Avalon>Manage")
    ix.application.get_main_menu().remove_command("Avalon>Work file")
    ix.application.get_main_menu().remove_command("Avalon>Project manager")
    ix.application.get_main_menu().remove_command("Avalon>Reset resolution")
    ix.application.get_main_menu().remove_command("Avalon>Reset frame range")
    ix.application.get_main_menu().remove_command("Avalon>")


def uninstall(config):
    """Install clarisse-specific functionality of avalon-core.

    This function is called automatically on calling `api.uninstall(clarisse)`.

    """
    _uninstall_menu()
    config = find_host_config(config)
    if hasattr(config, "uninstall"):
        config.uninstall()
    pyblish.api.deregister_host("clarisse")


def imprint_container(tool,
                      name,
                      namespace,
                      context,
                      loader=None):
    """Imprint a Loader with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        tool (object): The node in clarisse to imprint as container, usually a
            Loader.
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        loader (str, optional): Name of loader used to produce this container.

    Returns:
        None

    """

    data = [
        ("schema", "avalon-core:container-2.0"),
        ("id", AVALON_CONTAINER_ID),
        ("name", str(name)),
        ("namespace", str(namespace)),
        ("loader", str(loader)),
        ("representation", str(context["representation"]["_id"])),
    ]
    log.info(data)
    for key, value in data:
        print("data"), key, value
    ix.cmds.SetValues([tool+".id[0]"], [data['id']])
    ix.cmds.SetValues([tool+"name[0]"], [data['name']])
    ix.cmds.SetValues([tool+".namespace[0]"], [data['namespace']])
    ix.cmds.SetValues([tool+".loader[0]"], [data['loader']])
    ix.cmds.SetValues([tool+".representation[0]"], [data['representation']])
    return



def parse_container(tool):
    """Returns imprinted container data of a tool

    This reads the imprinted data from `imprint_container`.

    """
    container = command.ix_select(tool)

    log.info(container)
    get_id = container.get_attribute("id").get_string()
    get_name = container.get_attribute("name").get_string()
    get_namespace = container.get_attribute("namespace").get_string()
    get_loader = container.get_attribute("loader").get_string()
    get_representation = container.get_attribute("representation").get_string()
    return [get_id,get_name,get_namespace,get_loader,get_representation]


def get_current_clarisseproject():
    """Hack to get current clarisse_project_file in this session"""
    project_file = ix.application.get_factory().get_vars().get("PNAME").get_string()+".project"
    return(project_file)


@contextlib.contextmanager
def clarisse_project_file_lock_and_undo_chunk(clarisse_project_file, undo_queue_name="Script CMD"):
    """Lock clarisse_project_file and open an undo chunk during the context"""
    try:
        ix.begin_command_batch("Avalon: project undo")
        yield
    finally:
        ix.end_command_batch()
