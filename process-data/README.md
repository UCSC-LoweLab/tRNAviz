# tRNAviz-data

Data processing pipeline for tRNAviz

## Pipeline overview

0. Prerequisites
	- Python 3: pandas, Biopython
	- R: plyr, dplyr, tidyr, ggplot2, Biostrings, RColorBrewer
	- A list of taxids. If you need to, run `parse-genomeinfodb.py` to get this list.

1. Run tRNAscan-SE on all genomes.
	- We need `.out`, `.iso`, and `.ss` files, and to run with detailed output. 

2. Find taxonomy information for list of species along with relevant filepaths
	- Prerequisites: List of NCBI Taxonomy IDs. Also helpful for this list to contain paths to tRNAscan-SE output. (`taxids.tsv`)
	- Scripts:
		- `get-taxonomy.R` (`taxids.tsv` -> `genomes.tsv`)
			- Output list of species, plus taxonomic info from NCBI. 
		- `generate_newick_tree.py` (`genomes.tsv` -> `newick-tree.txt`)
			- Output a Newick tree that can be used for visualizing phylogenetic trees.


3. Parse tRNAscan-SE output
	- Prerequisites:
		- tRNAscan-SE output files (`.out`, `.ss`, `.iso`) separated into individual folders
	- A table containing paths for `.out`, `.iso`, and `.ss` files. Can be combined with `genomes.tsv` as additional columns. (`genomes.tsv`)
		- Covariance model specialized for alignment and numbering (specified by `-n` in `parse-tRNAs.py`)
		- Confidence set (if applicable) (`confidence-set.txt`)
	- Scripts:
		- `parse-tRNAs.py`: main driver script (`genomes.tsv`, `.out`, `.iso`, `.ss`, `numbering.sto`, `confidence-set.txt` -> `trna-df.tsv`)
		- `tRNA_position.py`: helper library that resolves Sprinzl tRNA positions
		- `sstofa3` (`.ss` -> `.fa`)
			- Removes introns by parsing the `.ss` file. Note that the default output is the same name as tRNAscan-SE `.fa` output, which contains introns! Introns are not okay!


4. Resolve consensus features and count base frequencies
	- Prerequisites:
		- Parsed data frame with each position as a column (`trnas.tsv`)
	- Scripts:
		- `resolve-consensus.py` (`taxonomy.tsv`, `trnas.tsv` -> `consensus.tsv`)
			- `consensus.tsv`: For each taxonomic group, lists consensus features for each position and isotype.
		- `count-freqs.py` (`taxonomy.tsv`, `trnas.tsv` -> `freqs.tsv`)
			- `freqs.tsv`: For each taxonomic group, lists base and base pair counts by position and isotype.


## Tuning the pipeline

Depending on your genome set, you will certainly need to make some changes to your workflow. Here's some examples:

- Adding a couple of lower scoring tRNAs is helpful for identifying minor conserved variants. For non-mammalian vertebrates though, I've locked in the tRNA set to the high confidence set, due to the sheer number of highly amplified tRNA genes.
- Fungi have more diverged tRNAs and score a bit lower using the eukaryotic covariance model, so a score threshold needs to be tuned to maximize the quality of your tRNA set.
