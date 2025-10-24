import streamlit as st
from pedal_steel import PedalSteel, Note
from chord_finder import ChordFinder, CHORD_TYPES
from chord_lookup import find_chord_positions

# --- Streamlit UI setup ---
st.set_page_config(page_title="Pedal Steel Chord Finder", layout="centered")
st.title("Pedal Steel Chord Finder")

mode = st.sidebar.radio("Mode", ["Chords at Position", "Find Positions for Chord"], key="mode_radio")

# --- PedalSteel and ChordFinder setup ---
import pandas as pd

if mode == "Chords at Position":
    st.header("Chords at Position")

    # Sidebar controls for position
    fret = st.sidebar.slider("Fret", min_value=0, max_value=24, value=0, key="fret_tab1")
    show_octave = st.sidebar.checkbox("Show Octave Numbers", value=True, key="octave_tab1")

    steel1 = PedalSteel()
    steel1.set_fret(fret)

    st.sidebar.subheader("Pedals")
    pedal_states = {}
    for pedal in ['A', 'B', 'C']:
        pedal_states[pedal] = st.sidebar.checkbox(f"Pedal {pedal}", value=False, key=f"pedal_{pedal}_tab1")
        steel1.pedal_lever_objects[pedal].active = pedal_states[pedal]

    st.sidebar.subheader("Knee Levers")
    lever_labels = {
        'LKL': "Left Knee Left (LKL)",
        'LKR': "Left Knee Right (LKR)",
        'RKL': "Right Knee Left (RKL)",
        'RKR': "Right Knee Right (RKR)"
    }
    lever_states = {}
    for lever in ['LKL', 'LKR', 'RKL', 'RKR']:
        lever_states[lever] = st.sidebar.checkbox(lever_labels[lever], value=False, key=f"lever_{lever}_tab1")
        steel1.pedal_lever_objects[lever].active = lever_states[lever]

    Note.show_octave = show_octave
    notes = steel1.get_current_notes()

    chord_finder1 = ChordFinder()
    pitch_classes = [n if not show_octave else n[:-1] if n[-1].isdigit() else n for n in notes]
    chords = chord_finder1.find_chords(pitch_classes)

    st.subheader("Possible Chords")
    if chords:
        chord_string_counts = []
        for chord in chords:
            chord_note_set = set(chord['notes'])
            string_numbers = [
                10 - idx for idx, n in enumerate(notes)
                if (n if not show_octave else n[:-1] if n[-1].isdigit() else n) in chord_note_set
            ]
            chord_string_counts.append((chord, len(string_numbers), string_numbers))
        # Sort by chord type order (from CHORD_TYPES), then by number of strings (descending)
        chord_type_order = list(CHORD_TYPES.keys())
        chord_string_counts.sort(key=lambda x: (
            chord_type_order.index(x[0]['type']) if x[0]['type'] in chord_type_order else 999,
            -x[1]
        ))
        sorted_chords = [x[0] for x in chord_string_counts]
        sorted_string_numbers = [x[2] for x in chord_string_counts]

        chord_options = [
            f"{chord['root']} {chord['type']} ({', '.join(chord['notes'])}) - {len(strings)} strings"
            for chord, _, strings in chord_string_counts
        ]
        selected_idx = st.selectbox(
            "Select a chord to highlight on the fretboard:",
            options=range(len(sorted_chords)),
            format_func=lambda i: chord_options[i],
            key="chord_select_tab1"
        )
        selected_chord = sorted_chords[selected_idx]
        chord_note_set = set(selected_chord['notes'])
        selected_string_numbers = sorted_string_numbers[selected_idx]

        st.subheader("Fretboard Diagram")
        fretboard_table = []
        in_chord_flags = []
        for i, note in enumerate(reversed(notes), 1):
            note_name = note if not show_octave else note[:-1] if note[-1].isdigit() else note
            in_chord = note_name in chord_note_set
            in_chord_flags.append(in_chord)
            fretboard_table.append({
                "String": i,
                "Note": note
            })
        fretboard_df = pd.DataFrame(fretboard_table)

        # Apply row shading for notes in chord
        def highlight_rows(row):
            if in_chord_flags[row.name]:
                return ['background-color: rgba(76, 175, 80, 0.3)'] * len(row)
            return [''] * len(row)

        styled_df = fretboard_df.style.apply(highlight_rows, axis=1)
        st.dataframe(styled_df, hide_index=True)

        string_numbers_str = ', '.join(str(s) for s in sorted(selected_string_numbers, reverse=True))
        st.write(f"**{selected_chord['root']} {selected_chord['type']}** uses strings: {string_numbers_str}")

    else:
        st.write("No chords found.")

