import argparse

from agents.agent import AgentRunner
from agents.conf import Config
from utils.utility import set_up

"""
Usage :
python src/validate1.py -tm conf/_test.toml
python3 src/validate1.py -tm conf/_test.toml
"""


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf-toml", "-tm", type=str, help="Please specify config TOML file."
    )
    return parser.parse_args()


def main() -> None:
    set_up()
    conf = Config.fetch(get_args().conf_toml)
    agent_runner = AgentRunner(conf)
    agent_runner.run()
    return


if __name__ == "__main__":
    main()
