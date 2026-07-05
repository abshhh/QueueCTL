import subprocess


def test_echo_command():

    result = subprocess.run(
        "echo hello",
        shell=True,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "hello" in result.stdout.lower()