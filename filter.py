def removeZeroLines(file_path):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	# Lọc các dòng bắt đầu bằng 'c' hoặc kết thúc bằng số lớn hơn 0
	filtered_lines = [line for line in lines if line.startswith(('c', 's')) or (line.strip()[-1].isdigit() and int(line.strip()[-1]) > 0)]

	# Lưu các dòng được giữ lại vào file filtered.txt
	with open('filtered.txt', 'w') as out_file:
		for line in filtered_lines:
			out_file.write(line)

# Thay 'filtered.txt' bằng đường dẫn tới file của bạn
#filter_lines('seq-f.txt'). 

def filter_lines(seq_file_path, input_file_path, H):
	count = 0  # Bước (1): Khai báo count = 0
	X = []  # Mảng để lưu các xâu con từ seq-f.txt

	# Bước (2): Đọc file seq-f.txt và lưu các xâu con vào mảng X
	with open(seq_file_path, 'r') as seq_file:
		for line in seq_file:
			parts = line.strip().split()
			if parts[0].startswith('f'):
				X.append(' '.join(parts[1:3]))  # Lưu 2 con số sau chữ 'f'

	# Bước (3): Duyệt từng phần tử của X và so sánh với nội dung của input1.txt
	with open(input_file_path, 'r') as input_file:
		input_lines = input_file.readlines()

	for element in X:
		for line in input_lines:
			#real = element % H
			new_element = "a " + element + " " #"(" + real + ")"
			if new_element in line:
				inc = int(line.strip().split()[-1]);
				count += (inc-1) # Tăng count
				print(new_element," ", (count - inc), " + ", inc, " = ", count)

	# Bước (4): In ra count
	print(f"Count sau khi lọc là: {count}")

# Thay 'seq-f.txt' và 'input1.txt' bằng đường dẫn tới file của bạn
removeZeroLines('seq-f.txt')
filter_lines('filtered.txt', 'TSG.txt', 23)
