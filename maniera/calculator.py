# calculator.py

import re
import math

whitespace_regex = re.compile(r"\/\/.*")
note_regex = re.compile(r"(\d+),\d+,(\d+),\d+,\d+,(\d+)")
section_regex = re.compile(r"\[(.*)\]")

class Maniera:

    def __init__(self, osupath, mods, score):
        """Initialize Maniera calculator."""
        self.osupath = osupath
        self.mods = mods
        self.score = score
        self.gamemode = 3
        self.od = 0
        self.keys = 0
        self.notes = []
        self.note_count = 0
        self.pp = 0
        self.sr = 0

        self.__parseBeatmapFile()

    def __parseNote(self, line):
        """Parse a note text into a note dict. (Internal use)."""
        m = re.match(note_regex, line)
        try:
            x = float( m.group(1) )
            start_t = float( m.group(2) )
            end_t = float( m.group(3) )
            key = math.floor( x * self.keys / 512 )

            if not end_t:
                end_t = start_t

            return {
                'key': key,
                'start_t': start_t,
                'end_t': end_t,
                'overall_strain': 1,
                'individual_strain': [0] * self.keys
            }
        except:
            pass

    def __parseBeatmapFile(self):
        """Parse a beatmap file and set class variables. (Internal use)."""
        with open(self.osupath) as bmap:
            textContent = bmap.read()
            lines = textContent.splitlines()

        section_name = ""
        for line in lines:

            if line == "" or re.match(whitespace_regex, line):
                continue

            m = re.match(section_regex, line)
            if m:
                section_name = m.group(1)
                continue

            if section_name == "Difficulty":
                if re.match(r"CircleSize:(.*)", line):
                    self.keys = int( re.match(r"CircleSize:(.*)", line).group(1) )
                if re.match(r"OverallDifficulty:(.*)", line):
                    self.od = float( re.match(r"OverallDifficulty:(.*)", line).group(1) )

            if section_name == "HitObjects":
                note = self.__parseNote(line)
                if note:
                    self.notes.append(note)

        self.notes.sort(key=lambda note: note['start_t'])
        self.note_count = len(self.notes)

    def _calculateStars(self):
        """Calculate star rating. (Internal use)."""
        time_scale = 1

        if self.mods & 64:
            time_scale = 1.5
        if self.mods & 256:
            time_scale = 0.75

        # Constants
        strain_step = 400 * time_scale
        weight_decay_base = 0.9
        individual_decay_base = 0.125
        overall_decay_base = 0.3
        star_scaling_factor = 0.018

        # Get strain of each note
        held_until = [0] * self.keys
        previous_note = None

        for note in self.notes:

            if not previous_note:
                previous_note = note
                continue

            time_elapsed = (note['start_t'] - previous_note['start_t']) / time_scale / 1000
            individual_decay = individual_decay_base ** time_elapsed
            overall_decay = overall_decay_base ** time_elapsed
            hold_factor = 1
            hold_addition = 0

            for i in range(self.keys):
                if note['start_t'] < held_until[i] and note['end_t'] > held_until[i]:
                    hold_addition = 1
                elif note['end_t'] == held_until[i]:
                    hold_addition = 0
                elif note['end_t'] < held_until[i]:
                    hold_factor = 1.25
                note['individual_strain'][i] = previous_note['individual_strain'][i] * individual_decay

            held_until[note['key']] = note['end_t']

            note['individual_strain'][note['key']] += 2 * hold_factor
            note['overall_strain'] = previous_note['overall_strain'] * overall_decay + (1 + hold_addition) * hold_factor

            previous_note = note

        # Get difficulty for each interval
        strain_table = []
        max_strain = 0
        interval_end_time = strain_step
        previous_note = None

        for note in self.notes:
            while note['start_t'] > interval_end_time:
                strain_table.append(max_strain)

                if not previous_note:
                    max_strain = 0
                else:
                    individual_decay = individual_decay_base ** ( (interval_end_time - previous_note['start_t']) / 1000)
                    overall_decay = overall_decay_base ** ( (interval_end_time - previous_note['start_t']) / 1000)
                    max_strain = previous_note['individual_strain'][previous_note['key']] * individual_decay + previous_note['overall_strain'] * overall_decay

                interval_end_time += strain_step

            strain = note['individual_strain'][note['key']] + note['overall_strain']
            if strain > max_strain:
                max_strain = strain
            previous_note = note

        # Get total difficulty
        difficulty = 0
        weight = 1
        strain_table.sort(reverse=True)
        for i in strain_table:
            difficulty += i * weight
            weight *= weight_decay_base

        return difficulty * star_scaling_factor

    def _calculatePP(self):
        """Calculate PP. To be run only after __calculateStars. (Internal use)."""
        score_rate = 1

        if self.mods & 1: # NF
            score_rate *= 0.5
        if self.mods & 2: # EZ
            score_rate *= 0.5
        if self.mods & 256: # HT
            score_rate *=0.5

        real_score = self.score / score_rate

        hit300_window = 34 + 3 * ( min( 10, max( 0, 10 - self.od ) ) )
        strain_value = (5 * max(1, self.sr / 0.2) - 4) ** 2.2 / 135 * (1 + 0.1 * min(1, self.note_count / 1500))

        if real_score <= 500000:
            strain_value = 0
        elif real_score <= 600000:
            strain_value *= ((real_score - 500000) / 100000 * 0.3)
        elif real_score <= 700000:
            strain_value *= (0.3 + (real_score - 600000) / 100000 * 0.25)
        elif real_score <= 800000:
            strain_value *= (0.55 + (real_score - 700000) / 100000 * 0.20)
        elif real_score <= 900000:
            strain_value *= (0.75 + (real_score - 800000) / 100000 * 0.15)
        else:
            strain_value *= (0.9 + (real_score - 900000) / 100000 * 0.1)

        acc_value = max(0, 0.2 - ( (hit300_window - 34) * 0.006667 ) ) * strain_value * ( max(0, real_score - 960000) / 40000) ** 1.1

        pp_multiplier = 0.8
        if self.mods & 1: # NF
            pp_multiplier *= 0.9
        if self.mods & 2: # EZ
            pp_multiplier *= 0.5

        return (strain_value ** 1.1 + acc_value ** 1.1) ** (1 / 1.1) * pp_multiplier


    def calculate(self):
        """Calculates PP and star rating."""
        self.sr = self._calculateStars()
        self.pp = self._calculatePP()
