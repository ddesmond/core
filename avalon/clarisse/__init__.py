"""Public API for CLARISSE

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    install,
    uninstall,
    ls,
    imprint_container,
    parse_container,
    get_current_clarisseproject,
    clarisse_project_file_lock_and_undo_chunk
)

from .workio import (
    open_file,
    save_file,
    current_file,
    has_unsaved_changes,
    file_extensions,
    work_root
)

from .lib import (
    maintained_selection
)

from .command import (
    ix_select,
    get_or_create_ctx,
    ix_create_avalon_item,
    reset_frame_range,
    reset_resolution,
    ix_load_referenced_file
)

__all__ = [
    "install",
    "uninstall",
    "ls",

    "imprint_container",
    "parse_container",

    "get_current_clarisseproject",
    "clarisse_project_file_lock_and_undo_chunk",

    # Workfiles API
    "open_file",
    "save_file",
    "current_file",
    "has_unsaved_changes",
    "file_extensions",
    "work_root",

    "ix_create_avalon_item",
    "ix_select",
    "get_or_create_ctx",
    "maintained_selection"

]

# Backwards API clarisse_project_fileatibility
open = open_file
save = save_file
