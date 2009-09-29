# 
# Copyright 2009 Mark Fiers, Plant & Food Research
# 
# This file is part of Moa - http://github.com/mfiers/Moa
# 
# Moa is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# Moa is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Moa.  If not, see <http://www.gnu.org/licenses/>.
# 

moa_title = Glimmer3

moa_description = Predicts (prokaryotic) using glimmer3.

moa_ids += glimmer3

glimmer3_help = Glimmer3 is a open reading frame discovery program		\
  from the EMBOSS [[emboss]] package. It takes a set of input			\
  sequences and predicts all open reading frames. Additionally, this	\
  template converts the default output (predicted protein sequences)	\
  to GFF3.


#########################################################################
# Prerequisite testing

prereqlist += prereq_glimmer3_installed

prereq_glimmer3_installed:
	@if ! which glimmer3 >/dev/null; then \
		echo "glimmer3 is either not installed or not in your \$$PATH" ;\
		false ;\
	fi


moa_must_define += glimmer3_input_dir
blast_input_dir_help = directory containing the input sequences

moa_may_define +=  glimmer3_gff_source
glimmer3_gff_source_help = source field to use in the gff. Defaults to "glimmer3"

moa_may_define += glimmer3_input_extension glimmer3_max_overlap \
	glimmer3_gene_len glimmer3_treshold

glimmer3_input_extension_help = input file extension. Defaults to 'fasta'
glimmer3_max_overlap_help = Maximum overlap, see the glimmer	\
  documentation for the -o or --max_olap parameter
glimmer3_gene_len_help = Minimum gene length (glimmer3 -g/--gene_len)
glimmer3_treshold_help = treshold for calling a gene a gene (glimmer3 -t)
moa_may_define += 

#preparing for possible gbrowse upload:
gup_gff_dir = ./gff
gup_upload_gff = T
gup_gffsource ?= $(blast_gff_source)

#include moabase, if it isn't already done yet..
include $(shell echo $$MOABASE)/template/moaBase.mk

glimmer3_max_overlap ?= 50
glimmer3_gene_len ?= 110
glimmer3_treshold ?= 30
glimmer3_gff_source ?= glimmer3
glimmer3_input_extension ?= fasta

glimmer3_input_files ?= $(wildcard $(glimmer3_input_dir)/*.$(glimmer3_input_extension))

glimmer3_output_files = $(addprefix out/, $(notdir $(patsubst		\
    %.$(glimmer3_input_extension), %.predict, $(glimmer3_input_files))))

glimmer3_cds_files = $(addprefix out/, $(notdir $(patsubst		\
    %.$(glimmer3_input_extension), %.cds.fasta, $(glimmer3_input_files))))

glimmer3_gff_files = $(addprefix gff/, $(notdir $(patsubst		\
    %.$(glimmer3_input_extension), %.gff, $(glimmer3_input_files))))

#glimmer3_gff_files = $(addprefix gff/, \
#	$(patsubst %.orf, %.gff, $(notdir $(glimmer3_output_files))))

glimmer3_test:
	@echo "Input extension: '$(glimmer3_input_extension)'"
	@echo "a blastdb file: '$(single_glimmer3_db_file)'"
	@echo "No inp files $(words $(glimmer3_input_files))"
	@echo "No orf files $(words $(glimmer3_output_files))"
	@echo "No gff files $(words $(glimmer3_gff_files))"

#prepare for glimmer3 - i.e. create directories
.PHONY: glimmer3_prepare
glimmer3_prepare:	
	-mkdir out 
	-mkdir gff	
	-mkdir train
	-mkdir fasta

.PHONY: glimmer3_post
glimmer3_post:

glimmer3_clean:
	-rm -rf ./gff/
	-rm -rf ./train/
	-rm -rf ./out/
	-rm -rf ./fasta/



.PHONY: glimmer3
glimmer3: $(glimmer3_gff_files) $(glimmer3_cds_files)

$(glimmer3_gff_files): gff/%.gff: out/%.predict
	cat $<											\
		| grep -v "^>"								\
		| sed "s/orf\([0-9]*\)/$*.g3.g\1/" 			\
		| awk ' {																	\
					printf "$*\t$(glimmer3_gff_source)\tCDS\t";									\
					if ($$4 > 0) { 													\
						printf "%s\t%s\t%s\t+\t%s", $$2, $$3, $$5, $$4; } 			\
					else { 															\
						printf "%s\t%s\t%s\t-\t%s", $$3, $$2, $$5, $$4; } 			\
					printf "\tID=%s;Name=%s\n", $$1, $$1;								\
				} ' 																\
		> $@

$(glimmer3_cds_files): out/%.cds.fasta: $(glimmer3_input_dir)/%.$(glimmer3_input_extension) out/%.predict
	cat $(realpath $(word 2,$^)) 					\
		| grep -v "^>"								\
		| extract -t $(realpath $<) -				\
		| sed "s/orf\([0-9]*\)/$*.g3.g\1/" 			\
		> $@
	fastaSplitter -f $@ -o fasta

$(glimmer3_output_files): out/%.predict: 											\
		$(glimmer3_input_dir)/%.$(glimmer3_input_extension) 						\
		 train/upstream.motif train/train1.icm
	startuse=`start-codon-distrib -3 train/all.seq train/run1.coords`;				\
	cd out; \
		glimmer3 																	\
			-o$(glimmer3_max_overlap) 												\
			-g$(glimmer3_gene_len)													\
			-t$(glimmer3_treshold)													\
			-b ../train/upstream.motif												\
			-P $$startuse															\
			$(realpath $<) 															\
			../train/train1.icm $*


#run the final prediction

#run elph to create analyze motifs
train/upstream.motif: train/upstream.train.set
	elph $< LEN=6 | get-motif-counts.awk > $@

#create an upstream set
train/upstream.train.set: train/run1.coords train/all.seq
	upstream-coords.awk 25 0 $< | extract train/all.seq - > $@

#get the coordinates of the precited seqs
train/run1.coords: train/run1.predict
	cat $< | grep -v "^>" > $@

#do the first glimmer run, based on the simple training set
train/run1.predict: train/train1.icm
	cd train; glimmer3 													\
		-o$(glimmer3_max_overlap) -g$(glimmer3_gene_len)				\
		-t$(glimmer3_treshold) 											\
		all.seq train1.icm run1

#build the first level model
train/train1.icm: train/train1.set
	build-icm -r $@ < $<

#create a training set
train/train1.set: train/all.seq train/long.orfs 
	extract -t $^ > $@

#assume a linear genome - circular would not make sense with
#possibly multiple genomes concatenated 
train/long.orfs: train/all.seq
	long-orfs -l -n -t 1.15 $< $@

#concatenate all seqs into one - this is only for training!!
train/all.seq: $(glimmer3_input_files)
	echo ">train" > $@
	for x in $^; do 												\
		cat $$x | grep -v "^>"  >> $@;								\
	done