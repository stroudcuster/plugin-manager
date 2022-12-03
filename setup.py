from setuptools import setup

with open('plugin_manager/version.py') as f:
    exec(f.read())

setup(
    name='json_plugin_mgr',
    version=__version__,
    packages=['dummy_package', 'plugin_manager', 'plugin_manager.gui', 'plugin_manager.model'],
    url='https://github.com/stroudcuster/plugin_manager',
    license='MIT',
    author='Stroud Custer',
    author_email='custerstroud@gmail.com',
    description='This app creates and maintains JSON format menu spec files to integrate plugin functionality with a primary app'
)
