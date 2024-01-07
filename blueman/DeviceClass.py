from gettext import gettext as _
import logging

major_cls = (
    # translators: device class
    _("Miscellaneous"),
    # translators: device class
    _("Computer"),
    # translators: device class
    _("Phone"),
    # translators: device class
    _("Access point"),
    # translators: device class
    _("Audio/video"),
    # translators: device class
    _("Peripheral"),
    # translators: device class
    _("Imaging"),
    # translators: device class
    _("Wearable"),
    # translators: device class
    _("Toy"),
    # translators: device class
    _("Uncategorized")
)

computer_minor_cls = (
    # translators: device class
    _("Uncategorized"),
    # translators: device class
    _("Desktop"),
    # translators: device class
    _("Server"),
    # translators: device class
    _("Laptop"),
    # translators: device class
    _("Handheld"),
    # translators: device class
    _("Palm"),
    # translators: device class
    _("Wearable")
)

phone_minor_cls = (
    # translators: device class
    _("Uncategorized"),
    # translators: device class
    _("Cellular"),
    # translators: device class
    _("Cordless"),
    # translators: device class
    _("Smartphone"),
    # translators: device class
    _("Modem"),
    # translators: device class
    _("ISDN")
)

access_point_minor_cls = (
    # translators: device class
    _("Fully"),
    # translators: device class
    _("1–17 percent"),
    # translators: device class
    _("17–33 percent"),
    # translators: device class
    _("33–50 percent"),
    # translators: device class
    _("50–67 percent"),
    # translators: device class
    _("67–83 percent"),
    # translators: device class
    _("83–99 percent"),
    # translators: device class
    _("Not available")
)

audio_video_minor_cls = (
    # translators: device class
    _("Uncategorized"),
    # translators: device class
    _("Headset"),
    # translators: device class
    _("Handsfree"),
    # translators: device class
    _("Unknown"),
    # translators: device class
    _("Microphone"),
    # translators: device class
    _("Loudspeaker"),
    # translators: device class
    _("Headphones"),
    # translators: device class
    _("Portable audio"),
    # translators: device class
    _("Car audio"),
    # translators: device class
    _("Set-top box"),
    # translators: device class
    _("Hi-Fi audio"),
    # translators: device class
    _("VCR"),
    # translators: device class
    _("Video camera"),
    # translators: device class
    _("Camcorder"),
    # translators: device class
    _("Video monitor"),
    # translators: device class
    _("Video display and loudspeaker"),
    # translators: device class
    _("Video conferencing"),
    # translators: device class
    _("Unknown"),
    # translators: device class
    _("Gaming/Toy")
)

peripheral_minor_cls = (
    # translators: device class
    _("Uncategorized"),
    # translators: device class
    _("Keyboard"),
    # translators: device class
    _("Pointing"),
    # translators: device class
    _("Combo")
)

imaging_minor_cls = (
    # translators: device class
    _("Display"),
    # translators: device class
    _("Camera"),
    # translators: device class
    _("Scanner"),
    # translators: device class
    _("Printer")
)

wearable_minor_cls = (
    # translators: device class
    _("Wrist watch"),
    # translators: device class
    _("Pager"),
    # translators: device class
    _("Jacket"),
    # translators: device class
    _("Helmet"),
    # translators: device class
    _("Glasses")
)

toy_minor_cls = (
    # translators: device class
    _("Robot"),
    # translators: device class
    _("Vehicle"),
    # translators: device class
    _("Doll"),
    # translators: device class
    _("Controller"),
    # translators: device class
    _("Game")
)

