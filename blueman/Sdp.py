from gettext import gettext as _
from typing import Optional
from uuid import UUID

# https://www.bluetooth.com/specifications/assigned-numbers/service-discovery
# http://git.kernel.org/cgit/bluetooth/bluez.git/tree/lib/sdp.h

SDP_SERVER_SVCLASS_ID = 0x1000
BROWSE_GRP_DESC_SVCLASS_ID = 0x1001
PUBLIC_BROWSE_GROUP = 0x1002
SERIAL_PORT_SVCLASS_ID = 0x1101
LAN_ACCESS_SVCLASS_ID = 0x1102
DIALUP_NET_SVCLASS_ID = 0x1103
IRMC_SYNC_SVCLASS_ID = 0x1104
OBEX_OBJPUSH_SVCLASS_ID = 0x1105
OBEX_FILETRANS_SVCLASS_ID = 0x1106
IRMC_SYNC_CMD_SVCLASS_ID = 0x1107
HEADSET_SVCLASS_ID = 0x1108
CORDLESS_TELEPHONY_SVCLASS_ID = 0x1109
AUDIO_SOURCE_SVCLASS_ID = 0x110a
AUDIO_SINK_SVCLASS_ID = 0x110b
AV_REMOTE_TARGET_SVCLASS_ID = 0x110c
ADVANCED_AUDIO_SVCLASS_ID = 0x110d
AV_REMOTE_SVCLASS_ID = 0x110e
AV_REMOTE_CONTROLLER_SVCLASS_ID = 0x110f
INTERCOM_SVCLASS_ID = 0x1110
FAX_SVCLASS_ID = 0x1111
HEADSET_AGW_SVCLASS_ID = 0x1112
WAP_SVCLASS_ID = 0x1113
WAP_CLIENT_SVCLASS_ID = 0x1114
PANU_SVCLASS_ID = 0x1115
NAP_SVCLASS_ID = 0x1116
GN_SVCLASS_ID = 0x1117
DIRECT_PRINTING_SVCLASS_ID = 0x1118
REFERENCE_PRINTING_SVCLASS_ID = 0x1119
IMAGING_SVCLASS_ID = 0x111a
IMAGING_RESPONDER_SVCLASS_ID = 0x111b
IMAGING_ARCHIVE_SVCLASS_ID = 0x111c
IMAGING_REFOBJS_SVCLASS_ID = 0x111d
HANDSFREE_SVCLASS_ID = 0x111e
HANDSFREE_AGW_SVCLASS_ID = 0x111f
DIRECT_PRT_REFOBJS_SVCLASS_ID = 0x1120
REFLECTED_UI_SVCLASS_ID = 0x1121
BASIC_PRINTING_SVCLASS_ID = 0x1122
PRINTING_STATUS_SVCLASS_ID = 0x1123
HID_SVCLASS_ID = 0x1124
HCR_SVCLASS_ID = 0x1125
HCR_PRINT_SVCLASS_ID = 0x1126
HCR_SCAN_SVCLASS_ID = 0x1127
CIP_SVCLASS_ID = 0x1128
VIDEO_CONF_GW_SVCLASS_ID = 0x1129
UDI_MT_SVCLASS_ID = 0x112a
UDI_TA_SVCLASS_ID = 0x112b
AV_SVCLASS_ID = 0x112c
SAP_SVCLASS_ID = 0x112d
PBAP_PCE_SVCLASS_ID = 0x112e
PBAP_PSE_SVCLASS_ID = 0x112f
PBAP_SVCLASS_ID = 0x1130
MAP_MSE_SVCLASS_ID = 0x1132
MAP_MCE_SVCLASS_ID = 0x1133
MAP_SVCLASS_ID = 0x1134
GNSS_SVCLASS_ID = 0x1135
GNSS_SERVER_SVCLASS_ID = 0x1136
MPS_SC_SVCLASS_ID = 0x113A
MPS_SVCLASS_ID = 0x113B
PNP_INFO_SVCLASS_ID = 0x1200
GENERIC_NETWORKING_SVCLASS_ID = 0x1201
GENERIC_FILETRANS_SVCLASS_ID = 0x1202
GENERIC_AUDIO_SVCLASS_ID = 0x1203
GENERIC_TELEPHONY_SVCLASS_ID = 0x1204
UPNP_SVCLASS_ID = 0x1205
UPNP_IP_SVCLASS_ID = 0x1206
UPNP_PAN_SVCLASS_ID = 0x1300
UPNP_LAP_SVCLASS_ID = 0x1301
UPNP_L2CAP_SVCLASS_ID = 0x1302
VIDEO_SOURCE_SVCLASS_ID = 0x1303
VIDEO_SINK_SVCLASS_ID = 0x1304
VIDEO_DISTRIBUTION_SVCLASS_ID = 0x1305
HDP_SVCLASS_ID = 0x1400
HDP_SOURCE_SVCLASS_ID = 0x1401
HDP_SINK_SVCLASS_ID = 0x1402
GENERIC_ACCESS_SVCLASS_ID = 0x1800
GENERIC_ATTRIB_SVCLASS_ID = 0x1801
BATTERY_SERVICE_SVCLASS_ID = 0x180F
APPLE_AGENT_SVCLASS_ID = 0x2112

