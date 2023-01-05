# DFAST_QC: DFAST Qauality Control

DFAST_QC conducts taxonomy and completeness check of the assembled genome.  

- Taxonomy check  
DFAST_QC evaluates taxonomic identity of the genome by querying against more than 15,000 reference genomes from type strains. To shorten the runtime, it first searches for universally-conserved housekeeping genes, such as _dnaB_ and _rpsA_ in the query genome, and they are queried against reference nucleotide databases to narrow down the number of genomes used in the downstream process. Then, average nucleotide identity is calculated against the selected reference genomes.  
DFAST_QC uses HMMer and NCBI Blast for the former process and [FastANI](https://doi.org/10.1038/s41467-018-07641-9) for the latter process.

- Completeness check  
DFAST_QC employs [CheckM](https://genome.cshlp.org/content/25/7/1043) to calculate completeness and contamination values of the genome. DFAST_QC automatically determines the reference marker set for CheckM based on the result of taxonomy check. Users can also arbitrarily specify the marker set to be used.

- GTDB search  
As of ver. 0.5.0, DFAST_QC can calculate ANI against GTDB representative genomes, thereby enabling species-level identification in the GTDB Taxonomy. Thie employs the same 2-step search as Taxonomy check

## System requirements and software dependencies
DFAST_QC runs on Linux / Mac (Intel CPU) with Python ver. 3.7 or later. It requires approximately 16Gbyte of memory. 
The following third party softwares/packages are required.  
- FastANI  
- HMMer  
- NCBI BLAST  
- Prodigal  
- CheckM  
- Python packages: peewee, more-itertools, ete3  

## Installation from source code
1. Source code
    ```
    $ git clone https://github.com/nigyta/dfast_qc.git
    ```
2. Install dependencies  
    We recommend using conda to install dependencies.  
    ```
    $ cd dfast_qc
    $ conda env create -f environment.yml
    ```
    This will create a conda environment named "dfast_qc" and install the above-mentioned dependencies in it.  

    Alternatively, after installing required softwares by yourself, you can install Python packages with the `pip` command.
    ```
    $ pip install -r requirements.txt
    ```

    __[Trouble shoot]__  
    If `fastANI` installed with the `conda` command does not work, please uninstall and re-install it with the commands below.  
    ```
    $ conda uninstall fastani
    $ conda install -c bioconda -c conda-forge fastani
    ```


## Installation from Bioconda
DFAST_QC is also available from [BioConda](https://bioconda.github.io/recipes/dfast_qc/README.html).
```
conda install -c bioconda dfast_qc
```
Reference data is not included in the conda package. Please install it following the steps below.

## Initial set up
Reference data of DFAST_QC is stored in a directory called `DQC_REFERENCE`. By default, it is located in the directory where DFAST_QC is installed (`PATH/TO/dfast_qc/dqc_reference`), or in `/dqc_reference` when the docker version is used.  
In general, you do not need to change this, but you can specify it in the config file or by using `-r` option.

__To prepare reference data, run the following command.__
```
$ sh initial_setup.sh [-n int]
```
`-n` denotes the number of threads for parallel processing (default: 1). As data preparation may take time, it is recommended specifying the value 4~8 (or more) for `-n`.

__Once reference data has been prepared, it can be updated by running command__
```
$ dqc_admin_tools.py update_all
```

Instead of running `initial_setup.sh`, you can prepare reference data by manually executing the following commands. Run `dqc_admin_tools.py -h` or `dqc_admin_tools.py subcommand -h` to show help.
  

1. Download master files  
    ```
    $ dqc_admin_tools.py download_master_files --targets asm ani tsr hmm igp
    ```
    This will download "Assembly report", "ANI report", "Type strain report", and "indistinguishable_groups_prokaryotes.txt" from the NCBI FTP server and HMMer profile for TIGR.  

2. Download/Update NCBI taxdump data
    ```
    $ dqc_admin_tools.py update_taxdump
    ```
3. Download reference genomes
    ```
    $ dqc_admin_tools.py download_genomes
    ```
    This will download reference genomic FASTA files from the NCBI Assembly database. As it attempts to download large number of genomes, it is recommended to enable parallel downloadin option (e.g. `--num_threads 4`)
4. Prepare reference profile HMM
    ```
    $ dqc_admin_tools.py prepare_reference_hmm
    ```
    This will generate a reference HMM file `DQC_REFERENCE/reference_markers.hmm`
5. Prepare reference marker FASTA file
    ```
    $ dqc_admin_tools.py prepare_reference_fasta
    ```
    This will generate a reference FASTA file `DQC_REFERENCE/reference_markers.fasta`
    it is recommended to enable parallel processing option (e.g. `--num_threads 4`)
6. Prepare SQLite database file
    ```
    $ dqc_admin_tools.py prepare_sqlite_db
    ```
    This will generate a reference file `DQC_REFERENCE/references.db`, which contains metadata for reference genomes.
7. Prepare CheckM data
    ```
    $ dqc_admin_tools.py prepare_checkm
    ```
    CheckM reference data will be downloaded and configured.
8. Update database for CheckM
    ```
    $ dqc_admin_tools.py update_checkm_db
    ```
    Will insert auxiliary data for CheckM into `DQC_REFERENCE/references.db`




## Usage
- Minimum  
    ```
    $ dfast_qc -i /path/to/input_genome.fasta
    ```
- Basic  
    ```
    $ dfast_qc -i /path/to/input_genome.fasta -o /path/to/output --num_threads 2
    ```
- GTDB search (disabled by default)  
    ```
    $ dfast_qc -i /path/to/input_genome.fasta -o /path/to/output --enable_gtdb [--disable_tc] [--disable_cc]
    ```

```
usage: dfast_qc [-h] [--version] [-i PATH] [-o PATH] [-t INT] [-r PATH]
                [-n INT] [--enable_gtdb] [--disable_tc] [--disable_cc]
                [--disable_auto_download] [--force] [--debug] [-p STR]
                [--show_taxon]

DFAST_QC: Taxonomy and completeness check

optional arguments:
  -h, --help            show this help message and exit
  --version             Show program version
  -i PATH, --input_fasta PATH
                        Input FASTA file (raw or gzipped) [required]
  -o PATH, --out_dir PATH
                        Output directory (default: OUT)
  -t INT, --taxid INT   NCBI taxid for completeness check. Use '--show_taxon'
                        for available taxids. (Default: Automatically inferred
                        from taxonomy check)
  -r PATH, --ref_dir PATH
                        DQC reference directory (default: DQC_REFERENCE_DIR)
  -n INT, --num_threads INT
                        Number of threads for parallel processing (default: 1)
  --enable_gtdb         Enable GTDB search
  --disable_tc          Disable taxonomy check using ANI
  --disable_cc          Disable completeness check using CheckM
  --disable_auto_download
                        Disable auto-download for missing reference genomes
  --force               Force overwriting result
  --debug               Debug mode
  -p STR, --prefix STR  Prefix for output (for debugging use, default: None)
  --show_taxon          Show available taxa for competeness check
  ```

## Example of Result
- `tc_result.tsv`: Taxonomy check result
- `cc_result.tsv`: Completeness check result
- `dqc_result.json`: DFAST_QC result in a json format as show below:
    ```
    {
        "tc_result": [
            {
                "organism_name": "Lactobacillus paragasseri",
                "strain": "strain=JCM 5343",
                "accession": "GCA_003307275.1",
                "taxid": 2107999,
                "species_taxid": 2107999,
                "relation_to_type": "type",
                "validated": true,
                "ani": 99.8183,
                "matched_fragments": 629,
                "total_fragments": 667,
                "status": "conclusive"
            },
            ...
            {
                "organism_name": "Lactobacillus gasseri",
                "strain": "strain=ATCC 33323",
                "accession": "GCA_000014425.1",
                ...
                "ani": 93.5813,
                "matched_fragments": 568,
                "total_fragments": 667,
                "status": "below_threshold"
            }
        ],
        "cc_result": {
            "completeness": 98.71,
            "contamination": 0.81,
            "strain_heterogeneity": 0.0
        }
    }
    ```

## Preparation for the GTDB reference data.
1. Download the representative genomes from GTDB and unarchive it.
    ```
    $ curl -LO https://data.gtdb.ecogenomic.org/releases/latest/genomic_files_reps/gtdb_genomes_reps.tar.gz
    $ tar xfz gtdb_genomes_reps.tar.gz
    ```
2. Place the unarchived folder under `DQC_REFERENCE`.  
Make sure that the folder name is identical to the value `GTDB_GENOME_DIR` specified in [config.py](dqc/config.py).  
    ```
    GTDB_GENOME_DIR = "gtdb_genomes_reps_r207"
    ```
3. Download the species list from GTDB.  
    ```
    curl -LO https://data.gtdb.ecogenomic.org/releases/latest/auxillary_files/sp_clusters.tsv
    ```
    The above command will download [this file](https://data.gtdb.ecogenomic.org/releases/latest/auxillary_files/sp_clusters.tsv) from GTDB.
4. Create a reference marker FASTA for GTDB representative genomes  
    This may take time since it tries to identify marker genes for more than 60,000 representative genomes.
    ```
    dqc_admin_tools.py prepare_reference_fasta --for_gtdb [--delete_existing_marker] [--num_threads 6]
    ```
5. Prepare the SQLite DB file for GTDB  
    ```
    dqc_admin_tools.py prepare_sqlite_db --for_gtdb
    ```

When the newer version of the GTDB representative genomes become available, repeat these steps.

## List of status in taxonomy check result
- __conclusive__: Effective ANI hit (>=95%) againt only 1 species, hence the species name is conclusively determined.
- __indistinguishable__: The genome belongs to one of the species that are difficult to distinguish using ANI (e.g. E. coli and Shigella spp.) 
- __inconsistent__: ANI hits against more than 2 differenct species. This may result from the comparison between very closely-related species or contamination of 2 different species.
- __below_threhold__: The ANI hit is below the threshold (95%)

Note that DFAST_QC cannot identify clades below species level.

## Run in Docker

Docker image is available at [dockerub](https://hub.docker.com/r/nigyta/dfast_qc).  
The example below shows how to invoke DFAST_QC with an input FASTA file (genome.fa) in the current directory.
```
docker run -it --rm --name dqc -v /path/to/dqc_reference:/dqc_reference -v $PWD:$PWD nigyta/dfast_qc dfast_qc -i $PWD/genome.fa -o $PWD/dfastqc_out
```