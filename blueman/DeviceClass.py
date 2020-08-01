from gettext import gettext as _
import logging

service_cls = [
    # translators: device class
    _("positioning"),
    # translators: device class
    _("networking"),
    # translators: device class
    _("rendering"),
    # translators: device class
    _("capturing"),
    # translators: device class
    _("object transfer"),
    # translators: device class
    _("audio"),
    # translators: device class
    _("telephony"),
    # translators: device class
    _("information")
]

major_cls = [
    # translators: device class
    _("miscellaneous"),
    # translators: device class
    _("computer"),
    # translators: device class
    _("phone"),
    # translators: device class
    _("access point"),
    # translators: device class
    _("audio/video"),
    # translators: device class
    _("peripheral"),
    # translators: device class
    _("imaging"),
    # translators: device class
    _("wearable"),
    # translators: device class
    _("toy"),
    # translators: device class
    _("uncategorized")
]

computer_minor_cls = [
    # translators: device class
    _("uncategorized"),
    # translators: device class
    _("desktop"),
    # translators: device class
    _("server"),
    # translators: device class
    _("laptop"),
    # translators: device class
    _("handheld"),
    # translators: device class
    _("palm"),
    # translators: device class
    _("wearable")
]

phone_minor_cls = [
    # translators: device class
    _("uncategorized"),
    # translators: device class
    _("cellular"),
    # translators: device class
    _("cordless"),
    # translators: device class
    _("smart phone"),
    # translators: device class
    _("modem"),
    # translators: device class
    _("isdn")
]

access_point_minor_cls = [
    # translators: device class
    _("fully"),
    # translators: device class
    _("1-17 percent"),
    # translators: device class
    _("17-33 percent"),
    # translators: device class
    _("33-50 percent"),
    # translators: device class
    _("50-67 percent"),
    # translators: device class
    _("67-83 percent"),
    # translators: device class
    _("83-99 percent"),
    # translators: device class
    _("not available")
]

audio_video_minor_cls = [
    # translators: device class
    _("uncategorized"),
    # translators: device class
    _("headset"),
    # translators: device class
    _("handsfree"),
    # translators: device class
    _("unknown"),
    # translators: device class
    _("microphone"),
    # translators: device class
    _("loudspeaker"),
    # translators: device class
    _("headphones"),
    # translators: device class
    _("portable audio"),
    # translators: device class
    _("car audio"),
    # translators: device class
    _("set-top box"),
    # translators: device class
    _("hifi audio"),
    # translators: device class
    _("vcr"),
    # translators: device class
    _("video camera"),
    # translators: device class
    _("camcorder"),
    # translators: device class
    _("video monitor"),
    # translators: device class
    _("video display and loudspeaker"),
    # translators: device class
    _("video conferencing"),
    # translators: device class
    _("unknown"),
    # translators: device class
    _("gaming/toy")
]

peripheral_minor_cls = [
    # translators: device class
    _("uncategorized"),
    # translators: device class
    _("keyboard"),
    # translators: device class
    _("pointing"),
    # translators: device class
    _("combo")
]

imaging_minor_cls = [
    # translators: device class
    _("display"),
    # translators: device class
    _("camera"),
    # translators: device class
    _("scanner"),
    # translators: device class
    _("printer")
]

wearable_minor_cls = [
    # translators: device class
    _("wrist watch"),
    # translators: device class
    _("pager"),
    # translators: device class
    _("jacket"),
    # translators: device class
    _("helmet"),
    # translators: device class
    _("glasses")
]

toy_minor_cls = [
    # translators: device class
    _("robot"),
    # translators: device class
    _("vehicle"),
    # translators: device class
    _("doll"),
    # translators: device class
    _("controller"),
    # translators: device class
    _("game")
]

