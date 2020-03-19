from main import Maniera

calc = Maniera('beatmap.osu', 64, 800000)
calc.calculate()

print(f"{round(calc.pp, 2)} PP - {round(calc.sr, 2)} Stars")