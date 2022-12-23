import pytest

import plugin_manager.model.plugin as plugin


@pytest.fixture
def plugin_menus_fixture() -> list[plugin.PluginMenu]:
    """
    Provides a list of 2 PluginMenu objects, each having 2 PluginMenuItem instances.  One of these menu items
    have an entry point name that will not be found, in order to test the failure modes of the Plugin module import
    process.

    :return: a list containing 2 PluginMenu objects
    :rtype: list[plugin_config.PluginMenu]:

    """
    plugin_menus: list[plugin.PluginMenu] = []
    item1: plugin.PluginMenuItem = plugin.PluginMenuItem(title='TPS Report: 1',
                                                         entry_point_name='action1',
                                                         select_person=True,
                                                         select_date_range=True,
                                                         select_dp_type=True)
    item2: plugin.PluginMenuItem = plugin.PluginMenuItem(title='Prophet and Loss: 2',
                                                         entry_point_name='action2',
                                                         select_person=True,
                                                         select_date_range=False,
                                                         select_dp_type=False)
    plugin_menus.append(plugin.PluginMenu(title='Menu One',
                                          module_name='tests.config.test_plugin_menus',
                                          items=[item1, item2]))

    item3: plugin.PluginMenuItem = plugin.PluginMenuItem(title='Bean Counter: not found',
                                                         entry_point_name='you_wont_find_me',
                                                         select_person=False,
                                                         select_date_range=False,
                                                         select_dp_type=False)
    item4: plugin.PluginMenuItem = plugin.PluginMenuItem(title='Mission Statement: 3',
                                                         entry_point_name='action3',
                                                         select_person=False,
                                                         select_date_range=True,
                                                         select_dp_type=False)
    plugin_menus.append(plugin.PluginMenu(title='Menu Two', module_name='tests.config.test_plugin_menus',
                                          items=[item3, item4]))

    return plugin_menus


@pytest.fixture
def plugin_fixture(plugin_menus_fixture) -> list[plugin.Plugin]:
    """
    Provides a list of 2 Plugin objects, each containing one of the PluginMenu objects provided by the plugin_menu_fixture

    :param plugin_menus_fixture: a list of 2 PluginMenu objects
    :return: a list of 2 Plugin objects
    :rtype: list[plugin_config.Plugin]

    """
    return [plugin.Plugin(name='Test Plugin 1',
                          description='Another piece of test code',
                          author_name='Stroud Custer',
                          author_email='stroudsjunk1@gmail.com',
                          menus=[plugin_menus_fixture[0]]),
            plugin.Plugin(name='Test Plugin 2',
                          description='Another piece of test code',
                          author_name='Steven Custer',
                          author_email='stevesjunk1@gmail.com',
                          menus=[plugin_menus_fixture[1]])]

