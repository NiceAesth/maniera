# 🎹 Maniera
## osu! Mania PP calculator written in Python.
Written with ❤️ by [Nice Aesthetics](https://aesth.dev). Based on [ompp-web](https://github.com/toxicpie/ompp-web)

Example Usage:
------
```py
from main import Maniera

calc = Maniera('beatmap.osu', 64, 800000)
calc.calculate()

print(f"{round(calc.pp, 2)} PP - {round(calc.sr, 2)} Stars")
```
Output:
```sh
564.36 PP - 8.16 Stars
```