gatt_appearance_categories = {
    0: ('Unknown', {0: _("Unknown")}),
    1: ('Phone', {0: _("Generic Phone")}),
    2: ('Computer', {0: _("Generic Computer")}),
    3: ('Watch', {0: _("Generic Watch"),
                  1: _("Watch: Sports Watch")}),
    4: ('Clock', {0: _("Generic Clock")}),
    5: ('Display', {0: _("Generic Display")}),
    6: ('Remote Control', {0: _("Generic Remote Control")}),
    7: ('Eye-glasses', {0: _("Generic Eye-glasses")}),
    8: ('Tag', {0: _("Generic Tag")}),
    9: ('Keyring', {0: _("Generic Keyring")}),
    10: ('Media Player', {0: _("Generic Media Player")}),
    11: ('Barcode Scanner', {0: _("Generic Barcode Scanner")}),
    12: ('Thermometer', {0: _("Generic Thermometer"),
                         1: _("Thermometer: Ear")}),
    13: ('Heart rate Sensor', {0: _("Generic Heart rate Sensor"),
                               1: _("Heart Rate Sensor: Heart Rate Belt")}),
    14: ('Blood Pressure', {0: _("Generic Blood Pressure"),
                            1: _("Blood Pressure: Arm"),
                            2: _("Blood Pressure: Wrist")}),
    15: ('Human Interface Device (HID)', {0: _("Human Interface Device (HID)"),
                                          1: _("Keyboard"),
                                          2: _("Mouse"),
                                          3: _("Joystick"),
                                          4: _("Gamepad"),
                                          5: _("Digitizer Tablet"),
                                          6: _("Card Reader"),
                                          7: _("Digital Pen"),
                                          8: _("Barcode Scanner")}),
    16: ('Glucose Meter', {0: _("Generic Glucose Meter")}),
    17: ('Running Walking Sensor', {0: _("Generic: Running Walking Sensor"),
                                    1: _("Running Walking Sensor: In-Shoe"),
                                    2: _("Running Walking Sensor: On-Shoe"),
                                    3: _("Running Walking Sensor: On-Hip")}),
    18: ('Cycling', {0: _("Generic: Cycling"),
                     1: _("Cycling: Cycling Computer"),
                     2: _("Cycling: Speed Sensor"),
                     3: _("Cycling: Cadence Sensor"),
                     4: _("Cycling: Power Sensor"),
                     5: _("Cycling: Speed and Cadence Sensor")}),
    # 19 - 48 reserved
    49: ('Pulse Oximeter', {0: _("Generic: Pulse Oximeter"),
                            1: _("Fingertip"),
                            2: _("Wrist Worn")}),
    50: ('Weight Scale', {0: _("Generic: Weight Scale")}),
    51: ('Personal Mobility Device', {0: _("Generic Personal Mobility Device"),
                                      1: _("Powered Wheelchair"),
                                      2: _("Mobility Scooter")}),
    52: ('Continuous Glucose Monitor', {0: _("Generic Continuous Glucose Monitor")}),
    53: ('Insulin Pump', {0: _("Generic Insulin Pump"),
                          1: _("Insulin Pump, durable pump"),
                          4: _("Insulin Pump, patch pump"),
                          8: _("Insulin Pen")}),
    54: ('Medication Delivery', {0: _("Generic Medication Delivery")}),
    # 55 - 80 reserved
    81: ('Outdoor Sports Activity', {0: _("Generic: Outdoor Sports Activity"),
                                     1: _("Location Display Device"),
                                     2: _("Location and Navigation Display Device"),
                                     3: _("Location Pod"),
                                     4: _("Location and Navigation Pod")})
}


def get_major_class(klass: int) -> str:
    index = (klass >> 8) & 0x1F

    if index > 8:
        return major_cls[9]

    return major_cls[index]


def get_minor_class(klass: int) -> str:
    if not klass:
        return _("unknown")

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
        return _("imaging")

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

    return _("unknown")


# First 10 bits is the category, the following 6 bits sub category
def gatt_appearance_to_name(appearance: int) -> str:
    cat = appearance >> 0x6
    subcat = appearance & 0x3f

    if (19 <= cat <= 48) or (55 <= cat <= 80):
        # These ranges are reserved
        logging.debug(f"Reserved category found: {appearance}")
        return gatt_appearance_categories[0][0]
    elif cat > 81:
        logging.warning(f"Invalid catagory found: {appearance}")
        return gatt_appearance_categories[0][0]

    cat_name, subcats = gatt_appearance_categories[cat]

    if subcat not in subcats:
        return cat_name
    else:
        return subcats[subcat]
