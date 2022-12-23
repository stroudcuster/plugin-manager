import json
import pathlib
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Optional

import ttkbootstrap as ttkb

import plugin_manager.model.json_handler as jh

import plugin_manager.model.plugin as model
import plugin_manager.gui.tk_widgets as plugin_widgets


class Application(ttkb.Window):
    """
    The top level GUI for the Plugin Manager application

    """
    MLABEL_NEW = 'New'
    MLABEL_OPEN = 'Open...'
    MLABEL_SAVE = 'Save'
    MLABEL_SAVE_AS = 'Save As...'
    MLABEL_QUIT = 'Quit'
    JSON_LABEL_TEXT = 'Plugin JSON File:'

    def __init__(self):
        """
        Creates an instance of the plugin_manager.gui.tk_gui.Application

        """
        ttkb.Window.__init__(self, title='Plugin Manager', themename='darkly')
        menubar = ttkb.Menu(self)
        self.config(menu=menubar)
        self.file_menu = ttkb.Menu(menubar, title='File')
        self.file_menu.add_command(label=Application.MLABEL_NEW, command=self.create_plugin)
        self.file_menu.add_command(label=Application.MLABEL_OPEN, command=self.browse_plugins)
        self.file_menu.add_command(label=Application.MLABEL_SAVE, command=self.save)
        self.file_menu.add_command(label=Application.MLABEL_SAVE_AS, command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=Application.MLABEL_QUIT, command=self.exit_app)
        menubar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.entryconfigure(Application.MLABEL_SAVE, state=ttkb.DISABLED)

        self.json_path: Optional[pathlib.Path] = pathlib.Path.cwd()
        self.plugin: Optional[model.Plugin] = None

        row: int = 0
        self.json_file_label = ttkb.Label(self, text=Application.JSON_LABEL_TEXT, anchor=tk.W, width=120)
        self.json_file_label.grid(column=0, row=row, padx=5, pady=5)
        self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=None)

        row += 1
        self.plugin_widget_row = row
        self.plugin_widget_columnspan = 6
        self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)

    def set_json_file_label(self, text: str) -> None:
        """
        Sets the text value of a label that displays the JSON file path name

        :param text: the text that will be appended to the stub plugin_manager.gui.tk_gui.Application.JSON_LABEL_TEXT
        :type text: str
        :return: None

        """
        self.json_file_label['text'] = f'{Application.JSON_LABEL_TEXT} {text}'

    def browse_plugins(self) -> None:
        """
        Presents an 'open file' dialog to allow the user to select a plugin spec JSON file, reads the JSON file,
        saves the resulting plugin_manager.model.Plugin object to the Application object state, then enables the
        Save and Save As menu options.  If the object decoded from the JSON file is not a Plugin object, a TypeError
        is thrown.

        :return: None

        """
        json_path_str: str = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if len(json_path_str) > 0:
            self.json_path = pathlib.Path(json_path_str)
            try:
                plugin = self.read_json(self.json_path)
                self.plugin = plugin
                self.plugin_widget.forget()
                self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=self.plugin)
                self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)
                self.file_menu.entryconfigure(Application.MLABEL_SAVE, state=ttkb.NORMAL)
                self.file_menu.entryconfigure(Application.MLABEL_SAVE_AS, state=ttkb.NORMAL)
                self.plugin_widget.focus_set()
                self.set_json_file_label(json_path_str)
            except TypeError:
                raise TypeError(sys.exc_info())

    def create_plugin(self) -> None:
        """
        Set up the GUI to create a new Plugin JSON file.  Disables the Save menu selection and enables the Save As
        selection

        :return: None

        """
        self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=None)
        self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)
        self.file_menu.entryconfigure(Application.MLABEL_SAVE, state=ttkb.DISABLED)
        self.file_menu.entryconfigure(Application.MLABEL_SAVE_AS, state=ttkb.NORMAL)
        self.set_json_file_label('')
        self.plugin_widget.focus_set()

    def exit_app(self) -> None:
        """
        Exit the application by ending the tkinter event loop

        :return: None

        """
        self.quit()

    def save(self) -> None:
        """
        Write the current state of the Plugin to the same file it was loaded from

        :return: None

        """
        self.write_json(self.json_path)

    def save_as(self, create: bool = False):
        """
        Display a 'Save As' dialog and write current state of the Plugin to the selected file.  If the Plugin
        was loaded from a JSON file rather than being newly created, present the file path containing the loaded
        file as the starting point for browsing the file system.

        :param create: is a new Plugin being created
        :type create: bool
        :return:None

        """
        if create:
            file_name: str = filedialog.asksaveasfilename(confirmoverwrite=True)
        else:
            file_name = filedialog.asksaveasfilename(confirmoverwrite=True, initialdir=self.json_path.parent.__str__())
        if len(file_name.strip()) > 0:
            self.write_json(pathlib.Path(file_name))
            self.set_json_file_label(file_name)

    def read_json(self, json_path: pathlib.Path) -> model.Plugin:
        """
        Read the specified JSON file and decode it to create a plugin_manager.model.Plugin object.  If the resulting
        object is not of this class, a TypeError is raised

        :param json_path: a Path object for the file to be read
        :type json_path: pathlib.Path
        :return: None

        """
        with self.json_path.open(mode='r') as json_file:
            json_str = json_file.read()
            plugin = json.loads(eval(json_str), object_hook=jh.plugin_object_hook)
            if not isinstance(plugin, model.Plugin):
                raise TypeError(f'Decoding JSON file {json_path.__str__()} created a {plugin.__class__.name}, not a'
                                'plugin-manager.model.Plugin')
            else:
                return plugin

    def write_json(self, json_path: pathlib.Path):
        """
        Encode the state of the current Plugin to JSON and write it to the specified file

        :param json_path: a Path object for the file to be written
        :type json_path: pathlib.Path
        :return: None

        """
        plugin: model.Plugin = self.plugin_widget.rebuild_plugin()
        json_str = json.dumps(plugin, cls=jh.PluginJSONEncoder)
        with json_path.open(mode='w') as json_file:
            json_file.write(json_str)
        self.json_path = json_path
        self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=None)
        self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)


if __name__ == '__main__':
    app = Application()
    app.mainloop()

