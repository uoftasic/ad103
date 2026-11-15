"""The operating point: 1.8 V supply, 100 kΩ resistor, diode to ground."""
import schemdraw.elements as elm

from circuit_style import drawing, save

d = drawing()
src = d.add(elm.SourceV().up().label("1.8 V"))
d.add(elm.Resistor().right().label("100 kΩ"))
d.add(elm.Dot().label("$v_\\mathrm{node}$", loc="top", ofst=0.15))
d.add(elm.Diode().down())
d.add(elm.Line().left().tox(src.start))
d.add(elm.Ground().at(src.start))
print(save(d, "ad103-operating-point-circuit"))