uuid_names = {
    0x0001: _("SDP"),
    0x0002: _("UDP"),
    0x0003: _("RFCOMM"),
    0x0004: _("TCP"),
    0x0005: _("TCS-BIN"),
    0x0006: _("TCS-AT"),
    0x0007: _("ATT"),
    0x0008: _("OBEX"),
    0x0009: _("IP"),
    0x000a: _("FTP"),
    0x000c: _("HTTP"),
    0x000e: _("WSP"),
    0x000f: _("BNEP"),
    0x0010: _("UPnP/ESDP"),
    0x0011: _("HIDP"),
    0x0012: _("Hardcopy Control Channel"),
    0x0014: _("Hardcopy Data Channel"),
    0x0016: _("Hardcopy Notification"),
    0x0017: _("AVCTP"),
    0x0019: _("AVDTP"),
    0x001b: _("CMTP"),
    0x001d: _("UDI_C-Plane"),
    0x001e: _("Multi-Channel Adaptation Protocol (MCAP)"),
    0x001f: _("Multi-Channel Adaptation Protocol (MCAP)"),
    0x0100: _("L2CAP"),
    0x1000: _("ServiceDiscoveryServerServiceClassID"),
    0x1001: _("BrowseGroupDescriptorServiceClassID"),
    0x1002: _("Public Browse Group"),
    0x1101: _("Serial Port"),
    0x1102: _("LAN Access Using PPP"),
    0x1103: _("Dialup Networking (DUN)"),
    0x1104: _("IrMC Sync"),
    0x1105: _("OBEX Object Push"),
    0x1106: _("OBEX File Transfer"),
    0x1107: _("IrMC Sync Command"),
    0x1108: _("Headset"),
    0x1109: _("Cordless Telephony"),
    0x110a: _("Audio Source"),
    0x110b: _("Audio Sink"),
    0x110c: _("Remote Control Target"),
    0x110d: _("Advanced Audio"),
    0x110e: _("Remote Control"),
    0x110f: _("Video Conferencing"),
    0x1110: _("Intercom"),
    0x1111: _("Fax"),
    0x1112: _("Headset Audio Gateway"),
    0x1113: _("WAP"),
    0x1114: _("WAP Client"),
    0x1115: _("PANU"),
    0x1116: _("Network Access Point"),
    0x1117: _("Group Network"),
    0x1118: _("DirectPrinting (BPP)"),
    0x1119: _("ReferencePrinting (BPP)"),
    0x111a: _("Imaging (BIP)"),
    0x111b: _("ImagingResponder (BIP)"),
    0x111c: _("ImagingAutomaticArchive (BIP)"),
    0x111d: _("ImagingReferencedObjects (BIP)"),
    0x111e: _("Handsfree"),
    0x111f: _("Handsfree Audio Gateway"),
    0x1120: _("DirectPrintingReferenceObjectsService (BPP)"),
    0x1121: _("ReflectedUI (BPP)"),
    0x1122: _("Basic Printing (BPP)"),
    0x1123: _("Printing Status (BPP)"),
    0x1124: _("Human Interface Device Service (HID)"),
    0x1125: _("HardcopyCableReplacement (HCR)"),
    0x1126: _("HCR_Print (HCR)"),
    0x1127: _("HCR_Scan (HCR)"),
    0x1128: _("Common ISDN Access (CIP)"),
    0x1129: _("VideoConferencingGW (VCP)"),
    0x112a: _("UDI-MT"),
    0x112b: _("UDI-TA"),
    0x112c: _("Audio/Video"),
    0x112d: _("SIM Access (SAP)"),
    0x112e: _("Phonebook Access (PBAP) - PCE"),
    0x112f: _("Phonebook Access (PBAP) - PSE"),
    0x1130: _("Phonebook Access (PBAP)"),
    0x1131: _("Headset"),
    0x1132: _("Message Access Server"),
    0x1133: _("Message Notification Server"),
    0x1134: _("Message Access Profile (MAP)"),
    0x1135: _("GNSS"),
    0x1136: _("GNSS Server"),
    0x1137: _("3D Display"),
    0x1138: _("3D Glasses"),
    0x1139: _("3D Synchronization (3DSP)"),
    0x113a: _("Multi-Profile Specification (MPS) Profile"),
    0x113b: _("Multi-Profile Specification (MPS) Service"),
    0x113c: _("Calendar, Task, and Notes (CTN) Access Service"),
    0x113d: _("Calendar, Task, and Notes (CTN) Notification Service"),
    0x113e: _("Calendar, Task, and Notes (CTN) Profile"),
    0x1200: _("PnP Information"),
    0x1201: _("Generic Networking"),
    0x1202: _("Generic FileTransfer"),
    0x1203: _("Generic Audio"),
    0x1204: _("Generic Telephony"),
    0x1303: _("Video Source"),
    0x1304: _("Video Sink"),
    0x1305: _("Video Distribution"),
    0x1400: _("HDP"),
    0x1401: _("HDP Source"),
    0x1402: _("HDP Sink"),
    0x1800: _("Generic Access"),
    0x1801: _("Generic Attribute"),
    0x1802: _("Immediate Alert"),
    0x1803: _("Link Loss"),
    0x1804: _("Tx Power"),
    0x1805: _("Current Time Service"),
    0x1806: _("Reference Time Update Service"),
    0x1807: _("Next DST Change Service"),
    0x1808: _("Glucose"),
    0x1809: _("Health Thermometer"),
    0x180A: _("Device Information"),
    0x180D: _("Heart Rate"),
    0x180E: _("Phone Alert Status Service"),
    0x180F: _("Battery Service"),
    0x1810: _("Blood Pressure"),
    0x1811: _("Alert Notification Service"),
    0x1812: _("Human Interface Device"),
    0x1813: _("Scan Parameters"),
    0x1814: _("Running Speed and Cadence"),
    0x1815: _("Automation IO"),
    0x1816: _("Cycling Speed and Cadence"),
    0x1818: _("Cycling Power"),
    0x1819: _("Location and Navigation"),
    0x181A: _("Environmental Sensing"),
    0x181B: _("Body Composition"),
    0x181C: _("User Data"),
    0x181D: _("Weight Scale"),
    0x181E: _("Bond Management"),
    0x181F: _("Continuous Glucose Monitoring"),
    0x1820: _("Internet Protocol Support"),
    0x1821: _("Indoor Positioning"),
    0x1822: _("Pulse Oximeter"),
    0x1823: _("HTTP Proxy"),
    0x1824: _("Transport Discovery"),
    0x1825: _("Object Transfer"),
    0x2112: _("AppleAgent"),
    0x2800: _("Primary Service"),
    0x2801: _("Secondary Service"),
    0x2802: _("Include"),
    0x2803: _("Characteristic Declaration"),
    0x2A00: _("Device Name"),
    0x2A01: _("Appearance"),
    0x2A02: _("Peripheral Privacy Flag"),
    0x2A03: _("Reconnection Address"),
    0x2A04: _("Peripheral Preferred Connection Parameters"),
    0x2A05: _("Service Changed"),
    0x2A23: _("System ID"),
    0x2A24: _("Model Number String"),
    0x2A25: _("Serial Number String"),
    0x2A26: _("Firmware Revision String"),
    0x2A27: _("Hardware Revision String"),
    0x2A28: _("Software Revision String"),
    0x2A29: _("Manufacturer Name String"),
    0x2A50: _("PnP ID"),
    0x2900: _("Characteristic Extended Properties"),
    0x2901: _("Characteristic User Description"),
    0x2902: _("Client Characteristic Configuration"),
    0x2903: _("Server Characteristic Configuration"),
    0x2904: _("Characteristic Presentation Format"),
    0x2905: _("Characteristic Aggregate Format"),
    0x2906: _("Valid Range"),
    0x2907: _("External Report Reference"),
    0x2908: _("Report Reference"),
}