gatt_appearance_categories = {
    0x00: ("Unknown", {0x00: _("Generic Unknown")}),
    0x01: ("Phone", {0x00: _("Generic Phone")}),
    0x02: ("Computer", {0x00: _("Generic Computer"),
                        0x01: _("Desktop Workstation"),
                        0x02: _("Server-class Computer"),
                        0x03: _("Laptop"),
                        0x04: _("Handheld PC/PDA (clamshell)"),
                        0x05: _("Palm-size PC/PDA"),
                        0x06: _("Wearable computer (watch size)"),
                        0x07: _("Tablet"),
                        0x08: _("Docking Station"),
                        0x09: _("All in One"),
                        0x0A: _("Blade Server"),
                        0x0B: _("Convertible"),
                        0x0C: _("Detachable"),
                        0x0D: _("IoT Gateway"),
                        0x0E: _("Mini PC"),
                        0x0F: _("Stick PC")}),
    0x03: ("Watch", {0x00: _("Generic Watch"),
                     0x01: _("Sports Watch"),
                     0x02: _("Smartwatch")}),
    0x04: ("Clock", {0x00: _("Generic Clock")}),
    0x05: ("Display", {0x00: _("Generic Display")}),
    0x06: ("Remote Control", {0x00: _("Generic Remote Control")}),
    0x07: ("Eye-glasses", {0x00: _("Generic Eye-glasses")}),
    0x08: ("Tag", {0x00: _("Generic Tag")}),
    0x09: ("Keyring", {0x00: _("Generic Keyring")}),
    0x0A: ("Media Player", {0x00: _("Generic Media Player")}),
    0x0B: ("Barcode Scanner", {0x00: _("Generic Barcode Scanner")}),
    0x0C: ("Thermometer", {0x00: _("Generic Thermometer"),
                           1: _("Ear Thermometer")}),
    0x0D: ("Heart Rate Sensor", {0x00: _("Generic Heart Rate Sensor"),
                                 1: _("Heart Rate Belt")}),
    0x0E: ("Blood Pressure", {0x00: _("Generic Blood Pressure"),
                              1: _("Arm Blood Pressure"),
                              2: _("Wrist Blood Pressure")}),
    0x0F: ("Human Interface Device", {0x00: _("Generic Human Interface Device"),
                                      0x01: _("Keyboard"),
                                      0x02: _("Mouse"),
                                      0x03: _("Joystick"),
                                      0x04: _("Gamepad"),
                                      0x05: _("Digitizer Tablet"),
                                      0x06: _("Card Reader"),
                                      0x07: _("Digital Pen"),
                                      0x08: _("Barcode Scanner"),
                                      0x09: _("Touchpad"),
                                      0x0a: _("Presentation Remote")}),
    0x10: ("Glucose Meter", {0x00: _("Generic Glucose Meter")}),
    0x11: ("Running Walking Sensor", {0x00: _("Generic Running Walking Sensor"),
                                      0x01: _("In-Shoe Running Walking Sensor"),
                                      0x02: _("On-Shoe Running Walking Sensor"),
                                      0x03: _("On-Hip Running Walking Sensor")}),
    0x12: ("Cycling", {0x00: _("Generic Cycling"),
                       0x01: _("Cycling Computer"),
                       0x02: _("Speed Sensor"),
                       0x03: _("Cadence Sensor"),
                       0x04: _("Power Sensor"),
                       0x05: _("Speed and Cadence Sensor")}),
    0x13: ("Control Device", {0x00: _("Generic Control Device"),
                              0x01: _("Switch"),
                              0x02: _("Multi-switch"),
                              0x03: _("Button"),
                              0x04: _("Slider"),
                              0x05: _("Rotary Switch"),
                              0x06: _("Touch Panel"),
                              0x07: _("Single Switch"),
                              0x08: _("Double Switch"),
                              0x09: _("Triple Switch"),
                              0x0A: _("Battery Switch"),
                              0x0B: _("Energy Harvesting Switch"),
                              0x0C: _("Push Button"),
                              0x0D: _("Dial")}),
    0x14: ("Network Device", {0x00: _("Generic Network Device"),
                              0x01: _("Access Point"),
                              0x02: _("Mesh Device"),
                              0x03: _("Mesh Network Proxy")}),
    0x15: ("Sensor", {0x00: _("Generic Sensor"),
                      0x01: _("Motion Sensor"),
                      0x02: _("Air quality Sensor"),
                      0x03: _("Temperature Sensor"),
                      0x04: _("Humidity Sensor"),
                      0x05: _("Leak Sensor"),
                      0x06: _("Smoke Sensor"),
                      0x07: _("Occupancy Sensor"),
                      0x08: _("Contact Sensor"),
                      0x09: _("Carbon Monoxide Sensor"),
                      0x0A: _("Carbon Dioxide Sensor"),
                      0x0B: _("Ambient Light Sensor"),
                      0x0C: _("Energy Sensor"),
                      0x0D: _("Color Light Sensor"),
                      0x0E: _("Rain Sensor"),
                      0x0F: _("Fire Sensor"),
                      0x10: _("Wind Sensor"),
                      0x11: _("Proximity Sensor"),
                      0x12: _("Multi-Sensor"),
                      0x13: _("Flush Mounted Sensor"),
                      0x14: _("Ceiling Mounted Sensor"),
                      0x15: _("Wall Mounted Sensor"),
                      0x16: _("Multisensor"),
                      0x17: _("Energy Meter"),
                      0x18: _("Flame Detector"),
                      0x19: _("Vehicle Tire Pressure Sensor")}),
    0x16: ("Light Fixtures", {0x00: _("Generic Light Fixtures"),
                              0x01: _("Wall Light"),
                              0x02: _("Ceiling Light"),
                              0x03: _("Floor Light"),
                              0x04: _("Cabinet Light"),
                              0x05: _("Desk Light"),
                              0x06: _("Troffer Light"),
                              0x07: _("Pendant Light"),
                              0x08: _("In-ground Light"),
                              0x09: _("Flood Light"),
                              0x0A: _("Underwater Light"),
                              0x0B: _("Bollard with Light"),
                              0x0C: _("Pathway Light"),
                              0x0D: _("Garden Light"),
                              0x0E: _("Pole-top Light"),
                              0x0F: _("Spotlight"),
                              0x10: _("Linear Light"),
                              0x11: _("Street Light"),
                              0x12: _("Shelves Light"),
                              0x13: _("Bay Light"),
                              0x14: _("Emergency Exit Light"),
                              0x15: _("Light Controller"),
                              0x16: _("Light Driver"),
                              0x17: _("Bulb"),
                              0x18: _("Low-bay Light"),
                              0x19: _("High-bay Light")}),
    0x17: ("Fan", {0x00: _("Generic Fan"),
                   0x01: _("Ceiling Fan"),
                   0x02: _("Axial Fan"),
                   0x03: _("Exhaust Fan"),
                   0x04: _("Pedestal Fan"),
                   0x05: _("Desk Fan"),
                   0x06: _("Wall Fan")}),
    0x18: ("HVAC", {0x00: _("Generic HVAC"),
                    0x01: _("Thermostat"),
                    0x02: _("Humidifier"),
                    0x03: _("De-humidifier"),
                    0x04: _("Heater"),
                    0x05: _("Radiator"),
                    0x06: _("Boiler"),
                    0x07: _("Heat Pump"),
                    0x08: _("Infrared Heater"),
                    0x09: _("Radiant Panel Heater"),
                    0x0A: _("Fan Heater"),
                    0x0B: _("Air Curtain")}),
    0x19: ("Air Conditioning", {0x00: _("Generic Air Conditioning")}),
    0x1A: ("Humidifier", {0x00: _("Generic Humidifier")}),
    0x1B: ("Heating", {0x00: _("Generic Heating"),
                       0x01: _("Radiator"),
                       0x02: _("Boiler"),
                       0x03: _("Heat Pump"),
                       0x04: _("Infrared Heater"),
                       0x05: _("Radiant Panel Heater"),
                       0x06: _("Fan Heater"),
                       0x07: _("Air Curtain")}),
    0x1C: ("Access Control", {0x00: _("Generic Access Control"),
                              0x01: _("Access Door"),
                              0x02: _("Garage Door"),
                              0x03: _("Emergency Exit Door"),
                              0x04: _("Access Lock"),
                              0x05: _("Elevator"),
                              0x06: _("Window"),
                              0x07: _("Entrance Gate"),
                              0x08: _("Door Lock"),
                              0x09: _("Locker")}),
    0x1D: ("Motorized Device", {0x00: _("Generic Motorized Device"),
                                0x01: _("Motorized Gate"),
                                0x02: _("Awning"),
                                0x03: _("Blinds or Shades"),
                                0x04: _("Curtains"),
                                0x05: _("Screen")}),
    0x1E: ("Power Device", {0x00: _("Generic Power Device"),
                            0x01: _("Power Outlet"),
                            0x02: _("Power Strip"),
                            0x03: _("Plug"),
                            0x04: _("Power Supply"),
                            0x05: _("LED Driver"),
                            0x06: _("Fluorescent Lamp Gear"),
                            0x07: _("HID Lamp Gear"),
                            0x08: _("Charge Case"),
                            0x09: _("Power Bank")}),
    0x1F: ("Light Source", {0x00: _("Generic Light Source"),
                            0x01: _("Incandescent Light Bulb"),
                            0x02: _("LED Lamp"),
                            0x03: _("HID Lamp"),
                            0x04: _("Fluorescent Lamp"),
                            0x05: _("LED Array"),
                            0x06: _("Multi-Color LED Array"),
                            0x07: _("Low voltage halogen"),
                            0x08: _("Organic light emitting diode (OLED)")}),
    0x20: ("Window Covering", {0x00: _("Generic Window Covering"),
                               0x01: _("Window Shades"),
                               0x02: _("Window Blinds"),
                               0x03: _("Window Awning"),
                               0x04: _("Window Curtain"),
                               0x05: _("Exterior Shutter"),
                               0x06: _("Exterior Screen")}),
    0x21: ("Audio Sink", {0x00: _("Generic Audio Sink"),
                          0x01: _("Standalone Speaker"),
                          0x02: _("Soundbar"),
                          0x03: _("Bookshelf Speaker"),
                          0x04: _("Standmounted Speaker"),
                          0x05: _("Speakerphone")}),
    0x22: ("Audio Source", {0x00: _("Generic Audio Source"),
                            0x01: _("Microphone"),
                            0x02: _("Alarm"),
                            0x03: _("Bell"),
                            0x04: _("Horn"),
                            0x05: _("Broadcasting Device"),
                            0x06: _("Service Desk"),
                            0x07: _("Kiosk"),
                            0x08: _("Broadcasting Room"),
                            0x09: _("Auditorium")}),
    0x23: ("Motorized Vehicle", {0x00: _("Generic Motorized Vehicle"),
                                 0x01: _("Car"),
                                 0x02: _("Large Goods Vehicle"),
                                 0x03: _("2-Wheeled Vehicle"),
                                 0x04: _("Motorbike"),
                                 0x05: _("Scooter"),
                                 0x06: _("Moped"),
                                 0x07: _("3-Wheeled Vehicle"),
                                 0x08: _("Light Vehicle"),
                                 0x09: _("Quad Bike"),
                                 0x0A: _("Minibus"),
                                 0x0B: _("Bus"),
                                 0x0C: _("Trolley"),
                                 0x0D: _("Agricultural Vehicle"),
                                 0x0E: _("Camper / Caravan"),
                                 0x0F: _("Recreational Vehicle / Motor Home")}),
    0x24: ("Domestic Appliance", {0x00: _("Generic Domestic Appliance"),
                                  0x01: _("Refrigerator"),
                                  0x02: _("Freezer"),
                                  0x03: _("Oven"),
                                  0x04: _("Microwave"),
                                  0x05: _("Toaster"),
                                  0x06: _("Washing Machine"),
                                  0x07: _("Dryer"),
                                  0x08: _("Coffee maker"),
                                  0x09: _("Clothes iron"),
                                  0x0A: _("Curling iron"),
                                  0x0B: _("Hair dryer"),
                                  0x0C: _("Vacuum cleaner"),
                                  0x0D: _("Robotic vacuum cleaner"),
                                  0x0E: _("Rice cooker"),
                                  0x0F: _("Clothes steamer")}),
    0x25: ("Wearable Audio Device", {0x00: _("Generic Wearable Audio Device"),
                                     0x01: _("Earbud"),
                                     0x02: _("Headset"),
                                     0x03: _("Headphones"),
                                     0x04: _("Neck Band")}),
    0x26: ("Aircraft", {0x00: _("Generic Aircraft"),
                        0x01: _("Light Aircraft"),
                        0x02: _("Microlight"),
                        0x03: _("Paraglider"),
                        0x04: _("Large Passenger Aircraft")}),
    0x27: ("AV Equipment", {0x00: _("Generic AV Equipment"),
                            0x01: _("Amplifier"),
                            0x02: _("Receiver"),
                            0x03: _("Radio"),
                            0x04: _("Tuner"),
                            0x05: _("Turntable"),
                            0x06: _("CD Player"),
                            0x07: _("DVD Player"),
                            0x08: _("Bluray Player"),
                            0x09: _("Optical Disc Player"),
                            0x0A: _("Set-Top Box")}),
    0x28: ("Display Equipment", {0x00: _("Generic Display Equipment"),
                                 0x01: _("Television"),
                                 0x02: _("Monitor"),
                                 0x03: _("Projector")}),
    0x29: ("Hearing aid", {0x00: _("Generic Hearing aid"),
                           0x01: _("In-ear hearing aid"),
                           0x02: _("Behind-ear hearing aid"),
                           0x03: _("Cochlear Implant")}),
    0x2A: ("Gaming", {0x00: _("Generic Gaming"),
                      0x01: _("Home Video Game Console"),
                      0x02: _("Portable handheld console")}),
    0x2B: ("Signage", {0x00: _("Generic Signage"),
                       0x01: _("Digital Signage"),
                       0x02: _("Electronic Label")}),
    0x31: ("Pulse Oximeter", {0x00: _("Generic Pulse Oximeter"),
                              0x01: _("Fingertip Pulse Oximeter"),
                              0x02: _("Wrist Worn Pulse Oximeter")}),
    0x32: ("Weight Scale", {0x00: _("Generic Weight Scale")}),
    0x33: ("Personal Mobility Device", {0x00: _("Generic Personal Mobility Device"),
                                        0x01: _("Powered Wheelchair"),
                                        0x02: _("Mobility Scooter")}),
    0x34: ("Continuous Glucose Monitor", {0x00: _("Generic Continuous Glucose Monitor")}),
    0x35: ("Insulin Pump", {0x00: _("Generic Insulin Pump"),
                            0x01: _("Insulin Pump, durable pump"),
                            0x04: _("Insulin Pump, patch pump"),
                            0x08: _("Insulin Pen")}),
    0x36: ("Medication Delivery", {0x00: _("Generic Medication Delivery")}),
    0x37: ("Spirometer", {0x00: _("Generic Spirometer"),
                          0x01: _("Handheld Spirometer")}),
    0x51: ("Outdoor Sports Activity", {0x00: _("Generic Outdoor Sports Activity"),
                                       0x01: _("Location Display"),
                                       0x02: _("Location and Navigation Display"),
                                       0x03: _("Location Pod"),
                                       0x04: _("Location and Navigation Pod")})
}


