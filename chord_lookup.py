"""
chord_lookup.py

Finds practical fret/pedal/lever combinations for a target chord on a pedal steel guitar.
Uses PedalSteel and ChordFinder classes.

Usage example (run as script):
    python chord_lookup.py "E" "maj"
"""

from pedal_steel import PedalSteel, Note
from chord_finder import ChordFinder
from itertools import product
from typing import List, Dict, Tuple, Optional

# --- Practical pedal and lever combinations ---

PEDAL_NAMES = ['A', 'B', 'C']
KNEE_NAMES = ['LKL', 'LKR', 'RKL', 'RKR']

def get_practical_pedal_combos() -> List[List[str]]:
    """Return all practical pedal combinations: single or two adjacent pedals."""
    combos = [
        [],
        ['A'],
        ['B'],
        ['C'],
        ['A', 'B'],
        ['B', 'C'],
    ]
    return combos

def get_practical_knee_combos() -> List[List[str]]:
    """Return all practical knee lever combinations."""
    left_options = [[], ['LKL'], ['LKR']]
    right_options = [[], ['RKL'], ['RKR']]
    combos = []
    for left in left_options:
        for right in right_options:
            combos.append(left + right)
    return combos

def get_all_practical_combos() -> List[Dict[str, List[str]]]:
    """Return all practical combinations of pedals and knee levers."""
    pedal_combos = get_practical_pedal_combos()
    knee_combos = get_practical_knee_combos()
    all_combos = []
    for pedals in pedal_combos:
        for knees in knee_combos:
            all_combos.append({
                'pedals': pedals,
                'knees': knees
            })
    return all_combos

def get_pitch_classes(notes: List[str]) -> List[str]:
    """Remove octave from notes, return pitch classes."""
    pcs = []
    for n in notes:
        if n[-1].isdigit():
            pcs.append(n[:-1])
        else:
            pcs.append(n)
    return pcs

def find_chord_positions(
    target_root: str,
    target_type: str,
    min_strings: int = 3,
    max_fret: int = 24
) -> List[Dict]:
    """
    For a given chord (root and type), find all practical fret/pedal/lever combos that produce it.
    Returns a list of dicts with fret, pedals, knees, and strings used.
    """
    steel = PedalSteel()
    finder = ChordFinder()
    results = []

    all_combos = get_all_practical_combos()

    for fret in range(0, max_fret + 1):
        steel.set_fret(fret)
        for combo in all_combos:
            # Reset all pedals/levers
            for p in PEDAL_NAMES + KNEE_NAMES:
                steel.pedal_lever_objects[p].active = False
            # Activate pedals
            for p in combo['pedals']:
                steel.pedal_lever_objects[p].active = True
            # Activate knees
            for k in combo['knees']:
                steel.pedal_lever_objects[k].active = True

            notes = steel.get_current_notes()
            pitch_classes = get_pitch_classes(notes)
            chords = finder.find_chords(pitch_classes)

            # Find if target chord is present
            for chord in chords:
                if chord['root'] == target_root and chord['type'] == target_type:
                    # Which strings are used?
                    chord_note_set = set(chord['notes'])
                    string_numbers = [
                        10 - idx for idx, n in enumerate(notes)
                        if (n[:-1] if n[-1].isdigit() else n) in chord_note_set
                    ]
                    if len(string_numbers) >= min_strings:
                        # Check for redundant pedals/levers
                        is_valid_position = True
                        active_pl_names = combo['pedals'] + combo['knees']
                        if active_pl_names:
                            chord_strings_set = set(string_numbers)
                            for pl_name in active_pl_names:
                                pl_obj = steel.pedal_lever_objects[pl_name]
                                # A pedal/lever is useful if it affects at least one string in the chord
                                is_pl_useful = False
                                for string_index in pl_obj.strings_affected:
                                    # Convert 0-based index to 1-based string number
                                    string_num = 10 - string_index
                                    if string_num in chord_strings_set:
                                        is_pl_useful = True
                                        break  # This pedal/lever is useful, check the next one
                                if not is_pl_useful:
                                    # This pedal/lever is redundant, so the whole position is invalid
                                    is_valid_position = False
                                    break  # No need to check other pedals/levers for this combo

                        if is_valid_position:
                            results.append({
                                'fret': fret,
                                'pedals': combo['pedals'],
                                'knees': combo['knees'],
                                'strings': sorted(string_numbers, reverse=True),
                                'notes': [notes[9 - (s - 1)] for s in sorted(string_numbers, reverse=True)]
                            })
    # Sort by number of strings (descending), then fret, then pedals/knees
    results.sort(key=lambda x: (-len(x['strings']), x['fret'], x['pedals'], x['knees']))
    return results

def print_chord_positions(positions: List[Dict], target_root: str, target_type: str, max_results: int = 10):
    print(f"\nWays to play {target_root} {target_type} chord (showing up to {max_results}):\n")
    if not positions:
        print("No positions found.")
        return
    for i, pos in enumerate(positions[:max_results], 1):
        pedal_str = '+'.join(pos['pedals']) if pos['pedals'] else 'none'
        knee_str = '+'.join(pos['knees']) if pos['knees'] else 'none'
        strings_str = ', '.join(str(s) for s in pos['strings'])
        notes_str = ', '.join(pos['notes'])
        print(f"{i}. Fret: {pos['fret']:2d} | Pedals: {pedal_str:8s} | Knees: {knee_str:12s} | Strings: {strings_str} | Notes: {notes_str}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python chord_lookup.py <root> <type>")
        print("Example: python chord_lookup.py E maj")
        sys.exit(1)
    root = sys.argv[1]
    ctype = sys.argv[2]
    positions = find_chord_positions(root, ctype)
    print_chord_positions(positions, root, ctype)