SDP_ATTR_RECORD_HANDLE = 0x0000
SDP_ATTR_SVCLASS_ID_LIST = 0x0001
SDP_ATTR_RECORD_STATE = 0x0002
SDP_ATTR_SERVICE_ID = 0x0003
SDP_ATTR_PROTO_DESC_LIST = 0x0004
SDP_ATTR_BROWSE_GRP_LIST = 0x0005
SDP_ATTR_LANG_BASE_ATTR_ID_LIST = 0x0006
SDP_ATTR_SVCINFO_TTL = 0x0007
SDP_ATTR_SERVICE_AVAILABILITY = 0x0008
SDP_ATTR_PFILE_DESC_LIST = 0x0009
SDP_ATTR_DOC_URL = 0x000a
SDP_ATTR_CLNT_EXEC_URL = 0x000b
SDP_ATTR_ICON_URL = 0x000c
SDP_ATTR_ADD_PROTO_DESC_LIST = 0x000d

SDP_ATTR_SUPPORTED_REPOSITORIES = 0x0314
SDP_ATTR_MAS_INSTANCE_ID = 0x0315
SDP_ATTR_SUPPORTED_MESSAGE_TYPES = 0x0316
SDP_ATTR_PBAP_SUPPORTED_FEATURES = 0x0317
SDP_ATTR_MAP_SUPPORTED_FEATURES = 0x0317

