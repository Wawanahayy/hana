color_codes = {
    "bg_black": "\033[40m",
    "bg_white": "\033[47m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_gray": "\033[48m",
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m"
}

def print_colored_blink(color_code, text):
    """Function to print text with color and blinking effect."""
    print(f"{color_code}\033[5m{text}\033[0m")

def display_colored_text():
    """Function to display a banner with colored and blinking text."""
    print_colored_blink(color_codes["bg_black"] + color_codes["cyan"], "============================================================")
    print_colored_blink(color_codes["bg_green"] + color_codes["white"], "=======================  J.W.P.A  ==========================")
    print_colored_blink(color_codes["bg_magenta"] + color_codes["white"], "================= @AirdropJP_JawaPride =====================")
    print_colored_blink(color_codes["bg_yellow"] + color_codes["black"], "=============== https://x.com/JAWAPRIDE_ID =================")
    print_colored_blink(color_codes["bg_red"] + color_codes["white"], "============= https://linktr.ee/Jawa_Pride_ID ==============")
    print_colored_blink(color_codes["bg_blue"] + color_codes["black"], "============================================================")
