import json
import pathlib
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Any, Callable, Optional

import ttkbootstrap as ttkb

import widgets.tk_widgets as widgets
import plugin_manager.model.json_handler as jh

import plugin_manager.model.plugin as model
import plugin_manager.gui.tk_widgets as plugin_widgets


class Application(ttkb.Window):
    def __init__(self):
        ttkb.Window.__init__(self, title='Plugin Manager', themename='darkly')

        self.json_path: Optional[pathlib.Path] = None
        self.plugin: Optional[model.Plugin] = None

        row: int = 0
        self.plugin_json_widget: widgets.LabeledTextWidget = \
            widgets.LabeledTextWidget(parent=self, label_text='Plugin JSON File:',
                                      label_width=15, label_grid_args={'column': 0, 'row': row, 'padx': 5, 'pady': 5},
                                      entry_width=100,
                                      entry_grid_args={'column': 1, 'row': row, 'padx': 5, 'pady': 5, 'columnspan': 2},
                                      regex_str=None)
        ttkb.Button(master=self, text='Browse ...', command=self.browse_plugins, width=10).grid(column=3, row=row,
                                                                                                padx=5, pady=5,
                                                                                                sticky=tk.EW)
        ttkb.Button(master=self, text='Create', command=self.create_plugin, width=10).grid(column=4, row=row, padx=5,
                                                                                 pady=5, sticky=tk.EW)
        ttkb.Button(master=self, text='Exit', command=self.exit_app, width=10).grid(column=5, row=row, padx=5, pady=5,
                                                                          sticky=tk.EW)
        self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=None, cancel_action=self.exit_app,
                                                         save_action=self.save, save_as_action=self.save_as)

        row += 1
        self.plugin_widget_row = row
        self.plugin_widget_columnspan = 6
        self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)

    def browse_plugins(self) -> None:
        json_path_str: str = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if len(json_path_str) > 0:
            self.json_path = pathlib.Path(json_path_str)
            with self.json_path.open(mode='r') as json_file:
                json_str = json_file.read()
                plugin = json.loads(eval(json_str), object_hook=jh.plugin_object_hook)
                if not isinstance(plugin, model.Plugin):
                    raise TypeError(f'Decoding JSON file {json_path_str} created a {plugin.__class__.name}, not a'
                                    'biometrics_tracker.config,model.Plugin')
                else:
                    self.plugin = plugin
                    self.plugin_widget.forget()
                    self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=self.plugin,
                                                                     cancel_action=self.exit_app,
                                                                     save_action=self.save,
                                                                     save_as_action=self.save_as)
                self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)
                self.plugin_widget.focus_set()

            self.plugin_json_widget.set_value(json_path_str)

    def create_plugin(self):
        self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=None,
                                                         cancel_action=self.exit_app,
                                                         save_action=None,
                                                         save_as_action=self.save_as)
        self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)
        self.plugin_widget.focus_set()

    def exit_app(self):
        self.quit()

    def save(self):
        self.write_json(self.json_path)

    def save_as(self, create: bool = False):
        if create:
            file_name: str = filedialog.asksaveasfilename(confirmoverwrite=True)
        else:
            file_name = filedialog.asksaveasfilename(confirmoverwrite=True, initialdir=self.json_path.parent.__str__())
        self.write_json(pathlib.Path(file_name))

    def write_json(self, json_path: pathlib.Path):
        plugin: model.Plugin = self.plugin_widget.rebuild_plugin()
        json_str = json.dumps(plugin, cls=jh.PluginJSONEncoder)
        with json_path.open(mode='w') as json_file:
            json_file.write(json_str)
        self.json_path = json_path
        self.plugin_widget = plugin_widgets.PluginWidget(self, plugin=None, cancel_action=self.exit_app,
                                                         save_action=self.save, save_as_action=self.save_as)
        self.plugin_widget.grid(column=0, row=self.plugin_widget_row, columnspan=self.plugin_widget_columnspan)


if __name__ == '__main__':
    app = Application()
    app.mainloop()

