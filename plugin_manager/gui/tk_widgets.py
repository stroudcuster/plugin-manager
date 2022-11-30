import importlib
import json
import pathlib
import tkinter as tk
import tkinter.filedialog as filedialog
import types
from typing import Any, Callable, Optional, Union

import ttkbootstrap as ttkb
import ttkbootstrap.scrolled as scrolled

import widgets.tk_widgets as widgets

import plugin_manager.model.plugin as model


class EntryPointWidget(ttkb.Frame):
    def __init__(self, parent, module: types.ModuleType, entry_point: Optional[Callable], column: int, row: int):
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

    def set_entry_point_name(self, name: str):
        if name in self.module.__dict__:
            if isinstance(self.module.__dict__[name], types.FunctionType):
                self.entry_point_name_var.set(name)
            else:
                raise ValueError(f'{name} is not a Function')
        else:
            raise ValueError(f'{name} is not in module {self.module.__name__}')

    def get_entry_point_name(self) -> str:
        return self.entry_point_name_var.get()

    def get_entry_point(self) -> Optional[types.FunctionType]:
        if self.get_entry_point_name() in self.module:
            return self.module[self.get_entry_point_name()]
        return None

    def get_module(self) -> types.ModuleType:
        return self.module


class PluginMenuItemWidget(ttkb.Frame):
    def __init__(self, parent, module: types.ModuleType, cancel_action: Callable, save_action: Callable,
                 menu_item: Optional[model.PluginMenuItem] = None, menu_iid: Optional[str] = None,
                 item_iid: Optional[str] = None):
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
            self.entry_point = entry_point_name
            self.menu_item.sel_person = sel_person
            self.menu_item.select_date_range = sel_date_range
            self.menu_item.select_dp_type = sel_dp_type
        return self.menu_item


class ModuleWidget(widgets.LabeledTextWidget):
    def __init__(self, parent, module_name: str, column: int, row: int):
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
        return self.get_value()

    def set_module_name(self, module_name: str) -> None:
        self.set_value(module_name)

    def get_module(self) -> types.ModuleType:
        try:
            module = importlib.import_module(self.get_module_name())
        except ModuleNotFoundError:
            module = None
        except ImportError:
            module = None
        return module


