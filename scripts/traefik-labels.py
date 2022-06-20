#!/usr/bin/env python3

"""traefik labels """

import sys
import logging
import argparse
import re
import ruamel.yaml

# ======================================================================
# add key=value to labels (or replace value, if key already exists)
# ======================================================================
def single_label(labels: list, key: str, val: str) -> None:
    """find provided key and replace val (or add, if no key was found)"""

    key_re = re.compile(rf"^{key}=")
    new_label = f"{key}={val}"

    for i, label in enumerate(labels):
        if key_re.match(label):
            labels[i] = new_label
            return
    labels.append(new_label)


# ======================================================================
# modify or add traefik labels
# ======================================================================
def traefik_labels(args: object) -> None:
    """modify or add traefik labels"""

    # load compose file
    compose_yaml = ruamel.yaml.load(args.file, ruamel.yaml.RoundTripLoader)

    # basic sanity checks
    if "services" not in compose_yaml:
        logging.error("missing 'services', in compose file, exiting")
        sys.exit(1)
    if args.service not in compose_yaml["services"]:
        logging.error("missing service '%s', in compose file, exiting", args.service)
        sys.exit(1)

    # add "labels" if necessary
    if "labels" not in compose_yaml["services"][args.service]:
        compose_yaml["services"][args.service]["labels"] = []

    # explicitely enable traefik when providers.docker.exposedbydefault=false
    single_label(
        compose_yaml["services"][args.service]["labels"], "traefik.enable", "true"
    )

    # add router rule
    single_label(
        compose_yaml["services"][args.service]["labels"],
        f"traefik.http.routers.{args.id}.rule",
        f"Host(`{args.id}.localhost`)",
    )

    # print compose file to stdout
    ruamel.yaml.dump(
        compose_yaml,
        sys.stdout,
        explicit_start=True,
        explicit_end=True,
        Dumper=ruamel.yaml.RoundTripDumper,
    )


# ======================================================================
# main
# ======================================================================


def main():
    """main"""

    logging.basicConfig(
        format="%(filename)s:%(lineno)d %(funcName)s(): %(message)s", level=logging.INFO
    )

    parser = argparse.ArgumentParser(description="traefik labels helper")
    parser.add_argument("file", type=argparse.FileType("r+"), help="compose file name")
    parser.add_argument("service", type=str, help="docker service name")
    parser.add_argument("id", type=str, help="deployment id")

    args = parser.parse_args()
    traefik_labels(args)


# ======================================================================
# guard
# ======================================================================
if __name__ == "__main__":
    main()
