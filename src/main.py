import argparse
import os
import logging
from utils.models.config import Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso-filename")
    parser.add_argument("--iso-url")
    parser.add_argument("--target-config-name", choices=['nuc', 'thinkpad'])
    parser.add_argument("--target-iso-filename")
    parser.add_argument("--multipass-auth")
    parser.add_argument('--target-os', default='debian', choices=['debian', 'raspbian', '-'])
    parser.add_argument('--auth-keys', type=lambda x: x.split(','), required=True, help='Comma-separated list of private keys')
    args = parser.parse_args()

    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))


    if args.target_os == "debian":
        from builders.debian import build_iso
    elif args.target_os == "raspbian":
        from builders.raspbian import build_iso

    build_iso(**args.__dict__)
    logging.info("Done")
