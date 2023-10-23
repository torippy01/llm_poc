import argparse



def get_CL_args_for_conf_toml() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf_toml",
        "-tm",
        type=str,
        help="Please specify config TOML file."
    )
    return parser.parse_args()