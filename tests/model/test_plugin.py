import plugin_manager.model.plugin as plugin
from tests.test_tools import compare_object, attr_error
from tests.plugin_fixtures import plugin_fixture, plugin_menus_fixture


def menu_error_preamble(title: str) -> str:
    return f'Menu {title}:'


def plugin_error_preamble(name: str) -> str:
    return f'Plugin {name}:'


def compare_menu(menu: plugin.PluginMenu, check_menu: plugin.PluginMenu):
    if not compare_object(menu, check_menu):
        assert menu.title == check_menu.title, \
            f'{menu_error_preamble(menu.title)} {attr_error("Title", menu.title, check_menu.title)}'
        assert menu.module_name == check_menu.module_name, \
            f'{menu_error_preamble(menu.title)} {attr_error("Package", menu.module_name, check_menu.module_name)}'
    for item, check_item in zip(menu.items, check_menu.items):
        if not compare_object(item, check_item):
            assert item.title == check_item.title, \
                f'{menu_error_preamble(menu.title)} Item: {item.title} {attr_error("Title", item.title, check_item.title)}'

            assert item.entry_point_name == check_item.entry_point_name, \
                f'{menu_error_preamble(menu.title)} Item: {item.title} ' \
                f'{attr_error("Entry Point", item.entry_point_name, check_item.entry_point_name)}'
            assert item.select_person == check_item.select_person, \
                f'{menu_error_preamble(menu.title)} Item: {item.title} ' \
                f'{attr_error("Select Person", item.select_person, check_item.select_person)}'
            assert item.select_date_range == check_item.select_date_range, \
                f'{menu_error_preamble(menu.title)} Item: {item.title} ' \
                f'{attr_error("Select Date Range", item.select_date_range, check_item.select_date_range)}'
            assert item.select_dp_type == check_item.select_dp_type, \
                f'{menu_error_preamble(menu.title)} Item: {item.title} ' \
                f'{attr_error("Select DataPoint Type", item.select_dp_type, check_item.select_dp_type)}'


def compare_plugin(plugin: plugin.Plugin, check_plugin: plugin.Plugin):
    if not compare_object(plugin, check_plugin):
        assert plugin.name == check_plugin.name, \
            f'{plugin_error_preamble(plugin.name)} {attr_error("Name", plugin.name, check_plugin.name)}'
        assert plugin.description == check_plugin.description, \
            f'{plugin_error_preamble(plugin.description)} {attr_error("Name", plugin.description, check_plugin.description)}'
        assert plugin.author_name == check_plugin.author_name, \
            f'{plugin_error_preamble(plugin.author_name)} {attr_error("Name", plugin.author_name, check_plugin.author_name)}'
        assert plugin.author_email == check_plugin.author_email, \
            f'{plugin_error_preamble(plugin.author_email)} {attr_error("Name", plugin.author_email, check_plugin.author_email)}'
        for menu, check_menu in zip(plugin.menus, check_plugin.menus):
            compare_menu(menu, check_menu)

