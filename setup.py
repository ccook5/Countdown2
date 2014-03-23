import sys
from cx_Freeze import setup, Executable
 
exe = Executable(
    script = "countdown.pyw",
    base   = "Win32GUI",
    )
 
setup(
    name        = "Countdown",
    version     = "0.5",
    description = "Display a countdown clock that counts down to a specific time.",
    executables = [exe]
    )