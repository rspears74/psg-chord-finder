# Pedal Steel Guitar Simulator

A web-based tool for exploring pedal steel guitar chord positions and discovering chord voicings using Streamlit.

## Features

- **Chords at Position**: Find all possible chords at a specific fret position with various pedal and knee lever combinations
- **Chord Position Finder**: Search for fret positions that produce a specific chord (e.g., E major, G minor7)
- Interactive fretboard visualization with highlighted chord notes
- Configurable pedal steel setup with standard E9 tuning
- Support for pedals (A, B, C) and knee levers (LKL, LKR, RKL, RKR)

## Installation

### Using Docker

```bash
docker-compose up
```

The app will be available at `http://localhost:8501`

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run app.py
```

## Usage

### Chords at Position Mode

1. Select a fret position using the slider
2. Activate desired pedals and knee levers
3. View all possible chords available at that position
4. Select a chord to see which strings to play

### Find Positions for Chord Mode

1. Choose a chord root and type
2. Set minimum number of strings to use
3. Optionally filter by specific fret
4. Click "Find Positions" to search
5. Browse through results and view detailed fingering diagrams

## Default Tuning

Standard E9 pedal steel tuning (strings 1-10):
- String 1: F#5
- String 2: D#5
- String 3: G#4
- String 4: E4
- String 5: B3
- String 6: G#3
- String 7: F#3
- String 8: E3
- String 9: D3
- String 10: B2

## License

MIT
