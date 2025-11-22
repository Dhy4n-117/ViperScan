from colorama import init, Fore, Style

# Initialize colorama (autoreset=True means it resets color after every print)
init(autoreset=True)

class Color:
    GREEN = Fore.GREEN + Style.BRIGHT
    RED = Fore.RED + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    BLUE = Fore.CYAN + Style.BRIGHT
    RESET = Style.RESET_ALL