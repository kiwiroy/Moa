glimmer3
------------------------------------------------

**Glimmer3**

::
    Predicts (prokaryotic) using glimmer3.


Commands
~~~~~~~~

**clean**
  Remove all job data, not the Moa job itself, note that this must be implemented by the template.


**run**
  Glimmer3 is a open reading frame discovery program from the EMBOSS [[emboss]] package. It takes a set of input sequences and predicts all open reading frames. Additionally, this template converts the default output (predicted protein sequences) to GFF3.





Parameters
~~~~~~~~~~



**gene_len**::
    Minimum gene length (glimmer3 -g/--gene_len)

  | *type*: `integer`
  | *default*: `110`
  | *optional*: `True`



**gff_source**::
    source field to use in the gff. Defaults to "glimmer3"

  | *type*: `string`
  | *default*: `glimmer3`
  | *optional*: `True`



**input_dir**::
    Input directory with the sequences to run glimmer3 on

  | *type*: `directory`
  | *default*: ``
  | *optional*: `True`



**input_extension**::
    input file extension. Defaults to fasta

  | *type*: `string`
  | *default*: `fasta`
  | *optional*: `True`



**max_overlap**::
    Maximum overlap, see the glimmer documentation for the -o or --max_olap parameter

  | *type*: `integer`
  | *default*: `50`
  | *optional*: `True`



**title**::
    A name for this job

  | *type*: `string`
  | *default*: ``
  | *optional*: `False`



**treshold**::
    treshold for calling a gene a gene (glimmer3 -t)

  | *type*: `integer`
  | *default*: `30`
  | *optional*: `True`



Other
~~~~~

**Backend**
  gnumake
**Author**
  Mark Fiers
**Creation date**
  Wed Nov 10 07:56:48 2010
**Modification date**
  Wed Nov 10 07:56:48 2010


