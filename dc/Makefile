dc: kjv.sh kjv.awk dc.tsv
	cat kjv.sh > $@

	echo 'exit 0' >> $@

	echo '#EOF' >> $@
	tar cz kjv.awk dc.tsv >> $@

	chmod +x $@

test: kjv.sh
	shellcheck -s sh kjv.sh

.PHONY: test
