import openai
import subprocess


def get_aws_cli_version():
    aws_cli_version = (
        subprocess.check_output(["aws", "--version"]).decode("utf-8").strip()
    )

    return aws_cli_version


def get_gpt_response(query: str):
    response = (
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": query}]
        )
        .choices[0]["message"]["content"]
        .strip()
    )

    return response
