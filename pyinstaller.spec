# -*- mode: python -*-

from PyInstaller.compat import modname_tkinter

block_cipher = None

DISTPATH="opt"

a = Analysis(['main.py'],
             pathex=['/home/maho/workspace/sneak'],
             binaries=None,
             datas=[('sneak.kv', '.'),
                    ('assets/objects*.png', 'assets'),
                    ('assets/objects.atlas', 'assets'),
                    ('assets/glsl', 'assets/glsl'),
                    ('assets/levels', 'assets/levels'),
                    ('assets/ttf', 'assets/ttf'),
                    ('snd/*.ogg', 'snd'),
             hiddenimports=[
                            'importlib', 
                            'redminelib', 'redminelib.resources', 
                            'cymunk.cymunk',
                            'kivent_core.managers.animation_manager',
                            'kivent_core.rendering.animation',
                            'kivent_core.rendering.gl_debug',
                            'kivent_core.rendering.svg_loader',
                            'kivent_core.memory_handlers.zonedblock',
                            'kivent_core.uix.cwidget'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[modname_tkinter, 'docutils'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='sneak.bin',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='khamster')

# vim: set syntax=python:

