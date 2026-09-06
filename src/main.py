import re
import json

EMAIL_SHAPE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
CARD_SHAPE_MAIN = re.compile(r"\b(?:\d[ \-]?){15}\d\b")   # 16 digits, 4-4-4-4
CARD_SHAPE_AMEX = re.compile(r"\b\d{4}[ \-]?\d{6}[ \-]?\d{5}\b")  # amex, 4-6-5
PHONE_SHAPE = re.compile(r"(?:\+?\d{1,3}[ \-]?)?(?:\(\d{2,4}\)[ \-]?)?\d{3}[ \-]?\d{3}[ \-]?\d{3,4}")
LINK_SHAPE = re.compile(r"https?://[^\s<>\"']+")

# things that should never be treated as normal ticket text

RED_FLAGS = [
    re.compile(r"<\s*script.*?>", re.IGNORECASE),
    re.compile(r"'\s*or\s*'?1'?\s*=\s*'?1", re.IGNORECASE),
]


def only_digits(chunk):
    keep = ""
    for ch in chunk:
        if ch.isdigit():
            keep = keep + ch
    return keep


def passes_luhn(digit_string):

    # trick to verify card numbers - double every 2nd digit from the right, subtract 9
    # if it goes over 9, add it all up, needs to divide evenly by 10

    total = 0
    double_it = False
    i = len(digit_string) - 1
    while i >= 0:
        n = int(digit_string[i])
        if double_it:
            n = n * 2
            if n > 9:
                n = n - 9
        total = total + n
        double_it = not double_it
        i = i - 1
    return total % 10 == 0


def find_emails(text):
    hits = EMAIL_SHAPE.findall(text)
    good_ones = []
    for addr in hits:
        if addr in good_ones:
            continue
        if "@@" in addr or ".." in addr:
            continue  # shape matched but it's clearly broken, skip it

        alu_type = "n/a"
        lowered = addr.lower()
        if lowered.endswith("@alumni.alueducation.com"):
            alu_type = "alumni"
        elif lowered.endswith("@si.alueducation.com"):
            alu_type = "si"
        elif lowered.endswith("@alueducation.com"):
            alu_type = "official"

        # mask it - keep first 2 chars of the name, hide the rest

        at = addr.find("@")
        name = addr[:at]
        if len(name) > 2:
            name = name[:2]
        masked = name + "***" + addr[at:]

        good_ones.append({"masked": masked, "alu_type": alu_type})
    return good_ones


def find_cards(text):
    good_ones = []
    seen_digits = []
    tossed = 0
    for hit in CARD_SHAPE_MAIN.findall(text) + CARD_SHAPE_AMEX.findall(text):
        digits = only_digits(hit)
        if digits in seen_digits:
            continue
        seen_digits.append(digits)
        if passes_luhn(digits):
            good_ones.append("*" * (len(digits) - 4) + digits[-4:])
        else:
            tossed = tossed + 1 #failed the cardcheck 
    return good_ones, tossed


def find_phones(text):

    # cards can look like phone numbers too, so blank cards out first

    cleaned = CARD_SHAPE_MAIN.sub(" ", text)
    cleaned = CARD_SHAPE_AMEX.sub(" ", cleaned)
    good_ones = []
    for hit in PHONE_SHAPE.findall(cleaned):
        if len(only_digits(hit)) < 9:
            continue
        hit = hit.strip()
        if hit not in good_ones:
            good_ones.append(hit)
    return good_ones


def find_links(text):
    good_ones = []
    for link in LINK_SHAPE.findall(text):
        while len(link) > 0 and link[-1] in ".,)":
            link = link[:-1]
        if link not in good_ones:
            good_ones.append(link)
    return good_ones


def find_red_flags(text):

    # things that should never be treated as data

    caught = []
    for line in text.split("\n"):
        for pattern in RED_FLAGS:
            hit = pattern.search(line)
            if hit:
                caught.append(hit.group(0))
    return caught


def run():
    input_file = open("input/raw-text.txt", "r", encoding="utf-8")
    ticket_text = input_file.read()
    input_file.close()

    cards, tossed_cards = find_cards(ticket_text)
    red_flags = find_red_flags(ticket_text)
    results = {
        "emails": find_emails(ticket_text),
        "cards": cards,
        "phones": find_phones(ticket_text),
        "links": find_links(ticket_text),
    }

    print("emails:", len(results["emails"]))
    print("cards kept:", len(results["cards"]), "| tossed:", tossed_cards)
    print("phones:", len(results["phones"]))
    print("links:", len(results["links"]))
    print("red flags (not saved):", len(red_flags))
    for flag in red_flags:
        print(" -", flag)

    output_file = open("output/sample-output.json", "w", encoding="utf-8")
    json.dump(results, output_file, indent=2)
    output_file.close()
    print("done, check output/sample-output.json for the results")


run()

