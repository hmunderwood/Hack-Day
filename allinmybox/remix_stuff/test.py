"""Reverse a song by playing its beats forward starting from the end of the song"""
import echonest.audio as audio

# Easy wrapper around mp3 decoding and Echo Nest analysis
audio_file = audio.LocalAudioFile("Haiti.mp3")

# You can manipulate the beats in a song as a native python list
beats = audio_file.analysis.beats
beats.reverse()

# And render the list as a new audio file!
audio.getpieces(audio_file, beats).encode("Haiti_modded.mp3")