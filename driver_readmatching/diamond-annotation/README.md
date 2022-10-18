## Diamond Annotation Pipeline
## Before running the pipeline, please change the 'dbpath' in /tools/diamondClass.py to your local directory path
## Also change the sys.path.insert in diamond_pipeline.py to your local directory path
This pipeline has been designed to run the blastx diamond pipeline 

        usage: diamond_pipeline.py [-h] --forward_pe_file FORWARD_PE_FILE
                           --reverse_pe_file REVERSE_PE_FILE --output_file
                           OUTPUT_FILE [--diamond_identity DIAMOND_IDENTITY]
                           [--diamond_mlen DIAMOND_MLEN]
                           [--diamond_evalue DIAMOND_EVALUE]
                           [--gene_coverage GENE_COVERAGE]
                           [--bowtie_16s_identity BOWTIE_16S_IDENTITY]
                           [--path_to_executables PATH_TO_EXECUTABLES]
                           [--database DATABASE]

		optional arguments:
		  -h, --help            show this help message and exit
		  --forward_pe_file FORWARD_PE_FILE
								forward mate from paired end library
		  --reverse_pe_file REVERSE_PE_FILE
								reverse mate from paired end library
		  --output_file OUTPUT_FILE
								save results to this file prefix
		  --diamond_identity DIAMOND_IDENTITY
								minimum identity for alignments [default 80]
		  --diamond_mlen DIAMOND_MLEN
								diamond minimum length for considering a hit [default
								25aa]
		  --diamond_evalue DIAMOND_EVALUE
								minimum e-value for alignments [default 1e-10]
		  --gene_coverage GENE_COVERAGE
								minimum coverage required for considering a full gene
								in percentage. This parameter looks at the full gene
								and all hits that align to the gene. If the overlap of
								all hits is below the threshold the gene is discarded.
								Use with caution [default 1]
		  --bowtie_16s_identity BOWTIE_16S_IDENTITY
								minimum identity a read as a 16s rRNA gene [default
								0.8]
		  --path_to_executables PATH_TO_EXECUTABLES
								path to ./bin/ under diamond-annotation
		  --database DATABASE   Choose database: 'deeparg' (for DeepARG) or 'card'(for
								CARD3.0.7) [default deeparg]