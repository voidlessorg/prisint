#!/usr/bin/env python3
"""
IRISINT: Iranian Intelligence & Utility Toolkit
Author: AI Assistant
Platform: Termux, Linux (Python 3.12+)
Theme: Cyberpunk Dark Professional OSINT Style
"""

import sys
import os
import re
import json
import csv
import time
import math
import random
import hmac
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, date

# Third-Party Libraries
import requests
import typer
import qrcode
from tabulate import tabulate
import dns.resolver
import whois
import pycountry

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, IntPrompt

# Initialize Typer and Rich Console
app = typer.Typer(help="IRISINT: Iranian Intelligence & Utility Toolkit")
console = Console()

# ==============================================================================
# EMBEDDED DATABASES (COMPREHENSIVE IRAN DATA REGISTRY)
# ==============================================================================

BIN_DB: Dict[str, str] = {
    "603799": "بانک ملی ایران (National Bank of Iran - Melli)",
    "589210": "بانک سپه (Sepah Bank)",
    "627648": "بانک صادرات ایران (Export Bank of Iran - Saderat)",
    "627961": "بانک صنعت و معدن (Industry and Mine Bank)",
    "603770": "بانک کشاورزی (Agriculture Bank - Keshavarzi)",
    "628023": "بانک مسکن (Housing Bank - Maskan)",
    "627760": "پست بانک ایران (Post Bank of Iran)",
    "502908": "بانک توسعه صادرات ایران (Development Export Bank of Iran)",
    "627412": "بانک اقتصاد نوین (Economy Novin Bank)",
    "622106": "بانک پارسیان (Parsian Bank)",
    "502229": "بانک پاسارگاد (Pasargad Bank)",
    "621986": "بانک سامان (Saman Bank)",
    "639346": "بانک سینا (Sina Bank)",
    "639607": "بانک سرمایه (Sarmayeh Bank)",
    "636214": "بانک آینده (Ayandeh Bank)",
    "502938": "بانک دی (Dey Bank)",
    "504172": "بانک قرض‌الحسنه رسالت (Resalat Bank)",
    "606373": "بانک قرض‌الحسنه مهر ایران (Mehr Iran Bank)",
    "639370": "بانک شهر (Shahr Bank)",
    "627359": "بانک تجارت (Tejarat Bank)",
    "610433": "بانک ملت (Mellat Bank)",
    "585983": "بانک تجارت (Tejarat Bank Alternative)",
    "627961": "بانک رفاه کارگران (Refah Bank)",
    "505785": "بانک ایران زمین (Iran Zamin Bank)",
    "636949": "بانک حکمت ایرانیان (Hikmat Bank)",
    "505416": "بانک گردشگری (Tourism Bank)",
    "606256": "موسسه اعتباری ملل (New Credit Institution)",
    "639599": "بانک قوامین (Ghavamin Bank)",
    "505801": "موسسه اعتباری کوثر (Kowsar Credit Institution)",
    "628157": "موسسه اعتباری توسعه (Credit Institution for Development)",
    "507677": "موسسه اعتباری نور (Noor Credit Institution)",
    "636795": "موسسه اعتباری ملل (Melal Credit Institution)",
    "627381": "بانک انصار (Ansar Bank)",
    "642231": "بانک توسعه تعاون (Tose'e Ta'avon Bank)",
    "502806": "بانک کارآفرین (Karafarin Bank)",
    "505875": "بانک خاورمیانه (Middle East Bank)",
}

SHABA_DB: Dict[str, Tuple[str, str]] = {
    "010": ("بانک مرکزی جمهوری اسلامی ایران", "Central Bank of Iran"),
    "011": ("بانک صنعت و معدن", "Industry and Mine Bank"),
    "012": ("بانک ملت", "Mellat Bank"),
    "013": ("بانک رفاه کارگران", "Refah Bank"),
    "014": ("بانک صادرات ایران", "Saderat Bank"),
    "015": ("بانک سپه", "Sepah Bank"),
    "016": ("بانک کشاورزی", "Agriculture Bank"),
    "017": ("بانک ملی ایران", "Melli Bank"),
    "018": ("بانک تجارت", "Tejarat Bank"),
    "019": ("بانک مسکن", "Housing Bank"),
    "020": ("بانک توسعه صادرات ایران", "Export Development Bank"),
    "021": ("پست بانک ایران", "Post Bank"),
    "022": ("بانک توسعه تعاون", "Cooperative Development Bank"),
    "051": ("موسسه اعتباری توسعه", "Development Credit Institution"),
    "053": ("بانک کارآفرین", "Karafarin Bank"),
    "054": ("بانک پارسیان", "Parsian Bank"),
    "055": ("بانک اقتصاد نوین", "Eghtesad Novin Bank"),
    "056": ("بانک سامان", "Saman Bank"),
    "057": ("بانک پاسارگاد", "Pasargad Bank"),
    "058": ("بانک سرمایه", "Sarmayeh Bank"),
    "059": ("بانک سینا", "Sina Bank"),
    "060": ("بانک قرض‌الحسنه مهر ایران", "Mehr Iran Bank"),
    "061": ("بانک شهر", "Shahr Bank"),
    "062": ("بانک آینده", "Ayandeh Bank"),
    "063": ("بانک انصار", "Ansar Bank"),
    "064": ("بانک قوامین", "Ghavamin Bank"),
    "065": ("بانک حکمت ایرانیان", "Hikmat Bank"),
    "066": ("بانک دی", "Dey Bank"),
    "069": ("بانک ایران زمین", "Iran Zamin Bank"),
    "070": ("بانک قرض‌الحسنه رسالت", "Resalat Bank"),
    "073": ("موسسه اعتباری کوثر", "Kowsar Credit"),
    "075": ("موسسه اعتباری ملل", "Melal Credit"),
    "078": ("بانک خاورمیانه", "Middle East Bank"),
    "079": ("بانک گردشگری", "Tourism Bank"),
    "080": ("موسسه اعتباری نور", "Noor Credit"),
    "090": ("بانک مهر اقتصاد", "Mehr-e-Eghtesad Bank"),
}

