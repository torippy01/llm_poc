import argparse



def get_cl_args_for_conf_toml() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf-toml",
        "-tm",
        type=str,
        help="Please specify config TOML file."
    )
    return parser.parse_args()
