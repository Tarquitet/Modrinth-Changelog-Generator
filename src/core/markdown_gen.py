def generate_diff(old_mods, new_mods):
    added = [m for m in new_mods if m not in old_mods]
    removed = [m for m in old_mods if m not in new_mods]
    updated = [m for m in new_mods if m in old_mods and new_mods[m] != old_mods[m]]

    output = "## Changelog\n\n"
    if added:
        output += "### Added\n" + "\n".join([f"* {m}" for m in added]) + "\n\n"
    if removed:
        output += "### Removed\n" + "\n".join([f"* {m}" for m in removed]) + "\n\n"
    if updated:
        output += "### Updated\n" + "\n".join([f"* {m}" for m in updated]) + "\n\n"
    if not added and not removed and not updated:
        output += "*No changes detected in the mod list.*\n"
        
    return output

def generate_full_list(new_mods):
    output = "## Included Mods\n\n"
    sorted_mods = sorted(new_mods.keys())
    for mod in sorted_mods:
        clean_name = mod.split('-mc')[0].split('+')[0]
        output += f"* {clean_name}\n"
    return output