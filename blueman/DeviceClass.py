from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from blueman.Functions import dprint

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


gatt_appearance_categories = {
    0: ('Unknown', {0: 'Unknown'}),
    1: ('Phone', {0: 'Generic Phone'}),
    2: ('Computer', {0: 'Generic Computer'}),
    3: ('Watch', {0: 'Generic Watch',
                  1: 'Watch: Sports Watch'}),
    4: ('Clock', {0: 'Generic Clock'}),
    5: ('Display', {0: 'Generic Display'}),
    6: ('Remote Control', {0: 'Generic Remote Control'}),
    7: ('Eye-glasses', {0: 'Generic Eye-glasses'}),
    8: ('Tag', {0: 'Generic Tag'}),
    9: ('Keyring', {0: 'Generic Keyring'}),
    10: ('Media Player', {0: 'Generic Media Player'}),
    11: ('Barcode Scanner', {0: 'Generic Barcode Scanner'}),
    12: ('Thermometer', {0: 'Generic Thermometer',
                         1: 'Thermometer: Ear'}),
    13: ('Heart rate Sensor', {0: 'Generic Heart rate Sensor',
                               1: 'Heart Rate Sensor: Heart Rate Belt'}),
    14: ('Blood Pressure', {0: 'Generic Blood Pressure',
                            1: 'Blood Pressure: Arm',
                            2: 'Blood Pressure: Wrist'}),
    15: ('Human Interface Device (HID)', {0: 'Human Interface Device (HID)',
                                          1: 'Keyboard',
                                          2: 'Mouse',
                                          3: 'Joystick',
                                          4: 'Gamepad',
                                          5: 'Digitizer Tablet',
                                          6: 'Card Reader',
                                          7: 'Digital Pen',
                                          8: 'Barcode Scanner'}),
    16: ('Glucose Meter', {0: 'Generic Glucose Meter'}),
    17: ('Running Walking Sensor', {0: 'Generic: Running Walking Sensor',
                                    1: 'Running Walking Sensor: In-Shoe',
                                    2: 'Running Walking Sensor: On-Shoe',
                                    3: 'Running Walking Sensor: On-Hip'}),
    18: ('Cycling', {0: 'Generic: Cycling',
                     1: 'Cycling: Cycling Computer',
                     2: 'Cycling: Speed Sensor',
                     3: 'Cycling: Cadence Sensor',
                     4: 'Cycling: Power Sensor',
                     5: 'Cycling: Speed and Cadence Sensor'}),
    # 19 - 48 reserved
    49: ('Pulse Oximeter', {0: 'Generic: Pulse Oximeter',
                            1: 'Fingertip',
                            2: 'Wrist Worn'}),
    50: ('Weight Scale', {0: 'Generic: Weight Scale'}),
    51: ('Personal Mobility Device', {0: 'Generic Personal Mobility Device',
                                      1: 'Powered Wheelchair',
                                      2: 'Mobility Scooter'}),
    52: ('Continuous Glucose Monitor', {0: 'Generic Continuous Glucose Monitor'}),
    53: ('Insulin Pump', {0: 'Generic Insulin Pump',
                          1: 'Insulin Pump, durable pump',
                          4: 'Insulin Pump, patch pump',
                          8: 'Insulin Pen'}),
    54: ('Medication Delivery', {0: 'Generic Medication Delivery'}),
    # 55 - 80 reserved
    81: ('Outdoor Sports Activity', {0: 'Generic: Outdoor Sports Activity',
                                     1: 'Location Display Device',
                                     2: 'Location and Navigation Display Device',
                                     3: 'Location Pod',
                                     4: 'Location and Navigation Pod'})
}


def get_major_class(klass):
    index = (klass >> 8) & 0x1F

    if index > 8:
        return major_cls[9]

    return major_cls[index]


def get_minor_class(klass, i18n=False):
    if klass == "unknown":
        if i18n:
            return _("unknown")
        else:
            return "unknown"

    i = (klass >> 8) & 0x1F

    if i == 1:
        minor_index = (klass >> 2) & 0x3F;
        if minor_index < len(computer_minor_cls):
            if i18n:
                return computer_minor_cls_i18n[minor_index]
            else:
                return computer_minor_cls[minor_index]
        else:
            return ""
    elif i == 2:
        minor_index = (klass >> 2) & 0x3F;
        if (minor_index < len(phone_minor_cls)):
            if i18n:
                return phone_minor_cls_i18n[minor_index]
            else:
                return phone_minor_cls[minor_index]
        return "";
    elif i == 3:
        minor_index = (klass >> 5) & 0x07;
        if (minor_index < len(access_point_minor_cls)):
            return access_point_minor_cls[minor_index]
        else:
            return "";
    elif i == 4:
        minor_index = (klass >> 2) & 0x3F;
        if (minor_index < len(audio_video_minor_cls)):
            if i18n:
                return audio_video_minor_cls_i18n[minor_index];
            else:
                return audio_video_minor_cls[minor_index];
        else:
            return "";
    elif i == 5:
        minor_index = (klass >> 6) & 0x03;
        if (minor_index < len(peripheral_minor_cls)):
            if i18n:
                return peripheral_minor_cls_i18n[minor_index];
            else:
                return peripheral_minor_cls[minor_index];
        else:
            return "";
    elif i == 6:
        return "imaging"

    elif i == 7:
        minor_index = (klass >> 2) & 0x3F;
        if (minor_index < len(wearable_minor_cls)):
            return wearable_minor_cls[minor_index];
        else:
            return "";
    elif i == 8:
        minor_index = (klass >> 2) & 0x3F;
        if (minor_index < len(toy_minor_cls)):
            return toy_minor_cls[minor_index];
        else:
            return "";

    if i18n:
        return _("unknown")
    else:
        return "unknown"


# First 10 bits is the category, the following 6 bits sub category
def gatt_appearance_to_name(appearance):
    cat = appearance >> 0x6
    subcat = appearance & 0x3f

    if (19 <= cat <= 48) or (55 <= cat <= 80):
        # These ranges are reserved
        dprint('Reserved category found: %s' % appearance)
        return gatt_appearance_categories[0][0]
    elif cat > 81:
        dprint('Invalid catagory found: %s' % appearance)
        return gatt_appearance_categories[0][0]

    cat_name, subcats = gatt_appearance_categories[cat]

    if subcat not in subcats:
        return cat_name
    else:
        return subcats[subcat]
