# coding=utf-8
service_cls = [
    "positioning",
    "networking",
    "rendering",
    "capturing",
    "object transfer",
    "audio",
    "telephony",
    "information"
]

major_cls = [
    "miscellaneous",
    "computer",
    "phone",
    "access point",
    "audio/video",
    "peripheral",
    "imaging",
    "wearable",
    "toy",
    "uncategorized"
]

computer_minor_cls = [
    "uncategorized",
    "desktop",
    "server",
    "laptop",
    "handheld",
    "palm",
    "wearable"
]
computer_minor_cls_i18n = [
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
    "wearable"
]

phone_minor_cls = [
    "uncategorized",
    "cellular",
    "cordless",
    "smart phone",
    "modem",
    "isdn"
]
phone_minor_cls_i18n = [
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
    "fully",
    "1-17 percent",
    "17-33 percent",
    "33-50 percent",
    "50-67 percent",
    "67-83 percent",
    "83-99 percent",
    "not available"
]

audio_video_minor_cls = [
    "uncategorized",
    "headset",
    "handsfree",
    "unknown",
    "microphone",
    "loudspeaker",
    "headphones",
    "portable audio",
    "car audio",
    "set-top box",
    "hifi audio",
    "vcr",
    "video camera",
    "camcorder",
    "video monitor",
    "video display and loudspeaker",
    "video conferencing",
    "unknown",
    "gaming/toy"
]
audio_video_minor_cls_i18n = [
    "uncategorized",
    # translators: device class
    _("headset"),
    # translators: device class
    _("handsfree"),
    # translators: device class
    _("unknown"),
    # translators: device class
    _("microphone"),
    "loudspeaker",
    "headphones",
    "portable audio",
    "car audio",
    "set-top box",
    "hifi audio",
    "vcr",
    "video camera",
    "camcorder",
    "video monitor",
    "video display and loudspeaker",
    "video conferencing",
    "unknown",
    "gaming/toy"
]
peripheral_minor_cls = [
    "uncategorized",
    "keyboard",
    "pointing",
    "combo"
]
peripheral_minor_cls_i18n = [
    "uncategorized",
    # translators: device class
    _("keyboard"),
    # translators: device class
    _("pointing"),
    "combo"
]

imaging_minor_cls = [
    "display",
    "camera",
    "scanner",
    "printer"
]

wearable_minor_cls = [
    "wrist watch",
    "pager",
    "jacket",
    "helmet",
    "glasses"
]

toy_minor_cls = [
    "robot",
    "vehicle",
    "doll",
    "controller",
    "game"
]


gatt_appearance = {
    0: "Unknown",
    64: "Generic Phone",
    128: "Generic Computer",
    192: "Generic Watch",
    193: "Watch: Sports Watch",
    256: "Generic Clock",
    320: "Generic Display",
    384: "Generic Remote Control",
    448: "Generic Eye-glasses",
    512: "Generic Tag",
    576: "Generic Keyring",
    640: "Generic Media Player",
    704: "Generic Barcode Scanner",
    768: "Generic Thermometer",
    769: "Thermometer: Ear",
    832: "Generic Heart rate Sensor",
    833: "Heart Rate Sensor: Heart Rate Belt",
    896: "Generic Blood Pressure",
    897: "Blood Pressure: Arm",
    898: "Blood Pressure: Wrist",
    960: "Human Interface Device (HID)",
    961: "Keyboard",
    962: "Mouse",
    963: "Joystick",
    964: "Gamepad",
    965: "Digitizer Tablet",
    966: "Card Reader",
    967: "Digital Pen",
    968: "Barcode Scanner",
    1024: "Generic Glucose Meter",
    1088: "Generic: Running Walking Sensor",
    1089: "Running Walking Sensor: In-Shoe",
    1090: "Running Walking Sensor: On-Shoe",
    1091: "Running Walking Sensor: On-Hip",
    1152: "Generic: Cycling",
    1153: "Cycling: Cycling Computer",
    1154: "Cycling: Speed Sensor",
    1155: "Cycling: Cadence Sensor",
    1156: "Cycling: Power Sensor",
    1157: "Cycling: Speed and Cadence Sensor",
    3136: "Generic: Pulse Oximeter",
    3137: "Fingertip",
    3138: "Wrist Worn",
    3200: "Generic: Weight Scale",
    3264: "Generic Personal Mobility Device",
    3265: "Powered Wheelchair",
    3266: "Mobility Scooter",
    3328: "Generic Continuous Glucose Monitor",
    5184: "Generic: Outdoor Sports Activity",
    5185: "Location Display Device",
    5186: "Location and Navigation Display Device",
    5187: "Location Pod",
    5188: "Location and Navigation Pod"
}

def get_major_class(klass):
    index = (klass >> 8) & 0x1F

    if index > 8:
        return major_cls[9]

    return major_cls[index]


def get_minor_class(klass, i18n=False):
    if not klass:
        if i18n:
            return _("unknown")
        else:
            return "unknown"

    i = (klass >> 8) & 0x1F

    if i == 1:
        minor_index = (klass >> 2) & 0x3F
        if minor_index < len(computer_minor_cls):
            if i18n:
                return computer_minor_cls_i18n[minor_index]
            else:
                return computer_minor_cls[minor_index]
        else:
            return ""
    elif i == 2:
        minor_index = (klass >> 2) & 0x3F
        if minor_index < len(phone_minor_cls):
            if i18n:
                return phone_minor_cls_i18n[minor_index]
            else:
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
            if i18n:
                return audio_video_minor_cls_i18n[minor_index]
            else:
                return audio_video_minor_cls[minor_index]
        else:
            return ""
    elif i == 5:
        minor_index = (klass >> 6) & 0x03
        if minor_index < len(peripheral_minor_cls):
            if i18n:
                return peripheral_minor_cls_i18n[minor_index]
            else:
                return peripheral_minor_cls[minor_index]
        else:
            return ""
    elif i == 6:
        return "imaging"

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

    if i18n:
        return _("unknown")
    else:
        return "unknown"


def gatt_appearance_to_name(appearance):
    return gatt_appearance[appearance]
