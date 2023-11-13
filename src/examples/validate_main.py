import argparse

from xecretary_core.agents.agent import AgentRunner
from xecretary_core.agents.conf import Config
from xecretary_core.utils.utility import set_up

"""
Usage :
python src/validate_main.py -tm conf/_test.toml
python3 src/validate_main.py -tm conf/_test.toml
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
