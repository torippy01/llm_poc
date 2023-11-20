from xecretary_core.agents.mode import AgentExecutionMode


def test_from_str_none_string():
    mode = AgentExecutionMode.from_str(string=None)
    assert mode is None


def test_from_str_inappropriate_string():
    mode = AgentExecutionMode.from_str(string="hoge")
    assert mode is None


def test_from_str_approproate_string():
    mode = AgentExecutionMode.from_str(string="qa")
    assert mode == AgentExecutionMode.QA

    mode = AgentExecutionMode.from_str(string="interactive")
    assert mode == AgentExecutionMode.INTERACTIVE

    mode = AgentExecutionMode.from_str(string="single")
    assert mode == AgentExecutionMode.SINGLE
