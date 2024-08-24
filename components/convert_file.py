def process_file(input_file, output_file):
    # Đọc file và tạo mảng S
    S = []
    lines = []
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.split()
            id1 = int(parts[1])
            id2 = int(parts[2])
            if id1 not in S:
                S.append(id1)
            if id2 not in S:
                S.append(id2)
            lines.append(parts)

    # Sắp xếp mảng S và tạo mảng N
    S.sort()
    N = list(range(1, len(S) + 1))
    #print(N)

    # Tạo một từ điển ánh xạ từ S sang N
    mapping = {s: n for s, n in zip(S, N)}
    #print(mapping)


    # Tạo lại file với các chỉ số ID1 và ID2 được thay thế
    with open(output_file, 'w') as f:
        for parts in lines:
            id1 = int(parts[1])
            id2 = int(parts[2])
            parts[1] = str(mapping[id1])
            parts[2] = str(mapping[id2])
            f.write(' '.join(parts) + '\n')

# Sử dụng hàm
process_file('3x3Wards.txt', '1based_3x3Wards.txt')