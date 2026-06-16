import sys
import re
import json
import hashlib
import base64
import urllib.parse
import uuid
import random
import string
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# Third-party libraries
try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt
    from rich import print as rprint
    import qrcode
    from tabulate import tabulate
except ImportError as e:
    print(f"Missing dependency: {e.name}. Please install required libraries:")
    print("pip install rich typer qrcode tabulate requests")
    sys.exit(1)

app = typer.Typer()
console = Console()

# --- EMBEDDED DATABASES ---

BANKS_BIN: Dict[str, str] = {
    "603799": "Melli", "170019": "Melli", "603769": "Saderat", "627648": "Saderat",
    "621986": "Saman", "624124": "Saman", "627412": "Eghtesad Novin", "627488": "Karafarin",
    "622106": "Parsian", "627884": "Parsian", "627353": "Tejarat", "585983": "Tejarat",
    "610433": "Mellat", "991975": "Mellat", "627381": "Ansar", "636214": "Ayandeh",
    "502229": "Pasargad", "639347": "Pasargad", "628023": "Maskan", "627961": " صنعت و معدن",
    "603770": "Keshavarzi", "639217": "Keshavarzi", "627760": "Post Bank", "502908": "Tose-e Taavon",
    "627429": "Tourism Bank", "502806": "Shahr", "502938": "Day", "606373": "Mehr Iran",
    "639346": "Sina", "639607": "Sarmayeh", "628157": "Moasese Ettebari Tose-e", "505801": "Kowsar",
    "504172": "Resalat", "505785": "Iran Zamin", "636949": "Hekmat", "606256": "Melal",
}

MOBILE_OPERATORS: Dict[str, str] = {
    "0910": "Hamrah Aval", "0911": "Hamrah Aval", "0912": "Hamrah Aval", "0913": "Hamrah Aval",
    "0914": "Hamrah Aval", "0915": "Hamrah Aval", "0916": "Hamrah Aval", "0917": "Hamrah Aval",
    "0918": "Hamrah Aval", "0919": "Hamrah Aval", "0990": "Hamrah Aval", "0991": "Hamrah Aval",
    "0930": "Irancell", "0933": "Irancell", "0935": "Irancell", "0936": "Irancell",
    "0937": "Irancell", "0938": "Irancell", "0939": "Irancell", "0901": "Irancell",
    "0902": "Irancell", "0903": "Irancell", "0904": "Irancell", "0905": "Irancell",
    "0934": "TKC", "0920": "Rightel", "0921": "Rightel", "0922": "Rightel",
    "0998": "Shatel Mobile", "0999": "Lotuspaly / Samantel",
}

PLATE_PROVINCES: Dict[str, str] = {
    "11": "Tehran (Central)", "22": "Tehran (West)", "33": "Tehran (South)", "44": "Tehran (East)",
    "55": "Tehran", "66": "Tehran", "77": "Tehran", "88": "Tehran", "99": "Tehran",
    "10": "Tehran", "20": "Tehran", "30": "Tehran", "12": "Khorasan Razavi", "32": "Khorasan Razavi",
    "42": "Khorasan Razavi", "13": "Isfahan", "23": "Isfahan", "43": "Isfahan", "14": "West Azerbaijan",
    "15": "Mazandaran", "16": "Gilat", "17": "Fars", "18": "Khuzestan", "19": "Kermanshah",
}

# --- LOGIC MODULES ---

def luhn_check(number: str) -> bool:
    """Standard Luhn Algorithm for card validation."""
    digits = [int(d) for d in number]
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            multiplied = digit * 2
            checksum += multiplied if multiplied < 10 else multiplied - 9
        else:
            checksum += digit
    return checksum % 10 == 0

def validate_national_id(melli_code: str) -> bool:
    """Validates Iranian National ID (Melli Code)."""
    if not re.match(r"^\d{10}$", melli_code):
        return False
    check = int(melli_code[9])
    summ = sum(int(melli_code[i]) * (10 - i) for i in range(9))
    remainder = summ % 11
    return (remainder < 2 and check == remainder) or (remainder >= 2 and check == 11 - remainder)

def validate_shaba(shaba: str) -> bool:
    """Validates Iranian IBAN (SHABA)."""
    shaba = shaba.upper().replace(" ", "").replace("IR", "")
    if len(shaba) != 24:
        return False
    # Move 'IR' (18 27) to the end
    reordered = shaba[2:] + "1827" + shaba[:2]
    try:
        return int(reordered) % 97 == 1
    except ValueError:
        return False

