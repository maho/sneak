# -*- mode: python -*-
from kivy.deps import sdl2, glew

block_cipher = None

a = Analysis(['main.py'],
             pathex=['Z:\\home\\maho\\workspace\\sneak'],
             binaries=[],
             datas=[('sneak.kv', '.'),
                    ('assets/objects*.png', 'assets'),
                    ('assets/objects.atlas', 'assets'),
                    ('assets/glsl', 'assets/glsl'),
                    ('assets/fonts', 'assets/fonts'),
                    ('snd/*.ogg', 'snd')],
             hiddenimports=[
                            'importlib', 
                            'cymunk.cymunk',
                            'kivent_core.managers.animation_manager',
                            'kivent_core.rendering.animation',
                            'kivent_core.rendering.gl_debug',
                            'kivent_core.rendering.svg_loader',
                            'kivent_core.memory_handlers.zonedblock',
                            'kivent_core.uix.cwidget'],

             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='sneak-win',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='img\\gplay\\sneak.ico')
