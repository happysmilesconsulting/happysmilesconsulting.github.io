SOURCES:=$(wildcard web_src/*.html)

all: $(SOURCES)
	for i in $(SOURCES); do \
		./build_html.py $$i; \
	done

.PHONY: all
