import re
import os
import contextlib

from . import pipeline


@contextlib.contextmanager
def maintained_selection():
    clarisse_project_file = pipeline.get_current_clarisseproject()
    return

