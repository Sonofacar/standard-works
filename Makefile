bom: bom.sh kjv.awk bom.tsv
	cat bom.sh > $@

	echo 'exit 0' >> $@

	echo '#EOF' >> $@
	tar cz kjv.awk bom.tsv >> $@

	chmod +x $@

test: bom.sh
	shellcheck -s sh bom.sh

.PHONY: test