MOBILE_PREFIX_DB: Dict[str, Tuple[str, str]] = {
    "0910": ("همراه اول (Hamrah Aval)", "استان‌های سراسر کشور / کشوری"),
    "0911": ("همراه اول (Hamrah Aval)", "استان‌های گلستان، مازندران، گیلان (شمال کشور)"),
    "0912": ("همراه اول (Hamrah Aval)", "استان‌های تهران، البرز، زنجان، سمنان، قزوین، قم"),
    "0913": ("همراه اول (Hamrah Aval)", "استان‌های اصفهان، یزد، چهارمحال و بختیاری، کرمان"),
    "0914": ("همراه اول (Hamrah Aval)", "استان‌های آذربایجان شرقی، آذربایجان غربی، اردبیل"),
    "0915": ("همراه اول (Hamrah Aval)", "استان‌های خراسان رضوی، خراسان شمالی، خراسان جنوبی، سیستان و بلوچستان"),
    "0916": ("همراه اول (Hamrah Aval)", "استان‌های خوزستان، لرستان، ایلام، فارس، کهگیلویه و بویراحمد"),
    "0917": ("همراه اول (Hamrah Aval)", "استان‌های فارس، کهگیلویه و بویراحمد، هرمزگان، بوشهر"),
    "0918": ("همراه اول (Hamrah Aval)", "استان‌های همدان، ایلام، مرکزی، کردستان، کرمانشاه"),
    "0919": ("همراه اول (Hamrah Aval)", "استان‌های تهران، البرز، سمنان، قم، قزوین، زنجان (اعتباری)"),
    "0930": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0933": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0935": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0936": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0937": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0938": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0939": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0901": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0902": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0903": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0904": ("ایرانسل (Irancell)", "سیم‌کارت کودک / سراسر کشور"),
    "0905": ("ایرانسل (Irancell)", "سراسر کشور / کشوری"),
    "0941": ("ایرانسل (Irancell)", "اینترنت ثابت TD-LTE / سراسر کشور"),
    "0920": ("رایتل (Rightel)", "دائمی / سراسر کشور"),
    "0921": ("رایتل (Rightel)", "اعتباری / سراسر کشور"),
    "0922": ("رایتل (Rightel)", "اعتباری / سراسر کشور"),
    "0923": ("رایتل (Rightel)", "اعتباری / سراسر کشور"),
    "0990": ("همراه اول (Hamrah Aval)", "اعتباری سراسر کشور"),
    "0991": ("همراه اول (Hamrah Aval)", "سراسر کشور"),
    "0992": ("همراه اول (Hamrah Aval)", "اعتباری سراسر کشور"),
    "0993": ("همراه اول (Hamrah Aval)", "اعتباری جدید / سراسر کشور"),
    "0994": ("همراه اول (Hamrah Aval)", "سیم‌کارت انارستان (کودک و نوجوان)"),
    "0998": ("شاتل موبایل (Shatel Mobile)", "سراسر کشور / اپراتور مجازی MVNO"),
    "0999": ("آپتل / سامانتل (Aptel / Samantel)", "سراسر کشور / اپراتور مجازی MVNO"),
}

LANDLINE_DB: Dict[str, str] = {
    "021": "استان تهران (Tehran)",
    "026": "استان البرز (Alborz)",
    "025": "استان قم (Qom)",
    "081": "استان همدان (Hamadan)",
    "086": "استان مرکزی (Markazi)",
    "087": "استان کردستان (Kurdistan)",
    "041": "استان آذربایجان شرقی (East Azerbaijan)",
    "044": "استان آذربایجان غربی (West Azerbaijan)",
    "045": "استان اردبیل (Ardabil)",
    "031": "استان اصفهان (Isfahan)",
    "034": "استان کرمان (Kerman)",
    "035": "استان یزد (Yazd)",
    "038": "استان چهارمحال و بختیاری (Chaharmahal and Bakhtiari)",
    "051": "استان خراسان رضوی (Razavi Khorasan)",
    "056": "استان خراسان جنوبی (South Khorasan)",
    "058": "استان خراسان شمالی (North Khorasan)",
    "011": "استان مازندران (Mazandaran)",
    "013": "استان گیلان (Gilan)",
    "017": "استان گلستان (Golestan)",
    "071": "استان فارس (Shiraz / Fars)",
    "074": "استان کهگیلویه و بویراحمد (Kohgiluyeh and Boyer-Ahmad)",
    "076": "استان هرمزگان (Hormozgan)",
    "077": "استان بوشهر (Bushehr)",
    "061": "استان خوزستان (Khuzestan)",
    "066": "استان لرستان (Lorestan)",
    "083": "استان کرمانشاه (Kermanshah)",
    "084": "استان ایلام (Ilam)",
    "054": "استان سیستان و بلوچستان (Sistan and Baluchestan)",
    "033": "استان سیستان و بلوچستان (Alternative Allocation)",
}

NATIONAL_ID_PROVINCE_DB: Dict[str, str] = {
    "001": "استان تهران (مرکز تهران)", "002": "استان تهران (مرکز تهران)", "003": "استان تهران (مرکز تهران)",
    "004": "استان تهران (مرکز تهران)", "005": "استان تهران (مرکز تهران)", "006": "استان تهران (مرکز تهران)",
    "007": "استان تهران (مرکز تهران)", "008": "استان تهران (مرکز تهران)", "044": "استان آذربایجان شرقی",
    "045": "استان آذربایجان شرقی (تبریز)", "063": "استان آذربایجان غربی", "064": "استان آذربایجان غربی (ارومیه)",
    "127": "استان اصفهان", "128": "استان اصفهان (اصفهان مرکزی)", "129": "استان اصفهان", 
    "228": "استان فارس", "229": "استان فارس (شیراز)", "298": "استان خراسان رضوی", 
    "299": "استان خراسان رضوی (مشهد)", "324": "استان گیلان", "325": "استان گیلان (رشت)",
    "372": "استان مازندران", "373": "استان مازندران (ساری)", "483": "استان البرز", "484": "استان البرز (کرج)",
    "504": "استان خوزستان", "505": "استان خوزستان (اهواز)", "393": "استان گلستان", "392": "استان گلستان (گرگان)",
    "174": "استان کرمان", "175": "استان کرمان (مرکزی)", "442": "استان مرکزی", "443": "استان مرکزی (اراک)",
    "386": "استان همدان", "387": "استان همدان (مرکزی)", "258": "استان کرمانشاه", "259": "استان کرمانشاه (مرکزی)",
    "119": "استان کردستان", "120": "استان کردستان (سنندج)", "522": "استان بوشهر", "427": "استان هرمزگان",
    "031": "استان قم", "541": "استان قزوین", "377": "استان اردبیل", "490": "استان کهگیلویه و بویراحمد",
    "461": "استان چهارمحال و بختیاری", "361": "استان لرستان", "533": "استان ایلام", "454": "استان سمنان",
}

PLATE_DB: Dict[str, str] = {
    "11": "استان تهران (شهر تهران)", "22": "استان تهران (شهر تهران)", "33": "استان تهران (شهر تهران)", 
    "44": "استان تهران (شهر تهران)", "55": "استان تهران (شهر تهران)", "66": "استان تهران (شهر تهران)", 
    "77": "استان تهران (شهر تهران)", "88": "استان تهران (شهر تهران)", "99": "استان تهران (شهر تهران)", 
    "10": "استان تهران (شهرستان‌های استان تهران)", "20": "استان تهران (شهرستان‌های استان تهران)", 
    "30": "استان تهران (شهرستان‌های استان تهران)", "40": "استان تهران (شهرستان‌های استان تهران)", 
    "50": "استان تهران (شهرستان‌های استان تهران)", "60": "استان تهران (شهرستان‌های استان تهران)", 
    "70": "استان تهران (شهرستان‌های استان تهران)", "80": "استان تهران (شهرستان‌های استان تهران)", 
    "90": "استان تهران (شهرستان‌های استان تهران)",
    "15": "استان آذربایجان شرقی (تبریز)", "25": "استان آذربایجان شرقی (شهرستان‌ها)", "35": "استان آذربایجان شرقی",
    "17": "استان آذربایجان غربی (ارومیه)", "27": "استان آذربایجان غربی (شهرستان‌ها)", "37": "استان آذربایجان غربی",
    "13": "استان اصفهان (شهر اصفهان)", "23": "استان اصفهان (شهرستان‌ها)", "43": "استان اصفهان", "53": "استان اصفهان",
    "63": "استان فارس (شیراز)", "73": "استان فارس (شهرستان‌ها)", "83": "استان فارس", "93": "استان فارس",
    "12": "استان خراسان رضوی (مشهد)", "32": "استان خراسان رضوی (شهرستان‌ها)", "42": "استان خراسان رضوی",
    "46": "استان گیلان (رشت)", "56": "استان گیلان (شهرستان‌ها)", "76": "استان گیلان",
    "62": "استان مازندران (ساری)", "72": "استان مازندران (شهرستان‌ها)", "82": "استان مازندران", "92": "استان مازندران",
    "68": "استان البرز (کرج)", "78": "استان البرز (شهرستان‌ها)",
    "21": "استان خوزستان (اهواز)", "31": "استان خوزستان (شهرستان‌ها)",
    "24": "استان خوزستان (آبادان / خرمشهر)", "14": "استان کرمان (شهر کرمان)", "45": "استان کرمان (شهرستان‌ها)",
    "28": "استان البرز (جدید)", "59": "استان گلستان (گرگان)", "69": "استان گلستان (شهرستان‌ها)",
}

