# positions mapping
offense_positions = ["C", "OG", "OT", "QB", "RB", "TE", "WR"]
offense_position_map = {
    "FB": "RB",
    "FB/DL": "RB",
    "FB/TE": "RB",
    "FB/RB": "RB",
    "FB/T": "TE",
    "FB/R": "RB",
    "FL": "WR",
    "FB-T": "TE",
    "FB'": "RB",
    "F": "TE",
    "HB": "RB",
    "HB-F": "TE",
    "HB/F": "TE",
    "H-B": "TE",
    "LOT": "OT",
    "LT": "OT",
    "LG": "OG",
    "LWR": "WR",
    "OL": "OG",
    "QB/W": "WR",
    "RB-F": "RB",
    "RB/F": "RB",
    "RB-K": "RB",
    "RB/K": "RB",
    "RWR": "WR",
    "RT": "OT",
    "RG": "OG",
    "SE": "WR",
    "T": "OT",
    "TE/L": "TE",
    "TE/W": "TE",
    "TE/F": "TE",
    "TE-F": "TE",
    "WR-K": "WR",
    "WR/K": "WR",
    "QB-W": "WR",
    "WR/RS": "WR",
    "WR/PR": "WR",
    "WR/P": "WR",
    "WR/R": "WR",
    "WR-R": "WR",
    "WR W": "WR",
    "G-C": "C",
    "G": "OG",
    "C/G": "C",
    "G/C": "C",
    "OW": "RB",
    "KR/P": "RB",
    "KR-R": "RB",
    "KR": "WR",
    "TB": "TE",
    "WC": "WR",
    "G/T": "OG",
    "T/G": "OT",
}

defense_positions = ["DEF", "DL", "DE", "CB", "LB", "S"]
defense_position_map = {
    "LCB": "CB",
    "RCB": "CB",
    "ILB": "LB",
    "MLB": "LB",
    "OLB": "LB",
    "LOLB": "LB",
    "DB": "CB",
    "FS": "S",
    "SS": "S",
    "SLB": "LB",
    "DT": "DE",
    "CB/R": "CB",
    "RDE": "DE",
    "NT": "DL",
    "NB": "S",
    "WLB": "LB",
    "ROLB": "LB",
    "LDT": "DE",
    "RDT": "DE",
    "DB/LB": "LB",
    "CB/RS": "CB",
}

special_positions = ["P", "K", "LS"]
special_position_map = {}

positions = offense_positions + defense_positions + special_positions