SDP_ATTR_SPECIFICATION_ID = 0x0200
SDP_ATTR_VENDOR_ID = 0x0201
SDP_ATTR_PRODUCT_ID = 0x0202
SDP_ATTR_VERSION = 0x0203
SDP_ATTR_PRIMARY_RECORD = 0x0204
SDP_ATTR_VENDOR_ID_SOURCE = 0x0205

SDP_ATTR_HID_DEVICE_RELEASE_NUMBER = 0x0200
SDP_ATTR_HID_PARSER_VERSION = 0x0201
SDP_ATTR_HID_DEVICE_SUBCLASS = 0x0202
SDP_ATTR_HID_COUNTRY_CODE = 0x0203
SDP_ATTR_HID_VIRTUAL_CABLE = 0x0204
SDP_ATTR_HID_RECONNECT_INITIATE = 0x0205
SDP_ATTR_HID_DESCRIPTOR_LIST = 0x0206
SDP_ATTR_HID_LANG_ID_BASE_LIST = 0x0207
SDP_ATTR_HID_SDP_DISABLE = 0x0208
SDP_ATTR_HID_BATTERY_POWER = 0x0209
SDP_ATTR_HID_REMOTE_WAKEUP = 0x020a
SDP_ATTR_HID_PROFILE_VERSION = 0x020b
SDP_ATTR_HID_SUPERVISION_TIMEOUT = 0x020c
SDP_ATTR_HID_NORMALLY_CONNECTABLE = 0x020d
SDP_ATTR_HID_BOOT_DEVICE = 0x020e

