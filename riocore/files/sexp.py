import ast


def loads(sdata):
    ref = []
    inside_q = 0
    inside_key = 0
    skey = {"str": ""}
    keys = []

    def add_ch(ch):
        ch = ch.replace('\\"', '\\\\"')
        if inside_key:
            if not inside_q and ch == " ":
                keys.append(skey["str"] + "'")
                skey["str"] = "'"
            else:
                skey["str"] += ch
        else:
            ref.append(ch)

    for ch in sdata:
        if ch in {"\n", "\t"}:
            continue
        if ch == '"':
            add_ch(ch)
            inside_q = 1 - inside_q
        elif inside_q:
            if ch == "'":
                add_ch("\\")
            add_ch(ch)
        elif ch == "(" and not inside_q:
            if inside_key:
                inside_key = 0
                if skey["str"].strip("'"):
                    keys.append(skey["str"] + "'")
                add_ch(",".join(keys))
                add_ch(",")

            add_ch("[")
            inside_key = 1
            skey["str"] = "'"
            keys = []
        elif ch == ")" and not inside_q:
            if inside_key:
                inside_key = 0
                if skey["str"].strip("'"):
                    keys.append(skey["str"] + "'")
                add_ch(",".join(keys))
            add_ch("],")
        elif ch == " " and not inside_key and not inside_q:
            inside_key = 1
            skey["str"] = "'"
            keys = []
            add_ch(ch)
        else:
            add_ch(ch)
    # print("".join(ref))
    # exit(0)
    lists = ast.literal_eval("".join(ref))
    if lists:
        # import json
        # print(json.dumps(lists[0], indent=4))
        return lists[0]


def dumps(lists):
    def lp(entry, result, prefix=""):
        if isinstance(entry, list):
            # bad hack for better debug-diffs
            if len(result) > 3 and "xy" in result[-4]:
                result.append(f" ({entry[0]}")
            else:
                result.append(f"\n{prefix}({entry[0]}")
            for part in entry[1:]:
                lp(part, result, prefix=f"{prefix}\t")
            if result[-1][-1] == ")":
                result.append(f"\n{prefix})")
            else:
                result.append(")")
        else:
            result.append(f" {entry.strip()}")

    result = []
    lp(lists, result)
    return "".join(result).strip()