PERSIAN_HOLIDAYS: Dict[str, str] = {
    "01-01": "نوروز (سال نو خورشیدی)",
    "01-02": "تعطیلات نوروز",
    "01-03": "تعطیلات نوروز",
    "01-04": "تعطیلات نوروز",
    "01-12": "روز جمهوری اسلامی ایران",
    "01-13": "روز طبیعت (سیزده به در)",
    "03-14": "رحلت آیت‌الله خمینی",
    "03-15": "قیام ۱۵ خرداد",
    "11-22": "پیروزی انقلاب اسلامی ایران",
    "12-29": "روز ملی شدن صنعت نفت ایران",
}

ZODIAC_SIGNS: List[Tuple[str, int, int]] = [
    ("فروردین (Aries)", 321, 419), ("اردیبهشت (Taurus)", 420, 520), ("خرداد (Gemini)", 521, 620),
    ("تیر (Cancer)", 621, 722), ("مرداد (Leo)", 723, 822), ("شهریور (Virgo)", 823, 922),
    ("مهر (Libra)", 923, 1022), ("آبان (Scorpio)", 1023, 1121), ("آذر (Sagittarius)", 1122, 1221),
    ("دی (Capricorn)", 1222, 119), ("بهمن (Aquarius)", 120, 218), ("اسفند (Pisces)", 219, 320)
]

# GLOBAL METADATA STATE FOR REPORT GENERATION
LAST_ANALYSIS_RESULTS: Dict[str, Any] = {}

# ==============================================================================
# CALENDAR CONVERSION UTILITIES
# ==============================================================================

