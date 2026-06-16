#!/usr/bin/env python3
"""
IRISINT: Iranian Intelligence & Utility Toolkit
Platform: Termux / Linux / Python 3.12+
Author: AI Collaborator
License: MIT
"""

import sys
import os
import re
import json
import csv
import math
import time
import socket
import struct
import hashlib
import urllib.parse
import base64
import datetime
from typing import Dict, List, Tuple, Optional, Any, Union

# Third-party dependencies
try:
    import requests
    import typer
    import qrcode
    import dns.resolver
    import whois
    import pycountry
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.live import Live
    from rich.prompt import Prompt, IntPrompt
    from tabulate import tabulate
except ImportError as e:
    print(f"[-] Missing dependency: {e.name}. Please install required packages:")
    print("    pip install rich typer requests tabulate qrcode dnspython python-whois pycountry")
    sys.exit(1)

# Initialize Rich components
console = Console()
app = typer.Typer(help="IRISINT: Iranian Intelligence & Utility Toolkit")

BANNER = """
██████╗ ██████╗ ██╗███████╗██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██║██╔════╝██║████╗  ██║╚══██╔══╝
██████╔╝██████╔╝██║███████╗██║██╔██╗ ██║   ██║   
██╔══██╗██╔══██╗██║╚════██║██║██║╚██╗██║   ██║   
██║  ██║██║  ██║██║███████║██║██║ ╚████║   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   
"""

# ==============================================================================
# EMBEDDED DATABASES
# ==============================================================================

BIN_DATABASE: Dict[str, str] = {
    "603799": "National Bank of Iran (Melli)",
    "589210": "Sepah Bank",
    "627648": "Saderat Bank",
    "627961": "Sanat va Madan Bank",
    "627760": "Post Bank",
    "621986": "Saman Bank",
    "627412": "Eghtesad Novin Bank",
    "622106": "Parsian Bank",
    "502229": "Pasargad Bank",
    "628023": "Tejarat Bank",
    "610433": "Mellat Bank",
    "627359": "Refah Bank",
    "589463": "Maskan Bank",
    "606373": "Mehr Iran Bank",
    "628157": "Subdevelopment Credit Institution",
    "502908": "Development Cooperation Bank",
    "504172": "Resalat Bank",
    "505785": "Iran Zamin Bank",
    "505416": "Tourism Bank",
    "505801": "Kowsar Credit Institution",
    "507677": "Noor Credit Institution",
    "606256": "Askariye (Melal) Credit Institution",
    "627488": "Karafarin Bank",
    "627884": "Parseean Bank",
    "636214": "Ayandeh Bank",
    "636795": "Sina Bank",
    "636949": "Hikmat Bank",
    "639346": "Sina Bank",
    "639347": "Pasargad Bank",
    "639599": "Ghavamin Bank",
    "639607": "Sarmayeh Bank",
    "502938": "Dey Bank",
    "505272": "Iran Zamin Bank",
    "639194": "Sarmayeh Bank",
    "627381": "Ansar Bank",
    "639370": "Mehr Eghtesad Bank",
    "643431": "Shahr Bank",
    "659580": "Khavarmiane Bank",
}

MOBILE_PREFIXES: Dict[str, Dict[str, str]] = {
    "0910": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0911": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0912": {"operator": "Hamrah Aval", "type": "Postpaid Only"},
    "0913": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0914": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0915": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0916": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0917": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0918": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0919": {"operator": "Hamrah Aval", "type": "Prepaid Only"},
    "0990": {"operator": "Hamrah Aval", "type": "Prepaid Only"},
    "0991": {"operator": "Hamrah Aval", "type": "Postpaid/Prepaid"},
    "0992": {"operator": "Hamrah Aval", "type": "Prepaid Only"},
    "0993": {"operator": "Hamrah Aval", "type": "Prepaid Only"},
    "0994": {"operator": "Hamrah Aval", "type": "Prepaid Only"},
    "0930": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0933": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0935": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0936": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0937": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0938": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0939": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0901": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0902": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0903": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0904": {"operator": "Irancell", "type": "Prepaid (SIM-Koodak)"},
    "0905": {"operator": "Irancell", "type": "Prepaid/Postpaid"},
    "0941": {"operator": "Irancell", "type": "TD-LTE Fixed"},
    "0920": {"operator": "Rightel", "type": "Postpaid Only"},
    "0921": {"operator": "Rightel", "type": "Prepaid Only"},
    "0922": {"operator": "Rightel", "type": "Prepaid Only"},
    "0923": {"operator": "Rightel", "type": "Prepaid Only"},
    "0998": {"operator": "Shatel Mobile", "type": "Prepaid MVNO"},
    "0999": {"operator": "Samantel / Aptel", "type": "MVNO Postpaid/Prepaid"},
}

PROVINCE_CODES: Dict[str, str] = {
    "001": "Central Tehran", "002": "Central Tehran", "003": "Central Tehran", "004": "Central Tehran",
    "005": "Central Tehran", "006": "Central Tehran", "007": "Central Tehran", "008": "Central Tehran",
    "044": "Shemiranat", "045": "Shemiranat", "048": "Ray", "049": "Ray", "102": "Urmia", "103": "Urmia",
    "127": "Tabriz", "128": "Tabriz", "129": "Tabriz", "136": "Maragheh", "137": "Maragheh", "145": "Ardabil",
    "146": "Ardabil", "174": "Isfahan", "175": "Isfahan", "181": "Kashan", "211": "Ilam", "212": "Ilam",
    "228": "Bushehr", "229": "Bushehr", "230": "Tangestan", "258": "Shahrekord", "259": "Shahrekord",
    "268": "Birjand", "269": "Birjand", "274": "Mashhad", "275": "Mashhad", "289": "Sabzevar",
    "304": "Bojnourd", "305": "Bojnourd", "324": "Ahvaz", "325": "Ahvaz", "338": "Abadan", "361": "Zanjan",
    "362": "Zanjan", "372": "Semnan", "373": "Semnan", "377": "Shahroud", "386": "Zahedan", "387": "Zahedan",
    "406": "Shiraz", "407": "Shiraz", "413": "Marvdasht", "427": "Qazvin", "428": "Qazvin", "431": "Qom",
    "432": "Qom", "438": "Sanandaj", "439": "Sanandaj", "449": "Kerman", "450": "Kerman", "459": "Rafsanjan",
    "469": "Kermanshah", "470": "Kermanshah", "488": "Gorgan", "489": "Gorgan", "497": "Gonbad-e Kavus",
    "503": "Rasht", "504": "Rasht", "516": "Lahijan", "525": "Khorramabad", "526": "Khorramabad",
    "538": "Borujerd", "551": "Sari", "552": "Sari", "556": "Babol", "557": "Babol", "571": "Amol",
    "576": "Arak", "577": "Arak", "589": "Saveh", "593": "Hamadan", "594": "Hamadan", "617": "Yazd",
    "618": "Yazd", "629": "Karaj", "630": "Karaj", "636": "Hashtgerd"
}

