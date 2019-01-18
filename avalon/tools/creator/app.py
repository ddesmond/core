
import sys
import inspect

from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ...vendor import qtawesome
from ...vendor import six
from ... import api, io, style
from .. import lib

module = sys.modules[__name__]
module.window = None
module.root = api.registered_root()

HelpRole = QtCore.Qt.UserRole + 2
FamilyRole = QtCore.Qt.UserRole + 3
ExistsRole = QtCore.Qt.UserRole + 4
PluginRole = QtCore.Qt.UserRole + 5

Separator = "---separator---"


class Window(QtWidgets.QDialog):

    stateChanged = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Instance Creator")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Store the widgets for lookup in here
        self.data = dict()

        # Store internal states in here
        self.state = {
            "valid": False
        }

        body = QtWidgets.QWidget()
        lists = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        listing = QtWidgets.QListWidget()
        asset = QtWidgets.QLineEdit()
        name = QtWidgets.QLineEdit()
        result = QtWidgets.QLineEdit()
        result.setStyleSheet("color: gray;")
        result.setEnabled(False)

        # region Menu for default variant names

        variant_button = QtWidgets.QPushButton()
        variant_button.setFixedWidth(18)
        variant_button.setFixedHeight(20)
        variant_menu = QtWidgets.QMenu(variant_button)
        variant_button.setMenu(variant_menu)

        # endregion

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(name)
        name_layout.addWidget(variant_button)
        name_layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(container)

        header = FamilyDescriptionWidget(parent=self)
        layout.addWidget(header)

        layout.addWidget(QtWidgets.QLabel("Family"))
        layout.addWidget(listing)
        layout.addWidget(QtWidgets.QLabel("Asset"))
        layout.addWidget(asset)
        layout.addWidget(QtWidgets.QLabel("Subset"))
        layout.addLayout(name_layout)
        layout.addWidget(result)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()

        useselection_chk = QtWidgets.QCheckBox("Use selection")
        useselection_chk.setCheckState(QtCore.Qt.Checked)

        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(useselection_chk, 1, 1)

        layout = QtWidgets.QHBoxLayout(lists)
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(body)
        layout.addWidget(lists)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)

        create_btn = QtWidgets.QPushButton("Create")
        error_msg = QtWidgets.QLabel()
        error_msg.setFixedHeight(20)

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(create_btn)
        layout.addWidget(error_msg)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "Create Button": create_btn,
            "Listing": listing,
            "Use Selection Checkbox": useselection_chk,
            "Variant": name,
            "Variant Menu": variant_menu,
            "Result": result,
            "Asset": asset,
            "Error Message": error_msg,
        }

        for _name, widget in self.data.items():
            widget.setObjectName(_name)

        create_btn.clicked.connect(self.on_create)
        name.returnPressed.connect(self.on_create)
        name.textChanged.connect(self.on_data_changed)
        asset.textChanged.connect(self.on_data_changed)
        listing.currentItemChanged.connect(self.on_selection_changed)
        listing.currentItemChanged.connect(header.set_item)

        self.stateChanged.connect(self._on_state_changed)

        # Defaults
        self.resize(300, 500)
        name.setFocus()
        create_btn.setEnabled(False)

    def _on_state_changed(self, state):
        self.state['valid'] = state
        self.data['Create Button'].setEnabled(state)

    def _build_menu(self, default_names):
        """Create optional predefined variant names

        Args:
            default_names(list): all predefined names

        Returns:
             None
        """

        menu = self.data["Variant Menu"]
        button = menu.parent()

        # Get and destroy the action group
        group = button.findChild(QtWidgets.QActionGroup)
        if group:
            group.deleteLater()

        state = any(default_names)
        button.setEnabled(state)
        if state is False:
            return

        # Build new action group
        group = QtWidgets.QActionGroup(button)
        for name in default_names:
            if name == Separator:
                menu.addSeparator()
                continue
            action = group.addAction(name)
            menu.addAction(action)

        group.triggered.connect(self._on_action_clicked)

    def _on_action_clicked(self, action):
        name = self.data["Variant"]
        name.setText(action.text())

    def _on_data_changed(self):

        listing = self.data["Listing"]
        asset_name = self.data["Asset"]
        variant = self.data["Variant"]
        result = self.data["Result"]

        item = listing.currentItem()
        variant_name = variant.text()
        asset_name = asset_name.text()

        # Get the assets from the database which match with the name
        assets_db = io.find(filter={"type": "asset"}, projection={"name": 1})
        assets = [asset for asset in assets_db if asset_name in asset["name"]]

        if assets:
            # Get plugin and family
            plugin = item.data(PluginRole)
            family = plugin.family.rsplit(".", 1)[-1]

            # Get all subsets of the current asset
            asset_ids = [asset["_id"] for asset in assets]
            subsets = io.find(filter={"type": "subset",
                                      "name": {"$regex": "{}*".format(family),
                                               "$options": "i"},
                                      "parent": {"$in": asset_ids}}) or []

            # Get all subsets' their variant name, "Default", "High", "Low"
            existed_variants = [sub["name"].split(family)[-1]
                                for sub in subsets]

            if plugin.variants and isinstance(plugin.variants, list):
                variants = plugin.variants[:] + [Separator]
                for var in [v for v in existed_variants if v not in variants]:
                    variants.append(var)
            else:
                variants = existed_variants

            self._build_menu(variants)

            # Update the result
            if variant_name:
                variant_name = variant_name[0].upper() + variant_name[1:]
            result.setText("{}{}".format(family, variant_name))

            item.setData(ExistsRole, True)
            self.echo("Ready ..")
        else:
            self._build_menu([])
            item.setData(ExistsRole, False)
            self.echo("'%s' not found .." % asset_name)

        # Update the valid state
        valid = (
            variant_name.strip() != "" and
            asset_name.strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled) and
            item.data(ExistsRole)
        )
        self.stateChanged.emit(valid)

    def on_data_changed(self, *args):

        # Set invalid state until it's reconfirmed to be valid by the
        # scheduled callback so any form of creation is held back until
        # valid again
        self.stateChanged.emit(False)

        lib.schedule(self._on_data_changed, 500, channel="gui")

    def on_selection_changed(self, *args):
        name = self.data["Variant"]
        item = self.data["Listing"].currentItem()

        plugin = item.data(PluginRole)
        if plugin is None:
            return

        if plugin.variants and isinstance(plugin.variants, list):
            default_variant = plugin.variants[0]
        else:
            default_variant = "Default"

        name.setText(default_variant)

        self.on_data_changed()

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self):

        listing = self.data["Listing"]
        asset = self.data["Asset"]
        asset.setText(api.Session["AVALON_ASSET"])

        has_families = False

        creators = api.discover(api.Creator)

        for creator in creators:
            label = creator.label or creator.family
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(HelpRole, creator.__doc__)
            item.setData(FamilyRole, creator.family)
            item.setData(PluginRole, creator)
            item.setData(ExistsRole, False)
            listing.addItem(item)

            has_families = True

        if not has_families:
            item = QtWidgets.QListWidgetItem("No registered families")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            listing.addItem(item)

        listing.setCurrentItem(listing.item(0))

    def on_create(self):

        # Do not allow creation in an invalid state
        if not self.state['valid']:
            return

        asset = self.data["Asset"]
        listing = self.data["Listing"]
        result = self.data["Result"]

        item = listing.currentItem()
        useselection_chk = self.data["Use Selection Checkbox"]

        if item is not None:
            subset_name = result.text()
            asset = asset.text()
            family = item.data(FamilyRole)
        else:
            return

        try:
            api.create(subset_name,
                       asset,
                       family,
                       options={"useSelection":
                                useselection_chk.checkState()}
                       )

        except NameError as e:
            self.echo(e)
            raise

        except (TypeError, RuntimeError, KeyError, AssertionError) as e:
            self.echo("Program error: %s" % str(e))
            raise

    def echo(self, message):
        widget = self.data["Error Message"]
        widget.setText(str(message))
        widget.show()

        lib.schedule(lambda: widget.setText(""), 5000, channel="message")


