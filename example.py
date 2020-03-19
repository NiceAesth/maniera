from main import Maniera

# 64 = DT (https://github.com/ppy/osu-api/wiki#mods)
# Maniera(path, modnum, score)
calc = Maniera('beatmap.osu', 64, 800000)
calc.calculate()

print(f"{round(calc.pp, 2)} PP - {round(calc.sr, 2)} Stars")