SDP_PRIMARY_LANG_BASE = 0x0100

SDP_UUID = 0x0001
UDP_UUID = 0x0002
RFCOMM_UUID = 0x0003
TCP_UUID = 0x0004
TCS_BIN_UUID = 0x0005
TCS_AT_UUID = 0x0006
OBEX_UUID = 0x0008
IP_UUID = 0x0009
FTP_UUID = 0x000a
HTTP_UUID = 0x000c
WSP_UUID = 0x000e
BNEP_UUID = 0x000f
UPNP_UUID = 0x0010
HIDP_UUID = 0x0011
HCRP_CTRL_UUID = 0x0012
HCRP_DATA_UUID = 0x0014
HCRP_NOTE_UUID = 0x0016
AVCTP_UUID = 0x0017
AVDTP_UUID = 0x0019
CMTP_UUID = 0x001b
UDI_UUID = 0x001d
MCAP_CTRL_UUID = 0x001e
MCAP_DATA_UUID = 0x001f
L2CAP_UUID = 0x0100

# GATT UUIDs section
GATT_PRIM_SVC_UUID = 0x2800
GATT_SND_SVC_UUID = 0x2801
GATT_INCLUDE_UUID = 0x2802
GATT_CHARAC_UUID = 0x2803

# GATT Characteristic Types
GATT_CHARAC_DEVICE_NAME = 0x2A00
GATT_CHARAC_APPEARANCE = 0x2A01
GATT_CHARAC_PERIPHERAL_PRIV_FLAG = 0x2A02
GATT_CHARAC_RECONNECTION_ADDRESS = 0x2A03
GATT_CHARAC_PERIPHERAL_PREF_CONN = 0x2A04
GATT_CHARAC_SERVICE_CHANGED = 0x2A05
GATT_CHARAC_SYSTEM_ID = 0x2A23
GATT_CHARAC_MODEL_NUMBER_STRING = 0x2A24
GATT_CHARAC_SERIAL_NUMBER_STRING = 0x2A25
GATT_CHARAC_FIRMWARE_REVISION_STRING = 0x2A26
GATT_CHARAC_HARDWARE_REVISION_STRING = 0x2A27
GATT_CHARAC_SOFTWARE_REVISION_STRING = 0x2A28
GATT_CHARAC_MANUFACTURER_NAME_STRING = 0x2A29
GATT_CHARAC_PNP_ID = 0x2A50

# GATT Characteristic Descriptors
GATT_CHARAC_EXT_PROPER_UUID = 0x2900
GATT_CHARAC_USER_DESC_UUID = 0x2901
GATT_CLIENT_CHARAC_CFG_UUID = 0x2902
GATT_SERVER_CHARAC_CFG_UUID = 0x2903
GATT_CHARAC_FMT_UUID = 0x2904
GATT_CHARAC_AGREG_FMT_UUID = 0x2905
GATT_CHARAC_VALID_RANGE_UUID = 0x2906
GATT_EXTERNAL_REPORT_REFERENCE = 0x2907
GATT_REPORT_REFERENCE = 0x2908


class ServiceUUID(UUID):
    def __init__(self, uuid: str):
        super().__init__(uuid)

    @property
    def short_uuid(self) -> Optional[int]:
        if self.reserved:
            return self.int >> 96 & 0xFFFF
        else:
            return None

    @property
    def name(self) -> str:
        if self.short_uuid:
            try:
                return uuid_names[self.short_uuid]
            except KeyError:
                return _("Unknown")
        elif self.int == 0:
            return _('Audio and input profiles')
        else:
            return _('Proprietary')

    @property
    def reserved(self) -> bool:
        return self.int & UUID('FFFF0000-0000-FFFF-FFFF-FFFFFFFFFFFF').int == \
            UUID('00000000-0000-1000-8000-00805F9B34FB').int
