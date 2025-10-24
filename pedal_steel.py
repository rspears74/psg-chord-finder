from typing import Dict, List, Optional

from chord_finder import ChordFinder


# Helper: note names in order, for transposition
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']

class Note:
    # Application-wide setting for displaying octave
    show_octave = False

    def __init__(self, name: str, octave: int):
        self.name = name
        self.octave = octave

    @classmethod
    def from_string(cls, note_str: str):
        # Handles both single and double character note names
        if len(note_str) == 2:
            name = note_str[0]
            octave = int(note_str[1])
        else:
            name = note_str[:2]
            octave = int(note_str[2])
        return cls(name, octave)

    def __add__(self, semitones: int):
        idx = NOTE_NAMES.index(self.name)
        idx_new = idx + semitones
        octave_shift, idx_final = divmod(idx_new, 12)
        return Note(NOTE_NAMES[idx_final], self.octave + octave_shift)

    def __str__(self):
        if Note.show_octave:
            return f"{self.name}{self.octave}"
        else:
            return f"{self.name}"

    def __repr__(self):
        return str(self)

class PedalOrLever:
    def __init__(self, strings: list, semitone_change: int):
        """
        strings: list of string numbers (1 = highest, 10 = lowest)
        semitone_change: integer (positive for raise, negative for lower)
        """
        # Convert string numbers to 0-based indices (0 = string 10, 9 = string 1)
        self.indices = [10 - s for s in strings]
        self.semitone_change = semitone_change
        self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    @property
    def strings_affected(self):
        return self.indices

    def get_changes(self, num_strings: int) -> list:
        """
        Returns a list of semitone changes for each string index.
        """
        return [
            self.semitone_change if i in self.indices else 0
            for i in range(num_strings)
        ]

class PedalSteel:
    def __init__(self):
        # Open string notes, string 10 (lowest) to 1 (highest)
        self.open_strings = [
            Note.from_string('B2'),   # 10
            Note.from_string('D3'),   # 9
            Note.from_string('E3'),   # 8
            Note.from_string('F#3'),  # 7
            Note.from_string('G#3'),  # 6
            Note.from_string('B3'),   # 5
            Note.from_string('E4'),   # 4
            Note.from_string('G#4'),  # 3
            Note.from_string('D#5'),  # 2
            Note.from_string('F#5'),  # 1
        ]
        self.fret = 0  # 0 = open

        # Define pedal and lever logic (string numbers: 1 = highest, 10 = lowest)
        self.pedal_lever_objects = {
            'A': PedalOrLever([5, 10], 2),        # 5 & 10 up whole step
            'B': PedalOrLever([3, 6], 1),         # 3 & 6 up half step
            'C': PedalOrLever([4, 5], 2),         # 4 & 5 up whole step
            'LKL': PedalOrLever([4, 8], 1),       # 4 & 8 up half step
            'LKR': PedalOrLever([4, 8], -1),      # 4 & 8 down half step
            'RKL': PedalOrLever([1, 7], 2),       # 1 & 7 up whole step
            'RKR': PedalOrLever([2, 9], -1),      # 2 & 9 down half step
        }

    def set_pedal_or_lever(self, name: str, state: bool):
        if name in self.pedal_lever_objects:
            self.pedal_lever_objects[name].active = state

    def set_fret(self, fret: int):
        self.fret = fret

    def get_current_notes(self) -> List[str]:
        # Start with open strings, apply fret
        notes = [note + self.fret for note in self.open_strings]

        # Gather all active pedals/levers
        active = [obj for obj in self.pedal_lever_objects.values() if obj.active]

        # Sum all semitone changes for each string
        semitone_changes = [0] * 10
        for obj in active:
            for idx, delta in enumerate(obj.get_changes(10)):
                semitone_changes[idx] += delta

        # Apply pedal/lever changes
        notes = [note + semitone_changes[i] for i, note in enumerate(notes)]
        return [str(note) for note in notes]

    def print_current_notes(self):
        notes = self.get_current_notes()
        # Print notes with string numbers (1 = highest, 10 = lowest)
        print("String notes (1 = highest, 10 = lowest):")
        for i, note in enumerate(notes[::-1], 1):
            print(f"String {i}: {note}")

        # Find and print all possible chords
        # Remove octave for chord finding
        pitch_classes = [str(note) if isinstance(note, str) else note.name for note in notes]
        finder = ChordFinder()
        chords = finder.find_chords(pitch_classes)
        if chords:
            print("\nPossible chords found:")
            for chord in chords:
                # Find which strings are used in this chord
                chord_note_set = set(chord['notes'])
                string_numbers = [
                    10 - idx for idx, n in enumerate(notes)
                    if (str(n) if isinstance(n, str) else n.name) in chord_note_set
                ]
                string_numbers_str = ', '.join(str(s) for s in sorted(string_numbers, reverse=True))
                print(f"{chord['root']} {chord['type']} (strings: {string_numbers_str})")
        else:
            print("\nNo chords found.")

if __name__ == "__main__":
    steel = PedalSteel()
    steel.set_fret(3)
    steel.pedal_lever_objects['A'].activate()
    steel.pedal_lever_objects['LKL'].activate()
    steel.print_current_notes()
