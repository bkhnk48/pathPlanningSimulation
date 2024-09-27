import os
import csv

class Logger:
    def __init__(self):
        pass
    def count_csv_rows(self, fileName):
        with open(fileName, mode='r', newline='') as file:
            reader = csv.reader(file)
            row_count = sum(1 for row in reader)
        return row_count

    def log(self, fileName, map, totalAGVs, H, d, solution, reachingTarget, halting, objectiveValue, runTime):
        # Kiểm tra xem fileName có đuôi .csv chưa, nếu chưa thì thêm vào
        if not fileName.endswith('.csv'):
            fileName += '.csv'
        initialIndex = 1

        # Kiểm tra xem file đã tồn tại chưa
        file_exists = os.path.isfile(fileName)

        # Mở file ở chế độ append
        with open(fileName, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Nếu file chưa tồn tại, thêm dòng tiêu đề
            if not file_exists:
                writer.writerow(['No', 'Map', 'Total AGVs', 'Horizontal Time', 'Time step', 'Solution', 
                                 'Num of Reaching Target AGVs', 'Num of Halting AGVs', 
                                 'Objective Value', 'Running Time(s)'])
                
            initialIndex = self.count_csv_rows(fileName)

            # Thêm dòng dữ liệu mới
            writer.writerow([initialIndex, map, totalAGVs, H, d, solution, reachingTarget, halting, 
                             objectiveValue, runTime])

# Ví dụ sử dụng
#logger = Logger()
#logger.log('logfile', 'Map1', 10, 5, 'Solution1', 8, 2, 100.0, 12.5)