def get_major_class(klass: int) -> str:
    index = (klass >> 8) & 0x1F

    if index > 8:
        return major_cls[9]

    return major_cls[index]


def get_minor_class(klass: int) -> str:
    if not klass:
        return _("Unknown")

    i = (klass >> 8) & 0x1F

    if i == 1:
        minor_index = (klass >> 2) & 0x3F
        if minor_index < len(computer_minor_cls):
            return computer_minor_cls[minor_index]
        else:
            return ""
    elif i == 2:
        minor_index = (klass >> 2) & 0x3F
        if minor_index < len(phone_minor_cls):
            return phone_minor_cls[minor_index]
        return ""
    elif i == 3:
        minor_index = (klass >> 5) & 0x07
        if minor_index < len(access_point_minor_cls):
            return access_point_minor_cls[minor_index]
        else:
            return ""
    elif i == 4:
        minor_index = (klass >> 2) & 0x3F
        if minor_index < len(audio_video_minor_cls):
            return audio_video_minor_cls[minor_index]
        else:
            return ""
    elif i == 5:
        minor_index = (klass >> 6) & 0x03
        if minor_index < len(peripheral_minor_cls):
            return peripheral_minor_cls[minor_index]
        else:
            return ""
    elif i == 6:
        return _("Imaging")

    elif i == 7:
        minor_index = (klass >> 2) & 0x3F
        if minor_index < len(wearable_minor_cls):
            return wearable_minor_cls[minor_index]
        else:
            return ""
    elif i == 8:
        minor_index = (klass >> 2) & 0x3F
        if minor_index < len(toy_minor_cls):
            return toy_minor_cls[minor_index]
        else:
            return ""

    return _("Unknown")


# First 10 bits is the category, the following 6 bits sub category
def gatt_appearance_to_name(appearance: int) -> str:
    cat = appearance >> 0x6
    subcat = appearance & 0x3f

    if (19 <= cat <= 48) or (55 <= cat <= 80):
        # These ranges are reserved
        logging.debug(f"Reserved category found: {appearance}")
        return gatt_appearance_categories[0][0]
    elif cat > 81:
        logging.warning(f"Invalid category found: {appearance}")
        return gatt_appearance_categories[0][0]

    cat_name, subcats = gatt_appearance_categories[cat]

    if subcat not in subcats:
        return cat_name
    else:
        return subcats[subcat]
