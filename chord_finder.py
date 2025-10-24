# ChordFinder: Identify chords from a list of note names (pitch classes, no octaves)
from itertools import combinations
from typing import List, Dict, Tuple, Set

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
NOTE_INDEX = {name: i for i, name in enumerate(NOTE_NAMES)}

# Chord formulas: intervals in semitones from root
CHORD_TYPES = {
    'maj':   [0, 4, 7],
    'min':   [0, 3, 7],
    'dim':   [0, 3, 6],
    'aug':   [0, 4, 8],
    'sus2':  [0, 2, 7],
    'sus4':  [0, 5, 7],
    'maj7':  [0, 4, 7, 11],
    '7':     [0, 4, 7, 10],
    'min7':  [0, 3, 7, 10],
    'm7b5':  [0, 3, 6, 10],  # half-diminished
    'dim7':  [0, 3, 6, 9],
    '6':     [0, 4, 7, 9],        # major 6th
    'min6':  [0, 3, 7, 9],        # minor 6th
    '9':     [0, 4, 7, 10, 2],    # dominant 9th (14 % 12 = 2)
    'maj9':  [0, 4, 7, 11, 2],    # major 9th
    'min9':  [0, 3, 7, 10, 2],    # minor 9th
    '11':    [0, 4, 7, 10, 2, 5],      # dominant 11th (14 % 12 = 2, 17 % 12 = 5)
    'maj11': [0, 4, 7, 11, 2, 5],      # major 11th
    'min11': [0, 3, 7, 10, 2, 5],      # minor 11th
    '13':    [0, 4, 7, 10, 2, 5, 9],   # dominant 13th (21 % 12 = 9)
    'maj13': [0, 4, 7, 11, 2, 5, 9],   # major 13th
    'min13': [0, 3, 7, 10, 2, 5, 9],   # minor 13th
}

class ChordFinder:
    def __init__(self):
        self.chord_types = CHORD_TYPES

    def note_to_index(self, note: str) -> int:
        """Convert note name to pitch class index."""
        if note not in NOTE_INDEX:
            raise ValueError(f"Unknown note: {note}")
        return NOTE_INDEX[note]

    def normalize_notes(self, notes: List[str]) -> Set[int]:
        """Convert note names to a set of pitch class indices."""
        return set(self.note_to_index(n) for n in notes)

    def find_chords(self, notes: List[str]) -> List[Dict]:
        """
        Given a list of note names (pitch classes, e.g. ['E', 'G#', 'B', 'D']),
        return a list of matching chords with root, type, and notes used.
        """
        found_chords = []
        unique_notes = list(set(notes))
        note_indices = [self.note_to_index(n) for n in unique_notes]

        # Try all combinations of 3 to 7 notes (triads up to 13th chords)
        for size in [3, 4, 5, 6, 7]:
            for combo in combinations(note_indices, size):
                for root_idx in combo:
                    intervals = sorted(((n - root_idx) % 12 for n in combo))
                    for chord_name, formula in self.chord_types.items():
                        if len(formula) == size and sorted(formula) == intervals:
                            root_name = NOTE_NAMES[root_idx]
                            chord_notes = [NOTE_NAMES[n] for n in combo]
                            found_chords.append({
                                'root': root_name,
                                'type': chord_name,
                                'notes': chord_notes
                            })
        # Remove duplicates (same root, type, notes)
        unique_chords = []
        seen = set()
        for chord in found_chords:
            key = (chord['root'], chord['type'], tuple(sorted(chord['notes'])))
            if key not in seen:
                unique_chords.append(chord)
                seen.add(key)
        return unique_chords

if __name__ == "__main__":
    # Example usage
    finder = ChordFinder()
    notes = ['E', 'G#', 'B', 'D', 'F#']
    chords = finder.find_chords(notes)
    for chord in chords:
        print(f"{chord['root']} {chord['type']}: {', '.join(chord['notes'])}")
