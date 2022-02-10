from decimal import Decimal
from g_codes import *

BIT_DIAMETER = Decimal('3') # mm
DEFAULT_FEED_RATE = 1000 # mm / min

MAX_FEED_RATE = 1720 # mm / min

STEPOVER = 40 # %

LENGTH_X = Decimal('261') # mm
LENGTH_Y = Decimal('90.0') # mm
MAX_Z = 5 # mm

DEPTH_PER_PASS = Decimal('0.2') # mm
TOTAL_DEPTH = Decimal('0.2') # mm

SPINDLE_SPEED = 8000 # RPM
SPINDLE_MAX_SPEED = 9460 # RPM, how fast your machine's spindle can spin. $

def decimal_range(start, stop, step):
  # Like range(), but for Decimals
  start = Decimal(start)
  step = Decimal(step)
  while start < stop:
    yield start
    start += step
  yield stop

def preamble_comment(bit_diameter, stepover, feedrate, x_len, y_len, cut_depth):
  return f"""; Surfacing / Flattening Operation
; Endmill Diameter: {bit_diameter}mm
; Stepover: {stepover}%, Feedrate: {feedrate}mm/min
; X: {x_len}, Y: {y_len}, Z: {cut_depth}
"""

def preamble(spindle_speed, max_z, feedrate):
  return [
    G54(),
    G21(),
    G90(),
    M3(spindle_speed),
    G4(1.8), # Wait for spindle to come up to speed
    G0(z=max_z),
    G0(x=0, y=0),
    G1(feedrate=feedrate),
  ]

def zig_zag_xy(x_len, y_len, bit_diameter, stepover, z, max_z):
  bit_radius = bit_diameter / 2

  init_x = bit_radius
  init_y = bit_radius

  max_x = x_len - bit_radius
  max_y = y_len - bit_radius

  result = [
    G0(x=init_x, y=init_y, z=max_z),
    G1(x=init_x, y=init_y, z=z),
  ]

  y_increment = bit_diameter * (Decimal(stepover) / 100)

  for i, y in enumerate(decimal_range(init_y, max_y, y_increment)):
    result.extend([
      G1(y=y),
      G1(x=max_x if i % 2 == 1 else init_x, y=y, z=z),
      G1(x=max_x if i % 2 == 0 else init_x, y=y, z=z),
    ])

  return result

def framing_pass(x_len, y_len, bit_diameter, z, max_z):
  bit_radius = bit_diameter / 2

  init_x = bit_radius
  init_y = bit_radius

  max_x = x_len - bit_radius
  max_y = y_len - bit_radius

  return [
    G0(x=init_x, y=init_y, z=max_z),
    G1(z=z),
    G1(x=init_x, y=max_y, z=z),
    G0(z=max_z),
    G0(x=max_x, y=max_y),
    G1(z=z),
    G1(x=max_x, y=init_y, z=z),
  ]

def main():
  # TODO: Pull this all out into argparse parameters.
  bit_diameter = BIT_DIAMETER
  stepover = STEPOVER
  feedrate = min(DEFAULT_FEED_RATE, MAX_FEED_RATE)
  x_len = LENGTH_X
  y_len = LENGTH_Y
  cut_depth_per_pass = DEPTH_PER_PASS
  total_cut_depth = TOTAL_DEPTH
  max_z = MAX_Z
  spindle_speed = min(SPINDLE_SPEED, SPINDLE_MAX_SPEED)

  result = preamble(spindle_speed, max_z, feedrate)

  for i, z in enumerate(decimal_range(cut_depth_per_pass, total_cut_depth, cut_depth_per_pass)):
    result.append("")
    result.append(f"; Pass {i + 1}")
    result.extend(zig_zag_xy(x_len, y_len, bit_diameter, stepover, -z, max_z))
    result.append(G0(z=max_z))
    result.append("")
    result.append(f"; Framing pass {i + 1}")
    result.extend(framing_pass(x_len, y_len, bit_diameter, -z, max_z))

  result.append("")
  result.append(f"; Finish steps")
  result.extend([
    G0(z=max_z),
    G0(x=0, y=0),
    M5(),
  ])

  with open('result.nc', 'w') as fout:
    fout.write(preamble_comment(bit_diameter, stepover, feedrate, x_len, y_len, total_cut_depth))
    fout.write("\n".join([str(command) for command in result]))
    fout.write("\n")

if __name__ == '__main__':
  main()
