PREFIX = /usr/local

std-works: std-works.sh std-works.awk TSVs/quad.tsv
	cat std-works.sh > $@

	echo 'exit 0' >> $@

	echo '#EOF' >> $@
	tar cz std-works.awk TSVs/quad.tsv >> $@

	chmod +x $@

test: std-works.sh
	shellcheck -s sh std-works.sh

clean:
	rm -f std-works

install: std-works
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp -f std-works $(DESTDIR)$(PREFIX)/bin
	chmod 775 $(DESTDIR)$(PREFIX)/bin/std-works

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/std-works

.PHONY: test clean install uninstall
