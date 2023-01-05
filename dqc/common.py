import sys
import os
import glob
import subprocess
import shutil
from logging import StreamHandler, FileHandler, Formatter, INFO, DEBUG, getLogger
from .config import config

def get_logger(name=None):
    if config.DEBUG:
        log_level = DEBUG
    else:
        log_level = INFO
    formatter = Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    logger = getLogger(name)
    handler = StreamHandler(stream=sys.stdout)
    handler.setLevel(log_level)  # INFO or DEBUG
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if config.LOG_FILE and not config.ADMIN:
        log_file = os.path.join(config.OUT_DIR, config.LOG_FILE)
        fh = FileHandler(log_file, mode="a", encoding="utf-8", delay=True)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    logger.setLevel(log_level)  # INFO or DEBUG
    return logger


logger = get_logger(__name__)


def run_command(cmd, task_name=None, shell=True):
    if task_name:
        logger.info("Task started: %s", task_name)
    if shell:
        cmd = " ".join(cmd)
    logger.info("Running command: %s", cmd)
    p = subprocess.run(cmd, shell=shell, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        logger.error("Command failed. Aborted. [%s]", cmd)
        logger.error("Output: %s\n%s", "-" * 80, p.stdout)
        exit(1)
    else:
        if task_name:
            logger.info("Task succeeded: %s", task_name)
        if p.stdout:
            logger.debug("%s output %s\n%s%s", task_name, "-" * 50, p.stdout, "-" * 50)


def prepare_output_directory():
    def _cleanup_results():
        result_file_names = [
            config.PRODIGAL_PROTEIN_FASTA,
            config.PRODIGAL_CDS_FASTA,
            config.HMMER_RESULT,
            config.MARKER_SUMMARY_FILE,
            config.QUERY_MARKERS_FASTA,
            config.BLAST_RESULT,
            config.TARGET_GENOME_LIST,
            config.FASTANI_RESULT,
            config.TC_RESULT,
            config.CC_RESULT,
            config.DQC_RESULT_JSON,
            config.GTDB_BLAST_RESULT,
            config.GTDB_TARGET_GENOME_LIST,
            config.GTDB_FASTANI_RESULT,
            config.GTDB_RESULT,
            config.LOG_FILE,
            "checkm.log",
        ]
        for file_name in result_file_names:
            file_path = os.path.join(config.OUT_DIR, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
        result_dir_names = [
            config.CHECKM_INPUT_DIR,
            config.CHECKM_RESULT_DIR
        ]
        for dir_name in result_dir_names:
            dir_path = os.path.join(config.OUT_DIR, dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)


    if os.path.exists(config.OUT_DIR):   
        if config.FORCE:
            # logger.warning("Will write results into existing directory [%s]", config.OUT_DIR)
            _cleanup_results()
        else:
            sys.stderr.write(f"Output directory already exists. Aborted. Set '--force' to overwrite results. [PATH: {config.OUT_DIR}]\n")
            exit(1)
    else:
        os.makedirs(config.OUT_DIR)
        # logger.info("Created result directory [%s]", config.OUT_DIR)


def is_empty_file(file_name):
    if not os.path.exists(file_name):
        logger.error("File not exists. [%s]", file_name)
        return True
    else:
        if os.path.getsize(file_name) == 0:
            logger.error("File is empty. [%s]", file_name)
            return True
        else:
            return False

def get_ref_path(base_name):
    return os.path.join(config.DQC_REFERENCE_DIR, base_name)

def get_gtdb_ref_genome_dir(accession):
    source_db, dir1, dir2, dir3 = accession[0:3], accession[4:7], accession[7:10], accession[10:13]
    gtdb_genome_dir = get_ref_path(config.GTDB_GENOME_DIR)
    gtdb_ref_fasta_dir = os.path.join(gtdb_genome_dir, source_db, dir1, dir2, dir3)
    return gtdb_ref_fasta_dir

def get_ref_genome_fasta(accession, for_gtdb=False):
    if for_gtdb:
        gtdb_ref_fasta_dir = get_gtdb_ref_genome_dir(accession)
        return os.path.join(gtdb_ref_fasta_dir, accession + "_genomic.fna.gz")
    else:
        genome_dir = get_ref_path(config.REFERENCE_GENOME_DIR)
        return os.path.join(genome_dir, accession + ".fna.gz")

def get_existing_gtdb_genomes():
    # Todo: check eof, broken file
    gtdb_genome_dir = get_ref_path(config.GTDB_GENOME_DIR)
    glob_pat = os.path.join(gtdb_genome_dir, "*", "*", "*", "*", "*_genomic.fna.gz")
    existing_genomes = []
    for file_name in glob.glob(glob_pat):
        if os.path.getsize(file_name) > 0:
            accession = os.path.basename(file_name).replace("_genomic.fna.gz", "")
            existing_genomes.append(accession)
    return existing_genomes

def fasta_reader(fasta_file_name):
    with open(fasta_file_name) as f:
        entries = f.read().strip(">").split("\n>")
    D = {}
    for entry in entries:
        lines = entry.strip().split("\n")
        seq_id = lines[0].split()[0]  # first line of the entry
        seq = "".join(lines[1:]).upper()  # remaining lines of the entry
        D[seq_id] = seq
    return D
