import importlib
import pathlib
import tkinter as tk
import tkinter.filedialog as filedialog
import types
from typing import Any, Callable, Optional, Union

import ttkbootstrap as ttkb

import widgets.ttkb_widgets as widgets

import plugin_manager.model.plugin as model


class EntryPointWidget(ttkb.Frame):
    """
    A ttkbootstrap.Combobox based widget that presents a list of module level functions that may be selected
    entrypoints for PluginMenuItems

    """
    def __init__(self, parent, module: types.ModuleType, entry_point: Optional[types.FunctionType], column: int, row: int):
        """
        Creates an instance of plugin_manager.gui.tk_widgets.EntryPointWidget

        :param parent: The GUI parent for this widget
        :param module: The Python module from which the functions will be drawn
        :type module: types.ModuleType
        :param entry_point: The current value for the widget
        :type entry_point: types.FunctionType
        :param column: the column for the widget's label to be gridded
        :type column: int
        :param row: the row for the widget's label to be gridded
        :type row: int

        """
        ttkb.Frame.__init__(self, master=parent)
        self.module = module
        ttkb.Label(master=self, text='Entry Point', width=10).grid(column=column, row=row, padx=5, pady=5,
                                                                   sticky=tk.NW)
        self.entry_point_name_var: ttkb.StringVar = ttkb.StringVar()
        entry_point_list: list[str] = []
        if self.module is not None:
            for name, obj in self.module.__dict__.items():
                if isinstance(obj, types.FunctionType):
                    entry_point_list.append(name)
        self.combo = ttkb.Combobox(master=self, textvariable=self.entry_point_name_var, values=entry_point_list,
                                   width=30)
        self.combo.grid(column=column+1, row=row, padx=5, pady=5, sticky=tk.NW)
        if entry_point is not None:
            if isinstance(entry_point, types.FunctionType):
                self.entry_point_name_var.set(entry_point.__name__)

    def set_entry_point_name(self, name: str) -> None:
        """
        Set the value of the entry point name

        :param name: the name's value
        :type name: str
        :return: None

        """
        if len(name) > 0:
            if name in self.module.__dict__:
                if isinstance(self.module.__dict__[name], types.FunctionType):
                    self.entry_point_name_var.set(name)
                else:
                    raise ValueError(f'{name} is not a Function')
            else:
                raise ValueError(f'{name} is not in module {self.module.__name__}')
        else:
            self.entry_point_name_var.set(name)

    def get_entry_point_name(self) -> str:
        """
        Retrieve the value of the entry point name

        :return: the entry point name
        :rtype: str

        """
        return self.entry_point_name_var.get()

    def get_entry_point(self) -> Optional[types.FunctionType]:
        """
        Retrieve the entry point function object or None if no entry point has been selected

        :return: the entry point function object
        :rtype: Optional[types.FunctionType]

        """
        if self.get_entry_point_name() in self.module:
            return self.module[self.get_entry_point_name()]
        return None

    def get_module(self) -> types.ModuleType:
        """
        Retrieve the module object

        :return: the module object
        :rtype: types.ModuleType

        """
        return self.module


