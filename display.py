from tabulate import tabulate
import libs.termcolors as tc


def describe(p):
    print("\n", tc.color.YELLOW+u"\U0001F5C0", " ",
          tc.color.BOLD + tc.color.BRIGHT_WHITE + p.name+tc.color.END, end=" "),

    if(p.is_active):
        osize = p.get_pretty_size()
        print(tc.color.GREEN + u"\U000023FA" + tc.color.END +
              "  active  "+tc.color.GREY+p.uid + tc.color.END)
        print(" |_ Short UID          : " + tc.color.BOLD +
              p.get_uid_short() + tc.color.END)
        print(" |_ Original Size      : " + tc.color.BOLD +
              "{}".format(osize) + tc.color.END)
        print(" |_ Created at         : " + p.get_pretty_created_time())
        print(" |_ Last accessed      : " + p.get_pretty_last_mod() + "\n")

    else:
        osize = p.get_pretty_size()
        csize = p.get_pretty_size(p.compressed_size)
        print(u"\U000023FA" + "  archived  " +
              tc.color.GREY+p.uid + tc.color.END)
        print(" |_ Short UID          : " + tc.color.BOLD +
              p.get_uid_short() + tc.color.END)
        print(" |_ Original Size      : " + tc.color.BOLD +
              "{}".format(osize) + tc.color.END)
        print(" |_ Compressed size    : " + tc.color.GREEN +
              tc.color.BOLD+"{}".format(csize) + tc.color.END)
        print(" |_ Compression ratio  : " + tc.color.BOLD +
              str(round((p.compressed_size * 1.05/p.size)*100, 1)) + "%" + tc.color.END)
        print(" |_ Last accessed      : {} \n".format(
            p.get_pretty_last_mod()))


def active(p_list):
    p_list.sort(key=lambda x: x.size, reverse=True)
    active_project_table = []

    for p in p_list:
        active_project_table.append([
            p.get_uid_short(),
            tc.color.BRIGHT_WHITE + tc.color.BOLD + p.name + tc.color.END,
            tc.color.GREY + p.get_pretty_last_mod() + tc.color.END,
            tc.color.BOLD + p.get_pretty_size() + tc.color.END
        ])

    print(
        "\n",
        tabulate(
            active_project_table,
            headers=["UID", "Name", "LastMod", "Size"]
        ),
        "\n")


def archive(p_list):
    p_list.sort(key=lambda x: x.size, reverse=True)
    archive_project_table = []

    for p in p_list:
        archive_project_table.append([
            p.get_uid_short(),
            tc.color.BRIGHT_WHITE + tc.color.BOLD + p.name + tc.color.END,
            tc.color.GREY + p.get_pretty_last_mod() + tc.color.END,
            tc.color.BOLD + p.get_pretty_size() + tc.color.END,
            tc.color.GREEN +
            p.get_pretty_size(p.compressed_size) + tc.color.END,
        ])

    print(
        "\n",
        tabulate(
            archive_project_table,
            headers=["UID", "Name", "Archived",
                     "OriginalSize", "CompressedSize"]
        ),
        "\n")
    return 0


def global_list(p_list):
    p_list.sort(key=lambda x: x.size, reverse=True)
    archive_project_table = []

    for p in p_list:
        size = p.get_pretty_size() if p.is_active else p.get_pretty_size(p.compressed_size)
        if (p.is_active):
            state = tc.color.GREEN + u"\U000023FA" + tc.color.END + "  Active"
        else:
            state = tc.color.YELLOW + u"\U000023FA" + tc.color.END + "  Archived"
        archive_project_table.append([
            p.get_uid_short(),
            tc.color.BRIGHT_WHITE + tc.color.BOLD + p.name + tc.color.END,
            tc.color.GREY + p.get_pretty_last_mod() + tc.color.END,
            tc.color.BOLD + size + tc.color.END,
            p.namespace,
            state,
        ])

    print(
        "\n",
        tabulate(
            archive_project_table,
            headers=["UID", "Name", "LastMod", "Size", "NameSpace", "State"]
        ),
        "\n")
    return 0