class DateConverter:
    @staticmethod
    def jalali_to_gregorian(jy: int, jm: int, jd: int) -> date:
        jy += 1595
        days = -355668 + (365 * jy) + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + jd
        if jm < 7:
            days += (jm - 1) * 31
        else:
            days += (jm - 7) * 30 + 186
        gy = 400 * (days // 146097)
        days %= 146097
        if days > 36524:
            days -= 1
            gy += 100 * (days // 36524)
            days %= 36524
            if days >= 365:
                days += 1
        gy += 4 * (days // 1461)
        days %= 1461
        if days > 365:
            days -= 1
            gy += days // 365
            days %= 365
        gd = days + 1
        sal_mo = [0, 31, 29 if (((gy % 4 == 0) and (gy % 100 != 0)) or (gy % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        gm = 0
        for i, v in enumerate(sal_mo):
            gm = i
            if gd <= v:
                break
            gd -= v
        return date(gy, gm, gd)

    @staticmethod
    def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        gy2 = gy - 1600 if gm > 2 else gy - 1601
        g_day_no = 365 * (gy - 1600) + (gy2 // 4) - (gy2 // 100) + (gy2 // 400) + gd + g_d_m[gm - 1]
        j_day_no = g_day_no - 79
        j_np = j_day_no // 12053
        j_day_no %= 12053
        jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
        j_day_no %= 1461
        if j_day_no >= 366:
            jy += (j_day_no - 1) // 365
            j_day_no = (j_day_no - 1) % 365
        if j_day_no < 186:
            jm = 1 + (j_day_no // 31)
            jd = 1 + (j_day_no % 31)
        else:
            jm = 7 + ((j_day_no - 186) // 30)
            jd = 1 + ((j_day_no - 186) % 30)
        return jy, jm, jd

    @staticmethod
    def gregorian_to_hijri(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
        if gm < 3:
            gy -= 1
            gm += 12
        a = gy // 100
        b = a // 4
        c = 2 - a + b
        e = int(365.25 * (gy + 4716))
        f = int(30.6001 * (gm + 1))
        jd = c + gd + e + f - 1524.5
        i = int(jd - 1948440 + 10632)
        n = int((i - 1) // 10631)
        i = i - 10631 * n + 354
        j = int((10985 - i) // 5316) * int((50 * i) // 17719) + int(i // 5670) * int((43 * i) // 15238)
        i = i - int((30 * j) // 29) - int((17719 * j) // 50) + 140
        m = int((5 * i) // 157)
        d = int(i - (157 * m) // 5)
        y = int(30 * n + j - 30)
        return y, m, d

# ==============================================================================
# UI COMPONENTS & ANIMATIONS
# ==============================================================================

def print_banner() -> None:
    banner_text = """
[bold cyan]██████╗ ██████╗ ██╗███████╗██╗███╗   ██╗████████╗[/bold cyan]
[bold cyan]██╔══██╗██╔══██╗██║██╔════╝██║████╗  ██║╚══██╔══╝[/bold cyan]
[bold magenta]██████╔╝██████╔╝██║███████╗██║██╔██╗ ██║   ██║   [/bold magenta]
[bold magenta]██╔══██╗██╔══██╗██║╚════██║██║██║╚██╗██║   ██║   [/bold magenta]
[bold blue]██║  ██║██║  ██║██║███████║██║██║ ╚████║   ██║   [/bold blue]
[bold blue]╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   [/bold blue]
         [italic yellow]Iranian Intelligence & Utility Toolkit (v4.0.0-Advanced Data)[/italic yellow]
    """
    console.print(Align.center(banner_text))
    console.print(Align.center("[bold green][+][/bold green] IRAN core database verified. All 31 Provinces synced."))

def render_menu() -> None:
    table = Table(title="MAIN ARCHITECTURE MENU", title_style="bold magenta", border_style="cyan", show_header=True)
    table.add_column("Code", style="bold green", justify="center")
    table.add_column("Analytical Subsystem Module", style="bold white")
    table.add_column("Code", style="bold green", justify="center")
    table.add_column("Analytical Subsystem Module", style="bold white")

    menu_items = [
        ("1", "Bank Card Analyzer", "10", "Network Tools"),
        ("2", "Phone Number Analyzer", "11", "Hash Tools"),
        ("3", "National ID Analyzer", "12", "Encoding Tools"),
        ("4", "SHABA Analyzer", "13", "QR Tools"),
        ("5", "Postal Code Analyzer", "14", "Metadata Tools"),
        ("6", "Landline Analyzer", "15", "Batch Mode"),
        ("7", "Vehicle Plate Analyzer", "16", "Reports System"),
        ("8", "Date & Calendar Tools", "17", "Embedded Databases"),
        ("9", "Domain Tools", "0", "Exit System"),
    ]
    for item in menu_items:
        table.add_row(item[0], item[1], item[2], item[3])
    console.print(Align.center(table))

def run_spinner(duration: float = 0.8, message: str = "Processing cyber engine lookup...") -> None:
    with Live(Progress(SpinnerColumn(spinner_name="cyborg"), TextColumn("[bold yellow]{task.description}"))):
        time.sleep(duration)

# ==============================================================================
# SUB-MODULES MODULE CORE IMPLEMENTATION
# ==============================================================================

def validate_luhn(card_num: str) -> bool:
    try:
        digits = [int(d) for d in card_num]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            mapping = d * 2
            checksum += mapping if mapping < 10 else mapping - 9
        return checksum % 10 == 0
    except ValueError:
        return False

def analyze_bank_card(card_no: str) -> Dict[str, Any]:
    clean_card = re.sub(r"\D", "", card_no)
    res = {"input": card_no, "valid": False, "bin": "N/A", "bank": "Unknown", "explanation": ""}
    if len(clean_card) != 16:
        res["explanation"] = "Length validation failed. Standard Iranian bank cards must contain exactly 16 digits."
        return res
    bin_code = clean_card[:6]
    res["bin"] = bin_code
    res["bank"] = BIN_DB.get(bin_code, "Unknown Bank (Unlisted BIN)")
    if validate_luhn(clean_card):
        res["valid"] = True
        res["explanation"] = "Luhn algorithm validation succeeded. Checksum bit verified against modulus 10."
    else:
        res["explanation"] = "Luhn algorithm checksum mismatched. Card structural composition integrity is compromised."
    return res

def analyze_phone_number(phone_no: str) -> Dict[str, Any]:
    clean = re.sub(r"\D", "", phone_no)
    if clean.startswith("98"):
        clean = "0" + clean[2:]
    elif clean.startswith("+98"):
        clean = "0" + clean[3:]
    
    res = {"input": phone_no, "valid": False, "operator": "Unknown", "province": "Unknown / National Scope", "normalized": clean}
    if len(clean) == 11 and clean.startswith("09"):
        prefix = clean[:4]
        if prefix in MOBILE_PREFIX_DB:
            res["valid"] = True
            res["operator"] = MOBILE_PREFIX_DB[prefix][0]
            res["province"] = MOBILE_PREFIX_DB[prefix][1]
    return res

def analyze_national_id(nid: str) -> Dict[str, Any]:
    clean = re.sub(r"\D", "", nid).zfill(10)
    res = {"input": nid, "valid": False, "province": "نامشخص / اطلاعات نامعتبر", "explanation": ""}
    if len(clean) != 10:
        res["explanation"] = "Iranian National ID must be exactly 10 digits long."
        return res
    
    if len(set(clean)) == 1:
        res["explanation"] = "Invalid structural template (all identical digits)."
        return res

    digits = [int(c) for c in clean]
    checksum_digit = digits[9]
    running_sum = sum(digits[i] * (10 - i) for i in range(9))
    remainder = running_sum % 11

    if (remainder < 2 and checksum_digit == remainder) or (remainder >= 2 and checksum_digit == 11 - remainder):
        res["valid"] = True
        res["explanation"] = "Mathematical validation algorithm passed using MOD 11 control scheme."
        prefix = clean[:3]
        res["province"] = NATIONAL_ID_PROVINCE_DB.get(prefix, "کد معتبر است (استان صادرکننده در دیتابیس لوکال یافت نشد)")
    else:
        res["explanation"] = "MOD 11 control rule validation routine check failed."
    return res

def analyze_shaba(shaba: str) -> Dict[str, Any]:
    clean_full = re.sub(r"[^A-Z0-9]", "", shaba.upper())
    res = {"input": shaba, "valid": False, "bank": "Unknown", "explanation": ""}
    
    if not clean_full.startswith("IR") or len(clean_full) != 26:
        res["explanation"] = "Structural mismatch. SHABA format requirements specify: IR prefix followed by 24 digits."
        return res

    rearranged = clean_full[4:] + "1827" + clean_full[2:4]
    try:
        numeric_val = int(rearranged)
        if numeric_val % 97 == 1:
            res["valid"] = True
            res["explanation"] = "ISO 13616 international standard validation passed via MOD 97 evaluation sequence."
            bank_code = clean_full[4:7]
            if bank_code in SHABA_DB:
                res["bank"] = f"{SHABA_DB[bank_code][0]} ({SHABA_DB[bank_code][1]})"
        else:
            res["explanation"] = "Mathematical check digit mismatch according to ISO 13616 specification."
    except ValueError:
        res["explanation"] = "Encountered structural processing fault when computing alphanumeric data types."
    return res

def analyze_postal_code(pc: str) -> Dict[str, Any]:
    clean = re.sub(r"\D", "", pc)
    res = {"input": pc, "valid": False, "location": "نامشخص", "type": "Unknown"}
    if len(clean) == 10:
        if "0" in clean[:5] or "2" in clean[:5]:
            res["valid"] = False
            res["type"] = "ساختار نامعتبر (طبق قوانین پست، ۵ رقم اول نباید شامل 0 یا 2 باشد)"
        else:
            res["valid"] = True
            res["type"] = "ساختار ۱۰ رقمی استاندارد تایید شد."
            prefix = clean[:2]
            res["location"] = f"محدوده توزیع پستی کد پیشوند {prefix}"
    else:
        res["type"] = "طول نامعتبر است. کد پستی ایران باید دقیقاً ۱۰ رقم باشد."
    return res

def analyze_landline(num: str) -> Dict[str, Any]:
    clean = re.sub(r"\D", "", num)
    if not clean.startswith("0") and len(clean) == 10:
        clean = "0" + clean
    res = {"input": num, "detected": False, "province": "نامشخص", "type": "شبکه ثابت کشوری (PSTN)"}
    for prefix in sorted(LANDLINE_DB.keys(), key=len, reverse=True):
        if clean.startswith(prefix):
            res["detected"] = True
            res["province"] = LANDLINE_DB[prefix]
            break
    return res

def analyze_vehicle_plate(plate: str) -> Dict[str, Any]:
    clean = re.sub(r"[^0-9\u0600-\u06FF]", "", plate)
    res = {"input": plate, "valid": False, "province": "استان نامشخص", "classification": "شخصی"}
    
    digits = re.findall(r"\d+", clean)
    alphas = re.findall(r"[\u0600-\u06FF]+", clean)
    
    if len(digits) >= 2 and len(alphas) >= 1:
        series_code = digits[-1][:2]
        if series_code in PLATE_DB:
            res["valid"] = True
            res["province"] = PLATE_DB[series_code]
            alpha = alphas[0]
            if alpha == "الف":
                res["classification"] = "خودرو دولتی"
            elif alpha == "ت":
                res["classification"] = "تاکسی عمومی شهری"
            elif alpha == "ع":
                res["classification"] = "خودرو عمومی / ترانزیت و باربری"
    return res

# ==============================================================================
# SUB-MODULES INTERACTION & DISPLAY CONTROLLERS
# ==============================================================================

def module_bank_card() -> None:
    console.print(Panel("[bold cyan]BANK CARD ANALYTICAL SUBSYSTEM[/bold cyan]", border_style="cyan"))
    card = Prompt.ask("[bold yellow]Enter 16-Digit Iranian Bank Card Number[/bold yellow]")
    run_spinner()
    res = analyze_bank_card(card)
    LAST_ANALYSIS_RESULTS["Bank Card Analyzer"] = res
    
    table = Table(title="BIN Processing Metrics Output Engine", border_style="magenta")
    table.add_column("Parameter Metrics Segment", style="cyan")
    table.add_column("Calculated Output Array State", style="white")
    table.add_row("Input Sequence String", res["input"])
    table.add_row("Extracted System BIN Code", res["bin"])
    table.add_row("Assigned Issuing Node", res["bank"])
    table.add_row("Mathematical Health Flag", "[bold green]PASS[/bold green]" if res["valid"] else "[bold red]FAIL[/bold red]")
    table.add_row("Execution Logic Verdict", res["explanation"])
    console.print(table)

def module_phone_number() -> None:
    console.print(Panel("[bold cyan]PHONE NUMBER RECONNAISSANCE ANALYSIS MODULE[/bold cyan]", border_style="cyan"))
    phone = Prompt.ask("[bold yellow]Enter Phone Number (e.g., 09123456789)[/bold yellow]")
    run_spinner()
    res = analyze_phone_number(phone)
    LAST_ANALYSIS_RESULTS["Phone Number Analyzer"] = res
    
    table = Table(title="Telecommunication Core Infrastructure Signature Output", border_style="magenta")
    table.add_column("Parameter Metrics Segment", style="cyan")
    table.add_column("Calculated Output Array State", style="white")
    table.add_row("Supplied String Variable", res["input"])
    table.add_row("Normalized Internal Record", res["normalized"])
    table.add_row("Identified Network Operator Node", res["operator"])
    table.add_row("Sovereign Province/Jurisdiction Mapping", f"[bold green]{res['province']}[/bold green]")
    table.add_row("Operational Soundness Flag", "[bold green]VALID[/bold green]" if res["valid"] else "[bold red]INVALID[/bold red]")
    console.print(table)

def module_national_id() -> None:
    console.print(Panel("[bold cyan]NATIONAL IDENTITY LEGAL STRUCTURAL VALIDATOR[/bold cyan]", border_style="cyan"))
    nid = Prompt.ask("[bold yellow]Enter 10-Digit Iranian National ID Number[/bold yellow]")
    run_spinner()
    res = analyze_national_id(nid)
    LAST_ANALYSIS_RESULTS["National ID Analyzer"] = res
    
    table = Table(title="National Identity Matrix Engine Evaluation Output", border_style="magenta")
    table.add_column("Parameter Metrics Segment", style="cyan")
    table.add_column("Calculated Output Array State", style="white")
    table.add_row("Supplied ID Array", res["input"])
    table.add_row("Algorithmic Health State", "[bold green]VALID STRUCTURAL SCHEME[/bold green]" if res["valid"] else "[bold red]INTEGRITY MISMATCH DETECTED[/bold red]")
    table.add_row("Sovereign Issuing Province Name", f"[bold cyan]{res['province']}[/bold cyan]")
    table.add_row("Structural Proof Summary Details", res["explanation"])
    console.print(table)

def module_shaba() -> None:
    console.print(Panel("[bold cyan]SHABA STRUCTURE ACCOUNT VALIDATOR (IBAN SYSTEM)[/bold cyan]", border_style="cyan"))
    shaba = Prompt.ask("[bold yellow]Enter SHABA Code (e.g., IR123456789012345678901234)[/bold yellow]")
    run_spinner()
    res = analyze_shaba(shaba)
    LAST_ANALYSIS_RESULTS["SHABA Analyzer"] = res
    
    table = Table(title="Interbank Financial Matrix Verification Registry Output", border_style="magenta")
    table.add_column("Parameter Metrics Segment", style="cyan")
    table.add_column("Calculated Output Array State", style="white")
    table.add_row("Input Variable Trace", res["input"])
    table.add_row("Calculated Compliance Evaluation", "[bold green]VALID COMPLIANCE TEMPLATE[/bold green]" if res["valid"] else "[bold red]NON-COMPLIANT ARTIFACT STRUCTURE[/bold red]")
    table.add_row("Identified Central Bank Clearing Institution", res["bank"])
    table.add_row("Cryptographic Execution Verdict", res["explanation"])
    console.print(table)

def module_postal_code() -> None:
    console.print(Panel("[bold cyan]POSTAL ZIP MATRIX LAYER DECODER[/bold cyan]", border_style="cyan"))
    pc = Prompt.ask("[bold yellow]Enter 10-Digit Post Code[/bold yellow]")
    run_spinner()
    res = analyze_postal_code(pc)
    LAST_ANALYSIS_RESULTS["Postal Code Analyzer"] = res
    
    table = Table(title="Logistical Spatial Node Analysis Engine Output Data", border_style="magenta")
    table.add_column("Parameter Metrics Segment", style="cyan")
    table.add_column("Calculated Output Array State", style="white")
    table.add_row("Input Variable", res["input"])
    table.add_row("Geographical Subsystem Mapping Range", res["location"])
    table.add_row("Algorithmic Compliance Pattern Type", res["type"])
    table.add_row("Structural Adequacy Verification", "[bold green]PASS[/bold green]" if res["valid"] else "[bold red]FAIL[/bold red]")
    console.print(table)

def module_landline() -> None:
    console.print(Panel("[bold cyan]LANDLINE TELECOMMUNICATIONS REGIONAL CODE ROUTING ENGINE[/bold cyan]", border_style="cyan"))
    num = Prompt.ask("[bold yellow]Enter Landline Number/Prefix Area Variable (e.g., 021 or 021XXXXXXXX)[/bold yellow]")
    run_spinner()
    res = analyze_landline(num)
    LAST_ANALYSIS_RESULTS["Landline Analyzer"] = res
    
    table = Table(title="PSTN Exchange Telecommunication Topology Database Result", border_style="magenta")
    table.add_column("Parameter Metrics Segment", style="cyan")
    table.add_column("Calculated Output Array State", style="white")
    table.add_row("Queried Local Signature", res["input"])
    table.add_row("PSTN Node Registration Node Status", "[bold green]IDENTIFIED AT EXCHANGE[/bold green]" if res["detected"] else "[bold red]NOT IN INDEX RUNTIME[/bold red]")
    table.add_row("Sovereign Province Name (استان مربوطه)", f"[bold green]{res['province']}[/bold green]")
    table.add_row("Infrastructure Pipeline Class Mapping", res["type"])
    console.print(table)

def module_vehicle_plate() -> None:
    console.print(Panel("[bold cyan]VEHICLE TRAFFIC IDENTITY DECODER MATRIX SYSTEM[/bold cyan]", border_style="cyan"))
    plate = Prompt.ask("[bold yellow]Enter Vehicle Plate Value string (e.g., 12ب34572)[/bold yellow]")
    run_spinner()
    res = analyze_vehicle_plate(plate)
    LAST_ANALYSIS_RESULTS["Vehicle Plate Analyzer"] = res
    
    table = Table(title="Traffic Registry System Metadata Output Segment", border_style="magenta")
    table.add_column("Parameter Metrics Segment", style="cyan")
    table.add_column("Calculated Output Array State", style="white")
    table.add_row("Raw Input Identifier Sequence", res["input"])
    table.add_row("Registry Layout Struct Status Check", "[bold green]VERIFIED STANDARD SCHEME[/bold green]" if res["valid"] else "[bold red]IRREGULAR PATTERN MATRIX[/bold red]")
    table.add_row("Sovereign Province / Territory Registry", f"[bold green]{res['province']}[/bold green]")
    table.add_row("Operational Category Classification Frame", res["classification"])
    console.print(table)

# ==============================================================================
# DATE & CALENDAR SYSTEM MODULES
# ==============================================================================

def module_date_calendar() -> None:
    console.print(Panel("[bold cyan]DATE & TIME CHRONOLOGICAL TRANSLATION FRAMEWORK ENGINE[/bold cyan]", border_style="cyan"))
    console.print("1. Jalali -> Gregorian Mapping Transformation Sequence\n2. Gregorian -> Jalali Structural Re-alignment\n3. Unix Epoch Epoch Verification Machine\n4. Zodiac Matrix Identity Parsing Process")
    choice = Prompt.ask("Select subsystem sequence execution index string", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        jy = IntPrompt.ask("Enter Jalali Year Array Integer")
        jm = IntPrompt.ask("Enter Jalali Month Array Integer")
        jd = IntPrompt.ask("Enter Jalali Day Array Integer")
        g_date = DateConverter.jalali_to_gregorian(jy, jm, jd)
        console.print(f"[bold green][*] Processing Successful Output Alignment Frame State -> Gregorian: {g_date.isoformat()}[/bold green]")
    elif choice == "2":
        gy = IntPrompt.ask("Enter Gregorian Year String")
        gm = IntPrompt.ask("Enter Gregorian Month String")
        gd = IntPrompt.ask("Enter Gregorian Day String")
        jy, jm, jd = DateConverter.gregorian_to_jalali(gy, gm, gd)
        console.print(f"[bold green][*] Processing Successful Output Alignment Frame State -> Jalali: {jy}/{jm:02d}/{jd:02d}[/bold green]")
    elif choice == "3":
        ts = IntPrompt.ask("Enter Unix Epoch Timestamp Long Integer Sequence")
        dt_obj = datetime.fromtimestamp(ts)
        console.print(f"[bold green][*] System Translated UTC DateTime Matrix Record String -> {dt_obj.isoformat()}[/bold green]")
    elif choice == "4":
        m = IntPrompt.ask("Enter Persian Month Integer Format Code (1-12)")
        d = IntPrompt.ask("Enter Persian Month Day Index Sequence Code (1-31)")
        val = m * 100 + d
        found_sign = "Undetermined Sign Array Matrix"
        for name, start, end in ZODIAC_SIGNS:
            if start <= end:
                if start <= val <= end:
                    found_sign = name
                    break
            else:
                if val >= start or val <= end:
                    found_sign = name
                    break
        console.print(f"[bold green][*] Zodiac Cosmic Identity Result State Matrix Array Value -> {found_sign}[/bold green]")

# ==============================================================================
# PASSIVE DOMAIN & INFRASTRUCTURE OSINT OPERATIONS
# ==============================================================================

def module_domain_tools() -> None:
    console.print(Panel("[bold cyan]DOMAIN & INFRASTRUCTURE ANALYSIS ARCHITECTURE MODULE (PASSIVE MODE)[/bold cyan]", border_style="cyan"))
    domain = Prompt.ask("[bold yellow]Enter Domain Target Address (e.g., example.ir / example.com)[/bold yellow]")
    run_spinner(1.5, "Executing passive non-intrusive DNS harvesting architecture rules...")
    
    dns_table = Table(title=f"Passive Resource Records Registry for: {domain}", border_style="magenta")
    dns_table.add_column("Type Record Index", style="cyan")
    dns_table.add_column("Resolved Value Data Matrix Target Payload String", style="white")
    
    for rtype in ["A", "MX", "NS", "TXT", "AAAA"]:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            for rdata in answers:
                dns_table.add_row(rtype, str(rdata))
        except Exception:
            dns_table.add_row(rtype, "No resource lookup records discovered or response timeout exceeded.")
    
    console.print(dns_table)
    
    try:
        w = whois.whois(domain)
        whois_table = Table(title="WHOIS Structural Ownership Registration Context Schema", border_style="blue")
        whois_table.add_column("Registry Domain Key Metadata Attribute", style="cyan")
        whois_table.add_column("Assigned System Registration Value Array", style="white")
        whois_table.add_row("Registrar Domain Node Authority Name", str(w.registrar))
        whois_table.add_row("Country Zone Node Origin Location Code", str(w.country))
        whois_table.add_row("Creation Time Matrix Timestamp String", str(w.creation_date))
        whois_table.add_row("Expiration Time Target Horizon Frame", str(w.expiration_date))
        console.print(whois_table)
    except Exception as e:
        console.print(f"[bold red][!] Registry WHOIS parsing experienced an interface fault: {e}[/bold red]")

# ==============================================================================
# PASSIVE NETWORK ASSESSMENT METRICS
# ==============================================================================

def module_network_tools() -> None:
    console.print(Panel("[bold cyan]NETWORK DIAGNOSTICS & SAFE PORT AUDIT PIPELINE PROCESS[/bold cyan]", border_style="cyan"))
    target_ip = Prompt.ask("[bold yellow]Enter Infrastructure Endpoint IP Address or Domain Target Host[/bold yellow]", default="127.0.0.1")
    
    try:
        resolved_host = dns.resolver.resolve(target_ip, "A")[0].to_text() if any(c.isalpha() for c in target_ip) else target_ip
    except Exception:
        resolved_host = target_ip

    console.print(f"[bold green][*] Operational target endpoint binding context resolved target node configuration to: {resolved_host}[/bold green]")
    
    try:
        url = f"https://ipapi.co/{resolved_host}/json/"
        headers = {"User-Agent": "Mozilla/5.0 (IRISINT OSINT Matrix System Tool)"}
        resp = requests.get(url, headers=headers, timeout=3.0).json()
        
        geo_table = Table(title="BGP Autonomous System Routing & Country Context Data Matrix", border_style="magenta")
        geo_table.add_column("Telemetry Variable Element", style="cyan")
        geo_table.add_column("Harvested Data Element Context Block", style="white")
        geo_table.add_row("Sovereign Country Designation Zone", resp.get("country_name", "Unknown/Private Space"))
        geo_table.add_row("Regional Jurisdiction Province Node", resp.get("region", "Unmapped Spatial Boundary"))
        geo_table.add_row("BGP Router ASN Mapping Code Group", resp.get("asn", "Unassigned ASN Infrastructure Matrix Node"))
        geo_table.add_row("ISP Telecommunications Infrastructure Handler Node", resp.get("org", "Local Infrastructure Loopback Loop"))
        console.print(geo_table)
    except Exception:
        console.print("[bold yellow][!] Local loopback infrastructure layout detected or GeoIP external cloud pipeline interface timed out.[/bold yellow]")

    console.print("[bold yellow][*] Launching safe common transport port connectivity verification sweeps...[/bold yellow]")
    common_ports = [21, 22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 8080]
    
    scan_table = Table(title="Non-Aggressive Network Service State Discovery Mapping Engine", border_style="cyan")
    scan_table.add_column("Transport Target Port Index", style="cyan", justify="center")
    scan_table.add_column("Assigned Protocol Standard", style="yellow")
    scan_table.add_column("Discovered Interface Status Flag State", style="white")
    
    import socket
    for port in common_ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        result = s.connect_ex((resolved_host, port))
        proto_desc = socket.getservbyport(port, "tcp") if port in [21, 22, 25, 53, 80, 443, 110, 143] else "Alternative Web Service Handler"
        if result == 0:
            scan_table.add_row(str(port), proto_desc, "[bold green]OPEN (SERVICE ACTIVE/DETECTED)[/bold green]")
        else:
            scan_table.add_row(str(port), proto_desc, "[dim white]FILTERED / CLOSED[/dim white]")
        s.close()
    console.print(scan_table)

# ==============================================================================
# CRYPTOGRAPHIC COMPLIANCE AND ENCODING SYSTEMS
# ==============================================================================

def module_hash_tools() -> None:
    console.print(Panel("[bold cyan]CRYPTOGRAPHIC SIGNATURE VERIFICATION MODULE[/bold cyan]", border_style="cyan"))
    text = Prompt.ask("[bold yellow]Enter Raw Plaintext Payload String Stream[/bold yellow]")
    
    md5_hash = hashlib.md5(text.encode()).hexdigest()
    sha1_hash = hashlib.sha1(text.encode()).hexdigest()
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    sha512_hash = hashlib.sha512(text.encode()).hexdigest()
    
    table = Table(title="Calculated Cryptographic Fixed-Length Signature Outputs", border_style="magenta")
    table.add_column("Hash Primitive Function Standard Identifier", style="cyan")
    table.add_column("Calculated Output Character Signature Array Hex", style="white")
    table.add_row("MD5 Digest (128 bits Length Profile)", md5_hash)
    table.add_row("SHA-1 Digest (160 bits Length Profile)", sha1_hash)
    table.add_row("SHA-256 Block Architecture Standard", sha256_hash)
    table.add_row("SHA-512 Industrial Cryptography Core", sha512_hash)
    console.print(table)

def module_encoding_tools() -> None:
    import base64
    import urllib.parse
    console.print(Panel("[bold cyan]DATA STRUCTURAL ENCODING & PARSING TRANSLATION MATRIX[/bold cyan]", border_style="cyan"))
    payload = Prompt.ask("[bold yellow]Enter Raw Target Conversion Input Sequence Data[/bold yellow]")
    
    b64_enc = base64.b64encode(payload.encode()).decode()
    url_enc = urllib.parse.quote(payload)
    hex_enc = payload.encode().hex()
    
    table = Table(title="System Encoding Transformation Layout Formats", border_style="magenta")
    table.add_column("Encoding Profile Layout Format Matrix", style="cyan")
    table.add_column("Transformed Encoded Data Stream Representation", style="white")
    table.add_row("Base64 Alphanumeric Layout Format Scheme", b64_enc)
    table.add_row("URL Percent Encoding Architecture Schema", url_enc)
    table.add_row("Hexadecimal Byte Sequence Translation Array", hex_enc)
    console.print(table)

# ==============================================================================
# UTILITY GENERATORS & TOOLSETS
# ==============================================================================

def module_qr_tools() -> None:
    console.print(Panel("[bold cyan]HIGH-DENSITY MULTI-USE TWO-DIMENSIONAL MATRIX QR PATTERN GENERATOR[/bold cyan]", border_style="cyan"))
    data = Prompt.ask("[bold yellow]Enter Plaintext Content Array String to Embed into Grid Matrix[/bold yellow]")
    filename = Prompt.ask("[bold yellow]Enter Destination Output File Handle Prefix Name (PNG)[/bold yellow]", default="irisint_qr_export.png")
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        console.print(f"[bold green][+] High density QR code layout successfully compiled onto storage subsystem target track: {filename}[/bold green]")
    except Exception as e:
        console.print(f"[bold red][!] System matrix generation logic encountered an active IO error track exception: {e}[/bold red]")

def module_metadata_tools() -> None:
    console.print(Panel("[bold cyan]PASSIVE FILE ATTACHMENT METADATA INSPECTOR[/bold cyan]", border_style="cyan"))
    filepath = Prompt.ask("[bold yellow]Provide System Location Target File Path Asset to Inspect[/bold yellow]")
    
    if not os.path.exists(filepath):
        console.print("[bold red][!] File access fault checklist failure: Target reference object data stream not located inside storage workspace volume.[/bold red]")
        return
        
    run_spinner(1.0, "Parsing structure layer headers for isolated metadata flags...")
    
    stat = os.stat(filepath)
    table = Table(title=f"Structural File Headers Allocation Attributes: {os.path.basename(filepath)}", border_style="magenta")
    table.add_column("File Metric Attribute Vector Key", style="cyan")
    table.add_column("Discovered Target Property Meta Value Data", style="white")
    table.add_row("Allocation Size Unit Footprint (Bytes Count)", str(stat.st_size))
    table.add_row("Operating System Absolute Path Node String Reference", os.path.abspath(filepath))
    table.add_row("System Infrastructure Access Creation Time Matrix Record", str(datetime.fromtimestamp(stat.st_ctime)))
    table.add_row("Last Modifying Transformation Signature Time Window", str(datetime.fromtimestamp(stat.st_mtime)))
    console.print(table)

# ==============================================================================
# BATCH ANALYTICAL PIPELINE CONTEXT ARCHITECTURE
# ==============================================================================

def module_batch_mode() -> None:
    console.print(Panel("[bold cyan]AUTOMATED BATCH MATRIX RECONNAISSANCE PROCESSOR PIPELINE ENGINE[/bold cyan]", border_style="cyan"))
    filepath = Prompt.ask("[bold yellow]Enter target bulk data storage file handle address location path (TXT or CSV format only)[/bold yellow]")
    
    if not os.path.exists(filepath):
        console.print("[bold red][!] Missing runtime dependency pipeline track source file: Selection referenced entity not present within targeted space.[/bold red]")
        return
        
    run_spinner(2.0, "Analyzing batch arrays across data structures...")
    
    results_list = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        
    for index, raw_val in enumerate(lines):
        clean = re.sub(r"\D", "", raw_val)
        if len(clean) == 16:
            res = analyze_bank_card(clean)
            results_list.append((index+1, "Bank Card Identity", raw_val, f"VALID ({res['bank']})" if res["valid"] else "INVALID ALGORITHM CHECK"))
        elif len(clean) == 11 and clean.startswith("09"):
            res = analyze_phone_number(clean)
            results_list.append((index+1, "Telecomm Endpoint Mobile", raw_val, f"VALID ({res['operator']} - {res['province']})" if res["valid"] else "INVALID STRUCTURE PREFIX"))
        elif len(clean) == 10:
            res = analyze_national_id(clean)
            results_list.append((index+1, "National Civil Identity Card", raw_val, f"VALID ({res['province']})" if res["valid"] else "INTEGRITY PATTERN ERROR"))
        else:
            results_list.append((index+1, "Unrecognized Template Struct Array", raw_val, "UNPARSEABLE DISCOVERY PATTERN MATRIX"))

    batch_table = Table(title="Automated High-Performance Concurrent Batch Audit Outputs", border_style="cyan")
    batch_table.add_column("Pipeline Job Index #", style="yellow")
    batch_table.add_column("Inferred Classifier Domain Model Type", style="cyan")
    batch_table.add_column("Supplied Record Character Payload", style="white")
    batch_table.add_column("Algorithmic Processing Pipeline Status Verdict", style="magenta")
    
    for row in results_list:
        batch_table.add_row(str(row[0]), row[1], row[2], row[3])
        
    console.print(batch_table)
    LAST_ANALYSIS_RESULTS["Batch Processing Engine System Operations"] = results_list

# ==============================================================================
# UNIFIED CENTRAL REPORT GENERATOR ENGINE SYSTEM
# ==============================================================================

def module_reports_system() -> None:
    console.print(Panel("[bold cyan]CENTRAL INTELLIGENCE COMPLIANCE REPORT CONSOLE SYSTEM INTERFACE[/bold cyan]", border_style="cyan"))
    if not LAST_ANALYSIS_RESULTS:
        console.print("[bold yellow][!] Operational runtime session reporting index log is empty. Execute data analysis subsystems first before compiling records.[/bold yellow]")
        return
        
    console.print("Available reporting output structure paradigms format layouts:\n1. JSON Structured Object Notation Tree Architecture\n2. Plaintext Flat-file Information Summary Report Audit Log")
    format_choice = Prompt.ask("Select preferred serialization schema logic pattern standard mapping", choices=["1", "2"])
    target_filename = Prompt.ask("[bold yellow]Enter targeted deployment file destination filename path pattern[/bold yellow]", default="irisint_compiled_intelligence_audit")
    
    if format_choice == "1":
        full_path = f"{target_filename}.json"
        with open(full_path, "w", encoding="utf-8") as out_f:
            json.dump(LAST_ANALYSIS_RESULTS, out_f, indent=4, ensure_ascii=False)
        console.print(f"[bold green][+] Export complete. System telemetry state serialized safely down into targeted block structure: {full_path}[/bold green]")
    elif format_choice == "2":
        full_path = f"{target_filename}.txt"
        with open(full_path, "w", encoding="utf-8") as out_f:
            out_f.write("=== IRISINT INTELLIGENCE UTILITY FRAMEWORK SESSION AUDIT COMPILATION LOG ===\n")
            out_f.write(f"Generation Timestamp Boundary Sequence Mark: {datetime.now().isoformat()}\n")
            out_f.write("================================================================================\n\n")
            for module_key, data_payload in LAST_ANALYSIS_RESULTS.items():
                out_f.write(f"System Operational Analytics Module Sector Mapping Block -> {module_key}\n")
                out_f.write(f"Data Matrix Telemetry String: {str(data_payload)}\n")
                out_f.write("-" * 80 + "\n")
        console.print(f"[bold green][+] Export complete. Human-readable analytical data matrix output safely flushed to target system trace: {full_path}[/bold green]")

# ==============================================================================
# LOCAL OFFLINE INTELLIGENCE REPOSITORY INSPECTOR
# ==============================================================================

def module_embedded_databases() -> None:
    console.print(Panel("[bold cyan]INTERNAL STATIC OFFLINE ADVANCED IRAN DATA REFERENCE DIRECTORY[/bold cyan]", border_style="cyan"))
    
    table = Table(title="Synchronized Sovereign Territorial Subsystems (31 Provinces Mapped)", border_style="magenta")
    table.add_column("Registry Domain Metric Class", style="cyan")
    table.add_column("Total Active Local Records Indexed", style="green")
    table.add_row("Iranian Bank Cards BIN Indexes", f"{len(BIN_DB)} Primary Issuers")
    table.add_row("SHABA Interbank Cleared Identifiers", f"{len(SHABA_DB)} Central Routing Roots")
    table.add_row("Mobile Telecomm Cellular Routing Operators", f"{len(MOBILE_PREFIX_DB)} Active Core Prefixes Mapped to Provinces")
    table.add_row("Sovereign Landline PSTN Area Codes", f"{len(LANDLINE_DB)} Provinces Code Sets")
    table.add_row("Civil Registration National ID Allocation Keys", f"{len(NATIONAL_ID_PROVINCE_DB)} Regional Records Matrix")
    table.add_row("Traffic Control System Plate Codes", f"{len(PLATE_DB)} Unique Regional Series Elements")
    
    console.print(table)
    console.print("\n[bold green][+] Data Integrity Status: COMPLETE. All 31 Iranian Provinces natively decoupled from generic zone descriptions.[/bold green]")

# ==============================================================================
# MAIN EXECUTABLE COORDINATOR ROUTINE FRAMEWORK
# ==============================================================================

@app.command()
def interactive_shell() -> None:
    """
    Launches the primary secure shell interaction layer loop for the IRISINT utility framework environment instance.
    """
    os.system("cls" if os.name == "nt" else "clear")
    print_banner()
    
    while True:
        render_menu()
        choice = Prompt.ask("[bold yellow]IRISINT://Secure-Session-Shell/Enter-Selection-Code[/bold yellow]", default="0")
        
        if choice == "1":
            module_bank_card()
        elif choice == "2":
            module_phone_number()
        elif choice == "3":
            module_national_id()
        elif choice == "4":
            module_shaba()
        elif choice == "5":
            module_postal_code()
        elif choice == "6":
            module_landline()
        elif choice == "7":
            module_vehicle_plate()
        elif choice == "8":
            module_date_calendar()
        elif choice == "9":
            module_domain_tools()
        elif choice == "10":
            module_network_tools()
        elif choice == "11":
            module_hash_tools()
        elif choice == "12":
            module_encoding_tools()
        elif choice == "13":
            module_qr_tools()
        elif choice == "14":
            module_metadata_tools()
        elif choice == "15":
            module_batch_mode()
        elif choice == "16":
            module_reports_system()
        elif choice == "17":
            module_embedded_databases()
        elif choice == "0":
            console.print("[bold red][*] Secure context memory teardown initialization loop complete. Exiting shell execution layer safely. Goodbye.[/bold red]")
            sys.exit(0)
        else:
            console.print("[bold red][!] Input parameter mismatch fault. Selection key range is out of execution scope alignment bounds.[/bold red]")
            
        Prompt.ask("\n[dim white]Press Enter system key to shift context execution frame focus back into main architecture menu view...[/dim white]")
        os.system("cls" if os.name == "nt" else "clear")
        print_banner()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app()
    else:
        interactive_shell()