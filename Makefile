BASE_VERSION=0.23
VERSION=$(BASE_VERSION).$(shell cat .release)


atlas: assets/objects.atlas

assets/objects.atlas: $(wildcard img/*.png)
	python -m kivy.atlas assets/objects 512x512 $(wildcard img/*.png)

.release: $(wildcard assets/fonts/* assets/glsl/ *.py snd/* *.kv) assets/objects.atlas
	echo $$(($$(cat .release) + 1)) > .release

debug: .release
	sudo -EH -u bdozer utils/buildozer.sh --verbose android debug deploy run logcat

debugrun:
	sudo -EH -u bdozer utils/buildozer.sh --verbose android deploy run logcat

export P4A_RELEASE_KEYSTORE=/home/maho/.buildozer/sneak-upload-keystore.jks
export P4A_RELEASE_KEYALIAS=myalias4
export P4A_RELEASE_KEYSTORE_PASSWD=$(shell cat .keypass)
export P4A_RELEASE_KEYALIAS_PASSWD=$(shell cat .keypass)

export APP_VERSION=$(VERSION)
export URL_kivy=https://github.com/mahomahomaho/kivy/archive/master2.zip

RELAPKNAME=sneakk-$(VERSION)-release.apk
RELAPKPATH=bin/$(RELAPKNAME)

release: $(RELAPKPATH)

$(RELAPKPATH): .release atlas
	sudo -EH -u bdozer utils/buildozer.sh --verbose android release
	# cp -v .buildozer/android/platform/build/dists/sneakk/bin/$(RELAPKNAME) bin/

upload: $(RELAPKPATH)
	python utils/basic_upload_apks.py maho.sneakk $(RELAPKPATH)



## linux dist
DISTDIR=$(CURDIR)/dist/$(VERSION)
PYINSTDIR=$(DISTDIR)/pyinstaller$(SUFFIX)
TARGZPATH=$(DISTDIR)/khamster$(SUFFIX)-$(VERSION)-amd64.tar.gz

targz:
	make $(TARGZPATH)

$(TARGZPATH): $(PYINSTDIR)/opt
	cd $(PYINSTDIR)/opt && fakeroot tar zcf $(TARGZPATH) sneak

$(PYINSTDIR)/opt $(PYINSTDIR)/usr: 
	make atlas .release
	rm -rf $(PYINSTDIR)/opt
	pyinstaller -y --distpath="$(PYINSTDIR)/opt" pyinstaller.spec 2>.pyinstaller.log
	echo '#!/bin/sh\ncd $$(dirname $$0) && KIVY_AUDIO=sdl2 ./sneak.bin\n' > $(PYINSTDIR)/opt/sneak/sneak
	chmod a+x $(PYINSTDIR)/opt/sneak/sneak
	rm -rf $(PYINSTDIR)/usr
	cd $(PYINSTDIR) && mkdir -p usr/local/bin && echo '#!/bin/sh\n/opt/sneak/sneak "$$@"' > usr/local/bin/sneak && chmod a+x usr/local/bin/sneak
	cp -v package/sneak.png $(PYINSTDIR)/opt/sneak/
	mkdir -p $(PYINSTDIR)/usr/share/applications
	cp -v package/sneak.desktop $(PYINSTDIR)/usr/share/applications


