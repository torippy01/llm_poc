from dataclasses import dataclass
from typing import Callable
from tools.command_predictor import CommandPredictor
from tools.parameter_predictor import ParameterPredictor
from tools.user_context_predictor import user_context_predictor_wrapper


@dataclass(frozen=True)
class CustomTool:
    command_predictor: CommandPredictor = CommandPredictor()  # type: ignore
    parameter_predictor: ParameterPredictor = ParameterPredictor()  # type: ignore
    user_context_predictor: Callable = user_context_predictor_wrapper
