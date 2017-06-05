Overall structure
==============================
	MIDI TXT
	Head
		Format 0 | Format 1 | Format 2
		n tracks | 1 track
		Division <int> | Division <int> <int>fps
	Track
		<events>
	EndTrack <marking>
	Track
		<events>
	EndTrack <marking>
	...


Smaller structures
------------------------------

### Notes ###

Notes are written as their corresponding letter, optionally followed by a '#' or 'b' if the note is sharp or flat, followed by the octave (ranging from -1..9) written as a typical number would be. 

	C4 Bb5 F#3

### Markings ###

Markings are used to indicate when an event occurs

	@mm.bb.ss
	@mm.bb.ss(offset)

mm - measure number

bb - beat of measure 

ss - sixteenth of measure

offset - extra division ticks not divisible by a sixteenth note

The first measure, beats and sixteenth are 1 indexed, thus 1.1.1 refers to the start of the track. Offset, however, is zero indexed, so 1.1.1 is equivalent to 1.1.1(0)

The Note event require a double marking; a marking for when the note begins and another for when the note ends

	@mm.bb.ss(offset):mm.bb.ss(offset)

### Strings ###

Strings are sequences of characters between two quotes "". Line breaks (\n), quotes (\") and backslashes (\\) should be escaped as written previously

	"Copyright (C) 2017"

### Hexes ###

0x followed by the data in hexadecimal
	
	0x1589A188B8
	

Events
------------------------------

	Channel <0..15>

	Note <note> <0..127> <marking> | Note <note> <0..127> <0..127> <marking>
	Program <0..127> <marking>
	Controller <0..127> <0..127> <marking>
	KeyPressure <note> <0..127> <marking>
	ChPressure <0..127> <marking>
	Bend <-8192..8191> <marking>

	MetaChannel <0..15> <marking>
	EndTrack <marking>
	KeySig <note> <major|minor> <marking>
	TimeSig <1..15> <pow of 2> <marking>
	Sequence <0..127> <marking>
	Name <string> <marking>
	Text <string> <marking>
	Instrument <string> <marking>
	Copyright <string> <marking>
	Lyric <string> <marking>
	Cue <string> <marking>
	Marker <string> <marking>
	SMTPEOffset <0..127>h<0..127>m<0..127>s(<0..127>.<00..99>) <marking>

	SYSEX <hex> <marking>
	SYSEX_ESC <hex> <marking>
	SYSEX_META <hex> <marking>

