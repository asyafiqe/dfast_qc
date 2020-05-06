import sys
import os
import subprocess
from logging import StreamHandler, FileHandler, Formatter, INFO, DEBUG, getLogger
from .config import config

def get_logger(name=None):
    if config.DEBUG:
        log_level = DEBUG
    else:
        log_level = INFO
    formatter = Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    logger = getLogger(name)
    handler = StreamHandler(stream=sys.stderr)
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


def run_command(cmd, task_name, shell=True):
    logger.info("Task started: %s", task_name)
    if shell:
        cmd = " ".join(cmd)
    logger.info("Running command: %s", cmd)
    p = subprocess.run(cmd, shell=shell, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        logger.error("%s failed. Aborted. [%s]", task_name, cmd)
        logger.error("%s output: %s\n%s", task_name, "-" * 80, p.stdout)
        exit(1)
    else:
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
            config.DQC_RESULT,
            config.DQC_RESULT_JSON,
            config.LOG_FILE
        ]
        for file_name in result_file_names:
            file_path = os.path.join(config.OUT_DIR, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)

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