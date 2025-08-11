def read_index(fpath):
    dct = {}
    with open(fpath, 'r', encoding='utf-8') as fo:
        for line in fo:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                key = parts[0].strip()  # 清除空格、制表符
                values = [p.strip() for p in parts[1:]]  # 同样清除
                dct[key] = values
    return dct

