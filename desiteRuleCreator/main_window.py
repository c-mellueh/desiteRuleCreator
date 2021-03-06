from __future__ import annotations

import copy
import sys,os,logging,logging.config

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QCompleter,QDialog

from desiteRuleCreator import icons
from desiteRuleCreator.Filehandling import open_file, desite_export, excel,save_file
from desiteRuleCreator.QtDesigns import ui_project_settings
from desiteRuleCreator.QtDesigns.ui_mainwindow import Ui_MainWindow
from desiteRuleCreator.Widgets import script_widget, property_widget, object_widget
from desiteRuleCreator.Windows import predefined_psets_window,graphs_window
from desiteRuleCreator.data import classes
from desiteRuleCreator.data.classes import Object, PropertySet
from desiteRuleCreator import logs

def get_icon():
    icon_path = os.path.join(icons.ICON_PATH, icons.ICON_DICT["icon"])
    return QtGui.QIcon(icon_path)

def start_log() -> None:
    if os.path.exists(logs.LOG_PATH):
        os.remove(logs.LOG_PATH)

    logging.config.fileConfig(logs.CONF_PATH, defaults={'logfilename': logs.LOG_PATH.replace("\\","/")})
    logger = logging.getLogger("simple_example")

class MainWindow(QMainWindow):
    def __init__(self,app):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app
        self.parent_property_window = None
        self.parent_property_window: predefined_psets_window.PropertySetInherWindow = self.open_pset_list()
        self.parent_property_window.hide()
        self.pset_window = None
        self.pset_table = self.ui.tableWidget_inherited

        # variables
        self.icon = get_icon()
        self.setWindowIcon(self.icon)
        self._save_path = None
        self._export_path = None
        self.active_object:classes.Object|None = None
        self.graph_window = None
        self.project = classes.Project(self, "")

        # init object and ProertyWidget
        object_widget.init(self)
        property_widget.init(self)
        script_widget.init(self)

        # connect Menubar signals
        self.ui.action_file_Open.triggered.connect(self.open_file_dialog)
        self.ui.action_file_new.triggered.connect(self.new_file)
        self.ui.action_file_Save.triggered.connect(self.save_clicked)
        self.ui.action_file_Save_As.triggered.connect(self.save_as_clicked)
        self.ui.action_desite_export.triggered.connect(self.export_desite_rules)
        self.ui.action_show_list.triggered.connect(self.open_pset_list)
        self.ui.action_settings.triggered.connect(self.open_settings)
        self.ui.action_export_bs.triggered.connect(self.export_bs)
        self.ui.action_export_bookmarks.triggered.connect(self.export_bookmarks)
        self.ui.action_export_boq.triggered.connect(self.export_boq)
        self.ui.action_show_graphs.triggered.connect(self.open_graph)

        self.ui.code_edit.textChanged.connect(self.update_script)
        self.ui.tree.resizeColumnToContents(0)
        self.save_path = None


    @property
    def save_path(self) -> str:
        return self._save_path

    @save_path.setter
    def save_path(self, value):
        self._save_path = value
        self._export_path = value

    @property
    def export_path(self):
        return self._export_path

    @export_path.setter
    def export_path(self, value):
        self._save_path = value
        self._export_path = value

    def update_script(self):
        script_widget.update_script(self)

    def export_desite_rules(self):
        desite_export.export_modelcheck(self)

    def closeEvent(self, event):
        action = save_file.close_event(self, event)

        if action:
            app.closeAllWindows()
            event.accept()
        else:
            event.ignore()

    # Filehandling
    def save_clicked(self):
        save_file.save_clicked(self)

    def open_pset_list(self):
        if self.parent_property_window is not None:
            self.parent_property_window.show()
        else:
            self.parent_property_window = predefined_psets_window.open_pset_list(self)

        return self.parent_property_window

    def save(self, path):
        save_file.save(self, path)

    def save_as_clicked(self):
        save_file.save_as_clicked(self)

    def new_file(self):
        open_file.new_file(self)

    def open_file_dialog(self, path=False):
        open_file.open_file_dialog(self, path)

    def merge_new_file(self):
        open_file.merge_new_file(self)

    def open_pset_menu(self,position):
        property_widget.open_menu(self,position)

    def open_file(self, path=""):

        if not path:
            cur_path = os.getcwd() + "/"
            path: str = QFileDialog.getOpenFileName(self, "Open File", str(cur_path),
                                                    "xml Files (*.xml *.DRCxml);; xlsx Files (*xlsx);;all (*.*)")[0]

        if path:
            if path.endswith("xlsx"):
                excel.start(self, path)
            else:
                open_file.import_data(self, path)

        self.ui.tree.resizeColumnToContents(0)
        self.load_graph(show=False)
        self.save_path = path

    # Main
    def clear_all(self):
        object_widget.clear_all(self)
        property_widget.clear_all(self)
        self.parent_property_window.clear_all()
        classes.Object._registry = list()
        classes.PropertySet._registry = list()
        classes.Attribute._registry= list()

    # ObjectWidget
    def reload_objects(self):
        object_widget.reload(self)

    def right_click(self, position: QtCore.QPoint):
        object_widget.right_click(self, position)

    def rc_collapse(self):
        object_widget.rc_collapse(self.ui.tree)

    def rc_expand(self):
        object_widget.rc_expand(self.ui.tree)

    def rc_group(self):
        object_widget.rc_group_items(self)

    def rc_rename(self):
        object_widget.rc_rename(self)

    def multi_selection(self):
        object_widget.multi_selection(self)

    def update_completer(self):
        completer = QCompleter(property_widget.predefined_pset_list(self), self)
        self.ui.lineEdit_ident_pSet.setCompleter(completer)
        self.ui.lineEdit_pSet_name.setCompleter(completer)

    def object_clicked(self, item):
        object_widget.single_click(self, item)

    def set_ident_line_enable(self, value: bool):
        object_widget.set_ident_line_enable(self, value)

    def delete_selected_scripts(self):
        script_widget.delete_objects(self)

    def script_list_clicked(self, item):
        script_widget.clicked(self, item)

    def clear_object_input(self):
        object_widget.clear_object_input(self)

    def add_object(self):
        object_widget.add_object(self)

    def add_object_to_tree(self, obj: Object, parent=None):
        return object_widget.add_object_to_tree(self, obj, parent)

    def delete_object(self):
        object_widget.delete_object(self)

    # PropertyWidget
    def attribute_double_clicked(self,item):
        property_widget.attribute_double_click(self,item)

    def delete_pset(self):
        property_widget.delete(self)

    def rename_pset(self):
        property_widget.rename(self)

    def text_changed(self, text):
        property_widget.text_changed(self, text)

    def set_right_window_enable(self, value: bool):
        property_widget.set_enable(self, value)
        script_widget.set_enable(self, value)

    def list_object_clicked(self, item):
        property_widget.left_click(self, item)

    def list_object_double_clicked(self, item):
        property_widget.double_click(self, item)

    def open_pset_window(self, property_set: PropertySet, active_object, window_title=None) -> property_widget.PropertySetWindow:
        return property_widget.open_pset_window(self, property_set, active_object, window_title)

    def add_pset(self):
        property_widget.add_pset(self)

    def add_script(self):
        script_widget.add_script(self)

    def selected_object(self):
        return object_widget.selected_object(self)

    def change_script_list_visibility(self):
        script_widget.change_script_list_visibility(self)

    def code_item_changed(self, item):
        script_widget.item_changed(self, item)

    def export_bs(self):
        desite_export.export_bs(self)

    def reload(self):
        object_widget.reload_tree(self)
        predefined_psets_window.reload(self)
        property_widget.reload(self)

    def open_settings(self):
        dialog = QDialog()
        widget = ui_project_settings.Ui_Dialog()
        widget.setupUi(dialog)
        dialog.setWindowIcon(icons.get_icon())
        dialog.setWindowTitle("Settings")
        widget.lineEdit_project_name.setText(self.project.name)
        widget.lineEdit_author.setText(self.project.author)
        widget.lineEdit_version.setText(self.project.version)

        if dialog.exec():
            self.project.name = widget.lineEdit_project_name.text()
            self.project.author = widget.lineEdit_author.text()
            self.project.version = widget.lineEdit_version.text()

    def export_bookmarks(self):
        desite_export.export_bookmarks(self)

    def open_graph(self):
        self.load_graph(True)

    def load_graph(self, show=True):

        if self.graph_window is None:
            self.graph_window = graphs_window.GraphWindow(self,show = show)
        else:
            if show:
                self.graph_window.show()
                self.graph_window.view.show()
                self.graph_window.fit_in()

    def export_boq(self):
        desite_export.export_boq(self)

def main():
    start_log()
    global app
    app = QApplication(sys.argv)

    window = MainWindow(app)
    window.show()
    window.resize(1200, 550)

    sys.exit(app.exec())
    pass


if __name__ == "__main__":
    main()
