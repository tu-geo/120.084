import re
import sys
import hashlib


CAT_PATTERN = {
    "NORAD": r"((<TD>\d{4,5}<\/TD>)+)",
    "COSPAR": r"((<TD>\d{7}<\/TD>)+)"
}


def run(category, filename):
    pattern = CAT_PATTERN[category]
    prog = re.compile(CAT_PATTERN[category], 0)
    ids = []
    #print("Scan", CAT_PATTERN[category])

    with open(filename, "r") as dat_file:
        for row in dat_file.readlines():
            r = prog.findall(str(row))
            if r:
                s = r[0][0].replace("</TD><TD>", ",").replace("<TD>", "").replace("</TD>", "").split(",")
                for item in s:
                    ids.append(item)
    return ids

if __name__ == "__main__":
    norad_file = sys.argv[1]
    cospar_file = sys.argv[2]
    mission = sys.argv[3].replace("_general.html", "")

    norad_id_list = run("NORAD", norad_file)
    cospar_id_list = run("COSPAR", cospar_file)

    final_list = []
    hash_value = hashlib.blake2b(digest_size=24)
    n_id = "00000"
    c_id = "0000000"
    hash_value.update("{}-{}".format(n_id, c_id).encode())
    h = hash_value.hexdigest()

    if len(norad_id_list) == len(cospar_id_list) and len(norad_id_list) != 0:
        unique_list = []
        for i in range(len(norad_id_list)):
            n_id = "{:05d}".format(int(norad_id_list[i]))
            c_id = str(cospar_id_list[i])
            hash_value.update("{}-{}".format(n_id, c_id).encode())
            h = hash_value.hexdigest()
            #print(h)
            #print(unique_list)
            if h not in unique_list:
                # print("Add {}-{}-{}".format(mission, n_id, c_id))
                final_list.append({
                    "mission": mission,
                    "norad": n_id,
                    "cospar": c_id,
                    "hash": h
                })
                unique_list.append(h)
    else:
        final_list.append({
            "mission": mission,
            "norad": n_id,
            "cospar": c_id,
            "hash": h
        })

    for item in final_list:
        print("{mission};{cospar};{norad};{hash}".format(**item))
