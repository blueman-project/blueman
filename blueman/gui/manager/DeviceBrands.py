"""Known device brands and product kinds, inferred from names and manufacturer IDs.

Only presentation is derived here: a brand label, a tint class, and artwork for
devices whose Bluetooth class is missing. Nothing is shown as fact unless the
device name or its advertised manufacturer identifier supports it, and no
trademarked logos are bundled.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from gettext import gettext as _


@dataclass(frozen=True)
class Brand:
    key: str
    name: str
    patterns: tuple[str, ...]
    company_ids: tuple[int, ...] = ()

    @property
    def css_class(self) -> str:
        return f"brand-{self.key}"


# Patterns are case-insensitive regular expressions matched against the device name;
# company IDs are Bluetooth SIG assigned numbers from the ManufacturerData property.
KNOWN_BRANDS: tuple[Brand, ...] = (
    Brand("apple", "Apple", (r"\bapple\b", r"\bairpods\b", r"\bmagic (keyboard|mouse|trackpad)\b",
                             r"\bi(phone|pad)\b", r"\bmacbook\b"), (0x004C,)),
    Brand("beats", "Beats", (r"\bbeats\b", r"\bpowerbeats\b")),
    Brand("samsung", "Samsung", (r"\bsamsung\b", r"\bgalaxy\b"), (0x0075,)),
    Brand("sony", "Sony", (r"\bsony\b", r"\bw[hf]-\w+", r"\blinkbuds\b", r"\bsrs-\w+", r"\bdualsense\b"),
          (0x012D,)),
    Brand("bose", "Bose", (r"\bbose\b", r"\bquietcomfort\b", r"\bsoundlink\b"), (0x009E,)),
    Brand("jbl", "JBL", (r"\bjbl\b",)),
    Brand("philips", "Philips", (r"\bphilips\b",)),
    Brand("oneplus", "OnePlus", (r"\boneplus\b",)),
    Brand("realme", "realme", (r"\brealme\b",)),
    Brand("xiaomi", "Xiaomi", (r"\bxiaomi\b", r"\bredmi\b", r"\bmi (smart )?band\b", r"\bpoco\b"), (0x038F,)),
    Brand("huawei", "Huawei", (r"\bhuawei\b", r"\bfreebuds\b"), (0x027D,)),
    Brand("google", "Google", (r"\bpixel\b", r"\bgoogle\b"), (0x00E0,)),
    Brand("microsoft", "Microsoft", (r"\bmicrosoft\b", r"\bsurface\b", r"\bxbox\b"), (0x0006,)),
    Brand("logitech", "Logitech", (r"\blogitech\b", r"\blogi\b", r"\bmx (master|keys|anywhere)\b"), (0x01DA,)),
    Brand("sennheiser", "Sennheiser", (r"\bsennheiser\b", r"\bmomentum\b")),
    Brand("jabra", "Jabra", (r"\bjabra\b",)),
    Brand("anker", "Anker", (r"\banker\b", r"\bsoundcore\b")),
    Brand("marshall", "Marshall", (r"\bmarshall\b",)),
    Brand("bang-olufsen", "Bang & Olufsen", (r"\bbang & olufsen\b", r"\bbeoplay\b", r"\bbeosound\b")),
    Brand("nothing", "Nothing", (r"^nothing\b", r"\bnothing (ear|phone|headphone)\b", r"\bcmf\b")),
    Brand("garmin", "Garmin", (r"\bgarmin\b", r"\bforerunner\b", r"\bf[eē]nix\b"), (0x0087,)),
    Brand("amazfit", "Amazfit", (r"\bamazfit\b",)),
    Brand("nintendo", "Nintendo", (r"\bnintendo\b", r"\bjoy-con\b", r"\bpro controller\b")),
    Brand("skullcandy", "Skullcandy", (r"\bskullcandy\b",)),
)

_COMPILED = tuple((brand, tuple(re.compile(p, re.IGNORECASE) for p in brand.patterns)) for brand in KNOWN_BRANDS)
_BY_COMPANY = {company: brand for brand in KNOWN_BRANDS for company in brand.company_ids}

BRAND_CSS_CLASSES = tuple(brand.css_class for brand in KNOWN_BRANDS)


def brand_for(name: str, company_ids: Iterable[int] = ()) -> Brand | None:
    """The device name wins, because it is what the user sees; then the advertised company."""
    for brand, patterns in _COMPILED:
        if any(pattern.search(name) for pattern in patterns):
            return brand
    for company in company_ids:
        if company in _BY_COMPANY:
            return _BY_COMPANY[company]
    return None


class ProductKind:
    EARBUDS = "earbuds"
    HEADPHONES = "headphones"
    SPEAKER = "speaker"
    WATCH = "watch"
    CONTROLLER = "controller"


_KIND_PATTERNS = (
    (ProductKind.WATCH, r"\bwatch\b|\bband\b|\bforerunner\b|\bf[eē]nix\b|\bvenu\b|\bamazfit\b"),
    (ProductKind.EARBUDS, r"\bbuds\b|\bairpods\b|\bearbuds\b|\bfreebuds\b|\blinkbuds\b|\bwf-\w+|\bear ?\(\d"),
    (ProductKind.HEADPHONES, r"\bheadphones?\b|\bwh-\w+|\bquietcomfort\b|\bmomentum\b"),
    (ProductKind.SPEAKER, r"\bspeaker\b|\bsoundlink\b|\bsoundbar\b|\bsrs-\w+"),
    (ProductKind.CONTROLLER, r"\bcontroller\b|\bdualsense\b|\bjoy-con\b|\bgamepad\b"),
)
_KIND_COMPILED = tuple((kind, re.compile(pattern, re.IGNORECASE)) for kind, pattern in _KIND_PATTERNS)

KIND_LABELS = {
    ProductKind.EARBUDS: _("Earbuds"),
    ProductKind.HEADPHONES: _("Headphones"),
    ProductKind.SPEAKER: _("Speaker"),
    ProductKind.WATCH: _("Smartwatch"),
    ProductKind.CONTROLLER: _("Game Controller"),
}

# Class names that carry no information, so a name-derived kind may replace them.
_UNINFORMATIVE_CATEGORIES = {"", _("Unknown"), _("Uncategorized"), _("Miscellaneous")}


def product_kind(name: str) -> str | None:
    for kind, pattern in _KIND_COMPILED:
        if pattern.search(name):
            return kind
    return None


def display_category(category: str, kind: str | None) -> str:
    """Keep the real Bluetooth class; fall back to the name-derived kind only when it says nothing."""
    if category in _UNINFORMATIVE_CATEGORIES and kind is not None:
        return KIND_LABELS[kind]
    return category
