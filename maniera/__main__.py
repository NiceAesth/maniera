# __main__.py

import sys
from maniera.calculator import Maniera

def main():
    """Calculate PP and SR for a mania score.
    Arguments: <path to .osu> <mods bitwise> <score>
    """
    if len(sys.argv) > 2:
        sys.argv[2] = int(sys.argv[2])
        sys.argv[3] = int(sys.argv[3])
        calc = Maniera(*sys.argv[1:4])
        calc.calculate()
        print("SR: {sr:.2f} PP: {pp:.2f}".format(sr=calc.sr, pp=calc.pp))

if __name__ == "__main__":
    main()