elif mode == "Find Positions for Chord":
    st.header("Chord Finder: Find Positions for a Target Chord")

    # Initialize session state for storing search results
    if 'positions' not in st.session_state:
        st.session_state.positions = None

    roots = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    types = [
        'maj', 'min', 'dim', 'aug', 'sus2', 'sus4',
        'maj7', '7', 'min7', 'm7b5', 'dim7', '6', 'min6',
        '9', 'maj9', 'min9', '11', 'maj11', 'min11', '13', 'maj13', 'min13'
    ]
    target_root = st.sidebar.selectbox("Chord Root", roots, index=roots.index('E'), key="target_root")
    target_type = st.sidebar.selectbox("Chord Type", types, index=types.index('maj'), key="target_type")

    min_strings = st.sidebar.slider("Minimum strings to use", 3, 10, 3, key="min_strings")

    # Optional fret input
    use_fret_filter = st.sidebar.checkbox("Filter by fret", value=False, key="use_fret_filter")
    target_fret = None
    if use_fret_filter:
        target_fret = st.sidebar.number_input("Fret to search", min_value=0, max_value=24, value=0, key="target_fret")

    # Results display options
    show_all_results = st.sidebar.checkbox("Show all results", value=False, key="show_all_results")
    max_results = 10
    if not show_all_results:
        max_results = st.sidebar.slider("Max results to show", 1, 20, 10, key="max_results")

    show_octave2 = st.sidebar.checkbox("Show Octave Numbers", value=True, key="octave_tab2")
    Note.show_octave = show_octave2

    if st.button("Find Positions", key="find_positions_btn"):
        with st.spinner("Searching for positions..."):
            positions = find_chord_positions(target_root, target_type, min_strings=min_strings)

            # Filter by fret if specified
            if use_fret_filter and target_fret is not None:
                positions = [pos for pos in positions if pos['fret'] == target_fret]

            st.session_state.positions = positions

    # Display results if they exist in the session state
    if st.session_state.positions:
        positions = st.session_state.positions
        results_to_show = positions if show_all_results else positions[:max_results]

        # Create dropdown options
        dropdown_options = []
        for i, pos in enumerate(results_to_show, 1):
            pedal_str = '+'.join(pos['pedals']) if pos['pedals'] else 'none'
            knee_str = '+'.join(pos['knees']) if pos['knees'] else 'none'
            strings_str = ', '.join(str(s) for s in pos['strings'])
            dropdown_options.append(
                f"{i}. Fret {pos['fret']} | Pedals: {pedal_str} | Knees: {knee_str} | Strings: {strings_str} ({len(pos['strings'])} strings)"
            )

        # Display dropdown
        selected_idx = st.selectbox(
            f"Select a position to view ({len(results_to_show)} of {len(positions)} found):",
            options=range(len(results_to_show)),
            format_func=lambda i: dropdown_options[i],
            key="position_select"
        )

        # Display selected position
        pos = results_to_show[selected_idx]
        steel2 = PedalSteel()
        steel2.set_fret(pos['fret'])
        for p in steel2.pedal_lever_objects:
            steel2.pedal_lever_objects[p].active = False
        for p in pos['pedals']:
            steel2.pedal_lever_objects[p].active = True
        for k in pos['knees']:
            steel2.pedal_lever_objects[k].active = True
        notes2 = steel2.get_current_notes()

        pedal_str = '+'.join(pos['pedals']) if pos['pedals'] else 'none'
        knee_str = '+'.join(pos['knees']) if pos['knees'] else 'none'
        strings_str = ', '.join(str(s) for s in pos['strings'])
        notes_str = ', '.join([notes2[10-s] for s in pos['strings']])

        st.subheader("Selected Position Details")
        st.markdown(
            f"**Fret:** {pos['fret']} &nbsp;&nbsp; "
            f"**Pedals:** {pedal_str} &nbsp;&nbsp; "
            f"**Knees:** {knee_str}  \n"
            f"**Strings:** {strings_str}  \n"
            f"**Notes:** {notes_str}"
        )

        st.subheader("Fretboard Diagram")
        fretboard_table = []
        in_chord_flags = []
        # Iterate from string 1 to 10 to match the other diagram
        for i, note in enumerate(reversed(notes2), 1):
            is_in_chord = i in pos['strings']
            in_chord_flags.append(is_in_chord)
            fretboard_table.append({
                "String": i,
                "Note": note
            })
        fretboard_df = pd.DataFrame(fretboard_table)

        # Apply row shading for notes in chord
        def highlight_rows(row):
            if in_chord_flags[row.name]:
                return ['background-color: rgba(76, 175, 80, 0.3)'] * len(row)
            return [''] * len(row)

        styled_df = fretboard_df.style.apply(highlight_rows, axis=1)
        st.dataframe(styled_df, hide_index=True)

    # Handle case where a search was performed but no results were found
    elif st.session_state.positions is not None:
        st.warning("No positions found. Please adjust your criteria and search again.")

st.markdown("---")
st.caption("Pedal Steel Chord Finder • Powered by Streamlit")
