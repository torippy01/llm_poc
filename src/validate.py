from agents.agent import AgentRunner
from config.config import Config
from utils.utility import set_up

"""
Usage :
python src/validate.py -tm conf/_test.toml
"""


def main():
    set_up()
    conf = Config.fetch_config()
    agent_runner = AgentRunner(conf)
    agent_runner.run()
    return


if __name__ == "__main__":
    main()
