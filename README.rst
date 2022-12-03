This application allows you to create and maintain JSON menu specification files that can be used add functionality to
an existing open source Python application through a plug in.  This would require a small modification to the existing
application to use the functionality provided by this API to create menu selections that will invoke entry points in
the plugin application.

The JSON files encode the properties of the plugin_manager.model.plugin.Plugin class, which contains  a list of
PluginMenu instances, each of which contains a list of PluginMenuItem instances:

+ Plugin:

    - Plugin Name

    - Description

    - Author Name

    - Author Email

    - Plugin Menu List:
                + Plugin Menu:
                    - Title

                    - Module Name

                    - Plugin Menu Item List:
                        + Plugin Menu Item:
                            - Title

                            - Entry Point Name

                            - Bools to select pre-invocation actions, such date range selection

The primary application incorporates the plugin menu(s) into it's menu hierarchy by invoking the
create_menu method of a PluginMenu object, passing the following callback functions to
this method:
    + an optional pre-invocation selection prompt function
    + a function that will add a menu item to the application's menu hierarchy, given a label text and a lambda to be invoked
    + a function that will add a menu to the application's menu hierarchy, give a label text

For the ttkbwidgets library source see https://github.com/stroudcuster/ttkbwidgets

To install from PyPI:  pip install json-plugin-mgr

