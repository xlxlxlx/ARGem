import argparse
from pipeline import pairedEndPipelineClass
import sys
import os
import time
import base64
import json
sys.path.insert(0, '/agroseek/www/wp-content/themes/twentyseventeen/scripts/diamond_pipeline/diamond-annotation/')


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--forward_pe_file", type=str, required=True,
                        help="forward mate from paired end library",)
    parser.add_argument("--reverse_pe_file", type=str, required=True,
                        help="reverse mate from paired end library",)
    parser.add_argument("--output_file", type=str, required=True,
                        help="save results to this file prefix",)

    parser.add_argument("--diamond_identity", type=float, default=80,
                        help="minimum identity for alignments [default 80]",)
    parser.add_argument("--diamond_mlen", type=float, default=25,
                        help="diamond minimum length for considering a hit [default 25aa]",)
    parser.add_argument("--diamond_evalue", type=float, default=1e-10,
                        help="minimum e-value for alignments [default 1e-10]",)
    parser.add_argument("--gene_coverage", type=float, default=1,
                        help="minimum coverage required for considering a full gene in percentage. This parameter looks at the full gene and all hits that align to the gene. If the overlap of all hits is below the threshold the gene is discarded. Use with caution [default 1]",)
    parser.add_argument("--bowtie_16s_identity", type=float, default=0.8,
                        help="minimum identity a read as a 16s rRNA gene [default 0.8]",)

    parser.add_argument("--path_to_executables", type=str, default="bin/",
                        help="path to ./bin/ under short_reads_pipeline",)
    parser.add_argument("--database", type=str, default="deeparg",
                        help="Choose database: 'deeparg' (for DeepARGdb) or 'card'(for CARD3.0.7) [default deeparg]",)

    return parser


if __name__ == "__main__":
    align_par = get_parser().parse_args()

    diamond_parameters = dict(
        identity=align_par.diamond_identity,
        mlen=align_par.diamond_mlen,
        evalue=align_par.diamond_evalue,
        database=align_par.database
    )

    parameters = dict(
        coverage=align_par.gene_coverage,
        identity_16s_alignment=align_par.bowtie_16s_identity
    )

    data = dict(
        pairedR1File=align_par.forward_pe_file,
        pairedR2File=align_par.reverse_pe_file,
        programs=align_par.path_to_executables,
        diamond_parameters=diamond_parameters,
        sample_output_file=align_par.output_file,
        parameters=parameters
    )

    pipe = pairedEndPipelineClass.PairedEnd(data)
    pipe.run()
