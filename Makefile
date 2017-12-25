BASE_VERSION=0.17
VERSION=$(BASE_VERSION).$(shell cat .release)


atlas: assets/objects.atlas

assets/objects.atlas: $(wildcard img/*.png)
	python -m kivy.atlas assets/objects 512x512 $(wildcard img/*.png)

uprel:
	echo $$(($$(cat .release) + 1)) > .release

build: uprel
	buildozer --verbose android debug 

export P4A_RELEASE_KEYSTORE=/home/maho/.buildozer/sneak-upload-keystore.jks
export P4A_RELEASE_KEYALIAS=myalias4
export P4A_RELEASE_KEYSTORE_PASSWD=$(shell cat .keypass)
export P4A_RELEASE_KEYALIAS_PASSWD=$(shell cat .keypass)

export APP_VERSION=$(VERSION)

RELAPKNAME=Sneakk-$(VERSION)-release.apk
RELAPKPATH=bin/$(RELAPKNAME)

release: $(RELAPKPATH)

$(RELAPKPATH): uprel atlas
	sudo -EH -u bdozer utils/buildozer.sh --verbose android release
	cp -v .buildozer/android/platform/build/dists/sneakk/bin/$(RELAPKNAME) bin/

upload: $(RELAPKPATH)
	python utils/basic_upload_apks.py maho.sneakk $(RELAPKPATH)



