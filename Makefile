atlas: assets/objects.atlas

assets/objects.atlas: $(wildcard img/*.png)
	python -m kivy.atlas assets/objects 512x512 $(wildcard img/*.png)

build:
	buildozer --verbose android debug 

