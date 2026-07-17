import ctypes
import sys

import pytest


@pytest.mark.skipif(sys.platform != "win32", reason="Windows INPUT ABI only")
def test_windows_input_structure_matches_win32_abi() -> None:
    from voice_typing_pro.windows_input import INPUT

    assert ctypes.sizeof(INPUT) == 40