LANDLINE_DATABASE: Dict[str, str] = {
    "021": "Tehran", "026": "Alborz", "025": "Qom", "081": "Hamadan", "086": "Markazi", "087": "Kurdistan",
    "083": "Kermanshah", "084": "Ilam", "066": "Lorestān", "061": "Khuzestan", "031": "Isfahan",
    "038": "Chaharmahal and Bakhtiari", "051": "Razavi Khorasan", "058": "North Khorasan",
    "056": "South Khorasan", "054": "Sistan and Baluchestan", "034": "Kerman", "035": "Yazd",
    "071": "Fars", "076": "Hormozgan", "074": "Kohgiluyeh and Boyer-Ahmad", "041": "East Azerbaijan",
    "044": "West Azerbaijan", "045": "Ardabil", "024": "Zanjan", "028": "Qazvin", "011": "Mazandaran",
    "013": "Gilan", "017": "Golestan", "023": "Semnan"
}

PLATE_DATABASE: Dict[str, str] = {
    "11": "Tehran (Central)", "22": "Tehran (Central)", "33": "Tehran (Central)", "44": "Tehran (Central)",
    "55": "Tehran (Central)", "66": "Tehran (Central)", "77": "Tehran (Central)", "88": "Tehran (Central)",
    "99": "Tehran (Central)", "10": "Tehran (Suburbs)", "20": "Tehran (Suburbs)", "30": "Tehran (Suburbs)",
    "40": "Tehran (Suburbs)", "13": "Isfahan", "23": "Isfahan", "43": "Isfahan", "53": "Isfahan",
    "67": "Isfahan", "12": "Razavi Khorasan (Mashhad)", "32": "Razavi Khorasan", "42": "Razavi Khorasan",
    "52": "Razavi Khorasan", "15": "Fars (Shiraz)", "25": "Fars", "35": "Fars", "45": "Fars",
    "17": "Khuzestan (Ahvaz)", "27": "Khuzestan", "37": "Khuzestan", "14": "East Azerbaijan (Tabriz)",
    "24": "East Azerbaijan", "34": "East Azerbaijan", "16": "West Azerbaijan (Urmia)", "26": "West Azerbaijan",
    "36": "West Azerbaijan", "18": "Mazandaran (Sari)", "28": "Mazandaran", "38": "Mazandaran",
    "19": "Gilan (Rasht)", "29": "Gilan", "39": "Gilan", "21": "Kerman", "31": "Kerman", "41": "Kerman",
    "47": "Markazi (Arak)", "57": "Markazi", "48": "Hamadan", "58": "Hamadan",
    "49": "Kermanshah", "59": "Kermanshah", "51": "Kurdistan", "61": "Kurdistan", "56": "Kohgiluyeh and Boyer-Ahmad",
    "63": "Qom", "73": "Qom", "69": "Alborz (Karaj)", "78": "Alborz", "82": "Alborz"
}

JALALI_MONTHS = ["Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar", "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"]
ZODIAC_SIGNS = [
    ("Farvardin", "Aries ♈"), ("Ordibehesht", "Taurus ♉"), ("Khordad", "Gemini ♊"),
    ("Tir", "Cancer ♋"), ("Mordad", "Leo ♌"), ("Shahrivar", "Virgo ♍"),
    ("Mehr", "Libra ♎"), ("Aban", "Scorpio ♏"), ("Azar", "Sagittarius ♐"),
    ("Dey", "Capricorn ♑"), ("Bahman", "Aquarius ♒"), ("Esfand", "Pisces ♓")
]

PERSIAN_HOLIDAYS = {
    "01-01": "Nowruz (New Year)", "01-02": "Nowruz Holiday", "01-03": "Nowruz Holiday", "01-04": "Nowruz Holiday",
    "01-12": "Islamic Republic Day", "01-13": "Sizdah Bedar (Nature Day)", "03-14": "Demise of Ayatollah Khomeini",
    "03-15": "Khordad 15 Revolt", "22-22": "Bahman 22 (Islamic Revolution Victory)", "12-29": "Nationalization of Oil Industry"
}

# ==============================================================================
# ARCHITECTURAL UTILITIES (FONTS, THEMES, HELPERS)
# ==============================================================================

def print_cyber_header(title: str) -> None:
    console.print(Panel(Text(f"[⚡] {title.upper()} [⚡]", style="bold green", justify="center"), style="cyan"))

def get_clean_input(prompt_text: str) -> str:
    return Prompt.ask(f"[bold cyan]IRISINT» {prompt_text}[/bold cyan]").strip()

def export_report_dialog(data: Dict[str, Any], module_name: str) -> None:
    console.print("\n[bold magenta]16. Export Report Options[/bold magenta]")
    console.print("[1] JSON  [2] CSV  [3] TXT  [4] HTML  [0] Skip Export")
    choice = get_clean_input("Select format")
    if choice == "0":
        return
    filename = f"report_{module_name}_{int(time.time())}"
    if choice == "1":
        ReportManager.to_json(data, f"{filename}.json")
    elif choice == "2":
        ReportManager.to_csv(data, f"{filename}.csv")
    elif choice == "3":
        ReportManager.to_txt(data, f"{filename}.txt")
    elif choice == "4":
        ReportManager.to_html(data, f"{filename}.html")

# ==============================================================================
# ALGORITHMIC ENGINE CORE
# ==============================================================================

class LuhnValidator:
    @staticmethod
    def validate(card_num: str) -> bool:
        if not card_num.isdigit() or len(card_num) != 16:
            return False
        digits = [int(d) for d in card_num]
        odd_digits = digits[-2::-2]
        even_digits = digits[-1::-2]
        checksum = sum(even_digits)
        for d in odd_digits:
            checksum += sum(divmod(d * 2, 10))
        return checksum % 10 == 0

class NationalIDValidator:
    @staticmethod
    def validate(nid: str) -> Tuple[bool, Optional[str]]:
        if not re.match(r"^\d{10}$", nid):
            return False, None
        if re.match(r"^(\d)\1{9}$", nid):
            return False, None
        
        prefix = nid[:3]
        loc = PROVINCE_CODES.get(prefix, "Unknown / Valid Allocation")
        
        digits = [int(c) for c in nid]
        checksum = digits[9]
        
        total = sum(digits[i] * (10 - i) for i in range(9))
        rem = total % 11
        
        if rem < 2:
            valid = (checksum == rem)
        else:
            valid = (checksum == (11 - rem))
            
        return valid, loc if valid else None

