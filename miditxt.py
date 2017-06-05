#
#  Copyright (C) 2017 brambleshadow4
#

import sys

def toMidi():
	pass 


def toTxt():
	txtname = filename
	txtname = txtname.replace(".mid",".txt")
	if txtname == filename:
		txtname += ".txt"
	f = open(filename,"rb")
	g = open(txtname,"w")

	#HEAD
	f.read(4) #MThd
	g.write("MIDI TXT\nHead\n")

	headLength = int.from_bytes(f.read(4),byteorder='big')

	if headLength < 6:
		raise Exception('MIDIFile: Head < 6 bytes')

	midiFileformat = int.from_bytes(f.read(2),byteorder='big')
	g.write("\tFormat "+ str(midiFileformat) + "\n")
	
	midiFiletracks = int.from_bytes(f.read(2),byteorder='big')
	if midiFiletracks > 1:
		g.write("\t" + str(midiFiletracks) + " tracks\n")
	else:
		g.write("\t1 track\n")

	divisionA = int.from_bytes(f.read(1),byteorder='big')
	divisionB = int.from_bytes(f.read(1),byteorder='big')
	if divisionA > 127:
		divisionA = 256 - divisionA
		g.write("\tDivision " + str(divisionB) + " " + str(divisionA) + "fps\n")
	else:
		divisionA = (divisionA << 8) + divisionB
		divisionB = -1
		g.write("\tDivision " + str(divisionA) + "\n")

	f.read(headLength-6)

	#Tracks
	meterMarkings = [(0,1,divisionA*4,divisionA)]
	meterMarkingRef = 0
	for i in range(midiFiletracks):
		print("Writing track " + str(i))
		dtTotal = 0
		events = []
		# (dt, measure no, measure len, beat len)
		
		prevStatus = (0, -1)
		metaCh = 0

		if f.read(4) != b"MTrk":
			raise Exception("MIDIFile: track missing MTrk header")
		
		trkLen = int.from_bytes(f.read(4),byteorder='big')

		def readVInt(f):
			sum1 = 0
			nonlocal trkLen
			while True:
				piece = int.from_bytes(f.read(1),byteorder='big')
				sum1 = (sum1 << 7) + (piece & 0x7F)
				trkLen -=1 
				if piece < 128:
					break
			#print(sum1)
			return sum1

		def m(dT):
			nonlocal meterMarkingRef
			
			while meterMarkingRef < len(meterMarkings)-1:
				dtf, _, _, _ = meterMarkings[meterMarkingRef+1]
				if dtf <= dT:
					meterMarkingRef += 1
				else:
					break
			while meterMarkingRef > 0:
				dtp, _, _, _ = meterMarkings[meterMarkingRef]
				if dT < dtp:
					meterMarkingRef -= 1
				else:
					break
			dt2, m, mlen, blen = meterMarkings[meterMarkingRef]

			#p = str(dT) + " @ Measure " + str(dt2) + " = "

			m += (dT-dt2)//mlen
			dT = (dT-dt2) % mlen 
			b = dT//blen
			dT -= b*blen
			b += 1
			sixteenth = dT//(divisionA/4)
			dT -= sixteenth*divisionA/4
			sixteenth += 1
			if dT == 0:
				dT = ""
			else:
				dT = "(" + str(int(dT)) + ")"
			#print(p + str(int(m)) + "." + str(int(b)) + "." + str(int(sixteenth)) + dT)
			return  str(int(m)) + "." + str(int(b)) + "." + str(int(sixteenth)) + dT

		def noteName(n):
			octave = n//12 -1
			note = ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"][n % 12]
			return note + str(octave)

		def metaTxt(txtLen):
			txt = f.read(txtLen).decode('utf-8')
			nonlocal trkLen
			trkLen -= txtLen 
			txt = txt.replace("\\","\\\\")
			txt = txt.replace("\n","\\n")
			txt = txt.replace("\"","\\\"")
			return "\""+ txt + "\""

		while trkLen > 0:
			dtTotal += readVInt(f)
			ev = int.from_bytes(f.read(1),byteorder='big')
			trkLen -= 1
			print("event")
			# Meta events
			if ev == 0xFF:
				print("meta")
				ev = int.from_bytes(f.read(1),byteorder='big')
				trkLen -=1
				evLen = readVInt(f)

				if ev == 0x2F:
					events.append(("EndTrack @" + m(dtTotal),()))
				elif ev == 0x00:
					seq = int.from_bytes(f.read(evLen),byteorder='big')
					trkLen -= evLen
					events.append(("\tSequence " + str(seq) + " @" + m(dtTotal),()))
				elif ev == 0x01:
					txt = metaTxt(evLen)
					events.append(("\tText " + txt +  " @" + m(dtTotal),()))
				elif ev == 0x02:
					txt = metaTxt(evLen)
					events.append(("\tCopyright " + txt +  " @" + m(dtTotal),()))
				elif ev == 0x03:
					txt = metaTxt(evLen)
					events.append(("\tName " + txt + " @" + m(dtTotal),()))
				elif ev == 0x04:
					txt = metaTxt(evLen)
					events.append(("\tInstrument " + txt +  " @" + m(dtTotal),()))
				elif ev == 0x05:
					txt = metaTxt(evLen)
					events.append(("\tLyric " + txt +  " @" + m(dtTotal),()))
				elif ev == 0x06:
					txt = metaTxt(evLen)
					events.append(("\tMarker " + txt +  " @" + m(dtTotal),()))
				elif ev == 0x07:
					txt = metaTxt(evLen)
					events.append(("\tCue " + txt +  " @" + m(dtTotal),()))
				elif ev == 0x20:
					ch = int.from_bytes(f.read(evLen),byteorder='big')
					trkLen -= evLen
					events.append(("\tMetaChannel " + str(ch) + " @" + m(dtTotal),()))
				elif ev == 0x51:
					tempo = int.from_bytes(f.read(evLen),byteorder='big')
					trkLen -= evLen
					tempo = 60000000/tempo
					tempo = ((tempo * 100)//1)/100
					events.append(("\tTempo " + str(tempo) + " @" + m(dtTotal),()))
				elif ev == 0x54:
					hours = int.from_bytes(f.read(1),byteorder='big')
					mins = int.from_bytes(f.read(1),byteorder='big')
					secs = int.from_bytes(f.read(1),byteorder='big')
					frames = int.from_bytes(f.read(1),byteorder='big')
					hundredths = int.from_bytes(f.read(1),byteorder='big')
					trkLen -=5
					events.append(("\tSMTPEOffset " + str(hours) + "h" + str(mins) + "m" + str(secs) + "s(" + str(frames + hundredths/100) + ")",()))
				elif ev == 0x58:
					counts = int.from_bytes(f.read(1),byteorder='big')
					beat = int.from_bytes(f.read(1),byteorder='big')
					clocks = int.from_bytes(f.read(1),byteorder='big')
					thirtyTwos = int.from_bytes(f.read(1),byteorder='big')
					beat2 = 1
					while beat >0:
						beat -= 1
						beat2 *= 2
					beat = beat2
					opt = ""
					if thirtyTwos != 8 or clocks != 24:
						opt = str(clocks) + " " + str(thirtyTwos) + " "
					trkLen -= 4
					events.append(("\tTimeSig " + str(counts) + " " + str(beat) + " " + opt + "@" + m(dtTotal),()))
					if divisionB == -1:
						#nonlocal meterMarkings
						dtOld,oldM,mlen,_ = meterMarkings[meterMarkingRef]
						measure = (dtTotal - dtOld)//mlen+oldM
						if ((dtTotal - dtOld)/mlen) % 1:
							measure += 1
						meterMarkings.append((dtTotal, measure, counts*divisionA*4/beat, divisionA*4/beat))
						print(meterMarkings)

				elif ev == 0x59:
					sharps = int.from_bytes(f.read(1),byteorder='big',signed=True)
					scaleType = int.from_bytes(f.read(1),byteorder='big')
					k = {"-70": "Cb major", "-60": "Gb major", "-50": "Db major", "-40": "Ab major", "-30": "Eb major", "-20": "Bb major", "-10": "F major", "00": "C major", "10": "G major", "20": "D major", "30": "A major", "40": "E major", "50": "B major", "60": "F# major", "70": "C# major","-71": "Gb minor", "-61": "minor", "-51": "minor", "-41": "minor", "-31": "minor", "-21": "minor", "-11": "minor", "01": "A minor", "11": "E minor", "21": "B minor", "31": "F# minor", "41": "C# minor", "51": "G# minor", "61": "D# minor", "71": "A# minor"}[str(sharps) + str(scaleType)]
					events.append(("\tKeySig " + k + " @" + m(dtTotal),()))
				elif ev == 0x7F:
					msgHex = "0x" + codecs.encode(f.read(evLen),"hex").decode("utf-8")
					trkLen -= evLen
					events.append(("\tSYSEX_META " + msgHex + " @" + m(dtTotal),()))
				else:
					events.append(("\tUnknown MetaEvent " + hex(ev),()))
					trkLen -= evLen
					f.read(evLen)
				
			elif ev == 0xF0 or ev == 0xF7:
				print("sysex")
				msgLength = readVInt(f)
				msgHex = "0x" + codecs.encode(f.read(msgLength),"hex").decode("utf-8")
				if ev == 0xF0:
					events.append("\tSYSEX " + msgHex + " @" + m(dtTotal))
				else:
					events.append("\tSYSEX_ESC " + msgHex + " @" + m(dtTotal))
			# Normal Events
			else:
				fstByte = ev
				chan = 0

				if ev < 128:
					ev, chan = prevStatus
				else:
					fstByte = int.from_bytes(f.read(1),byteorder='big')
					trkLen -= 1
					chan = ev & 0x0F
					ev = ev & 0xF0

				pev, pchan = prevStatus
				if pchan != chan:
					events.append(("\tChannel "+str(chan),()))
				
				if ev == 0x80:
					trkLen -= 1
					note = noteName(fstByte)
					value = int.from_bytes(f.read(1),byteorder='big')
					events.append(("",("off",note, value, m(dtTotal))))
					
				elif ev == 0x90:
					trkLen -= 1
					note = noteName(fstByte)
					vel = int.from_bytes(f.read(1),byteorder='big')
					if vel == 0:
						events.append(("",("off",note, 64, m(dtTotal))))
						
					else:
						
						events.append(("",("on",note, vel, m(dtTotal))))

				elif ev == 0xA0:
					trkLen -= 1
					key = noteName(fstByte)
					press = str(int.from_bytes(f.read(1),byteorder='big'))
					events.append(("\tKeyPressure " + note + " " + press + " @" + m(dtTotal),()))

				elif ev == 0xB0:
					trkLen -= 1
					ctrl = str(fstByte)
					val = str(int.from_bytes(f.read(1),byteorder='big'))
					events.append(("\tController " + ctrl + " " + val + " @" + m(dtTotal),()))

				elif ev == 0xC0:
					prg = str(fstByte)
					events.append(("\tProgram " + prg + " @" + m(dtTotal),()))

				elif ev == 0xD0:
					press = str(fstByte)
					events.append(("\tChPressure " + press + " @" + m(dtTotal),()))

				elif ev == 0xE0:
					trkLen -= 1
					a = str(fstByte)
					b = str(int.from_bytes(f.read(1),byteorder='big'))
					mod = (a<<7)+b - 8192
					events.append(("\tBend " + mod + " @" + m(dtTotal),()))

				prevStatus = (ev, chan)
				
			# "asd".encode('utf-8')
			# b"asd".decode('utf-8')
			#codecs.encode(bytes,"hex")
		
		noteEvents = []
		for i in range(0,len(events)):
			#print(events[i])
			_, tup = events[i]
			if len(tup):
				noteEvents.append(i)

		i = 0
		while i < len(noteEvents):
			_, (t, note, val, dt) = events[noteEvents[i]]
			if t == 'off':
				at = i
				_, (a, b, c, d) = events[noteEvents[i]]
				while i >= 0 and (a == "off" or b != note):
					i -= 1
					_, (a, b, c, d) = events[noteEvents[i]]
				if i != -1:
					_, (t2, note, strike, start) = events[noteEvents[i]] 
					if val == 64 or val == 0:
						val = ""
					else:
						val = str(val) + " "
					events[noteEvents[i]] = ("\tNote " + note + " " + str(strike) + " " + val + "@" + start + ":" + dt),("off",note,strike,start)
				i = at
			i += 1
		
		g.write("Track\n")

		#print(events)
		for (s,_) in events:
			if s != "":
				g.write(s+"\n")
		

	f.close()
	g.close()


filename = ""
if len(sys.argv) > 1:
	filename = sys.argv[1]
else:
	filename = input("Filename: ")

try:
	f = open(filename,"rb")
	fType = f.read(8)

	if fType == b"MIDI TXT":
		f.close()
		print("Converting to .midi")
		toMidi()
	elif fType[0:4] == b"MThd":
		f.close()
		print ("Converting to .txt")
		toTxt()
	else:
		print ("This isn't a MIDI file or a .txt file in MIDI TXT format")
except OSError: 
	print("Unable to open " + filename)




'''function toTXT()
{
	var txt = "MIDI TXT\n";

	txt += "Head\n";
	txt += "\tFormat " + MIDIFile.format + "\n";
	txt += "\t" + MIDIFile.tracks + " tracks\n";
	txt += "\tDivision " + MIDIFile.division + "\n";

	var doMeasures =(MIDIFile.fps == undefined? true: false);

	
	for(var j =0; j < MIDIFile.tracks; j++)
	{
		track = MIDIFile["rk"+j];
		for(var i = 1; i < track.length; i++)
		{
			track[i].delay = track[i].delay + track[i-1].delay; 
		}
	}

	var track = MIDIFile.rk0; 
	var timeSigs = [{deltaTime: 0, measure: 1, counts: 4, sub: 4, sixteenth: MIDIFile.division/4}];

	if(doMeasures)
	{
		for(var i =0; i < track.length; i++)
		{
			if(track[i].type== "time_sig")
			{
				var newSig = {};
				var oldSig = timeSigs[timeSigs.length-1]

				newSig.counts = track[i].data.counts;
				newSig.sub =  16/Math.pow(2,track[i].data.beatnote);
				newSig.deltaTime = track[i].delay;
				newSig.sixteenth = Number(MIDIFile.division)/4;
				newSig.measure = timeSigs[timeSigs.length-1].measure + (newSig.deltaTime - oldSig.deltaTime)/oldSig.counts/oldSig.sub/oldSig.sixteenth;

				timeSigs.push(newSig);		
			}
		}

		function toMeasure(dTime)
		{
			var i = 0;
			while(i+1 < timeSigs.length && timeSigs[i+1].deltaTime < dTime)
				i++;
			
			var measure = timeSigs[i].measure;
			dTime = dTime - timeSigs[i].deltaTime;
			
			measure += Math.floor(dTime/timeSigs[i].counts/timeSigs[i].sub/timeSigs[i].sixteenth);
			dTime = dTime % (timeSigs[i].counts*timeSigs[i].sub*timeSigs[i].sixteenth);

			var count = 1 + Math.floor(dTime/timeSigs[i].sub/timeSigs[i].sixteenth);
			dTime = dTime % (timeSigs[i].sub*timeSigs[i].sixteenth);

			var sub = 1;
			if(timeSigs[i].sub >= 1)
			{
				sub =  1 + Math.floor(dTime/timeSigs[i].sixteenth);
				dTime = dTime % timeSigs[i].sixteenth;

			}

			return measure +"." + count + "." + sub + (dTime == 0? "": "("+dTime+")"); 
		}
		console.log(timeSigs);


		for(var j = 0; j < MIDIFile.tracks; j++)
		{
			track = MIDIFile["rk"+j];
			for(var i =0; i < track.length; i++)
			{
				track[i].delay = toMeasure(track[i].delay);
			}
		}
		
	}


	for(var i =0; i < MIDIFile.tracks; i++)
	{
		var notes = ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"];

		function toNote(n)
		{
			return notes[n%12] +(Math.floor(n/12)-1);
		}


		var track = MIDIFile["rk"+i];
		txt += "Track\n";
		var channel = -1;
		for(var j = 0; j < track.length; j++)
		{
			if(track[j].channel != undefined && track[j].channel != channel)
			{
				txt += "\tChannel " + track[j].channel + "\n";
				channel = track[j].channel;
			}
			
			if(track[j].type == "note_on" && track[j].data.vel != 0)
			{
				var tstamp = " @" + track[j].delay;
				var k = j+1;
				while(k < track.length)
				{
					if(track[k].channel == channel)
					{
						if(track[k].type == "note_on" && track[k].data.note == track[j].data.note && track[k].data.vel == 0)
							break;
						if(track[k].type == "note_off" && track[k].data.note == track[j].data.note)
							break;
					}
					k++;
				}

				var vel = track[j].data.vel;
				if(k < track.length)
				{
					tstamp += "::" + track[k].delay;
					if(track[k].type == "note_off" && track[k].data.vel != 64 && track[k].data.vel != 0)
						vel += " " + track[k].data.vel;
				}

				txt+="\tNote " + toNote(track[j].data.note) + " " + vel + tstamp + "\n";
			}
			else if(track[j].type == "time_sig")
			{
				txt+="\tTimeSig " + track[j].data.counts + " " + Math.pow(2,track[j].data.beatnote) 
					+ " @" +  track[j].delay + "\n";
			}
			else if(track[j].type == "key_sig")
			{
				txt+="\tKeySig " + track[j].data.key + " " + track[j].data.scale 
					+ " @" + track[j].delay + "\n";
			}
			else if(track[j].type == "tempo")
			{
				txt+="\tTempo " + track[j].data.bpm + " @" + track[j].delay + "\n";
			}
			else if(track[j].type == "channel_prefix")
				txt+="\tMetaChannel " + track[j].data + " @" + track[j].delay + "\n";
			else if(track[j].type == "track_name")
				txt+="\tName \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if(track[j].type == "instrument_name")
				txt+="\tInstrument \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if(track[j].type == "seq_num")
				txt+="\tSequence \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if(track[j].type == "text")
				txt+="\tText \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if(track[j].type == "copyright")
				txt+="\tCopyright \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if(track[j].type == "lyric")
				txt+="\tLyric \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if(track[j].type == "cue")
				txt+="\tCue \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if(track[j].type == "marker")
				txt+="\tMarker \"" + track[j].data + "\" @" +track[j].delay + "\n";
			else if (track[j].type == "sysex")
				txt+="\tSYSEX " + track[j].data + " @" +track[j].delay + "\n";
			else if (track[j].type == "sysex_esc")
				txt+="\tSYSEX_ESC " + track[j].data + " @" +track[j].delay + "\n";
			
			else if(track[j].type == "key_pressure")
				txt+="\tKeyPressure " + toNote(track[j].data.note) + " " + track[j].data.pressure + " @" +track[j].delay + "\n";
			else if(track[j].type == "controller_change")
				txt+="\tController " + track[j].data.controller + " " + track[j].data.value +" @" +track[j].delay + "\n";
			else if(track[j].type == "program_change")
				txt+="\tProgram " + track[j].data + " @" + track[j].delay + "\n";
			else if(track[j].type == "channel_pressure")
				txt+="\tChPressure " + track[j].data + " @" + track[j].delay + "\n";
			else if(track[j].type == "pitch_bend")
			{
				var bend = track[j].data.lsb + (track[j].data.msb<<7) - 8192;
				txt+="\tBend " + bend + " @" + track[j].delay + "\n";
			}
			else if(track[j].type == "end_of_track")
			{
				txt+="EndTrack @" + track[j].delay + "\n";
			}
			else if (track[j].type == "note_off" || track[j].type == "note_on"){}
			else
			{
				txt+="\tUNKNOWN " + track[j].type + "\n";
			}
		}
	}

	document.getElementById('MIDI TXT').innerHTML = txt;
}'''

'''function compileTXT(input)
{
	input = input.split(/\r\n|\n/g);

	for(var i=0; i < input.length; i++)
	{
		input[i] = input[i].replace(/\s+/," ");
		input[i] = input[i].trim();
		input[i] = input[i].split(" ");
	}

	var head = {};

	if(input.length < 5)
		throw new Error("Head requires 5 lines");

	if(input[0][0] != "MIDI" && input[0][1] != "TXT")
		throw new Error("File must begin with MIDI TXT");
	
	if(input[1][0] != "Head")
		throw new Error("Head must begin on second line");
	
	if(input[2][0] != "Format")
		throw new Error("Format must be in Head");
	if(input[2][1] != "1")
		throw new Error("Only format 1 midi files are currently supported");

	head.format = Number(input[2][1]);

	if(input[3][1] != "tracks" && input[3][1] != "track")
		throw new Error("track count must be in head");
	
	head.tracks = Number(input[3][0])

	if(input[4][0] != "Division")
		throw new Error("Division must be in head");

	head.division = Number(input[4][1]);

	if(head.tracks < 1)
		throw new Error("MIDI files must have at least 1 track");

	var i = -1;
	tracksRAW = [];
	for(var j = 5; j < input.length; j++)
	{
		if(input[j][0] == "Track")
		{
			i++;
		}
		else if (i != -1)
		{
			if(tracksRAW[i] == undefined)
				tracksRAW[i] = []; 
			tracksRAW[i].push(input[j])
		}
	}
	if(tracksRAW.length != head.tracks)
		throw new Error("Inconsistent number of tracks");
	console.log(head);

	function mapMeasure(map, s)
	{
		s = s.split(".");
		if(s[2].indexOf("(") != -1)
		{
			s.push(s[2].substring(s[2].indexOf("(")));
			s[2] = s[2].substring(0,s[2].indexOf("("));
			s[3] = s[3].replace(/\((\d+)\)/,"$1");
		}
		else
			s.push("0");
		for(i in s)
			s[i] = Number(s[i]);	

		var i=0;
		var k=map.length;
		while(k-i > 1)
		{
			var j = Math.floor((i+k)/2);
			
			if(map[j].m <= s[0])
				i = j;
			else
				k = j;
		}
		var entry = map[i];
		
		return entry.dt + (s[0]-entry.m)*entry.c1 + (s[1]-1)*entry.c2 + (s[2]-1)*entry.c3 + s[3];
	}
	
	function getMapping(trackNo)
	{
		var map = [{"m":1,"dt":0,"c1":head.division*4,"c2":head.division,"c3":head.division/4}];
		for(var i=0; i <tracksRAW[trackNo].length; i++)
		{
			if(tracksRAW[trackNo][i][0] == "TimeSig")
			{
				var timeStamp = tracksRAW[trackNo][i][3].substring(1);
				var s = timeStamp;
				s = s.split(".");
				if(s[2].indexOf("(") != -1)
				{
					s.push(s[2].substring(s[2].indexOf("(")));
					s[2] = s[2].substring(0,s[2].indexOf("("));
					s[3] = s[3].replace(/\((\d+)\)/,"$1");
				}
				else
					s.push("0");
				//if(m == timeStamp)
				//	throw new Error("TimeSig: Bad measure format");

				console.log(s[0]);
				s[0] = Number(s[0]);
				
				
				if(map[map.length-1].m >= s[0] && s[0] != 1)
					throw new Error("TimeSig: marking out of order");

				var count = Number(tracksRAW[trackNo][i][1]);
				var beat = Number(tracksRAW[trackNo][i][2]);

				if([1,2,4,8,16,32,64].indexOf(beat) == -1)
					throw new Error("TimeSig: bad beat");

				var marking = {};
				console.log(map.slice());
				console.log(timeStamp);
				marking.dt = mapMeasure(map,timeStamp);
				marking.m = (s[1] == "1" && s[2]=="1" && s[3]=="0")? s[0]:s[0]+1;
				console.log(s);

				marking.c3 = head.division/4;
				marking.c2 = head.division*4/beat;
				marking.c1 = marking.c2*count;

				if(marking.m == 1)
					map = [marking];
				else
					map.push(marking);
			}
		}
		return map;
	}

	function REMatch(regex,string)
	{
		return regex.exec(string) && string.replace(regex,"") == "";
	}

	var MeasureMappings = getMapping(0);
	console.log(MeasureMappings);	

	function checkDT(l)
	{
		if(!REMatch(/@\d+\.\d+\.\d+(\(\d+\))?/,l[l.length-1]))
			throw new Error("Invalid Timestamp");
		return mapMeasure(MeasureMappings,l[l.length-1].substring(1));
	}


	for(var i=0; i < tracksRAW.length; i++)
	{
		var track = []
		var channel = 0;
		while(tracksRAW[i].length)
		{
			var item = tracksRAW[i].shift();
			if(item[0] == "Channel")
			{
				channel = item[1]&15;
			}
			if(item[0] == "Note")
			{
				//Note <n> <on> <off> <dt>
				if(item.length != 4 && item.length != 5)
					throw new Error("Invalid Note");

				if(!REMatch(/[ABCDEFG][b#]?-?\d/,item[1]))
					throw new Error("Invalid Note");
				
				var pitchClass = item[1].replace(/([ABCDEFG][b#]?)-?\d/,"$1");
				var range = item[1].replace(/[ABCDEFG][b#]?(-?\d)/,"$1");
				var vel = Number(item[2]);
				var rel = 64;

				if(item.length == 5)
					rel = Number(item[3]);

				if(!REMatch(/@\d+\.\d+\.\d+(\(\d+\))?::\d+\.\d+\.\d+(\(\d+\))?/,item[item.length-1]))
					throw new Error("Invalid Note");
				
				var dt1 = item[item.length-1].replace(/@(\d+\.\d+\.\d+(\(\d+\))?)::\d+\.\d+\.\d+(\(\d+\))?/,"$1");
				var dt2 = item[item.length-1].replace(/@\d+\.\d+\.\d+(\(\d+\))?::(\d+\.\d+\.\d+(\(\d+\))?)/,"$2");

				dt1 = mapMeasure(MeasureMappings,dt1);
				dt2 = mapMeasure(MeasureMappings,dt2);

				g= {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11,"C#":1,"D#":3,"E#":5,"F#":6,"G#":8,"A#":10,"B#":0,"Cb":11,"Db":1,"Eb":3,"Fb":4,"Gb":6,"Ab":8,"Bb":10};
				pitchClass = g[pitchClass];
				range = Number(range)*12 + 12;

				track.push({dt:dt1,event:[0x90+channel,pitchClass+range,vel%128]});
				track.push({'dt':dt2,'f':true,'event':[0x80+channel,pitchClass+range,rel%128]});
			}
			else if(item[0] == "EndTrack")
			{
				var dt1 = checkDT(item);
				track.push({dt:dt1,event:[0xFF,0x2F,0x00]});
				break;
			}
			else if(item[0] == "TimeSig")
			{
				var dt1 = checkDT(item);
				if(!REMatch(/\d+/, item[1]))
					throw new Error("Invalid TimeSig");
				if(!REMatch(/\d+/, item[2]))
					throw new Error("Invalid TimeSig");
				var top = Number(item[1]);
				var bottom = Number(item[2]);
				if(top < 1 || top > 16)
					throw new Error("Invalid TimeSig");
					
				var powB = 0;
				while(bottom > 1)
				{
					powB++;
					bottom /=2; 
				}
				if(bottom != 1)
					throw new Error("Invalid TimeSig");

				console.log(top + " " + powB);

				track.push({dt:dt1,event:[0xFF,0x58,4,top,powB,24,8]});
				
			}
			else if(item[0] == "Tempo")
			{
				var dt1 = checkDT(item);

				if(!REMatch(/\d+\.?\d+/, item[1]))
					throw new Error("Invalid Tempo");

				var micro = Math.round(60000000/Number(item[1]));

				micro1 = micro % 256;
				micro2 = Math.floor(micro/256)%256;
				micro3 = Math.floor(micro/256/256)%256;

				track.push({dt:dt1,event:[0xFF,0x51,3,micro3,micro2,micro1]});
			}
			else if(item[0] == "Program")
			{
				var dt1 = checkDT(item);
				
				track.push({dt:dt1,event:[0xC0+channel,Number(item[1])&255]});
			}
			else if(item[0] == "KeySig")
			{
				var dt1 = checkDT(item);

				var table = {
					"c major": [0,0],
					"d major": [2,0],
					"e major": [4,0],
					"f major": [-1,0],
					"g major": [1,0],
					"a major": [3,0],
					"b major": [5,0],
					"c# major": [7,0],
					"d# major": [-3,0],
					"e# major": [-1,0],
					"f# major": [6,0],
					"g# major": [-4,0],
					"a# major": [-2,0],
					"b# major": [0,0],
					"cb major": [-7,0],
					"db major": [-5,0],
					"eb major": [-3,0],
					"fb major": [4,0],
					"gb major": [-6,0],
					"ab major": [-4,0],
					"bb major": [-2,0],

					"c minor": [-3,1],
					"d minor": [-1,1],
					"e minor": [1,1],
					"f minor": [-4,1],
					"g minor": [1,1],
					"a minor": [0,1],
					"b minor": [2,1],
					"c# minor": [4,1],
					"d# minor": [6,1],
					"e# minor": [-4,1],
					"f# minor": [3,1],
					"g# minor": [5,1],
					"a# minor": [7,1],
					"b# minor": [-3,1],
					"cb minor": [2,1],
					"db minor": [4,1],
					"eb minor": [-6,1],
					"fb minor": [,1],
					"gb minor": [,1],
					"ab minor": [-7,1],
					"bb minor": [-5,1]
				}

				var key = item[1] + " " + item[2];
				key = key.toLowerCase();

				track.push({dt:dt1,event:[0xFF,0x59,2,table[key][0],table[key][1]]});
			}
			else if (item[0] == "Controller")
			{
				var dt1 = checkDT(item);
				track.push({dt:dt1,event:[0xB0+channel,Number(item[1])&255,Number(item[2])&255]});
			}
			else if (item[0] == "ChPressure")
			{
				var dt1 = checkDT(item);
				track.push({dt:dt1,event:[0xD0+channel,Number(item[1])&255]});
			}
			else if (item[0] == "Pressure")
			{
				var dt1 = checkDT(item);
				if(!REMatch(/[ABCDEFG][b#]?-?\d/,item[1]))
					throw new Error("Invalid Note");
				
				var pitchClass = item[1].replace(/([ABCDEFG][b#]?)-?\d/,"$1");
				var range = item[1].replace(/[ABCDEFG][b#]?(-?\d)/,"$1");
				g= {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11,"C#":1,"D#":3,"E#":5,"F#":6,"G#":8,"A#":10,"B#":0,"Cb":11,"Db":1,"Eb":3,"Fb":4,"Gb":6,"Ab":8,"Bb":10};
				pitchClass = g[pitchClass];
				range = Number(range)*12 + 12;

				track.push({dt:dt1,event:[0xA0+channel,(pitchClass+range)&255,Number(item[2])&255]});
			}
			else if (item[0] == "Bend")
			{
				var dt1 = checkDT(item);
				var norm = Number(item[1]) + 8192;
				var B1 = Math.floor(norm/128)&127;
				var B2 = norm&127;
				track.push({dt:dt1,event:[0xE0+channel,B1,B2]});
			}
			else if (item[0] == "")
			{
				var dt1 = checkDT(item);
				track.push({dt:dt1,event:[]});
			}
		}

		track.sort(function(a,b){
			if(a.dt - b.dt != 0)
				return a.dt - b.dt;
			else if(a.f)
				return -1;
			else if(b.f)
				return 1;
			return 0;
		});

		function toVarInt(k)
		{
			var arr = [];
			arr.unshift(k%128);
			k = Math.floor(k/128);

			while(k>0)
			{
				arr.unshift(k%128+128);
				k = Math.floor(k/128);
			}
			return arr;
		}



		for(var j=track.length-1; j>0; j--)
		{
			track[j].dt = track[j].dt - track[j-1].dt;
			track[j].dt = toVarInt(track[j].dt);
			
			//check running status maybe?
			track[j]= track[j].dt.concat(track[j].event);
		}
		track[0].dt = toVarInt(track[j].dt);
		track[0] = track[0].dt.concat(track[0].event);

		var merge = [];
		while(track.length)
		{
			var merge = merge.concat(track.shift());
		}

		var sizeInt = merge.length;
		var size = [];
		for(var j=0; j<4; j++)
		{
			size.unshift(sizeInt%256);
			sizeInt = Math.floor(sizeInt/256);
		}

		var header = [0x4D, 0x54, 0x72, 0x6B].concat(size);
		merge = header.concat(merge);
		tracksRAW[i] = merge;

	}

		//MThd <4 bytes size> <2 bytes format><2 bytes tracks> <2 bytes division>
	var head = [0x4D,0x54,0x68,0x64,0,0,0,6,
		0,head.format,
		Math.floor(head.tracks/256),head.tracks & 255,
		127 & Math.floor(head.division/256), head.division&255] ;
		
	while(tracksRAW.length)
		head = head.concat(tracksRAW.shift());

	var blob = new Blob([Uint8Array.from(head)],{type: "octet/stream"});
	var url = window.URL.createObjectURL(blob);

	var link = document.createElement('a');
	link.href = url;
	link.download = "untitled.midi";

	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
}'''
