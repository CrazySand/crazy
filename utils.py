import msvcrt
import re

from colorama import Fore, Style

def cinput(prompt: str) -> str:
    while msvcrt.kbhit():
        msvcrt.getch()
    return input(prompt)

def standard_filename(string):
    pattern = r"[^a-zA-Z0-9\u4E00-\u9FA5_]+"
    return re.sub(pattern, "_", string)

class CS:

    @staticmethod
    def red(string: str) -> str:
        return Fore.RED + string + Style.RESET_ALL
    
    @staticmethod
    def green(string: str) -> str:
        return Fore.GREEN + string + Style.RESET_ALL
    
    @staticmethod
    def purple(string: str) -> str:
        return Fore.MAGENTA + string + Style.RESET_ALL
    
    @staticmethod
    def yellow(string: str) -> str:
        return Fore.YELLOW + string + Style.RESET_ALL

    @staticmethod
    def blue(string: str) -> str:
        return Fore.LIGHTBLUE_EX + string + Style.RESET_ALL