class PluginMenuItemWidget(ttkb.Frame):
    """
    A ttkbootstrap based widget that presents and collects the information to create a plugin_manager.model.PluginMenuItem object

    """
    def __init__(self, parent, module: types.ModuleType, cancel_action: Callable, save_action: Callable,
                 menu_item: Optional[model.PluginMenuItem] = None, menu_iid: Optional[str] = None,
                 item_iid: Optional[str] = None):
        """
        Creates an instance of plugin_manager.gui.tk_widgets.PluginMenuItemWidget

        :param parent: the GUI parent for this widget
        :param module: the module associated with the parent plugin_manager.model.PluginMenu
        :type module: types.ModuleType
        :param cancel_action: a callback routine to be invoked if the Cancel button is clicked
        :type cancel_action: Callable
        :param save_action: a callback routine to be invoked if the Save button is clicked
        :type save_action: Callable
        :param menu_item: an existing PluginMenuItem object
        :type menu_item: plugin_manager.model.PlugingMenuItem
        :param menu_iid: the iid of the parent PluginMenu in the PluginMenuTreeWidget
        :type menu_iid: str
        :param item_iid: the iid of the existing PluginMenuItem in the PluginMenuTreeWidget
        :type item_iid: str

        """
        ttkb.Frame.__init__(self, master=parent)
        self.menu_iid: Optional[str] = menu_iid
        self.item_iid: Optional[str] = item_iid
        self.module = module
        self.menu_item: model.PluginMenuItem = menu_item
        row: int = 0
        self.title_widget = widgets.LabeledTextWidget(parent=self, label_text='Title', label_width=10,
                                                      label_grid_args={'column': 0, 'row': 0, 'padx': 5, 'pady': 5},
                                                      entry_width=40,
                                                      entry_grid_args={'column': 1, 'row': 0, 'padx': 5, 'pady': 5,
                                                      'columnspan': 3})

        row += 1
        if self.menu_item is not None:
            self.entry_point = None
            if self.module is not None and self.menu_item.entry_point_name in self.module.__dict__:
                self.entry_point = self.module.__dict__[self.menu_item.entry_point_name]
        self.entry_point_widget = EntryPointWidget(parent=self, module=module, entry_point=self.entry_point, column=0,
                                                   row=row)
        self.entry_point_widget.grid(column=1, row=row, columnspan=3)

        row += 1
        check_btn_frame = ttkb.Frame(master=self)
        ttkb.Label(master=check_btn_frame, text='Preprocessing Selections:', width=25).grid(column=0, row=0)
        self.sel_person_var = ttkb.IntVar()
        check_button = widgets.Checkbutton(check_btn_frame, text='Person', variable=self.sel_person_var, padding=5,
                                           width=15)
        check_button.grid(column=1, row=0)
        self.sel_dates_var = ttkb.IntVar()
        check_button = widgets.Checkbutton(check_btn_frame, text='Date Range', variable=self.sel_dates_var, padding=5,
                                           width=15)
        check_button.grid(column=2, row=0)
        self.sel_dp_type_var = ttkb.IntVar()
        check_button = widgets.Checkbutton(check_btn_frame, text='DataPoint Type', variable=self.sel_dp_type_var,
                                           padding=5, width=15)
        check_button.grid(column=3, row=0)
        check_btn_frame.grid(column=0, row=row, columnspan=2)

        row += 1
        ttkb.Button(self, text='Cancel', command=cancel_action).grid(column=1, row=row, padx=5, pady=5, sticky=tk.NW)
        ttkb.Button(self, text='Save', command=save_action).grid(column=3, row=row, padx=5, pady=5, sticky=tk.NE)

        if self.menu_item is not None:
            self.title_widget.set_value(menu_item.title)
            if self.menu_item.select_person:
                self.sel_person_var.set(1)
            if self.menu_item.select_date_range:
                self.sel_dates_var.set(1)
            if self.menu_item.select_dp_type:
                self.sel_dp_type_var.set(1)

    def get_menu_item(self) -> model.PluginMenuItem:
        """
        Creates and returns a plugin_manager.model.PluginMenuItem object from the widget's  prompt values

        :return:  a PluginMenuItem object built from the widget's prompt values
        :rtype: plugin_manager.model.PluginItem

        """
        title: str = self.title_widget.get_value()
        entry_point_name: str = self.entry_point_widget.get_entry_point_name()
        sel_person: bool = self.sel_person_var.get() == 1
        sel_date_range: bool = self.sel_dates_var.get() == 1
        sel_dp_type: bool = self.sel_dp_type_var.get() == 1
        if self.menu_item is None:
            self.menu_item = model.PluginMenuItem(title=title, entry_point_name=entry_point_name,
                                                  select_person=sel_person, select_date_range=sel_date_range,
                                                  select_dp_type=sel_dp_type)
        else:
            self.menu_item.title = title
            self.menu_item.entry_point_name = entry_point_name
            self.menu_item.sel_person = sel_person
            self.menu_item.select_date_range = sel_date_range
            self.menu_item.select_dp_type = sel_dp_type
        return self.menu_item


class ModuleWidget(widgets.LabeledTextWidget):
    """
    A widget that allows the user to select a Python module from a directory structure.

    """
    def __init__(self, parent, module_name: str, column: int, row: int):
        """
        Creates an instance of ModuleWidget

        :param parent: the GUI parent for this widget
        :param module_name: the initial value for the widget module name prompt
        :type module_name: str
        :param column: the column the widgetss label will be gridded to.  The entry widget will be gridded to column + 1
        :type column: int
        :param row: the row the widget's label and entry widget will be gridded to
        :type row: int

        """
        widgets.LabeledTextWidget.__init__(self, parent=parent, label_text='Module', label_width=10,
                                           label_grid_args={'column': column, 'row': row, 'padx': 5, 'pady': 5,
                                           'sticky': tk.NW}, entry_width=100,
                                           entry_grid_args={'column': column+1, 'row': row, 'padx': 5, 'pady': 5,
                                           'sticky': tk.NW, 'columnspan': 2}, regex_str='\\s*([\\w,.]*)\\s*')
        if len(module_name.strip()) > 0:
            self.set_value(module_name)

        ttkb.Button(parent, text='Browse ...', command=self.browse).grid(column=column+3, row=row, padx=5, pady=5)
        parent.columnconfigure(0, weight=20)
        parent.columnconfigure(1, weight=60)
        parent.columnconfigure(2, weight=20)

    def browse(self):
        """
        Presents an open file dialog set up to select python .py files.  The name of the file becomes the new value
        for the module name entry widget

        :return: None

        """
        parts: list[str] = self.get_value().split('.')
        module_path: pathlib.Path = pathlib.Path()
        for part in parts:
            module_path = pathlib.Path(module_path, part)
        mod_path_str: str = filedialog.askopenfilename(filetypes=[('Python', '*.py')],
                                                       initialdir=module_path.parent.__str__(),
                                                       initialfile=module_path.name)
        mod_name: str = ''
        parts: tuple[str] = pathlib.Path(mod_path_str).parts
        mod_path: pathlib.Path = pathlib.Path()
        for part in parts:
            mod_path = pathlib.Path(mod_path, part)
            if mod_path.is_dir() and pathlib.Path(mod_path, '__init__.py').exists():
                if len(mod_name) == 0:
                    mod_name = part
                else:
                    mod_name = f'{mod_name}.{part}'
            elif len(mod_name) > 0:
                mod_name = f'{mod_name}.{part.replace(".py", "")}'
        self.set_module_name(mod_name)

    def get_module_name(self) -> str:
        """
        Retrieves the module name

        :return: module name
        :rtype: str
        """
        return self.get_value()

    def set_module_name(self, module_name: str) -> None:
        """
        Sets the widget's module name prompt value

        :param module_name: the value to be set
        :type module_name: str
        :return: None

        """
        self.set_value(module_name)

    def get_module(self) -> types.ModuleType:
        """
        Retrieves the module object selected by the user

        :return: a Python module object
        :rtype: types.ModuleType

        """
        try:
            module = importlib.import_module(self.get_module_name())
        except ModuleNotFoundError:
            module = None
        except ImportError:
            module = None
        return module


