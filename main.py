from simulator import Simulator
import argparse
import logging

parser = argparse.ArgumentParser(
    description='MDP Maze Exploration Module'
)
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

x = Simulator()
