import pigpio
from time import sleep

class Servo:

    def __init__(self, pin, pwm_range, start_pos=50, buffer=0, delta=1.5):
        self.pin = pin
        self.range = pwm_range
        self.pi = pigpio.pi()
        self.pi.set_mode(pin, pigpio.OUTPUT)
        self.start = start_pos
        self.pos = self.translate(self.start)
        self.buffer = buffer  # PWM amount to specify as acceleration / deceleration buffer
        self.delta = delta  # amount of change in acceleration / deceleration (as a multiple of current increment)

        self.move(self.start)

    def move_relative(self, percentage):
        new = self.pos + self.translate(percentage)
        if self.range[0] <= new <= self.range[0]:
            print(new)
            self.do_move(self.pos, new)
            self.pos = new
        else:
            raise ValueError('Percentage %d out of range' % percentage)

    def move(self, percentage):
        if 0 <= percentage <= 100:
            new = self.translate(percentage)
            print(new)
            self.do_move(self.pos, new)
            self.pos = new
        else:
            raise ValueError('Percentage %d out of range' % percentage)

    def do_move(self, old, new):
        current = old if self.buffer > 0 else new

        increment = 1
        decelerate = False

        safety = 1000  # quit after 1000 iterations, in case something has gone wrong

        # debug info
        position = []
        increments = []

        while current <= new and safety:
            safety = safety - 1
            self.pi.set_servo_pulsewidth(self.pin, current)
            if self.buffer > 0:
                sleep(0.1)  # @todo calculate wait time based on movement amount
            else:
                sleep(0.5)

            increments.append(increment)
            position.append(current)

            if current == new:
                print(len(increments))
                print(increments)
                print(position)
                break

            # Accelerate / Decelerate
            # @todo simplify
            if old < new:
                if increment < self.buffer and not decelerate:
                    increment = increment * self.delta if increment * self.delta < self.buffer else self.buffer
                    current = current + increment if current + increment < new else new
                elif decelerate:
                    increment = increment / self.delta if increment / self.delta > 1 else 1
                    current = current + increment if current + increment < new else new
                else:
                    current = new - self.buffer
                    decelerate = True
            else:
                if increment < self.buffer and not decelerate:
                    increment = increment * self.delta if increment * self.delta < self.buffer else self.buffer
                    current = current - increment if current - increment > new else new
                elif decelerate:
                    increment = increment / self.delta if increment / self.delta > 1 else 1
                    current = current - increment if current - increment > new else new
                else:
                    current = new + self.buffer
                    decelerate = True


    def reset(self):
        self.move(self.start)
    
    def translate(self, value):
        # Figure out how 'wide' each range is
        leftSpan = 100 - 0
        rightSpan = self.range[1] - self.range[0]

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return self.range[0] + (valueScaled * rightSpan)
