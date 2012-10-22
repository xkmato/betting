import distutils.core
import py2exe

distutils.core.setup(
    name='bettin',
    version='1',
    packages=[''],
    url='www.countrysportsbet.com',
    license='',
    author='kenneth',
    author_email='kbonky@gmail.com',
    description='Country Sport Bet by AwesomeNux',

    windows = [
            {
            'script': 'bet_interface.py',
            'icon_resources': [(1, "icon.ico")],
            }
    ],

    options = {
        'py2exe': {
#            'packages':'bettin',
            'dist_dir':'dist',
            'includes': 'cairo, pango, pangocairo, atk, gobject, gio',
            }
    },

    data_files=[
        'interface.glade',
        'bet.sqlite3',
        'Microsoft.VC90.CRT.manifest',
        'msvcm90.dll',
        'msvcp90.dll',
        'msvcr90.dll',
        ]
)