class FamilyDescriptionWidget(QtWidgets.QWidget):
    """A family description widget.

    Shows a family icon, family name and a help description.
    Used in creator header.

     _________________
    |  ____           |
    | |icon| FAMILY   |
    | |____| help     |
    |_________________|

    """

    SIZE = 35

    def __init__(self, parent=None):
        super(FamilyDescriptionWidget, self).__init__(parent=parent)

        # Header font
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(14)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        icon = QtWidgets.QLabel()
        icon.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)

        # Add 4 pixel padding to avoid icon being cut off
        icon.setFixedWidth(self.SIZE + 4)
        icon.setFixedHeight(self.SIZE + 4)
        icon.setStyleSheet("""
        QLabel {
            padding-right: 5px;
        }
        """)

        label_layout = QtWidgets.QVBoxLayout()
        label_layout.setSpacing(0)

        family = QtWidgets.QLabel("family")
        family.setFont(font)
        family.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)

        help = QtWidgets.QLabel("help")
        help.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        label_layout.addWidget(family)
        label_layout.addWidget(help)

        layout.addWidget(icon)
        layout.addLayout(label_layout)

        self.help = help
        self.family = family
        self.icon = icon

    def set_item(self, item):
        """Update elements to display information of a family item.

        Args:
            family (dict): A family item as registered with name, help and icon

        Returns:
            None

        """
        if not item:
            return

        # Support a font-awesome icon
        plugin = item.data(PluginRole)
        icon = getattr(plugin, "icon", "info-circle")
        assert isinstance(icon, six.string_types)
        icon = qtawesome.icon("fa.{}".format(icon), color="white")
        pixmap = icon.pixmap(self.SIZE, self.SIZE)
        pixmap = pixmap.scaled(self.SIZE, self.SIZE)

        # Parse a clean line from the Creator's docstring
        docstring = inspect.getdoc(plugin)
        help = docstring.splitlines()[0] if docstring else ""

        self.icon.setPixmap(pixmap)
        self.family.setText(item.data(FamilyRole))
        self.help.setText(help)


def show(debug=False, parent=None):
    """Display asset creator GUI

    Arguments:
        creator (func, optional): Callable function, passed `name`,
            `family` and `use_selection`, defaults to `creator`
            defined in :mod:`pipeline`
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    if module.window:
        module.window.close()
        del(module.window)

    if debug:
        from avalon import mock
        for creator in mock.creators:
            api.register_plugin(api.Creator, creator)

        import traceback
        sys.excepthook = lambda typ, val, tb: traceback.print_last()

        io.install()

        any_project = next(
            project for project in io.projects()
            if project.get("active", True) is not False
        )

        api.Session["AVALON_PROJECT"] = any_project["name"]
        module.project = any_project["name"]

    with lib.application():
        window = Window(parent)
        window.setStyleSheet(style.load_stylesheet())
        window.refresh()
        window.show()

        module.window = window