class PluginMenuWidget(ttkb.Frame):
    def __init__(self, parent, cancel_action: Callable, save_action: Callable,
                 menu: Optional[model.PluginMenu] = None, menu_iid: Optional[str] = None):
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
    MENU_STR = 'menu_str'
    ITEM_STR = 'item_str'
    REPR = 'repr'
    MENU_TAG = 'menu'
    ITEM_TAG = 'item'

    def __init__(self, parent, select_menu_action: Callable, select_item_action: Callable,
                 menus: list[model.PluginMenu] = []):
        ttkb.Treeview.__init__(self, master=parent, columns=(PluginMenuTree.MENU_STR, PluginMenuTree.ITEM_STR,
                                                             PluginMenuTree.REPR))
        self.configure(displaycolumns=[PluginMenuTree.MENU_STR, PluginMenuTree.ITEM_STR])
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=50)
        self.heading(PluginMenuTree.MENU_STR, text='Menu')
        self.heading(PluginMenuTree.ITEM_STR, text='Menu Item')
        self.menus: list[model.PluginMenu] = menus
        self.select_menu_action = select_menu_action
        self.select_item_action = select_item_action
        for menu in menus:
            menu_iid: str = self.insert(parent='', index='end', text='Menu:', open=True,
                                        tags=[PluginMenuTree.MENU_TAG, ])
            self.save_menu_attr(menu_iid=menu_iid, menu=menu)
            for item in menu.items:
                item_iid = self.insert(parent=menu_iid, index='end', text='Menu Item:',
                                       tags=[PluginMenuTree.ITEM_TAG, ])
                self.save_item_attr(item_iid, item)
                idx = self.index(item_iid)
                pass
        self.tag_bind(PluginMenuTree.MENU_TAG, '<<TreeviewSelect>>', self.select_menu_action)
        self.tag_bind(PluginMenuTree.ITEM_TAG, '<<TreeviewSelect>>', self.select_item_action)

    def prev_index(self, iid: str) -> int:
        return self.index(self.prev(iid))

    def next_index(self, iid: str) -> Union[int, str]:
        idx = self.index(self.next(iid))
        if idx == 0:
            return 'end'
        else:
            return idx

    def save_menu_attr(self, menu_iid: str, menu: model.PluginMenu) -> None:
        self.set(menu_iid, PluginMenuTree.MENU_STR, menu.__str__())
        self.set(menu_iid, PluginMenuTree.ITEM_STR, '')
        self.set(menu_iid, PluginMenuTree.REPR, menu.__repr__())

    def insert_menu(self, idx: Union[int, str]) -> tuple[str, model.PluginMenu]:
        menu_iid: str = self.insert(parent='', index=idx, text='Menu:', open=True, tags=[PluginMenuTree.MENU_TAG])
        new_menu: model.PluginMenu = model.PluginMenu(title='New Menu', module_name='', items=[])
        self.save_menu_attr(menu_iid, new_menu)
        self.insert_menu_item(menu_iid=menu_iid, idx='end')
        self.selection_set(menu_iid)
        return menu_iid, new_menu

    def save_item_attr(self, item_iid: str, item: model.PluginMenuItem) -> None:
        self.set(item_iid, PluginMenuTree.MENU_STR, '')
        self.set(item_iid, PluginMenuTree.ITEM_STR, item.__str__())
        self.set(item_iid, PluginMenuTree.REPR, item.__repr__())

    def insert_menu_item(self, menu_iid: str, idx: Union[int, str]) -> tuple[str, model.PluginMenuItem]:
        new_item: model.PluginMenuItem = model.PluginMenuItem(title='New Item', entry_point_name='',
                                                              select_person=False, select_date_range=False,
                                                              select_dp_type=False)
        item_iid: str = self.insert(parent=menu_iid, index=idx, text='Menu Item:', tags=[PluginMenuTree.ITEM_TAG, ])
        self.save_item_attr(item_iid, new_item)
        self.selection_set(item_iid)
        return item_iid, new_item


