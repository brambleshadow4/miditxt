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


Notes, markings, strings, hex
------------------------------

	### Notes

		Notes are written as their corresponding letter, optionally followed by a '#' or 'b' if the note is sharp or flat, followed by the octave (ranging from -1..9) written as a typical number would be. 

		E.g. C4 Bb5 F#3

	### Markings

	Markings are used to indicate when an event occurs

	@mm.bb.ss(offset)
		mm - measure number
		bb - beat of measure 
		ss - sixteenth of measure
		offset - extra 

	Example: 1.1.1 refers to the start of the track

	Notes require a double marking; one for when the note begins and another for when the note ends
	
	@mm.bb.ss(offset):mm.bb.ss(offset)

	### Strings

	Strings are sequences of characters between two quotes "". Line breaks (\n), quotes (\") and backslashes (\\) should be escaped as written previously

	### Hexes

		0x followed by the data in hexadecimal
	

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
	KeySig <note> <major|minor>
	TimeSig <1..15> <pow of 2> <marking>
	Sequence <0..127>
	Name <string>
	Text <string>
	Instrument <string>
	Copyright <string>
	Lyric <string>
	Cue <string>
	Marker <string>
	SMTPEOffset <0..127>h<0..127>m<0..127>s(<0..127>.<00..99>)
	
	SYSEX <hex> <timestamp>
	SYSEX_ESC <hex> <timestamp>
	SYSEX_META <hex> <timestamp>

