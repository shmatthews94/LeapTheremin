from audio import *
from pyo import *
import numpy as np
import threading
import Leap, sys, thread, time
from Leap import CircleGesture
globfreq = 440
globvol = .5
globfeedback = .25
pentatonic = False
globrighty = 0
globrightx = 0
globlefty = 0
globleftx = 0
supersaw = False

def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n

def pentatonic_scale(palm_y):
	if(palm_y < 25):
		return 27.50*4
	if(palm_y >= 25 and palm_y < 50):
		return 32.7*4
	if(palm_y >= 50 and palm_y < 75):
		return 36.71*4
	if(palm_y >= 75 and palm_y < 100):
		return 41.20*4
	if(palm_y >= 100 and palm_y < 125):
		return 49.00*4
	if(palm_y >= 125 and palm_y < 150):
		return 55.00*4
	if(palm_y >= 150 and palm_y < 175):
		return 65.41*4
	if(palm_y >= 175 and palm_y < 200):
		return 73.42*4
	if(palm_y >= 200 and palm_y < 225):
		return 82.41*4
	if(palm_y >= 225 and palm_y < 250):
		return 98.00*4
	if(palm_y >= 250 and palm_y < 275):
		return 110.0*4
	if(palm_y >= 275 and palm_y < 300):
		return 130.81*4
	if(palm_y >= 300 and palm_y < 325):
		return 130.81*4
	if(palm_y >= 325 and palm_y < 350):
		return 146.83*4
	if(palm_y >= 350 and palm_y < 375):
		return 164.81*4
	if(palm_y >= 375):
		return 98.00*8

def update_leap(controller, stream):
	global globfreq
	global globvol
	global globfeedback
	global globrighty
	global globlefty
	global globrightx
	global globleftx
	global pentatonic
	global supersaw
	threading.Timer(.01, update_leap, [controller, stream]).start()
	frame = controller.frame()
	for hand in frame.hands:
		handType = "Left hand" if hand.is_left else "Right hand"
		if handType == 'Right hand':
			globrighty = hand.palm_position.y
			globrightx = hand.palm_position.x
			if(pentatonic):
				globfreq = pentatonic_scale(hand.palm_position.y)
			else:
				globfreq = globrighty
		if handType == 'Left hand':
			globlefty = hand.palm_position.y
			globleftx = hand.palm_position.x
			globvol = hand.palm_position.y/350
			globfeedback = (hand.palm_position.x+120)/120
			globfeedback = clamp(globfeedback, 0.0, 0.8)
    	if globrighty > 300 and globlefty > 300:
    		pentatonic = not pentatonic
    		time.sleep(.1)
    	if globrightx > 175 and globleftx < -175:
    		supersaw = not supersaw
    		time.sleep(.1)

def main():
	global pentatonic
	global supersaw
	pentatonic = False
	supersaw = False
	p, stream = get_stream()
	controller = Leap.Controller()
	controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
	frame = controller.frame()
	update_leap(controller, stream)
	s = Server().boot()
	s.start()
	src = BrownNoise(.1).mix(2).out()
	a = Sine(freq=440, mul=0.1).out()
	saw = SuperSaw(freq=[49,50], detune=a, bal=0.7, mul=0.2).out()
	testvolume = .5

	while True:
		try:
			if(supersaw):
				a.setMul(0)
				saw.setFreq(globfreq)
				saw.setMul(globvol)
				flg = Delay(src, delay=a, feedback=globfeedback).out()
				time.sleep(.01)
			else:
				saw.setMul(0)
				a.setFreq(globfreq)
				a.setMul(globvol)
				flg = Delay(src, delay=a, feedback=globfeedback).out()
				time.sleep(.01)
		except KeyboardInterrupt:
			finish(p, stream)
			break
			exit(0)

if __name__ == '__main__':
	main()