class PluginMenuWidget(ttkb.Frame):
    """
    Prompts the user for the information necessary to construct a plugin_manager.model.PluginMenu object

    """
    def __init__(self, parent, cancel_action: Callable, save_action: Callable,
                 menu: Optional[model.PluginMenu] = None, menu_iid: Optional[str] = None):
        """
        Creates an instance of PluginMenuWidget

        :param parent: the GUI parent of this widget
        :param cancel_action: a callback routine to be invoked when the Cancel button is clicked
        :type cancel action: Callable
        :param save_action: a callback routine to be invoked when the Save button is clicked
        :type save_action: Callable
        :param menu: a PluginMenu object or None
        :param menu_iid: the iid of the PluginMenu object, taken from the PluginMenuTreeWidget

        """
        ttkb.Frame.__init__(self, master=parent)
        self.menu_iid: Optional[str] = menu_iid
        self.menu: Optional[model.PluginMenu] = menu
        row: int = 0
        self.title_widget = widgets.LabeledTextWidget(parent=self, label_text='Title', label_width=10,
                                                      label_grid_args={'column': 0, 'row': row, 'padx': 5, 'pady': 5},
                                                      entry_width=30,
                                                      entry_grid_args={'column': 1, 'row': row, 'padx': 5, 'pady': 5,
                                                                       'columnspan': 2})
        row += 1
        module_name: str = ''
        if menu is not None:
            self.title_widget.set_value(menu.title)
            module_name = menu.module_name
        self.module_widget = ModuleWidget(parent=self, module_name=module_name, column=0, row=row)

        row += 1
        ttkb.Button(self, text='Cancel', command=cancel_action).grid(column=0, row=row, padx=5, pady=5, sticky=tk.NW)
        ttkb.Button(self, text='Save', command=save_action).grid(column=2, row=row, padx=5, pady=5, sticky=tk.NW)

    def get_menu(self) -> model.PluginMenu:
        """
        Creates and returns a PluginMenu object from the widget's prompt values

        :return: a PluginMenu object
        :rtype: plugin_manager.model.PluginMenu

        """
        title = self.title_widget.get_value()
        module = self.module_widget.get_module_name()
        if self.menu is None:
            items: list[model.PluginMenuItem] = []
            self.menu = model.PluginMenu(title=title, module_name=module, items=items)
        else:
            self.menu.title = title
            self.menu.module_name = module
        return self.menu


