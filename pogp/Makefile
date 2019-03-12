pogp: kjv.sh kjv.awk pogp.tsv
	cat kjv.sh > $@

	echo 'exit 0' >> $@

	echo '#EOF' >> $@
	tar cz kjv.awk pogp.tsv >> $@

	chmod +x $@

test: kjv.sh
	shellcheck -s sh kjv.sh

.PHONY: test