def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
    """Basic conversion algorithm for Gregorian to Jalali."""
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    for i in range(gm2):
        g_day_no += g_days_in_month[i]
    if gm2 > 1 and ((gy2 % 4 == 0 and gy2 % 100 != 0) or (gy2 % 400 == 0)):
        g_day_no += 1
    g_day_no += gd2

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    for i in range(11):
        if j_day_no < j_days_in_month[i]:
            jm = i + 1
            jd = j_day_no + 1
            return jy, jm, jd
        j_day_no -= j_days_in_month[i]
    jm = 12
    jd = j_day_no + 1
    return jy, jm, jd

# --- UI HELPERS ---

def show_banner():
    banner = """
[bold cyan]██████╗ ██████╗ ██╗███████╗██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██║██╔════╝██║████╗  ██║╚══██╔══╝
██████╔╝██████╔╝██║███████╗██║██╔██╗ ██║   ██║   
██╔══██╗██╔══██╗██║╚════██║██║██║╚██╗██║   ██║   
██║  ██║██║  ██║██║███████║██║██║ ╚████║   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝[/bold cyan]
[dim yellow]Iranian Intelligence & Utility Toolkit (IRISINT)[/dim yellow]
    """
    console.print(banner)

def get_status_icon(valid: bool) -> str:
    return "[green]✔ VALID[/green]" if valid else "[red]✘ INVALID[/red]"

# --- CLI COMMANDS ---

@app.command()
def bank(card_number: str = typer.Argument(..., help="16-digit Iranian bank card number")):
    """Analyze Iranian Bank Card."""
    clean_card = card_number.replace("-", "").replace(" ", "")
    bin_code = clean_card[:6]
    bank_name = BANKS_BIN.get(bin_code, "Unknown Bank")
    is_valid = luhn_check(clean_card) and len(clean_card) == 16

    table = Table(title="Bank Card Analysis", show_header=False, border_style="cyan")
    table.add_row("Card Number", clean_card)
    table.add_row("Issuing Bank", f"[bold]{bank_name}[/bold]")
    table.add_row("BIN Code", bin_code)
    table.add_row("Luhn Validation", get_status_icon(is_valid))
    
    console.print(Panel(table, title="[bold white]IRISINT Result[/bold white]", border_style="blue"))

@app.command()
def phone(number: str = typer.Argument(..., help="Iranian phone number (e.g. 0912...)")):
    """Analyze Mobile Phone Operator."""
    clean_num = number.strip()
    if clean_num.startswith("+98"): clean_num = "0" + clean_num[3:]
    prefix = clean_num[:4]
    operator = MOBILE_OPERATORS.get(prefix, "Unknown / Landline")
    
    table = Table(title="Phone Analysis", show_header=False, border_style="cyan")
    table.add_row("Input", clean_num)
    table.add_row("Operator", f"[bold magenta]{operator}[/bold magenta]")
    table.add_row("Type", "Mobile" if prefix in MOBILE_OPERATORS else "Fixed/Unknown")
    
    console.print(Panel(table, border_style="blue"))

@app.command()
def national_id(code: str = typer.Argument(..., help="10-digit National ID")):
    """Validate Iranian National ID."""
    is_valid = validate_national_id(code)
    city_code = code[:3]
    
    table = Table(title="National ID Analysis", show_header=False, border_style="cyan")
    table.add_row("National ID", code)
    table.add_row("City Code Prefix", city_code)
    table.add_row("Status", get_status_icon(is_valid))
    
    console.print(Panel(table, border_style="blue"))

@app.command()
def shaba(code: str = typer.Argument(..., help="SHABA Number (IR...)")):
    """Validate and Parse Iranian SHABA (IBAN)."""
    is_valid = validate_shaba(code)
    bank_id = code[4:7] if len(code) > 7 else "???"
    
    table = Table(title="SHABA Analysis", show_header=False, border_style="cyan")
    table.add_row("SHABA", code.upper())
    table.add_row("Bank ID Part", bank_id)
    table.add_row("Status", get_status_icon(is_valid))
    
    console.print(Panel(table, border_style="blue"))

@app.command()
def date(
    year: int = typer.Option(None), 
    month: int = typer.Option(None), 
    day: int = typer.Option(None),
    now: bool = typer.Option(False, "--now", help="Show current dates")
):
    """Gregorian to Jalali Date Converter."""
    if now:
        dt = datetime.now()
        year, month, day = dt.year, dt.month, dt.day
    elif not (year and month and day):
        rprint("[red]Error: Please provide --year, --month, --day or use --now[/red]")
        return

    jy, jm, jd = gregorian_to_jalali(year, month, day)
    
    table = Table(title="Calendar Conversion", border_style="yellow")
    table.add_column("Type", style="cyan")
    table.add_column("Date", style="bold white")
    table.add_row("Gregorian", f"{year}-{month:02d}-{day:02d}")
    table.add_row("Jalali", f"{jy}/{jm:02d}/{jd:02d}")
    
    console.print(table)

