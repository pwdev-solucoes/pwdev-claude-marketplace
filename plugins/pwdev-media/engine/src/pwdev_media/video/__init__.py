"""Talking-video pipeline shared by the pwdev video plugins (HyperFrames and Remotion).

transcribe → phrases/takes → edl → cut by the waveform → render cut.mp4 → check → gate → captions.
Every timing comes from the real audio; nothing is estimated.
"""
