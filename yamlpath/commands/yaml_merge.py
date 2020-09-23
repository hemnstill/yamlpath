"""
Enable users to merge YAML/Compatible files.

Due to the complexities of merging, users are given deep control over the merge
operation via both default behaviors as well as per YAML Path behaviors.

Copyright 2020 William W. Kimball, Jr. MBA MSIS

=== TODOs ===
This must permit output to STDOUT, suppressing all non-critical output.
This must also permit taking RHS from STDIN and as a parameter value.
"""
import sys
import argparse
from os import access, R_OK
from os.path import isfile

from yamlpath.enums import (
    AnchorConflictResolutions,
    AoHMergeOpts,
    ArrayMergeOpts,
    HashMergeOpts
)
from yamlpath.func import get_yaml_data, get_yaml_editor
from yamlpath import Merger, MergerConfig

from yamlpath.wrappers import ConsolePrinter

# Implied Constants
MY_VERSION = "0.0.1"

def processcli():
    """Process command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Merges two or more YAML/Compatible files together.",
        epilog="The left-to-right order of YAML_FILEs is significant.  Except\
            when this behavior is deliberately altered by your options, data\
            from files on the right overrides data in files to their left.  \
            For more information about YAML Paths, please visit\
            https://github.com/wwkimball/yamlpath."
    )
    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s " + MY_VERSION)

    parser.add_argument("-c", "--config",
                        help="INI syle configuration file for YAML Path\
                              specified merge control options")

    parser.add_argument(
        "-a", "--anchors",
        choices=[l.lower() for l in AnchorConflictResolutions.get_names()],
        type=str.lower,
        help="means by which Anchor name conflicts are resolved\
              (overrides [defaults]anchors set via --config|-c and cannot be\
              overridden by [rules] because Anchors apply to the whole file);\
              default=stop")
    parser.add_argument(
        "-A", "--arrays",
        choices=[l.lower() for l in ArrayMergeOpts.get_names()],
        type=str.lower,
        help="default means by which Arrays are merged together\
              (overrides [defaults]arrays but is overridden on a YAML Path\
              basis via --config|-c); default=all")
    parser.add_argument(
        "-H", "--hashes",
        choices=[l.lower() for l in HashMergeOpts.get_names()],
        type=str.lower,
        help="default means by which Hashes are merged together\
              (overrides [defaults]hashes but is overridden on a YAML Path\
              basis in [rules] set via --config|-c); default=stop")
    parser.add_argument(
        "-o", "--aoh",
        choices=[l.lower() for l in AoHMergeOpts.get_names()],
        type=str.lower,
        help="default means by which Arrays-of-Hashes are merged together\
              (overrides [defaults]aoh but is overridden on a YAML Path\
              basis in [rules] set via --config|-c); default=all")

    noise_group = parser.add_mutually_exclusive_group()
    noise_group.add_argument(
        "-d", "--debug", action="store_true",
        help="output debugging details")
    noise_group.add_argument(
        "-v", "--verbose", action="store_true",
        help="increase output verbosity")
    noise_group.add_argument(
        "-q", "--quiet", action="store_true",
        help="suppress all output except errors")

    parser.add_argument("rhs_files", metavar="YAML_FILE", nargs="+",
                        help="one or more YAML files to merge,\
                              order-significant")
    return parser.parse_args()

def validateargs(args, log):
    """Validate command-line arguments."""
    has_errors = False

    # There must be at least two input files
    if len(args.rhs_files) < 2:
        has_errors = True
        log.error("There must be at least two YAML_FILEs.")

    # When set, the configuration file must be a readable file
    if args.config and not (
            isfile(args.config)
            and access(args.config, R_OK)
    ):
        has_errors = True
        log.error(
            "INI style configuration file is not readable:  " + args.config)

    if has_errors:
        sys.exit(1)

def main():
    """Main code."""
    args = processcli()
    log = ConsolePrinter(args)
    validateargs(args, log)

    # The first input file is the prime
    fileiterator = iter(args.rhs_files)
    prime_yaml = get_yaml_editor()
    prime_file = next(fileiterator)
    prime_data = get_yaml_data(prime_yaml, log, prime_file)
    merger = Merger(log, prime_data, MergerConfig(log, args))

    # ryamel.yaml unfortunately tracks comments AFTER each YAML key/value.  As
    # such, it is impossible to copy comments from RHS to LHS in any sensible
    # way.  This leads to absurd merge results that are data-accurate but
    # comment-insane.  This ruamel.yaml design decision forces me to simply
    # delete all comments from all merge documents to produce a sensible
    # result.
    Merger.delete_all_comments(prime_data)

    # Merge additional input files into the prime
    exit_state = 0
    rhs_yaml = get_yaml_editor()
    for rhs_file in fileiterator:
        # Each YAML_FILE must actually be a file; because merge data is
        # expected, this is a fatal failure.
        if not isfile(rhs_file):
            log.error("Not a file:  {}".format(rhs_file))
            exit_state = 2
            break

        log.info("Processing {}...".format(rhs_file))

        # Try to open the file; failures are fatal
        rhs_data = get_yaml_data(rhs_yaml, log, rhs_file)
        if rhs_data is None:
            # An error message has already been logged
            exit_state = 3
            break

        # Merge the new RHS into the prime LHS
        merger.merge_with(rhs_data)

        log.debug("main: resulting document:")
        log.debug(merger.data)

    # Output the final document
    prime_yaml.dump(merger.data, sys.stdout)
    sys.exit(exit_state)

if __name__ == "__main__":
    main()  # pragma: no cover
