pogp: kjv.sh kjv.awk pogp.tsv
	cat kjv.sh > $@

	echo 'exit 0' >> $@

	echo '#EOF' >> $@
	tar cz kjv.awk pogp.tsv >> $@

	chmod +x $@

test: kjv.sh
	shellcheck -s sh kjv.sh

clean:
	rm -f pogp

install: pogp
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp -f pogp $(DESTDIR)$(PREFIX)/bin
	chmod 755 $(DESTDIR)$(PREFIX)/bin/pogp

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/pogp

.PHONY: test clean install uninstall