class PluginMenuTree(ttkb.Treeview):
    """
    A widget based on the ttkbootstrap.Treeview widget.  The tree items are PluginMenu object and their PluginMenuItem
    children.  The tree structure is the repository for the PluginMenu and PluginMenuItems maintained by the Plugin
    Management app.  This is an easy way to keep track of insertions and deletions.  The Plugin object written to JSON
    is created from the nodes in this tree.  Each PluginMenu node contains two fields; one containing the output of
    the Plugin Menu object's __str__ method, and the other containing the object itself.  The PluginMenu objects are
    stored with an empty PluginMenuItem list.  A PluginMenu object children will be stored in PluginMenuItem nodes
    that descend for it's node. Each PluginMenuItem node also contains two fields;  one for the output of it's
    __str__ method and the other for the object itself.

    """
    MENU_STR = 'menu_str'
    ITEM_STR = 'item_str'
    REPR = 'repr'
    MENU_TAG = 'menu'
    ITEM_TAG = 'item'

    def __init__(self, parent, select_menu_action: Callable, select_item_action: Callable,
                 menus: list[model.PluginMenu] = []):
        """
        Creates an instance of PluginMenuTreeWidget

        :param parent: the GUI parent for this widget
        :param select_menu_action: a callback method to be invoked when a PluginMenu node is selected by the user
        :type select_menu_action: Callable
        :param select_item_action: a callback method to be invoked when a PluginMenuItem node is selected by the user.
        :type select_item_action: Callable
        :param menus: a list of PluginMenu objects to be used in building the Treeview widget
        :type menus: list[PluginMenu]

        """
        ttkb.Treeview.__init__(self, master=parent, columns=(PluginMenuTree.MENU_STR, PluginMenuTree.ITEM_STR,
                                                             PluginMenuTree.REPR), show='headings')
        hscroll = ttkb.Scrollbar(master=self, orient=tk.HORIZONTAL, command=self.xview)
        vscroll = ttkb.Scrollbar(master=self, orient=tk.VERTICAL, command=self.yview)
        self.configure(displaycolumns=[PluginMenuTree.MENU_STR, PluginMenuTree.ITEM_STR], height=50,
                       yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        vscroll.grid(column=1, row=0, sticky=tk.NS)
        hscroll.grid(column=0, row=1, sticky=tk.EW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.column('#1', minwidth=40, stretch=False)
        self.heading(PluginMenuTree.MENU_STR, text='Menu', anchor=tk.W)
        self.heading(PluginMenuTree.ITEM_STR, text='Menu Item', anchor=tk.W)
        self.select_menu_action = select_menu_action
        self.select_item_action = select_item_action
        if len(menus) > 0:
            for menu in menus:
                menu_iid: str = self.insert(parent='', index='end', text='Menu:', open=True,
                                            tags=[PluginMenuTree.MENU_TAG, ])
                self.save_menu_attr(menu_iid=menu_iid, menu=menu)
                for item in menu.items:
                    item_iid = self.insert(parent=menu_iid, index='end', text='Menu Item:',
                                           tags=[PluginMenuTree.ITEM_TAG, ])
                    self.save_item_attr(item_iid, item)
        else:
            self.insert_menu(idx=-1)
        self.tag_bind(PluginMenuTree.MENU_TAG, '<<TreeviewSelect>>', self.select_menu_action)
        self.tag_bind(PluginMenuTree.ITEM_TAG, '<<TreeviewSelect>>', self.select_item_action)

    def prev_index(self, iid: str) -> int:
        """
        Returns the index of the previous node at the hierachical level of the node indicated by the provided iid

        :param iid: the iid of the node relative to which the previous node will be selected
        :type iid: str`
        :return: the index of the previous node, or -1 if the speicified node is the first node in the tree root's node list
        :rtype: int

        """
        return self.index(self.prev(iid))

    def next_index(self, iid: str) -> Union[int, str]:
        idx = self.index(self.next(iid))
        if idx == 0:
            return 'end'
        else:
            return idx

    def save_menu_attr(self, menu_iid: str, menu: model.PluginMenu) -> None:
        """
        Update the node specified my menu_iid with the supplied PluginMenu object

        :param menu_iid: the iid of the tree node to be updated
        :type menu_iid: str
        :param menu: the PluginMenu object to be stored in the tree node
        :type menu: plugin_manager.model.PluginMenu
        :return: None

        """
        self.set(menu_iid, PluginMenuTree.MENU_STR, menu.__str__())
        self.set(menu_iid, PluginMenuTree.ITEM_STR, '')
        self.set(menu_iid, PluginMenuTree.REPR, menu.__repr__())

    def insert_menu(self, idx: Union[int, str]) -> tuple[str, model.PluginMenu]:
        """
        Insert a PluginMenu node and a child PluginMenuItem node before the node indicated by the idx argument and
        return an empty PluginMenu object associated with the inserted node.  The PluginMenuItem node is created
        to provided the menu's initial item, since another PluginMenuItem node can only be inserted by selecting an
        existing PluginMenu node

        :param idx: the index of the node the new node will be inserted before
        :type idx: int
        :return: an empty PluginMenu object
        :rtype: plugin_manager.model.PluginMenu

        """
        menu_iid: str = self.insert(parent='', index=idx, text='Menu:', open=True, tags=[PluginMenuTree.MENU_TAG])
        new_menu: model.PluginMenu = model.PluginMenu(title='New Menu', module_name='', items=[])
        self.save_menu_attr(menu_iid, new_menu)
        _, new_item = self.insert_menu_item(menu_iid=menu_iid, idx='end')
        new_menu.add_item(new_item)
        self.selection_set(menu_iid)
        return menu_iid, new_menu

    def save_item_attr(self, item_iid: str, item: model.PluginMenuItem) -> None:
        """
        Update the node specified my menu_iid with the supplied PluginMenu object

        :param menu_iid: the iid of the tree node to be updated
        :type menu_iid: str
        :param item: the PluginMenuItem object to be stored in the tree node
        :type item: plugin_manager.model.PluginMenuItem
        :return: None

        """
        self.set(item_iid, PluginMenuTree.MENU_STR, '')
        self.set(item_iid, PluginMenuTree.ITEM_STR, item.__str__())
        self.set(item_iid, PluginMenuTree.REPR, item.__repr__())

    def insert_menu_item(self, menu_iid: str, idx: Union[int, str]) -> tuple[str, model.PluginMenuItem]:
        """
        Insert a PluginMenuItem node before the node indicated by the idx argument and return an empty PluginMenuItem
        object associated with the inserted node.

        :param idx: the index of the node the new node will be inserted before
        :type idx: int
        :return: an empty PluginMenuItem object
        :rtype: plugin_manager.model.PluginMenuItem

        """
        new_item: model.PluginMenuItem = model.PluginMenuItem(title='New Item', entry_point_name='',
                                                              select_person=False, select_date_range=False,
                                                              select_dp_type=False)
        item_iid: str = self.insert(parent=menu_iid, index=idx, text='Menu Item:', tags=[PluginMenuTree.ITEM_TAG, ])
        self.save_item_attr(item_iid, new_item)
        self.selection_set(item_iid)
        return item_iid, new_item

    def rebuild_plugin(self, plugin: model.Plugin) -> model.Plugin:
        """
        Update the provided Plugin object with the PluginMenu/PluginMenuItem objects stored in the Treeview widget's
        nodes.

        :param plugin: the Plugin to be updated.
        :type plugin: plugin_manager.model.Plugin
        :return: the updated Plugin object
        :rtype; plugin_manager.model.Plugin

        """
        menu_list: list[model.PluginMenu] = []
        menu_iids: tuple[str] = self.get_children(item='')
        for menu_idx in range(0, len(menu_iids)):
            menu_iid = menu_iids[menu_idx]
            menu_item_list: list[model.PluginMenuItem] = []
            menu_item_iids: tuple[str] = self.get_children(item=menu_iid)
            if len(menu_item_iids) > 0:
                for menu_item_idx in range(0, len(menu_item_iids)):
                    menu_item_iid = menu_item_iids[menu_item_idx]
                    repr_str: str = self.set(menu_item_iid, PluginMenuTree.REPR)
                    menu_item_list.append(eval(repr_str))
                repr_str = self.set(menu_iid, PluginMenuTree.REPR)
                menu: model.PluginMenu = eval(repr_str)
                menu.items.extend(menu_item_list)
                menu_list.append(menu)
        plugin.menus = menu_list
        return plugin


class PluginWidget(ttkb.Frame):
    """
    Prompts the user for the title, description, author name and author email properties to be used in creating or
    updating a plugin_manager.model.Plugin object

    """
    def __init__(self, parent, plugin: Optional[model.Plugin]):
        """
        Creates an instance of PluginWidget

        :param parent: the GUI parent of this widget
        :param plugin: a Plugin object or none
        :type plugin: plugin_manager.model.Plugin

        """
        ttkb.Frame.__init__(self, master=parent)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.plugin: Optional[model.Plugin] = plugin
        self.create: bool = False
        self.current_menu: Optional[model.PluginMenu] = None
        self.current_menu_iid: Optional[str] = None
        self.current_item: Optional[model.PluginMenuItem] = None
        self.current_item_iid: Optional[str] = None

        header_frame: ttkb.Frame = ttkb.Frame(master=self)
        header_frame.columnconfigure(0, weight=0)
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(2, weight=0)
        for row in range(0, 4):
            header_frame.rowconfigure(row, weight=1)

        row: int = 0
        self.name_widget = widgets.LabeledTextWidget(parent=header_frame, label_text='Name:', label_width=15,
                                                     label_grid_args={'column': 0, 'row': row, 'padx': 5, 'pady': 5},
                                                     entry_width=30,
                                                     entry_grid_args={'column': 1, 'row': row, 'padx': 5, 'pady': 5,
                                                                      'columnspan': 3})
        row += 1
        self.desc_widget = widgets.LabeledTextWidget(parent=header_frame, label_text='Description:', label_width=15,
                                                     label_grid_args={'column': 0, 'row': row, 'padx': 5, 'pady': 5},
                                                     entry_width=50,
                                                     entry_grid_args={'column': 1, 'row': row, 'padx': 5, 'pady': 5,
                                                                      'columnspan': 3})
        row += 1
        self.author_name_widget = widgets.LabeledTextWidget(parent=header_frame, label_text='Author Name:',
                                                            label_width=15,
                                                            label_grid_args={'column': 0, 'row': row, 'padx': 5,
                                                                             'pady': 5}, entry_width=50,
                                                            entry_grid_args={'column': 1, 'row': row, 'padx': 5, 'pady': 5,
                                                                     'columnspan': 3})
        row += 1
        self.author_email_widget = widgets.LabeledTextWidget(parent=header_frame, label_text='Author Email:',
                                                             label_width=15,
                                                             label_grid_args={'column': 0, 'row': row, 'padx': 5,
                                                                              'pady': 5},
                                                             entry_width=50,
                                                             entry_grid_args={'column': 1, 'row': row, 'padx': 5,
                                                                              'pady': 5, 'columnspan': 3})
        row += 1
        ttkb.Label(header_frame, text=' ').grid(column=0, row=row, padx=5, pady=5, columnspan=3, sticky=tk.W)
        ttkb.Label(header_frame,
                   text='Click on a menu or item to select it for edit or deletion, or to insert above or below it.'
                        'To insert a menu, first select a menu, then click Insert Above or Insert Below, and a menu '
                        'and a single menu item under it will be created.  To insert a menu item, select a menu item '
                        'under the menu you wish to add an item to, then click Insert Above or Insert Below. If the'
                        'menu item information exceeds it''s column width, you can move the menu item column by '
                        'placing the cursor over the left edge of the Menu Item heading until a drag cursor is '
                        'displayed.  Hold the left mouse button down while dragging the column to the left or right.',
                   wraplength=800, justify=tk.LEFT, anchor=tk.W) \
            .grid(column=0, row=row, padx=5, columnspan=3, rowspan=5, sticky=tk.W)

        header_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tk.EW)

        self.tree_frame = ttkb.Frame(self)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.columnconfigure(1, weight=0)
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.rowconfigure(1, weight=1)
        self.tree_frame.rowconfigure(2, weight=1)
        menus: list[model.PluginMenu] = []
        if self.plugin is not None and self.plugin.menus is not None:
            menus = self.plugin.menus
        self.menu_tree = PluginMenuTree(parent=self.tree_frame, select_menu_action=self.select_menu,
                                        select_item_action=self.select_menu_item, menus=menus)
        self.menu_tree.grid(column=0, row=0, rowspan=3, sticky=tk.NSEW)
        self.insert_above_btn = ttkb.Button(master=self.tree_frame, text='Insert Above',
                                            command=self.insert_above)
        self.insert_above_btn.grid(column=1, row=0, padx=5, pady=5, sticky=tk.EW)

        self.insert_below_btn = ttkb.Button(master=self.tree_frame, text='Insert Below',
                                            command=self.insert_below)
        self.insert_below_btn.grid(column=1, row=1, padx=5, pady=5, sticky=tk.EW)

        row += 1
        self.delete_btn = ttkb.Button(master=self.tree_frame, text='Delete', command=self.delete)
        self.delete_btn.grid(column=1, row=2, padx=5, pady=5, sticky=tk.EW)

        self.tree_frame.grid(column=0, row=2, padx=10, pady=5, stick=tk.NSEW)

        self.footer_frame: Optional[ttkb.Frame] = None
        self.footer_widget: Optional[ttkb.Frame] = None
        self.replace_footer()

        if self.plugin is not None:
            self.populate_plugin_widget()

    def focus_set(self):
        """
        Delegate focus set calls to the Plugin Name widgetd

        :return: None

        """
        self.name_widget.focus_set()

    def disable_insert(self):
        """
        Disable the Insert Above and Insert Below buttons

        :return: None

        """
        self.insert_above_btn.configure(state=tk.DISABLED)
        self.insert_below_btn.configure(state=tk.DISABLED)

    def enable_insert(self):
        """
        Enable the Insert Above and Insert Below buttons

        :return: None

        """
        self.insert_above_btn.configure(state=tk.NORMAL)
        self.insert_below_btn.configure(state=tk.NORMAL)

    def replace_footer(self):
        """
        Create a blank place holder Frame and grid it into footer frame

        :return: None

        """
        if self.footer_frame is not None:
            self.footer_frame.forget()
        self.footer_frame = ttkb.Frame(self)
        self.footer_widget = ttkb.Frame(self.footer_frame)
        for row in range(0, 4):
            ttkb.Label(self.footer_widget, text=' ', width=150).grid(column=0, row=row, padx=5, pady=5)
        self.footer_widget.grid(column=0, row=0, sticky=tk.NSEW)
        self.footer_frame.grid(column=0, row=3, padx=15, pady=5, sticky=tk.NSEW)

    def cancel(self):
        """
        A callback method to be invoked when the Cancel button on the PluginMenuWidget or PluginMenuItemWidget is
        clicked

        :return: None

        """
        self.replace_footer()
        self.enable_insert()

    def populate_plugin_widget(self):
        """
        Set the plugin name, description and author name and email using the provied Plugin object

        :return: None

        """
        self.name_widget.set_value(self.plugin.name)
        self.desc_widget.set_value(self.plugin.description)
        self.author_name_widget.set_value(self.plugin.author_name)
        self.author_email_widget.set_value(self.plugin.author_email)

    def save_menu(self):
        """
        A callback method to be invoked to save an updated PluginMenu object to its node in its PlugInMenuTree node.
        After saving the object, the Insert Above/Below buttons are enabled and a placeholder frame is inserted into
        the footer frame

        :return: None

        """
        self.current_menu = self.footer_widget.get_menu()
        self.menu_tree.save_menu_attr(self.current_menu_iid, self.current_menu)
        self.enable_insert()
        self.replace_footer()

    def select_menu(self, event):
        """
        A callback to be invoked when a Plugin node on the PluginMenuTreeWidget is clicked

        :param event:
        :return: None
        """
        tree_element = self.menu_tree.selection()
        repr_str: str = self.menu_tree.set(tree_element[0], PluginMenuTree.REPR)
        menu: model.PluginMenu = eval(repr_str)
        if not isinstance(menu, model.PluginMenu):
            raise ValueError(f'The __repr__ value {repr_str} at iid {tree_element[0]} is not valid')
        else:
            self.current_menu = menu
            self.current_menu_iid = tree_element[0]
            self.current_item = None
            self.current_item_iid = None
        self.populate_menu_widget(menu_iid=self.current_menu_iid, menu=self.current_menu)
        self.enable_insert()

    def populate_menu_widget(self, menu_iid: str, menu: model.PluginMenu):
        """
        Creates a PluginMenuWidget from the provided PluginMenu object, places the widget in the footer frame
        """
        self.footer_frame.forget()
        self.footer_widget = PluginMenuWidget(self.footer_frame, cancel_action=self.cancel,
                                              save_action=self.save_menu, menu=menu,
                                              menu_iid=menu_iid)
        self.footer_widget.grid(column=0, row=0, sticky=tk.NSEW)
        self.footer_frame.grid(column=0, row=3, padx=15, pady=5, sticky=tk.NSEW)

    def save_menu_item(self):
        """
        A callback method to be invoked when the Save button on the PluginMenuWidget is clicked

        :return: None

        """
        self.current_item: model.PluginMenuItem = self.footer_widget.get_menu_item()
        self.menu_tree.save_item_attr(self.current_item_iid, self.current_item)
        self.enable_insert()
        self.replace_footer()

    def select_menu_item(self, event):
        """
        A callback method to be invoked when a PluginMenu node on the PluginMenuTreeWidget is clicked

        :param event:
        :return: None

        """
        tree_element = self.menu_tree.selection()
        repr_str: str = self.menu_tree.set(tree_element[0], PluginMenuTree.REPR)
        item: model.PluginMenuItem = eval(repr_str)
        if not isinstance(item, model.PluginMenuItem):
            raise ValueError(f'The __repr__ value {repr_str} at iid {tree_element[0]} is not valid')
        item_parent = self.menu_tree.parent(tree_element[0])
        repr_str: str = self.menu_tree.set(item_parent, PluginMenuTree.REPR)
        menu: model.PluginMenu = eval(repr_str)
        if not isinstance(menu, model.PluginMenu):
            raise ValueError(f'The __repr__ value {repr_str} at iid {tree_element[0]} is not valid')
        else:
            self.current_menu = menu
            self.current_menu_iid = item_parent
            self.current_item = item
            self.current_item_iid = tree_element[0]
        self.populate_menu_item_widget(module_name=self.current_menu.module_name, menu_iid=item_parent,
                                       item_iid=tree_element[0], item=self.current_item)
        self.enable_insert()

    def populate_menu_item_widget(self, module_name: str, menu_iid: str, item_iid: str,
                                  item: model.PluginMenuItem) -> None:
        """
        Creates a PluginMenuItemWidget and populates its prompt values fro the provided PluginMenuItem.  Before
        creating the widget, the module specified by the module_name property is imported.  If the module is not
        found a ModuleNotFound exception is thrown.  If the module cannot be imported because off syntax errors,
        an ImportError exception is thrown.

        :param module_name:
        :param menu_iid:
        :param item_iid:
        :param item:
        :return:
        """
        if len(module_name) > 0:
            try:
                module: Optional[types.ModuleType] = importlib.import_module(module_name)
            except ModuleNotFoundError:
                module = None
            except ImportError:
                module = None
        else:
            module = None
        self.footer_frame.forget()
        self.footer_frame = ttkb.Frame(self)
        self.footer_widget = PluginMenuItemWidget(self.footer_frame, module=module, cancel_action=self.cancel,
                                                  save_action=self.save_menu_item, menu_item=item,
                                                  menu_iid=menu_iid, item_iid=item_iid)
        self.footer_widget.grid(column=0, row=0, sticky=tk.NSEW)
        self.footer_frame.grid(column=0, row=3, padx=15, pady=5, sticky=tk.NSEW)

    def insert_above(self) -> None:
        """
        A callback method to be invoked when the Insert Above button on the PluginMenuTreeWidget is clicked.  The
        invocation is delegated to the insert_item_above method if a PluginMenuItem node was selected when the
        button was clicked, or the insert_menu_above if a PluginMenu node was selected when the button was clicked

        :return: None

        """
        if self.current_menu is not None:
            if self.current_item is not None:
                self.current_item_iid, self.current_item = self.insert_item_above()
                self.current_menu.add_item(self.current_item)
                self.populate_menu_item_widget(module_name=self.current_menu.module_name,
                                               menu_iid=self.current_menu_iid, item_iid=self.current_item_iid,
                                               item=self.current_item)
            else:
                self.current_menu_iid, self.current_menu = self.insert_menu_above()
                self.plugin.add_menu(self.current_menu)
                self.populate_menu_widget(menu_iid=self.current_menu_iid, menu=self.current_menu)
        self.disable_insert()

    def insert_below(self) -> None:
        """
        A callback method to be invoked when the Insert Above button on the PluginMenuTreeWidget is clicked.  The
        invocation is delegated to the insert_item_below method if a PluginMenuItem node was selected when the
        button was clicked, or the insert_menu_below if a PluginMenu node was selected when the button was clicked

        :return: None

        """
        if self.current_menu is not None:
            if self.current_item is not None:
                self.current_item_iid, self.current_item = self.insert_item_below()
                self.current_menu.add_item(self.current_item)
                self.populate_menu_item_widget(module_name=self.current_menu.module_name,
                                               menu_iid=self.current_menu_iid, item_iid=self.current_item_iid,
                                               item=self.current_item)
            else:
                self.current_menu_iid, self.current_menu = self.insert_menu_below()
                self.plugin.add_menu(self.current_menu)
                self.populate_menu_widget(menu_iid=self.current_menu_iid, menu=self.current_menu)
        self.disable_insert()

    def delete(self) -> None:
        """
        A callback method to be invoked when the Delete button is clicked on the PluginMenuTreeWidget is clicked.
        The invokation is delegated to the delete_item or delete_menu method, depending on whether a PluginMenuItem
        or PluginMenu was selected when the button was clicked

        :return: None

        """
        if self.current_menu is not None:
            if self.current_item is not None:
                self.delete_item()
            else:
                self.delete_menu()
        self.enable_insert()
        self.replace_footer()

    def insert_menu_above(self) -> tuple[str, model.PluginMenu]:
        """
        Insert a PluginMenu node above the selected node in the PluginMenuTreeWidget

        :returns: the iid and PluginMenu object associated with the inserted node.
        :rtype: tuple[str, plugin_manager.model.PluginMenu]

        """
        idx = self.menu_tree.index(self.current_menu_iid)
        return self.menu_tree.insert_menu(idx)

    def insert_menu_below(self) -> tuple[str, model.PluginMenu]:
        """
        Insert a PluginMenu node below the selected node in the PluginMenuTreeWidget

        :returns: the iid and PluginMenu object associated with the inserted node.
        :rtype: tuple[str, plugin_manager.model.PluginMenu]

        """
        idx = self.menu_tree.next_index(self.current_menu_iid)
        return self.menu_tree.insert_menu(idx)

    def delete_menu(self):
        """
        Delete the currently selected PluginMenu node on the PluginMenuTreeWidget

        :return: None

        """
        self.menu_tree.delete(self.footer_widget.menu_iid)
        self.current_menu = None
        self.current_menu_iid = None

    def insert_item_above(self) -> tuple[str, model.PluginMenuItem]:
        """
         Insert a PluginMenuItem node above the selected node in the PluginMenuTreeWidget

         :returns: the iid and PluginMenuItem object associated with the inserted node.
         :rtype: tuple[str, plugin_manager.model.PluginMenuItem]

         """
        idx = self.menu_tree.index(self.current_item_iid)
        return self.menu_tree.insert_menu_item(self.current_menu_iid, idx)

    def insert_item_below(self) -> tuple[str, model.PluginMenuItem]:
        """
         Insert a PluginMenuItem node below the selected node in the PluginMenuTreeWidget

         :returns: the iid and PluginMenuItem object associated with the inserted node.
         :rtype: tuple[str, plugin_manager.model.PluginMenuItem]

         """
        idx = self.menu_tree.next_index(self.current_item_iid)
        return self.menu_tree.insert_menu_item(self.current_menu_iid, idx)

    def delete_item(self):
        """
        Delete the currently selected PluginMenuItem node on the PluginMenuTreeWidget

        :return: None

        """
        self.menu_tree.delete(self.footer_widget.item_iid)
        self.current_item = None
        self.current_item_iid = None

    def rebuild_plugin(self) -> model.Plugin:
        """
        Create a Plugin object from the prompts on the PluginWidget and the nodes on the PluginMenuTreeWidget

        :return: the created Plugin object
        :rtype: plugin_manager.model.Plugin

        """
        if self.plugin is None:
            self.plugin = model.Plugin(name=self.name_widget.get_value(),
                                       description=self.desc_widget.get_value(),
                                       author_name=self.author_name_widget.get_value(),
                                       author_email=self.author_email_widget.get_value(),
                                       menus=[])
        else:
            self.plugin.name = self.name_widget.get_value()
            self.plugin.description = self.desc_widget.get_value()
            self.plugin.author_name = self.author_name_widget.get_value()
            self.plugin.author_email = self.author_email_widget.get_value()
        return self.menu_tree.rebuild_plugin(self.plugin)

