class GCode(object):
  def comment(self):
    return ""

  def __str__(self) -> str:
    return f"{self.code()}{self.comment()}"

class G0(GCode):
  def __init__(self, x=None, y=None, z=None) -> None:
    if (x is None and y is None and z is None):
      raise TypeError("G0 needs at least one axis")
    self.x = x
    self.y = y
    self.z = z

  def coordinate(self):
    result = []
    if self.x is not None:
      result.append(f"X{self.x}")
    if self.y is not None:
      result.append(f"Y{self.y:.4f}")
    if self.z is not None:
      result.append(f"Z{self.z}")
    return result

  def code(self):
    return f"G0 {' '.join(self.coordinate())}"

class G1(GCode):
  def __init__(self, x=None, y=None, z=None, feedrate=None) -> None:
    if (x is None and y is None and z is None and feedrate is None):
      raise TypeError("G1 needs at least one axis, or a feedrate")
    self.x = x
    self.y = y
    self.z = z
    self.feedrate = feedrate

  def coordinate(self):
    result = []
    if self.x is not None:
      result.append(f"X{self.x}")
    if self.y is not None:
      result.append(f"Y{self.y:.4f}")
    if self.z is not None:
      result.append(f"Z{self.z}")
    return result

  def comment(self):
    return f"; Set feedrate to {self.feedrate} mm/min" if self.feedrate else ""

  def code(self):
    attributes = self.coordinate()
    if self.feedrate:
      attributes.append(f"F{self.feedrate}")
    return f"G1 {' '.join(attributes)}"

class G4(GCode):
  def __init__(self, duration) -> None:
    self.duration = duration

  def comment(self):
    return f"; Wait for {self.duration} seconds"

  def code(self):
    return f"G4 P{self.duration}"


class G21(GCode):
  def comment(self):
    return f"; mm-mode"

  def code(self):
    return f"G21"


class G54(GCode):
  def comment(self):
    return f"; Work Coordinates"

  def code(self):
    return f"G54"


class G90(GCode):
  def comment(self):
    return f"; Absolute Positioning"

  def code(self):
    return f"G90"

class G91(GCode):
  def comment(self):
    return f"; Relative Positioning"

  def code(self):
    return f"G91"


class M3(GCode):
  def __init__(self, spindle_speed) -> None:
    self.spindle_speed = spindle_speed

  def comment(self):
    return f"; Spindle on to {self.spindle_speed} RPM"

  def code(self):
    return f"M3 S{self.spindle_speed}"


class M5(GCode):
  def comment(self):
    return f"; Stop spindle"

  def code(self):
    return f"M5 S0"
