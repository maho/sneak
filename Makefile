BASE_VERSION=0.25
RELEASE=$(shell cat .release)
VERSION=$(BASE_VERSION).$(RELEASE)


atlas: assets/objects.atlas

assets/objects.atlas: $(wildcard img/*.png)
	python -m kivy.atlas assets/objects 512x512 $(wildcard img/*.png)

.release: $(wildcard assets/fonts/* assets/glsl/ *.py snd/* *.kv) assets/objects.atlas buildozer.spec Makefile
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
export URL_kivent_core=https://github.com/mahomahomaho/kivent/archive/mymaster3.zip

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
PYINSTDIR=$(DISTDIR)/pyinstaller
PYINSTBIN=$(PYINSTDIR)/opt/sneak/sneak.bin
TARGZPATH=$(DISTDIR)/sneak-$(VERSION)-amd64.tar.gz
DEBPATH=$(DISTDIR)/sneak_$(VERSION)-1_amd64.deb
INTERMEDIARYTARBZ=$(PYINSTDIR)/sneak-$(VERSION).tar.gz

x:
	echo $(PYINSTDIR)

targz:
	mkdir -p $(DISTDIR)
	make $(TARGZPATH)

$(TARGZPATH): $(PYINSTBIN)
	cd $(PYINSTDIR)/opt && fakeroot tar zcf $(TARGZPATH) sneak

$(PYINSTBIN):
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

$(INTERMEDIARYTARBZ): $(PYINSTBIN) $(PYINSTDIR)/usr/share/applications/sneak.desktop
	cd $(PYINSTDIR) && fakeroot tar zcf $(INTERMEDIARYTARBZ) opt usr

$(DEBPATH): $(INTERMEDIARYTARBZ)
	cd $(PYINSTDIR) && fakeroot alien -k --to-deb --target=amd64 $(INTERMEDIARYTARBZ)
	mv -v $(PYINSTDIR)/*.deb $(DISTDIR)/
	echo "$(SUFFIX)" > $(DEBPATH).suffix

deb:
	make $(DEBPATH)

EXEPATH=$(DISTDIR)/sneak-$(VERSION).exe
EXEZIPPATH=$(DISTDIR)/sneak-$(VERSION).zip

$(EXEPATH):
	make atlas .release
	windist/vw/bin/wine pyinstaller -y --distpath="$(PYINSTDIR)" sneak-win.spec 2>.pyinstaller-win.log
	mv $(PYINSTDIR)/sneak-win.exe $(EXEPATH)

$(EXEZIPPATH): $(EXEPATH)
	zip $(EXEZIPPATH) $(EXEPATH)

exezip:
	make $(EXEZIPPATH)

