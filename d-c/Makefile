d-c: kjv.sh kjv.awk dc.tsv
	cat kjv.sh > $@

	echo 'exit 0' >> $@

	echo '#EOF' >> $@
	tar cz kjv.awk dc.tsv >> $@

	chmod +x $@

test: kjv.sh
	shellcheck -s sh kjv.sh

clean:
	rm -f d-c

install: dc
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp -f d-c $(DESTDIR)$(PREFIX)/bin
	chmod 775 $(DESTDIR)$(PREFIX)/bin/d-c

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/d-c

.PHONY: test clean install uninstall