class PluginWidget(ttkb.Frame):
    def __init__(self, parent, plugin: Optional[model.Plugin], cancel_action: Callable, save_action: Callable,
                 save_as_action: Callable):
        ttkb.Frame.__init__(self, master=parent)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.plugin: Optional[model.Plugin] = plugin
        self.cancel_action: Callable = cancel_action
        self.save_action: Callable = save_action
        self.save_as_action: Callable = save_as_action
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
        self.save_btn = ttkb.Button(master=header_frame, text='Save Plugin', command=self.save_action)
        self.save_btn.grid(column=0, row=row, padx=5, pady=5, sticky=tk.EW)

        self.save_as_btn = ttkb.Button(master=header_frame, text='Save Plugin As ...', command=self.save_as_action)
        self.save_as_btn.grid(column=1, row=row, padx=5, pady=5, sticky=tk.W)

        row += 1
        ttkb.Label(header_frame,
                   text='Click on a menu or item to select it for edit or deletion, or to insert above or below it.'
                        'To insert a menu, first select a menu, then click Insert Above or Insert Below, and a menu '
                        'and a single menu item under it will be created.  To insert a menu item, select a menu item '
                        'under the menu you wish to add an item to, then click Insert Above or Insert Below.',
                   wraplength=800, justify=tk.LEFT, anchor=tk.W) \
            .grid(column=0, row=row, padx=5, columnspan=3, rowspan=3, sticky=tk.W)

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
        self.name_widget.focus_set()

    def disable_insert(self):
        self.insert_above_btn.configure(state=tk.DISABLED)
        self.insert_below_btn.configure(state=tk.DISABLED)

    def enable_insert(self):
        self.insert_above_btn.configure(state=tk.NORMAL)
        self.insert_below_btn.configure(state=tk.NORMAL)

    def replace_footer(self):
        if self.footer_frame is not None:
            self.footer_frame.forget()
        self.footer_frame = ttkb.Frame(self)
        self.footer_widget = ttkb.Frame(self.footer_frame)
        for row in range(0, 4):
            ttkb.Label(self.footer_widget, text=' ', width=150).grid(column=0, row=row, padx=5, pady=5)
        self.footer_widget.grid(column=0, row=0, sticky=tk.NSEW)
        self.footer_frame.grid(column=0, row=3, padx=15, pady=5, sticky=tk.NSEW)

    def cancel(self):
        self.replace_footer()
        self.enable_insert()

    def populate_plugin_widget(self):
        self.name_widget.set_value(self.plugin.name)
        self.desc_widget.set_value(self.plugin.description)
        self.author_name_widget.set_value(self.plugin.author_name)
        self.author_email_widget.set_value(self.plugin.author_email)

    def save_menu(self):
        self.current_menu = self.footer_widget.get_menu()
        self.menu_tree.save_menu_attr(self.current_menu_iid, self.current_menu)
        self.enable_insert()

    def select_menu(self, event):
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
        self.footer_frame.forget()
        self.footer_widget = PluginMenuWidget(self.footer_frame, cancel_action=self.cancel,
                                              save_action=self.save_menu, menu=menu,
                                              menu_iid=menu_iid)
        self.footer_widget.grid(column=0, row=0, sticky=tk.NSEW)
        self.footer_frame.grid(column=0, row=3, padx=15, pady=5, sticky=tk.NSEW)

    def save_menu_item(self):
        self.current_item: model.PluginMenuItem = self.footer_widget.get_menu_item()
        self.menu_tree.save_item_attr(self.current_item_iid, self.current_item)
        self.enable_insert()

    def select_menu_item(self, event):
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
        print('insert_above')
        if self.current_menu is not None:
            if self.current_item is not None:
                self.current_item_iid, self.current_item = self.insert_item_above()
                self.populate_menu_item_widget(module_name=self.current_menu.module_name,
                                               menu_iid=self.current_menu_iid, item_iid=self.current_item_iid,
                                               item=self.current_item)
            else:
                self.current_menu_iid, self.current_menu = self.insert_menu_above()
                self.populate_menu_widget(menu_iid=self.current_menu_iid, menu=self.current_menu)
        self.disable_insert()

    def insert_below(self) -> None:
        print('insert_below')
        if self.current_menu is not None:
            if self.current_item is not None:
                self.current_item_iid, self.current_item = self.insert_item_below()
                self.populate_menu_item_widget(module_name=self.current_menu.module_name,
                                               menu_iid=self.current_menu_iid, item_iid=self.current_item_iid,
                                               item=self.current_item)
            else:
                self.current_menu_iid, self.current_menu = self.insert_menu_below()
                self.populate_menu_widget(menu_iid=self.current_menu_iid, menu=self.current_menu)
        self.disable_insert()

    def delete(self) -> None:
        if self.current_menu is not None:
            if self.current_item is not None:
                self.delete_item()
            else:
                self.delete_menu()
        self.enable_insert()

    def insert_menu_above(self) -> tuple[str, model.PluginMenu]:
        idx = self.menu_tree.index(self.current_menu_iid)
        print(f'insert_menu_above iid {self.current_menu_iid} idx {idx}')
        return self.menu_tree.insert_menu(idx)

    def insert_menu_below(self) -> tuple[str, model.PluginMenu]:
        idx = self.menu_tree.next_index(self.current_menu_iid)
        print(f'insert_menu_below iid {self.current_menu_iid} idx {idx}')
        return self.menu_tree.insert_menu(idx)

    def delete_menu(self):
        self.menu_tree.delete(self.footer_widget.menu_iid)
        self.current_menu = None
        self.current_menu_iid = None

    def insert_item_above(self) -> tuple[str, model.PluginMenuItem]:
        idx = self.menu_tree.index(self.current_item_iid)
        print(f'insert_item_above iid {self.current_item_iid} idx {idx}')
        return self.menu_tree.insert_menu_item(self.current_menu_iid, idx)

    def insert_item_below(self) -> tuple[str, model.PluginMenuItem]:
        idx = self.menu_tree.next_index(self.current_item_iid)
        print(f'insert_item_above iid {self.current_item_iid} idx {idx}')
        return self.menu_tree.insert_menu_item(self.current_menu_iid, idx)

    def delete_item(self):
        self.menu_tree.delete(self.footer_widget.item_iid)
        self.current_item = None
        self.current_item_iid = None

