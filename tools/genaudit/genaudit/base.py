
import os
import argparse

from genaudit import Audit, GitRepo

def _get_directory(config_file_dir, cfg_location, cli_location):
    location = cli_location if cli_location else cfg_location
    return location if os.path.isabs(location) else os.path.join(config_file_dir, location)

def init_from_command_line_arguments(args: argparse.Namespace) -> tuple[Audit, GitRepo]:
    """ Sets up a genaudit.GitRepo from commonly used command line arguments:
          audit_config_dir (mandatory)
        --token            (mandatory)
        --cache-location   (optional, overrides config setting)
        --repo-location    (optional, overrides config setting)
    """

    audit = Audit(args.audit_config_dir)
    cache = _get_directory(args.audit_config_dir, audit.cache_location, args.cache_location)
    checkout = _get_directory(args.audit_config_dir, audit.local_checkout, args.repo_location)
    repo = GitRepo(args.token, cache, checkout, audit.github_handle, audit.main_branch)
    return audit, repo