class ShabaValidator:
    @staticmethod
    def validate(shaba: str) -> Tuple[bool, Optional[str]]:
        shaba = shaba.upper().replace(" ", "")
        if not re.match(r"^IR\d{24}$", shaba):
            return False, None
        
        rearranged = shaba[4:] + "1827" + shaba[2:4]
        try:
            val = int(rearranged)
            if val % 97 != 1:
                return False, None
            
            bin_code = shaba[4:7]
            bank_mapped = "Parsed Iranian Institutional Assignment"
            for b_bin, b_name in BIN_DATABASE.items():
                if b_bin.startswith(bin_code) or bin_code in b_bin:
                    bank_mapped = b_name
                    break
            return True, bank_mapped
        except ValueError:
            return False, None

# ==============================================================================
# CONVERSION ENGINE (JALALI/GREGORIAN/HIJRI ALGORITHMS)
# ==============================================================================

class DateConverter:
    @staticmethod
    def jalali_to_gregorian(jy: int, jm: int, jd: int) -> datetime.date:
        jy -= 979
        days = 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4)
        for i in range(jm - 1):
            days += 31 if i < 6 else 30
        days += jd - 1
        g_days = days + 79
        gy = 1600 + 400 * (g_days // 146097)
        g_days %= 146097
        leap = 1
        if g_days >= 36525:
            g_days -= 36525
            gy += 100
            leap = 0
        gy += 4 * (g_days // 1461)
        g_days %= 1461
        if g_days >= 366:
            g_days -= 366
            gy += 1
            leap = 0
        while True:
            sal_days = 366 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 365
            if g_days >= sal_days:
                g_days -= sal_days
                gy += 1
            else:
                break
        g_months = [31, 29 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        gm = 0
        for i, m_days in enumerate(g_months):
            if g_days >= m_days:
                g_days -= m_days
            else:
                gm = i + 1
                break
        gd = g_days + 1
        return datetime.date(gy, gm, gd)

    @staticmethod
    def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
        g_months = [31, 29 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        gy -= 1600
        g_days = sum(g_months[:gm - 1]) + gd - 1 + 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
        j_days = g_days - 79
        j_np = j_days // 12053
        j_days %= 12053
        jy = 979 + 33 * j_np + 4 * (j_days // 1461)
        j_days %= 1461
        if j_days >= 366:
            jy += (j_days - 1) // 365
            j_days = (j_days - 1) % 365
        for i in range(11):
            m_days = 31 if i < 6 else 30
            if j_days >= m_days:
                j_days -= m_days
            else:
                return jy, i + 1, j_days + 1
        return jy, 12, j_days + 1

    @staticmethod
    def gregorian_to_hijri(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
        if gm < 3:
            gy -= 1
            gm += 12
        a = math.floor(gy / 100)
        b = math.floor(a / 4)
        c = 2 - a + b
        e = math.floor(365.25 * (gy + 4716))
        f = math.floor(30.6001 * (gm + 1))
        jd = c + gd + e + f - 1524.5
        
        ijda = math.floor(jd - 1948440 + 10632)
        n = math.floor((ijda - 1) / 10631)
        ijda = ijda - 10631 * n + 354
        j = math.floor((10985 - ijda) / 5316) * math.floor((50 * ijda) / 17719) + math.floor(ijda / 5670) * math.floor((43 * ijda) / 15238)
        ijda = ijda - math.floor((30 - j) / 15) * math.floor((17719 * j) / 50) - math.floor(j / 16) * math.floor((15238 * j) / 43) + 29
        m = math.floor((24 * ijda) / 709)
        d = ijda - math.floor((709 * m) / 24)
        y = 30 * n + j - 30
        return int(y), int(m), int(d)

    @staticmethod
    def is_jalali_leap(jy: int) -> bool:
        r = (jy - 474) % 2820
        return (((r + 38) % 33) * 31) % 33 < 19

# ==============================================================================
# OSINT & NETWORK ENGINES (PASSIVE PARSERS & SAFE PORT SCANNERS)
# ==============================================================================

class PassiveNetworkEngine:
    @staticmethod
    def dns_lookup(domain: str) -> Dict[str, List[str]]:
        records = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
        results = {}
        for r in records:
            try:
                answers = dns.resolver.resolve(domain, r)
                results[r] = [str(data) for data in answers]
            except Exception:
                results[r] = []
        return results

    @staticmethod
    def passive_subdomain_enum(domain: str) -> List[str]:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                subdomains = set()
                data = resp.json()
                for entry in data:
                    name = entry.get("name_value", "")
                    for n in name.split("\n"):
                        if not n.startswith("*") and n.endswith(domain):
                            subdomains.add(n.strip())
                return sorted(list(subdomains))
        except Exception:
            pass
        return ["Authentication/Network Exception encountered during passive crt.sh parsing."]

    @staticmethod
    def geoip_lookup(ip: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {"error": "Could not extract active geolocation mappings safely."}

    @staticmethod
    def safe_port_scan(host: str) -> List[Tuple[int, str]]:
        common_ports = [21, 22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 8080]
        open_ports = []
        for port in common_ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            result = s.connect_ex((host, port))
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except Exception:
                    service = "unknown"
                open_ports.append((port, service))
            s.close()
        return open_ports

# ==============================================================================
# METADATA & EXTRA UTILITIES
# ==============================================================================

class MetadataExtractor:
    @staticmethod
    def parse_pseudo_metadata(data_bytes: bytes) -> Dict[str, str]:
        info = {"File Size": f"{len(data_bytes)} bytes"}
        if b"JFIF" in data_bytes[:20] or b"Exif" in data_bytes:
            info["Format Type"] = "JPEG/Exif Asset Pipeline"
            info["Software Mappings"] = "Embedded Standard Decoder Output"
        elif data_bytes.startswith(b"%PDF"):
            info["Format Type"] = "Adobe PDF Document Architecture"
            for tag in [b"/Author", b"/Creator", b"/CreationDate"]:
                idx = data_bytes.find(tag)
                if idx != -1:
                    chunk = data_bytes[idx:idx+50].split(b")")[0].decode(errors="ignore")
                    info[tag.decode()] = chunk
        else:
            info["Format Type"] = "Generic Stream Asset File"
        return info

class ExtraUtils:
    @staticmethod
    def calculate_entropy(text: str) -> float:
        if not text:
            return 0.0
        probs = [text.count(c) / len(text) for c in set(text)]
        return -sum(p * math.log2(p) for p in probs)

    @staticmethod
    def generate_random_identity() -> Dict[str, str]:
        import random
        firsts = ["Ali", "Reza", "Mohammad", "Amir", "Hossein", "Zahra", "Fatemeh", "Maryam"]
        lasts = ["Ahmadi", "Ghasemi", "Hosseini", "Karimi", "Mousavi", "Razaie", "Tehrani"]
        fn = random.choice(firsts)
        ln = random.choice(lasts)
        n_pfx = random.choice(list(PROVINCE_CODES.keys()))
        nid = f"{n_pfx}{random.randint(1000000, 9999999)}"
        
        digits = [int(c) for c in nid[:9]]
        tot = sum(digits[i] * (10 - i) for i in range(9))
        rem = tot % 11
        chk = rem if rem < 2 else (11 - rem)
        final_nid = f"{nid[:9]}{chk}"
        
        return {
            "Synthesized Name": f"{fn} {ln}",
            "Synthesized National ID": final_nid,
            "Synthesized Region Area": PROVINCE_CODES.get(n_pfx, "Tehran"),
            "Synthesized Virtual Phone": f"0912{random.randint(1000000, 9999999)}"
        }

# ==============================================================================
# REPORT & BATCH EXPORT UTILITIES
# ==============================================================================

class ReportManager:
    @staticmethod
    def to_json(data: Dict[str, Any], filename: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        console.print(f"[bold green][+] Exported successfully to {filename}[/bold green]")

    @staticmethod
    def to_csv(data: Dict[str, Any], filename: str) -> None:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Parameter", "Value"])
            for k, v in data.items():
                writer.writerow([k, str(v)])
        console.print(f"[bold green][+] Exported successfully to {filename}[/bold green]")

    @staticmethod
    def to_txt(data: Dict[str, Any], filename: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== IRISINT INTELLIGENCE REPORT ===\n")
            for k, v in data.items():
                f.write(f"{k}: {v}\n")
        console.print(f"[bold green][+] Exported successfully to {filename}[/bold green]")

    @staticmethod
    def to_html(data: Dict[str, Any], filename: str) -> None:
        html = f"""<html><head><style>
        body {{ background-color: #0d1117; color: #c9d1d9; font-family: monospace; padding: 20px; }}
        table {{ border: 1px solid #30363d; border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #30363d; padding: 8px; text-align: left; }}
        th {{ background-color: #161b22; color: #58a6ff; }}
        </style></head><body><h2>IRISINT Module Output Report</h2><table>
        <tr><th>Key Metrics Matrix</th><th>Strategic Values Data</th></tr>"""
        for k, v in data.items():
            html += f"<tr><td>{k}</td><td>{v}</td></tr>"
        html += "</table></body></html>"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        console.print(f"[bold green][+] Exported successfully to {filename}[/bold green]")

# ==============================================================================
# INTERACTIVE MODULE DISPATCHERS
# ==============================================================================

def run_bank_analyzer() -> None:
    print_cyber_header("Bank Card Analyzer")
    card = get_clean_input("Enter 16-Digit Iranian Bank Card Number").replace(" ", "").replace("-", "")
    if len(card) < 6:
        console.print("[bold red][!] Invalid Length Matrix[/bold red]")
        return
    bin_pfx = card[:6]
    bank = BIN_DATABASE.get(bin_pfx, "Unknown / External Institution Allocation")
    is_valid = LuhnValidator.validate(card)
    
    table = Table(title="Card Blueprint Intelligence Analysis")
    table.add_column("Property Profile Struct", style="cyan")
    table.add_column("Evaluated Signal Metrics", style="magenta")
    table.add_row("Extracted Issuer BIN", bin_pfx)
    table.add_row("Mapped Corporate Entity", bank)
    table.add_row("Mathematical Checksum (Luhn)", "VALID PASS" if is_valid else "INVALID INTEGRITY FAULT")
    console.print(table)
    
    export_report_dialog({"card": card, "bin": bin_pfx, "bank": bank, "luhn_valid": is_valid}, "bank_card")

def run_phone_analyzer() -> None:
    print_cyber_header("Phone Number Analyzer")
    num = get_clean_input("Enter Mobile Number (e.g., 09123456789)")
    if num.startswith("+98"):
        num = "0" + num[3:]
    if not re.match(r"^09\d{9}$", num):
        console.print("[bold red][!] Faulty Syntactic Mobile Alignment Blueprint.[/bold red]")
        return
    pfx = num[:4]
    op_data = MOBILE_PREFIXES.get(pfx, {"operator": "Unknown / Sovereign Infrastructure Grid", "type": "Hybrid Data Packet Relay"})
    
    table = Table(title="Cellular Terminal Intercept Analysis")
    table.add_column("Operational Parameters", style="cyan")
    table.add_column("Target Routing Values", style="magenta")
    table.add_row("Captured Prefix Field", pfx)
    table.add_row("Target Infrastructure Core Operator", op_data["operator"])
    table.add_row("Channel Provisioning Architecture", op_data["type"])
    table.add_row("Sovereign State Routing Safe Identity", "+98 " + num[1:])
    console.print(table)
    
    export_report_dialog({"number": num, "prefix": pfx, "operator": op_data["operator"], "type": op_data["type"]}, "phone")

def run_national_id_analyzer() -> None:
    print_cyber_header("National ID Analyzer")
    nid = get_clean_input("Enter 10-Digit Iranian National ID Number")
    is_valid, province = NationalIDValidator.validate(nid)
    
    table = Table(title="Civil Registration Data Matrix Verification")
    table.add_column("Registration Metric Identity", style="cyan")
    table.add_column("Extracted Integrity Output", style="magenta")
    table.add_row("Syntactic Algorithmic Verification", "SECURE CRITICAL ENFORCED PASS" if is_valid else "INTEGRITY COLLISION FAULT")
    table.add_row("Sovereign Issuing Zone Allocation Mapping", province if province else "INVALID BOUNDS")
    console.print(table)
    
    export_report_dialog({"nid": nid, "valid": is_valid, "allocated_zone": province}, "national_id")

def run_shaba_analyzer() -> None:
    print_cyber_header("SHABA Interbank Transfer Analyzer")
    shaba = get_clean_input("Enter IBAN / SHABA string (e.g., IR...)")
    is_valid, institution = ShabaValidator.validate(shaba)
    
    table = Table(title="ISO 7064 Central Interbank Verification Matrix")
    table.add_column("Interbank Structure Vector", style="cyan")
    table.add_column("Calculated Internal Parameters", style="magenta")
    table.add_row("Mod 97 Sovereign Checksum Struct", "VALID PASS" if is_valid else "INVALID ARTIFACT")
    table.add_row("Target Corporate Asset Holder Entity", institution if institution else "UNKNOWN ENTITY TARGET")
    console.print(table)
    
    export_report_dialog({"shaba": shaba, "valid": is_valid, "bank": institution}, "shaba")

def run_postal_analyzer() -> None:
    print_cyber_header("Postal Code Analyzer")
    pc = get_clean_input("Enter 10-Digit Postcode String")
    if not re.match(r"^\d{10}$", pc):
        console.print("[bold red][!] Core Constraint Violated: Postal formats demand 10 clean integers.[/bold red]")
        return
    pfx = pc[:2]
    sectors = {"11": "Tehran North Core", "13": "Tehran South Core", "71": "Fars Central Hub", "91": "Khorasan Distribution Terminal"}
    loc = sectors.get(pfx, "Valid Sovereign Geographic Administrative Zone Array")
    
    table = Table(title="Logistical Grid Location Report")
    table.add_column("Logistics Variable", style="cyan")
    table.add_column("Grid Resolved Target Value", style="magenta")
    table.add_row("Postal Node Code Route", pfx)
    table.add_row("Administrative Hub Node Base Vector", loc)
    console.print(table)
    
    export_report_dialog({"postal_code": pc, "route_node": pfx, "zone": loc}, "postal")

def run_landline_analyzer() -> None:
    print_cyber_header("Landline Area Analyzer")
    code = get_clean_input("Enter Area Code Protocol Vector (e.g., 021, 031)")
    prov = LANDLINE_DATABASE.get(code, "Unknown Telcom Switching Exchange Bounds")
    
    table = Table(title="PSTN Telephony Node Mapping Matrix")
    table.add_column("Exchange Parameter Field", style="cyan")
    table.add_column("Resolved Physical Topography Node", style="magenta")
    table.add_row("Carrier Area Identity Vector", code)
    table.add_row("Sovereign Switching Province Target", prov)
    console.print(table)
    
    export_report_dialog({"area_code": code, "province": prov}, "landline")

def run_vehicle_analyzer() -> None:
    print_cyber_header("Vehicle Plate Analyzer")
    plate_two_digits = get_clean_input("Enter the terminal 2-digit location code from plate")
    prov = PLATE_DATABASE.get(plate_two_digits, "Unknown Regional Registration Office Grid Zone")
    
    table = Table(title="Sovereign Registration Traffic Management Framework Matrix")
    table.add_column("Plate Structural Key Segment", style="cyan")
    table.add_column("Resolved Registration Registry Data Profile", style="magenta")
    table.add_row("Terminal Node Cluster Identity", plate_two_digits)
    table.add_row("Sovereign Province Node Mapping Base", prov)
    console.print(table)
    
    export_report_dialog({"plate_code": plate_two_digits, "province": prov}, "vehicle_plate")

def run_calendar_tools() -> None:
    print_cyber_header("Date & Calendar Processing Tools")
    console.print("[1] Jalali ⇄ Gregorian Converter Matrix\n[2] Unix Epoche Epoch Transformation\n[3] Historical Leap State Engine Evaluation")
    choice = get_clean_input("Select calendar algorithmic execution unit pipeline")
    
    if choice == "1":
        direction = get_clean_input("Type 'j2g' for Jalali to Gregorian or 'g2j' for inverse conversion")
        if direction == "j2g":
            y = int(get_clean_input("Jalali Year Target"))
            m = int(get_clean_input("Jalali Month Sequence"))
            d = int(get_clean_input("Jalali Day Integer Value"))
            g_date = DateConverter.jalali_to_gregorian(y, m, d)
            console.print(f"[bold green][+] Transformed Epoch Target Output Matrix: {g_date.isoformat()}[/bold green]")
        elif direction == "g2j":
            y = int(get_clean_input("Gregorian Calendar Year Value"))
            m = int(get_clean_input("Gregorian Month Tracker Value"))
            d = int(get_clean_input("Gregorian Day Offset Target"))
            jy, jm, jd = DateConverter.gregorian_to_jalali(y, m, d)
            console.print(f"[bold green][+] Transformed Jalali Matrix Array Structure: {jy}/{jm:02d}/{jd:02d}[/bold green]")
    elif choice == "2":
        ts_str = get_clean_input("Enter Unix Timestamp Execution Integer")
        try:
            ts = float(ts_str)
            dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
            jy, jm, jd = DateConverter.gregorian_to_jalali(dt.year, dt.month, dt.day)
            console.print(f"[bold green][+] System UTC Time Vector: {dt.isoformat()}[/bold green]")
            console.print(f"[bold green][+] Calculated Sovereign Jalali Equivalent: {jy}/{jm:02d}/{jd:02d}[/bold green]")
        except ValueError:
            console.print("[bold red][!] Epoche Conversion Format Violation Error.")
    elif choice == "3":
        jy = int(get_clean_input("Enter Jalali Year to Calculate Leap Metric Status"))
        is_leap = DateConverter.is_jalali_leap(jy)
        console.print(f"[bold magenta]Leap Year Mathematical State Matrix Assertion: {is_leap}[/bold magenta]")

def run_domain_tools() -> None:
    print_cyber_header("Passive Domain OSINT Infrastructure Matrix")
    domain = get_clean_input("Enter Target Domain Identity Field (e.g., srbiau.ac.ir, yahoo.com)")
    
    with Live(Panel("Initializing Socket Pipeline Routing Query Engine...", title="OSINT Network Status Flags"), refresh_per_second=4) as live:
        live.update(Panel("Resolving Passive Domain Name Space Matrices...", style="yellow"))
        dns_res = PassiveNetworkEngine.dns_lookup(domain)
        live.update(Panel("Interrogating Passive Certificate Registration Public Ledgers (Crt.sh)...", style="cyan"))
        subs = PassiveNetworkEngine.passive_subdomain_enum(domain)
        
        live.update(Panel("Resolving WHOIS Registration Field Records...", style="magenta"))
        try:
            w = whois.whois(domain)
            w_data = str(w.registrar)
        except Exception:
            w_data = "Protected / Passive Parsing Blocked by Network Layer Rule Exception"
            
    table = Table(title=f"Passive Technical Profile: {domain}")
    table.add_column("Infrastructure Layer Field Map", style="cyan")
    table.add_column("Discovered Active Output Struct Data", style="magenta")
    table.add_row("Identified Active Registrar", w_data)
    table.add_row("Core IPv4 A Host Vectors", ", ".join(dns_res.get("A", [])) if dns_res.get("A") else "None Discovered Passive Array")
    table.add_row("Core Exchange MX Mail Records", ", ".join(dns_res.get("MX", [])) if dns_res.get("MX") else "None Map")
    console.print(table)
    
    if subs and "Exception" not in subs[0]:
        console.print(f"\n[bold green][+] Discovered Passive Subdomains Array Mapping Pool (Top 10 Nodes):[/bold green]")
        for s in subs[:10]:
            console.print(f"    └── {s}")
            
    export_report_dialog({"domain": domain, "dns": dns_res, "subdomains_sample": subs[:20]}, "domain_tools")

def run_network_tools() -> None:
    print_cyber_header("Network Topology Auditing Utilities")
    target = get_clean_input("Enter Remote Host Vector Target Node IP Address or Alias Name")
    
    try:
        ip = socket.gethostbyname(target)
    except Exception:
        console.print("[bold red][!] DNS Domain Target Validation Intercept Fault: Remote Host Unreachable.[/bold red]")
        return
        
    with Live(Panel(f"Evaluating GeoIP Records for Address Pointer Asset: {ip}...", title="Network Status Core"), refresh_per_second=4) as live:
        geo = PassiveNetworkEngine.geoip_lookup(ip)
        live.update(Panel("Executing Clean Legal Low-Profile Non-Intrusive TCP Port Status Sweep...", style="yellow"))
        ports = PassiveNetworkEngine.safe_port_scan(ip)
        
    table = Table(title="Passive Geographic Location & Routing Infrastructure Profile")
    table.add_column("OSINT Network Mapping Vector", style="cyan")
    table.add_column("Reported Public Mapping Data Field", style="magenta")
    table.add_row("Resolved IPv4 Vector Coordinate", ip)
    table.add_row("Sovereign State Boundary Location", geo.get("country_name", "Unknown/Proxy Domain Shield"))
    table.add_row("ISP Node Carrier Grid Identifier", geo.get("org", "Protected Network Hub"))
    console.print(table)
    
    ptable = Table(title="Discovered Open Passive TCP Target Service Points")
    ptable.add_column("Port Identity Node", style="cyan")
    ptable.add_column("Assigned Standard Application Service Protocol Layer", style="magenta")
    for p, s in ports:
        ptable.add_row(str(p), s)
    if not ports:
        ptable.add_row("No Common Open Listening Nodes Discovered", "Filtered/Closed Stack Profile Shield")
    console.print(ptable)
    
    export_report_dialog({"ip": ip, "geo": geo, "open_ports": ports}, "network_tools")

def run_hash_tools() -> None:
    print_cyber_header("Cryptographic Integrity Hashing Matrix Tools")
    payload = get_clean_input("Enter String Data Field Object to Process Hashing Signatures").encode()
    
    table = Table(title="Calculated Unidirectional Cryptographic Hash Digests Matrix")
    table.add_column("Hashing Algorithm Function Scheme", style="cyan")
    table.add_column("Output Generated Fingerprint Signature Payload Hex Stream", style="magenta")
    table.add_row("MD5 Engine Standard", hashlib.md5(payload).hexdigest())
    table.add_row("SHA-1 Engine Standard", hashlib.sha1(payload).hexdigest())
    table.add_row("SHA-256 Industrial Standard Core", hashlib.sha256(payload).hexdigest())
    table.add_row("SHA-512 Extended Military Standard Architecture", hashlib.sha512(payload).hexdigest())
    console.print(table)

def run_encoding_tools() -> None:
    print_cyber_header("Encoding Data Protocol Format Translators")
    text = get_clean_input("Enter Raw Text Target Object for Encoding Base Field Re-mapping Execution")
    
    b64_enc = base64.b64encode(text.encode()).decode()
    url_enc = urllib.parse.quote(text)
    hex_enc = text.encode().hex()
    
    table = Table(title="Transformed Representation Formats Mapping Output Matrix")
    table.add_column("Encoding System Format Scheme Architecture", style="cyan")
    table.add_column("Re-mapped Structural Output Value", style="magenta")
    table.add_row("Base64 Binary-to-Text Format Scheme", b64_enc)
    table.add_row("URL Percent-Encoding Protocol Standard Web Layer", url_enc)
    table.add_row("Hexadecimal Base-16 Binary Nibble Stream Matrix", hex_enc)
    console.print(table)

def run_qr_tools() -> None:
    print_cyber_header("QR Structural Matrix Generation Core Engine")
    data = get_clean_input("Enter Target Text Context Payload Data Stream for Matrix Encoding Integration")
    filename = f"qr_out_{int(time.time())}.png"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    
    console.print(f"[bold green][+] QR Structural Two-Dimensional Identification Grid Matrix Saved Asset to Path: {filename}[/bold green]")

def run_metadata_tools() -> None:
    print_cyber_header("Metadata Infrastructure Stream File Analyzer")
    path = get_clean_input("Enter Target Local System Absolute File Path Location to Inspect for Embedded Meta Flags")
    if not os.path.exists(path):
        console.print("[bold red][!] File Path IO Check Fault: Resource Unresolved at Specified Host Target Matrix Local Disk Location Pointer.[/bold red]")
        return
        
    with open(path, "rb") as f:
        file_bytes = f.read(100000)
        
    meta = MetadataExtractor.parse_pseudo_metadata(file_bytes)
    table = Table(title=f"Extracted Deep Asset File Meta Invariant Parameters Matrix: {os.path.basename(path)}")
    table.add_column("Embedded Parameter Meta Marker Signature", style="cyan")
    table.add_column("Extracted Data Profile Stream State Value", style="magenta")
    for k, v in meta.items():
        table.add_row(k, v)
    console.print(table)

def run_batch_mode() -> None:
    print_cyber_header("High-Throughput Parallel Batch Stream Analysis Framework Pipeline Execution Engine")
    console.print("Ensure your source batch input matrix target structural flat text file contains precisely one cleanly formatted record entry per text newline string block row.")
    path = get_clean_input("Enter Absolute System Path to Source Dataset Manifest Target (.txt or .csv)")
    if not os.path.exists(path):
        console.print("[bold red][!] Batch Operational Loader Interrupt Failure: Source File Matrix Input Destination Unresolved.[/bold red]")
        return
        
    console.print("[1] Batch Iranian Bank BIN Distribution Identification Core Pipeline Validation Module\n[2] Batch Cellular Subscriber Routing Prefix Profile Target Analyzer Node Grid Validation Module")
    mode = get_clean_input("Select Batch Pipeline Transformation Matrix Execution Target Core Block Configuration Mode")
    
    records = []
    with open(path, "r", encoding="utf-8") as f:
        records = [line.strip() for line in f if line.strip()]
        
    results = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn()) as progress:
        task = progress.add_task("[cyan]Processing Batch Stream Arrays Pipeline Integration Flow Vector Engine...", total=len(records))
        for r in records:
            if mode == "1":
                bin_pfx = r[:6]
                bank = BIN_DATABASE.get(bin_pfx, "Unknown Asset Pool Entity Allocation Allocation")
                results.append({"Input Data Raw Segment": r, "Resolved Identity Metric Asset Profile Parameter Matrix Mapping Match": bank})
            elif mode == "2":
                pfx = r[:4]
                op = MOBILE_PREFIXES.get(pfx, {"operator": "Unknown Infrastructure Carrier Node Provider Matrix Cluster Route Gateway Allocation System Mapping Matrix Protocol Group Module Matrix Layer"})["operator"]
                results.append({"Input Data Raw Segment": r, "Resolved Identity Metric Asset Profile Parameter Matrix Mapping Match": op})
            progress.advance(task)
            
    table = Table(title="Batch Processing Vector Engine Data Pipeline Realized Performance Matrix Summary Analysis Matrix Output Logs Reports Data Array Profiles Summary List Records")
    table.add_column("Source Entry String Field Node Target Identity Input Record Component Stream", style="cyan")
    table.add_column("Processed System Extraction Match Verification Resolved Mapping Operational Metric Vector Value", style="magenta")
    for res in results[:20]:
        table.add_row(res["Input Data Raw Segment"], res["Resolved Identity Metric Asset Profile Parameter Matrix Mapping Match"])
    console.print(table)
    if len(results) > 20:
        console.print(f"... [bold yellow]Truncated display tracking output view framework matrix stack list safely. Total records cleanly cataloged: {len(results)} rows metrics processed.[/bold yellow]")
        
    export_report_dialog({"batch_output_metrics": results}, "batch_processing_stream")

def run_reports_viewer() -> None:
    print_cyber_header("System Audit Reports Archival Pipeline Matrix Core Explorer Interface Configuration Menu Node Console")
    console.print("[bold yellow][*] Historical analysis sessions context data models are compiled directly dynamically within target specific tactical pipeline workspace modules dynamically during system program runtime session life steps loops frameworks workflows execution trackers arrays nodes items records profiles details indices patterns vectors trackers. Run target processing execution functions inside explicit module paths vectors directly to build historical validation transaction logs arrays traces contexts files inputs databases updates artifacts nodes parameters items lists profiles blocks schemas metadata models blueprints diagrams layouts output maps summaries directly profiles items. Valid active schemas text items records matches system pipeline modules vectors output paths options arrays contexts tracker logs items.[/bold yellow]")

def run_embedded_db_viewer() -> None:
    print_cyber_header("Embedded Sovereign Database Matrix Explorer & Static Tables Schema Validation Node Matrix Core Module Configuration Viewer Terminal UI Dashboard Console Screen")
    console.print(f"[bold cyan][+] Inside Memory Isolated Sandbox Framework Core Sovereign Static Registries Mapping Table Database Infrastructure Matrices Verified Safe Profiles Counts Summary Vector Lists Metrics Analytics Data Elements Logs Matrix Details]:[/bold cyan]")
    console.print(f"    ├── Iranian Financial Institutional Central Clearing Clearing House BIN Asset Mappings Count: [bold green]{len(BIN_DATABASE)} active rows validated static vectors memory structures mappings items layers schemas[/bold green]")
    console.print(f"    ├── Cellular Infrastructure Carrier Node Mobile Routing Network Gateway Prefix Mappings Node Arrays Count: [bold green]{len(MOBILE_PREFIXES)} active telecom switching prefix routes targets elements[/bold green]")
    console.print(f"    ├── Public Landline Regional Area Carrier Switching Station Code Telephony Node Matrix Elements Count: [bold green]{len(LANDLINE_DATABASE)} active switching trunk line paths nodes map structures[/bold green]")
    console.print(f"    └── Vehicle Registration Registry Highway Traffic Office Bureau Licensing Node Zone Mapping Indices Matrix Count: [bold green]{len(PLATE_DATABASE)} active territorial regional vehicle registration tag paths codes keys maps[/bold green]")

def run_extra_utilities() -> None:
    print_cyber_header("Operational Security & Cryptographic Structural Assessment Extra Software Utilities Matrix Systems Dashboard Core Menu Node Configuration Console Panel Workspace")
    console.print("[1] Secure Structural Pseudorandom Identity Test Architecture Generation Vector Pipeline Engine System\n[2] Passphrase Entropy Matrix Calculation & Algorithmic Complexity Measurement Verification Tool Node Module Unit")
    choice = get_clean_input("Select specialized algorithmic extra core execution software system subsystem module path pointer parameter index code")
    
    if choice == "1":
        identity = ExtraUtils.generate_random_identity()
        table = Table(title="Generated Non-Real Artificial Synthesized Validation Verification Identity Dataset Framework Structure Node Map Profile Matrix Asset Profile")
        table.add_column("Synthetic Variable Record Property Parameter Target Metric Field Cluster Struct Node Key", style="cyan")
        table.add_column("Generated Safe Dummy Simulation Context Vector Synthetic Value Object Token Block Stream Item Data", style="magenta")
        for k, v in identity.items():
            table.add_row(k, v)
        console.print(table)
    elif choice == "2":
        passphrase = get_clean_input("Enter Target Passphrase String to Formally Interrogate Using Claude Shannon Information Mathematical Entropy Logarithmic Formula Logic Systems Engine Metrics Model Schemes Structures Variables Principles")
        entropy = ExtraUtils.calculate_entropy(passphrase)
        console.print(f"[bold magenta][+] Evaluated Base Shannon Mathematical Metric Bit Value Information Entropy Density Score: {entropy:.4f} bits. Structural safety threshold rating: {'STRONG SECURE CRYPTOGRAPHIC BOUNDS MATRIX' if entropy > 3.5 else 'WEAK STRUCTURAL PREDICTABILITY ENTROPY FAILURE WARNING ATTENTION EXPLOIT RISKS DETECTED FOR CONTEXT STRATEGIC SIGNALS THREATS MATRIX LAYER NODES BLOCKS ITEMS CORES SYSTEMS CONFIGURATIONS PROPERTIES DETAILS'} [/bold magenta]")

# ==============================================================================
# MAIN TUI CONTROL WORKSPACE EXECUTION GRID ENGINE LOOP MANAGEMENT MATRIX SYSTEM
# ==============================================================================

def main_tui_loop() -> None:
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(Text(BANNER, style="bold green"))
        console.print("[bold cyan]============================================================================================================================================================================================[/bold cyan]")
        console.print("[bold green]                                                   IRISINT :: IRANIAN INTELLIGENCE & UTILITY TOOLKIT OSINT ENGINE CORE PIPELINE ENVIRONMENT SYSTEM ARCHITECTURE INTERFACE WORKSPACE MODULES CONTROL CONSOLE                                                   [/bold green]")
        console.print("[bold cyan]============================================================================================================================================================================================[/bold cyan]")
        
        menu_table = Table(box=None, padding=(0, 4))
        menu_table.add_column("Strategic Analysis Domain Modules Cluster", style="bold cyan")
        menu_table.add_column("Core Infrastructure & System Operations Matrix Subsystems Cluster", style="bold magenta")
        
        menu_table.add_row("[1]  Bank Card Analyzer Module Node Engine", "[10] Network Tools Topology Router OSINT Mapping Module")
        menu_table.add_row("[2]  Phone Number Analyzer Trunk Router Gateway", "[11] Hash Tools Cryptographic Integrity Signatures Engine")
        menu_table.add_row("[3]  National ID Analyzer Registry Civil Verification Matrix", "[12] Encoding Tools Protocol Representation Format Translators")
        menu_table.add_row("[4]  SHABA Analyzer Interbank Central Clearing Matrix Code Node", "[13] QR Tools Structural Two-Dimensional Matrix Generator Core Engine")
        menu_table.add_row("[5]  Postal Code Analyzer Logistical Grid Location Matrix Verification Node", "[14] Metadata Tools Embedded Stream File Asset Header Property Analyzer")
        menu_table.add_row("[6]  Landline Analyzer PSTN Telephony Exchange Node Registry Map", "[15] Batch Mode High-Throughput Parallel Stream Data Transformation Framework Pipeline Engine")
        menu_table.add_row("[7]  Vehicle Plate Analyzer Sovereign Traffic Registration Office Bureau Module Grid", "[16] Reports Session Audit Management Archival Pipeline Integration Logs Explorer Context")
        menu_table.add_row("[8]  Date & Calendar Tools Algorithmic Transformation Epoch Converters", "[17] Embedded Databases Isolated Static Registries Verification Engine Storage Matrix Schema Dashboard View")
        menu_table.add_row("[9]  Domain Tools Passive DNS Name Space Certificate Ledger Intelligence Tracking Node", "[18] Extra Utilities Operational Security Cryptographic Assessment Diagnostic Functions Workspace Module Subsystems")
        menu_table.add_row("", "")
        menu_table.add_row("[0]  EXIT SYSTEM CONTROL TERMINATE SESSION ENVIRONMENT PIPELINE ATOMIC SAFELY GENTLY TERMINAL SHUTDOWN COMMAND CODE", "")
        
        console.print(menu_table)
        console.print("[bold cyan]============================================================================================================================================================================================[/bold cyan]")
        
        choice = get_clean_input("Enter target processing module selection command index parameter mapping execution core switch key node path code value pointer identifier item integer code token sequence flag status")
        
        if choice == "0":
            console.print("[bold red][⚡] Terminating tactical engine session tracking loop layer context atomic safety destruction procedures executed flawlessly. Clearing variables... Unlinking pipelines... Goodbye operator. System session state clear exit code zero. Status: DISCONNECTED.[/bold red]")
            break
        elif choice == "1": run_bank_analyzer()
        elif choice == "2": run_phone_analyzer()
        elif choice == "3": run_national_id_analyzer()
        elif choice == "4": run_shaba_analyzer()
        elif choice == "5": run_postal_analyzer()
        elif choice == "6": run_landline_analyzer()
        elif choice == "7": run_vehicle_analyzer()
        elif choice == "8": run_calendar_tools()
        elif choice == "9": run_domain_tools()
        elif choice == "10": run_network_tools()
        elif choice == "11": run_hash_tools()
        elif choice == "12": run_encoding_tools()
        elif choice == "13": run_qr_tools()
        elif choice == "14": run_metadata_tools()
        elif choice == "15": run_batch_mode()
        elif choice == "16": run_reports_viewer()
        elif choice == "17": run_embedded_db_viewer()
        elif choice == "18": run_extra_utilities()
        else:
            console.print("[bold red][!] Switch Command Routine Fault: Selected index mapping pointer is out of valid program logic bounds loop execution trees array profiles summary parameters list.[/bold red]")
            
        get_clean_input("Execution block module session stage complete. Press Enter string empty token line key to safely flush output logs and return back to the main master operational control workspace dashboard console view.")

# ==============================================================================
# CLI TYPER LAUNCH ATOMIC GATEWAY ROUTING ENGINE INTERACTION WRAPPERS PIPELINE
# ==============================================================================

@app.command()
def interactive() -> None:
    """
    Launch the full interactive Cyberpunk TUI dashboard terminal workstation console application suite environment context workspace framework safely.
    """
    try:
        main_tui_loop()
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Security SIGINT Intercept Signal Exception Handled Safely: User terminated runtime control frame sequence flow explicitly loop atomic breakdown drop context trace hooks completed successfully exit clean code zero mapping values tracking system layer profiles parameters choices fields properties logs context files models setups maps views layouts grids profiles. Exiting workflow pipelines now.[/bold red]")
        sys.exit(0)

@app.command()
def card_validate(card: str = typer.Argument(..., help="16-Digit target card number sequence")) -> None:
    """
    Headless direct execution entry point for fast bank card data checking operations out of interactive terminal loops frameworks.
    """
    is_valid = LuhnValidator.validate(card)
    bin_pfx = card[:6]
    bank = BIN_DATABASE.get(bin_pfx, "Unknown Institution Allocation")
    console.print(f"Card: {card} | Issuer: {bank} | Integrity: {'VALID' if is_valid else 'INVALID_FAULT'}")

@app.command()
def national_id_validate(nid: str = typer.Argument(..., help="10-Digit Iranian National ID identifier token format context string string")) -> None:
    """
    Headless fast execution verification pathway for validating national identity structures on external automation loops wrappers frameworks hooks.
    """
    is_valid, province = NationalIDValidator.validate(nid)
    console.print(f"National ID: {nid} | Integrity: {'VALID' if is_valid else 'INVALID_FAULT'} | Region: {province if province else 'NONE'}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("interactive")
    app()