@app.command()
def hash_tool(text: str, algo: str = "sha256"):
    """Generate hashes for text."""
    algo = algo.lower()
    data = text.encode()
    
    if algo == "md5": h = hashlib.md5(data)
    elif algo == "sha1": h = hashlib.sha1(data)
    elif algo == "sha256": h = hashlib.sha256(data)
    elif algo == "sha512": h = hashlib.sha512(data)
    else:
        rprint("[red]Unsupported algorithm[/red]")
        return
        
    console.print(f"[bold cyan]{algo.upper()}:[/bold cyan] [white]{h.hexdigest()}[/white]")

@app.command()
def qr(data: str, filename: str = "irisint_qr.png"):
    """Generate a QR code."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Generating QR...", total=None)
        img = qrcode.make(data)
        img.save(filename)
    rprint(f"[green]QR Code saved to: {filename}[/green]")

@app.command()
def plate(number: str):
    """Analyze Iranian vehicle plate (First 2 digits)."""
    code = number[:2]
    prov = PLATE_PROVINCES.get(code, "Unknown / Specialized")
    rprint(Panel(f"Plate Prefix: [bold]{code}[/bold]\nProvince: [bold cyan]{prov}[/bold cyan]", title="Plate Analysis"))

@app.command()
def random_id():
    """Generate a random identity for testing."""
    f_names = ["Ali", "Reza", "Saeed", "Mohammad", "Amir", "Zahra", "Maryam"]
    l_names = ["Ahmadi", "Hosseini", "Karimi", "Mousavi", "Hashemi", "Amiri"]
    
    fake_name = f"{random.choice(f_names)} {random.choice(l_names)}"
    fake_code = "".join([str(random.randint(0, 9)) for _ in range(9)])
    # Add valid check digit for fake code
    summ = sum(int(fake_code[i]) * (10 - i) for i in range(9))
    rem = summ % 11
    check = rem if rem < 2 else 11 - rem
    fake_melli = f"{fake_code}{check}"
    
    rprint(Panel(f"Name: {fake_name}\nNational ID: {fake_melli}\nUUID: {uuid.uuid4()}", title="Test Data"))

# --- MAIN MENU ---

def interactive_menu():
    while True:
        console.clear()
        show_banner()
        
        menu_table = Table(box=None, show_header=False)
        menu_table.add_column("ID", style="bold yellow")
        menu_table.add_column("Feature", style="white")
        
        features = [
            ("1", "Bank Card Analyzer"),
            ("2", "Phone Number Analyzer"),
            ("3", "National ID Analyzer"),
            ("4", "SHABA Analyzer"),
            ("5", "Vehicle Plate Analyzer"),
            ("6", "Date Converter (Now)"),
            ("7", "Hash Tools (SHA256)"),
            ("8", "Random Identity Gen"),
            ("9", "QR Code Generator"),
            ("0", "Exit")
        ]
        
        for fid, fdesc in features:
            menu_table.add_row(fid, fdesc)
            
        console.print(Panel(menu_table, title="[bold cyan]MAIN MENU[/bold cyan]", border_style="cyan"))
        
        choice = Prompt.ask("Select an option", choices=[f[0] for f in features], default="0")
        
        if choice == "1":
            num = Prompt.ask("Enter Card Number")
            bank(num)
        elif choice == "2":
            num = Prompt.ask("Enter Phone Number")
            phone(num)
        elif choice == "3":
            code = Prompt.ask("Enter National ID")
            national_id(code)
        elif choice == "4":
            code = Prompt.ask("Enter SHABA (IR...)")
            shaba(code)
        elif choice == "5":
            num = Prompt.ask("Enter Plate Prefix (2 digits)")
            plate(num)
        elif choice == "6":
            date(now=True)
        elif choice == "7":
            txt = Prompt.ask("Enter text to hash")
            hash_tool(txt)
        elif choice == "8":
            random_id()
        elif choice == "9":
            txt = Prompt.ask("Enter QR Data")
            qr(txt)
        elif choice == "0":
            rprint("[bold red]Exiting IRISINT...[/bold red]")
            break
            
        Prompt.ask("\nPress Enter to continue")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """IRISINT: Iranian Intelligence & Utility Toolkit"""
    if ctx.invoked_subcommand is None:
        interactive_menu()

if __name__ == "__main__":
    app()