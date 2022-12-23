import decimal
import json
import pathlib
import pytest

import plugin_manager.model.json_handler as jh
import plugin_manager.model.plugin as plugin_model

from tests.plugin_fixtures import plugin_fixture, plugin_menus_fixture
from tests.test_tools import compare_object, attr_error
from tests.model.test_plugin import compare_plugin, compare_menu


@pytest.mark.Plugins
def test_plugin_json(tmpdir, plugin_menus_fixture, plugin_fixture):
    for menu in plugin_menus_fixture:
        json_str = json.dumps(menu, cls=jh.PluginJSONEncoder)
        assert json_str is not None and len(json_str) > 0, f'No JSON Output for Menu {menu.title}'
        check_menu = json.loads(eval(json_str), object_hook=jh.plugin_object_hook)
        assert check_menu is not None, "JSON PluginMenu de-serialization failed"
        compare_menu(menu, check_menu)

    for plugin in plugin_fixture:
        json_str = json.dumps(plugin, cls=jh.PluginJSONEncoder)
        assert json_str is not None and len(json_str) > 0, f'No JSON Output for Plugin {plugin.name}'
        check_plugin = json.loads(eval(json_str), object_hook=jh.plugin_object_hook)
        assert check_plugin is not None, "JSON Plugin de-serialization failed"
        compare_plugin(plugin, check_plugin)


@pytest.mark.Plugins
def test_save_and_retrieve_plugin(tmpdir, plugin_fixture):
    plugin_path = pathlib.Path(tmpdir, 'plugins')
    plugin_path.mkdir(exist_ok=True)
    jh.save_plugins(plugin_fixture, plugin_path)
    check_plugins: list[plugin_model.Plugin] = jh.retrieve_plugins(plugin_path)
    assert len(check_plugins) == len(plugin_fixture), f'Wrote {len(plugin_fixture)} files, Read {len(check_plugins)} files'
    for plugin, check_plugin in zip(plugin_fixture, check_plugins):
        compare_plugin(plugin, check_plugin)

