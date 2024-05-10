import os
import re
import json
from collections import deque
from scipy.sparse import lil_matrix
#from ortools.linear_solver import pywraplp
import pdb
"""
Mô tả yêu cầu của code:
https://docs.google.com/document/d/13S_Ycg-aB4GjEm8xe6tAoUHzhS-Z1iFnM4jX_bWFddo/edit?usp=sharing
"""

class GraphProcessor:
    def __init__(self):
        self.Adj = []  # Adjacency matrix
        self.M = 0
        self.H = 0
        self.d = 0
        self.alpha = 1
        self.beta = 1
        self.gamma = 1
        self.ID = 0
        self.earliness = 0
        self.tardiness = 0
        self.spaceEdges = []
        self.tsEdges = set()
    def process_input_file(self, filepath):
        self.spaceEdges = []
        try:
            with open(filepath, 'r') as file:
                self.M = 0
                for line in file:
                    parts = line.strip().split()
                    if parts[0] == 'a' and len(parts) == 6:
                        id1, id2 = int(parts[1]), int(parts[2])
                        self.spaceEdges.append(parts)
                        self.M = max(self.M, id1, id2)
            print("Doc file hoan tat, M =", self.M)
        except FileNotFoundError:
            print("File khong ton tai!")
            return

    def generate_hm_matrix(self):
        self.matrix = [[j + 1 + self.M * i for j in range(self.M)] for i in range(self.H)]
        print("Hoan tat khoi tao matrix HM!")
        # for row in self.matrix:
        #     print(' '.join(map(str, row)))

    def generate_adj_matrix(self):
        size = (self.H + 1) * self.M + 1
        self.Adj = lil_matrix((size, size), dtype=int)

        for edge in self.spaceEdges:
            if len(edge) >= 6 and edge[3] == '0' and edge[4] == '1':
                u, v, c = int(edge[1]), int(edge[2]), int(edge[5])
                for i in range(self.H + 1):
                    source_idx = i * self.M + u
                    target_idx = (i + c) * self.M + v
                    print(f"i = {i} {source_idx} {target_idx} = 1")

                    if source_idx < size and target_idx < size:
                        self.Adj[source_idx, target_idx] = 1

        for i in range(size):
            j = i + self.M * self.d
            if j < size and (i % self.M == j % self.M):
                self.Adj[i, j] = 1

        print("Hoan tat khoi tao Adjacency matrix!")

        rows, cols = self.Adj.nonzero()
        with open('adj_matrix.txt', 'w') as file:
            for i, j in zip(rows, cols):
                file.write(f"({i}, {j})\n")
        print("Cac cap chi so (i,j) khac 0 cua Adjacency matrix duoc luu tai adj_matrix.txt.")

    def create_tsg_file(self):
        output_lines = []
        Q = deque(range((self.H + 1)* self.M + 1))

        edges_with_cost = { (int(edge[1]), int(edge[2])): int(edge[5]) for edge in self.spaceEdges if edge[3] == '0' and edge[4] == '1' }
        self.tsEdges = set()

        while Q:
            ID = Q.popleft()
            for j in self.Adj.rows[ID]:  # Direct access to non-zero columns for row ID in lil_matrix
                u, v = ID % self.M, j % self.M
                u = u if u != 0 or ID == 0 else self.M
                #if(v == 0):
                #if (ID == 1 and j == 11):
                    #pdb.set_trace()
                v = v if v != 0 or ID == 0 else self.M
                #start_time = (ID // self.M) if (ID // self.M) != 0 else ID
                #if (start_time + edges_with_cost.get((u, v), -1) == j // self.M) and ((u, v) in edges_with_cost):
                if ((ID // self.M) + edges_with_cost.get((u, v), -1) == (j // self.M) - (v//self.M)) and ((u, v) in edges_with_cost):
                    c = edges_with_cost[(u, v)]
                    output_lines.append(f"a {ID} {j} 0 1 {c}")
                    self.tsEdges.add((ID, j, 0, 1, c))
                elif ID + self.M * self.d == j and ID % self.M == j % self.M:
                    output_lines.append(f"a {ID} {j} 0 1 {self.d}")
                    self.tsEdges.add((ID, j, 0, 1, self.d))

        with open('TSG.txt', 'w') as file:
            for line in output_lines:
                file.write(line + "\n")
        print("Da tao TSG.txt.")


    def query_edges_by_source_id(self):
        source_id = int(input("Nhap vao ID nguon: "))

        edges = []
        try:
            with open('TSG.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if parts[0] == 'a' and int(parts[1]) == source_id:
                        edges.append(line.strip())
        except FileNotFoundError:
            print("File TSG.txt khong ton tai!")
            return

        if edges:
            print(f"Cac canh co ID nguon la {source_id}:")
            for edge in edges:
                print(edge)
        else:
            print(f"Khong tim thay canh nao co ID nguon la {source_id}.")

    def check_file_conditions(self):
        try:
            seen_edges = set()
            with open('TSG.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if parts[0] != 'a':
                        continue
                    ID1, ID2 = int(parts[1]), int(parts[2])

                    # Condition 1: ID1 should not equal ID2
                    if ID1 == ID2:
                        print("False")
                        return

                    # Condition 2: If ID1 before ID2, then ID2 should not come before ID1
                    if (ID1, ID2) in seen_edges or (ID2, ID1) in seen_edges:
                        print("False")
                        return
                    else:
                        seen_edges.add((ID1, ID2))

                    # Condition 3: ID2/self.M should be greater than ID1/self.M
                    if not (ID2 // self.M > ID1 // self.M):
                        print("False")
                        return

            print("True")
        except FileNotFoundError:
            print("File TSG.txt khong ton tai!")

    def update_file(self):
        ID1 = int(input("Nhap ID1: "))
        ID2 = int(input("Nhap ID2: "))
        C12 = int(input("Nhap trong so C12: "))

        i1, i2 = ID1 // self.M, ID2 // self.M
        if i2 - i1 != C12:
            print('Status: i2 - i1 != C12')
            ID2 = ID1 + self.M * C12

        existing_edges = set()
        try:
            with open('TSG.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    try:
		     # Chỉ xử lý các dòng có ít nhất 3 phần tử và bắt đầu bằng 'a'
                        if parts[0] == 'a' and len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
                            existing_edges.add((int(parts[1]), int(parts[2])))
                    except ValueError:
                    # Bỏ qua các dòng không thể chuyển đổi sang số nguyên
                        continue
                    except IndexError:
                    # Bỏ qua các dòng không có đủ phần tử
                        continue
                    #existing_edges.add((int(parts[1]), int(parts[2])))
        except FileNotFoundError:
            print("File TSG.txt khong ton tai!")
            return

        if (ID1, ID2) not in existing_edges:
            Q = deque([ID2])
            visited = {ID2}
            new_edges = [(ID1, ID2, C12)]

            while Q:
                ID = Q.popleft()
                for j in self.Adj.rows[ID]:
                    if j not in visited:
                        u, v = ID % self.M, j % self.M
                        c = self.d if ID + self.M * self.d == j and ID % self.M == j % self.M else C12
                        if (ID // self.M) + c == j // self.M:
                            new_edges.append((ID, j, c))
                            Q.append(j)
                            visited.add(j)

            with open('TSG.txt', 'a') as file:
                for ID, j, c in new_edges:
                    file.write(f"a {ID} {j} 0 1 {c}\n")
            print("Da cap nhat file TSG.txt.")

    def add_restrictions(self):
        alpha = input("Nhập vào alpha: ")
        beta = input("Nhập vào beta: ")
        gamma = input("Nhập vào gamma: ")
        self.alpha = int(alpha) if alpha else 1
        self.beta = int(beta) if beta else 1
        self.gamma = int(gamma) if gamma else 1
        restriction_count = input("Hãy nhập số lượng các restriction: ")
        self.restriction_count = int(restriction_count) if restriction_count else 1
        startBan, endBan = map(int, input("Khung thời gian cấm (nhập hai số phân tách bằng khoảng trắng a b): ").split())
        self.startBan = startBan
        self.endBan = endBan
        self.restrictions = []

        for i in range(self.restriction_count):
            print(f"Restriction {i + 1}:")
            #restriction = list(map(int, input("\tKhu vực cấm: ").split()))
            u, v = map(int, input("\tKhu vực cấm (nhập hai số phân tách bằng khoảng trắng a b): ").split())

            self.restrictions.append((u, v))
        self.Ur = int(input("Số lượng hạn chế: "))

    def process_restrictions(self):
        S = set()
        R = []
        newA = set()
        startBan = self.startBan
        endBan = self.endBan #16, 30  # Giả sử giá trị cố định cho ví dụ này
        
        edges_with_cost = { (int(edge[1]), int(edge[2])): int(edge[5]) for edge in self.spaceEdges if edge[3] == '0' and edge[4] == '1' }
        # Xác định các điểm bị cấm
        for restriction in self.restrictions:
            for time in range(startBan, endBan + 1):
                edge = []
                #point = restriction[0] #, restriction[1]]:
                #S.add(point)
                timeSpacePoint_0 = time*self.M + restriction[0]
                Cost = edges_with_cost.get((restriction[0], restriction[1]), -1)
                timeSpacePoint_1 = (time + Cost)*self.M + restriction[1]
                edge.append(timeSpacePoint_0)
                edge.append(timeSpacePoint_1)
                R.append(edge)
                self.Adj[edge[0], edge[1]] = 0

        # Xử lý các cung cấm
        #for edge in self.spaceEdges:
            #ID1, ID2 = int(edge[1]), int(edge[2])
            #t1, u, v, t2 = ID1 // self.M, ID1 % self.M, ID2 % self.M, ID2 // self.M
            #if (u in S and v in S):
                #if ((t1 <= endBan and endBan <= t2) or (t1 <= startBan and startBan <= t2) or (t1 <= startBan and endBan <= t2)):
                    #R.add((ID1, ID2))
        
        self.tsEdges = [e for e in self.tsEdges if [e[0], e[1]] not in R]
        with open('TSG.txt', 'w') as file:
            for edge in self.tsEdges:
                file.write(f"a {edge[0]} {edge[1]} {edge[2]} {edge[3]} {edge[4]}\n")
        #self.create_tsg_file()
        
        # Tạo các cung mới dựa trên các cung cấm
        if R:
            Max = self.getMaxID() + 1
            #Max = max(ID2 for _, ID2 in R) + 1
            aS, aT, aSubT = Max, Max + 1, Max + 2
            Max += 3
            e1 = (aS, aT, 0, self.H, int(self.gamma/self.alpha))
            e2 = (aS, aSubT, 0, self.H, int(self.gamma/self.alpha))
            e3 = (aSubT, aT, 0, self.H, 0)
            newA.update({e1, e2, e3})
            for e in R:
                e4 = (e[0], aS, 0, 1, 0)
                e5 = (aT, e[1], 0, 1, int(self.gamma))
                newA.update({e4, e5})

        self.tsEdges.extend(e for e in newA if e not in self.tsEdges)
        #pdb.set_trace()
        # Ghi các cung mới vào file TSG.txt
        with open('TSG.txt', 'a') as file:
            for edge in newA:
                c = int(edge[4])
                file.write(f"a {edge[0]} {edge[1]} {edge[2]} {edge[3]} {c}\n")
                #print(f"{c} a {edge[0]} {edge[1]} {edge[2]} {edge[3]} {c}")
        #with open('TSG.txt', 'w') as file:
        #    for edge in self.spaceEdges:
        #        file.write(f"a {edge[0]} {edge[1]} {edge[2]} {edge[3]} {edge[4]}\n")
        print("Đã cập nhật các cung mới vào file TSG.txt.")

    def getMaxID(self):
      max_val = 0
      try:
        with open('TSG.txt', 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts[0] == 'a':
                    max_val = max(max_val, int(parts[2]))
      except FileNotFoundError:
        pass
      return max_val
      
    def update_tsg_with_constraints(self):
      # Tìm giá trị lớn nhất trong TSG.txt
      max_val = self.getMaxID()
      #print(f"max_val = {max_val}")
      max_val += 1
      R = set()
      new_edges = set()
      # Duyệt các dòng của file TSG.txt
      try:
        with open('TSG.txt', 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts[0] == 'a' and len(parts) == 6:
                    ID2 =int(parts[2])
                    for i in range(1, self.H + 1):
                        j = i * self.M + self.ID
                        if j == ID2:
                            C = int(int(self.beta) * max(self.earliness - i, 0, i - self.tardiness) / int(self.alpha))
                            new_edges.add((j, max_val, 0, 1, C))
                            break

      except FileNotFoundError:
        pass

      #pdb.set_trace()
      Count = 0
      self.tsEdges.update(e for e in new_edges if e not in self.tsEdges)
      # Ghi các cung mới vào file TSG.txt
      with open('TSG.txt', 'a') as file:
        for edge in new_edges:
            Count += 1
            file.write(f"a {edge[0]} {edge[1]} {edge[2]} {edge[3]} {edge[4]}\n")
      print(f"Đã cập nhật {Count} cung mới vào file TSG.txt.")




    #Dưới đây là chương trình Python theo yêu cầu của bạn:

    def append_new_edges_to_tsg(self):
        # Yêu cầu nhập liệu từ người dùng
        ID = int(input("Nhập ID: "))
        earliness = int(input("Nhập earliness: "))
        tardiness = int(input("Nhập tardiness: "))
        alpha = input("Nhập alpha (nhấn Enter để lấy giá trị mặc định là 1): ")
        beta = input("Nhập beta (nhấn Enter để lấy giá trị mặc định là 1): ")

        # Nếu người dùng không nhập gì, sử dụng giá trị mặc định là 1
        self.alpha = int(alpha) if alpha else 1
        self.beta = int(beta) if beta else 1

        # Đọc file TSG.txt và tìm giá trị Max
        max_id = 0
        with open('TSG.txt', 'r') as file:
            for line in file:
                if line.startswith('a'):
                    _, id1, id2, _, _, _ = line.split()
                    max_id = max(max_id, int(id1), int(id2))

        max_id += 1

        # Tạo các cung mới và lưu vào R
        R = []
        with open('TSG.txt', 'r') as file:
            for line in file:
                if line.startswith('a'):
                    _, id1, id2, _, _, _ = line.split()
                    for i in range(1, self.H+1):  # Giả sử H là biến đã được định nghĩa trước
                        j = i * self.M + ID  # Giả sử M là biến đã được định nghĩa trước
                        if j == int(id2):
                            C = self.beta * max(earliness - i, 0, i - tardiness) / self.alpha
                            C = int(C)
                            s = f'a {j} {max_id} 0 1 {C}'
                            R.append(s)
                            #max_id += 1  # Cập nhật Max sau mỗi lần thêm cung mới

        # Ghi nối đuôi các cung mới vào TSG.txt
        with open('TSG.txt', 'a') as file:
            for s in R:
                file.write(s + '\n')



    def update_tsg_with_T(self):
        T = int(input("Nhập giá trị T: "))
        # Đảm bảo T là một giá trị nguyên dương
        if not isinstance(T, int) or T <= 0:
            print("Giá trị của T phải là một số nguyên dương.")
            return

        new_lines = []

        # Đọc và kiểm tra từng dòng trong file TSG.txt cũ
        try:
            with open('TSG.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 6 and parts[0] == 'a':
                        ID1, ID2 = int(parts[1]), int(parts[2])

                        # Kiểm tra điều kiện ID1 và ID2
                        if ID1 >= T * self.M and ID2 >= T * self.M:
                            new_lines.append(line)
        except FileNotFoundError:
            print("Không tìm thấy file TSG.txt.")
            return

        # Ghi các dòng thỏa điều kiện vào file TSG.txt mới
        with open('TSG_new.txt', 'w') as file:
            for line in new_lines:
                file.write(line)
        print("Đã tạo file TSG_new.txt mới với các dòng thỏa điều kiện.")



    def add_problem_info(self):
      json_filepath = input("Nhap ten file dau vao: ")
      try:

          with open(json_filepath, 'r') as json_file:
              data = json.load(json_file)
              AGV_number = data["AGV"]["number"]
              itinerary_start = data["itinerary"]["start"]
              itinerary_end = data["itinerary"]["end"]

              # Tính toán max_id và số lượng cung (A) từ file TSG.txt
              max_id = 0
              A = 0
              with open('TSG.txt', 'r') as tsg_file:
                  for line in tsg_file:
                      if line.startswith('a'):
                          A += 1
                          _, id1, id2, _, _, _ = line.split()
                          max_id = max(max_id, int(id1), int(id2))

              # Tạo dòng thông tin về bài toán cần giải
              problem_info_line = f"p min {max_id} {A}\n"

              # Tạo dòng thông tin về lịch trình
              itinerary_lines = []
              for item in itinerary_start:
                  time_values = item["time"]
                  for time_value in time_values:
                      point_id = item["point"] + self.M * time_value
                      itinerary_lines.append(f"n {point_id} 1\n")
              for item in itinerary_end:
                  point_id = item["point"][0]
                  time_values = item["time"]
                  itinerary_lines.append(f"n {point_id} -1\n")
                  self.ID = point_id
                  self.earliness = time_values[0]
                  self.tardiness = time_values[1]
                  self.alpha = 1
                  self.beta =  1
                  self.update_tsg_with_constraints()


              # Ghi dòng thông tin về bài toán và lịch trình vào đầu file TSG.txt
              with open('TSG.txt', 'r+') as tsg_file:
                  content = tsg_file.read()
                  tsg_file.seek(0, 0)
                  tsg_file.write(problem_info_line + ''.join(itinerary_lines) + content)

              print("Đã thêm thông tin về bài toán vào file TSG.txt.")
      except FileNotFoundError:
          print("Không tìm thấy file JSON hoặc TSG.txt.")




    def remove_duplicate_lines(self):
            try:
                # Read lines from TSG.txt
                with open('TSG.txt', 'r') as file:
                    lines = file.readlines()

                seen_lines = set()
                unique_lines = []
                for line in lines:
                    if re.match(r'^a\s+\d+\s+\d+', line):
                        if line.strip() not in seen_lines:
                            unique_lines.append(line)
                            seen_lines.add(line.strip())
                    else:
                        unique_lines.append(line)

                # Write unique lines back to TSG.txt
                with open('TSG.txt', 'w') as file:
                    file.writelines(unique_lines)

                print("Removed duplicate lines from TSG.txt.")
            except FileNotFoundError:
                print("File TSG.txt not found.")



    def remove_redundant_edges(self):
            # Tập R: ID của nút nguồn
            R = set()
            # Tập E: ID của nút đích
            E = set()

            try:
                # Đọc dòng p min Max A
                with open('TSG.txt', 'r') as file:
                    lines = file.readlines()
                    if lines:
                        first_line = lines[0].strip()
                        if first_line.startswith('p min'):
                            # Tìm tất cả các dòng bắt đầu bằng 'n' và lưu vào tập S
                            S = set()
                            for line in lines[1:]:
                                if line.startswith('n'):
                                    _, node_id, _ = line.split()
                                    S.add(int(node_id))

                            # Lưu ID của nút nguồn vào tập R
                            for line in lines[1:]:
                                if line.startswith('a'):
                                    _, source_id, _, _, _, _ = line.split()
                                    source_id = int(source_id)
                                    if source_id not in S:
                                        R.add(source_id)

                            # Lưu ID của nút đích vào tập E
                            for line in lines[1:]:
                                if line.startswith('a'):
                                    _, _, target_id, _, _, _ = line.split()
                                    E.add(int(target_id))

                        else:
                            print("File không đúng định dạng.")
                            return
                    else:
                        print("File rỗng.")
                        return
            except FileNotFoundError:
                print("File không tồn tại.")
                return

            try:
                # Đọc từng dòng của file và loại bỏ các cạnh dư thừa
                with open('TSG.txt', 'r') as file:
                    lines = file.readlines()

                    # Dòng mới sau khi loại bỏ các cạnh dư thừa
                    new_lines = []

                    for line in lines:
                        if line.startswith('a'):
                            _, source_id, target_id, _, _, _ = line.split()
                            source_id = int(source_id)
                            target_id = int(target_id)

                            # Nếu source_id không thuộc S và không thuộc E, loại bỏ cạnh
                            if source_id not in S and source_id not in E:
                                continue

                        # Thêm dòng vào danh sách mới
                        new_lines.append(line)

                # Ghi các dòng mới vào file TSG.txt
                with open('TSG.txt', 'w') as file:
                    file.writelines(new_lines)

                print("Đã loại bỏ các cạnh dư thừa từ file TSG.txt.")
            except FileNotFoundError:
                print("File không tồn tại.")

    def remove_descendant_edges(self):
      source_id = int(input("Nhập ID của điểm gốc: "))
      try:
        with open('TSG.txt', 'r') as file:
            lines = file.readlines()
      except FileNotFoundError:
        print("File TSG.txt không tồn tại.")
        return

      # Tạo một danh sách chứa các cung cần giữ lại sau khi gỡ bỏ
      new_lines = []

      # Tạo một hàng đợi để duyệt qua các cung
      queue = deque([source_id])

      # Dùng set để lưu trữ ID của các cung cần loại bỏ
      to_remove = set()

      while queue:
        current_id = queue.popleft()
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 6 and parts[0] == 'a':
                if int(parts[1]) == current_id:
                    destination_id = int(parts[2])
                    to_remove.add(line.strip())
                    queue.append(destination_id)

      # Xóa các cung con cháu xuất phát từ điểm gốc khỏi danh sách cung ban đầu
      for line in lines:
        if line.strip() not in to_remove:
            new_lines.append(line)

      # Ghi lại các cung còn lại vào file TSG.txt
      with open('TSG.txt', 'w') as file:
        file.writelines(new_lines)

      print("Đã gỡ bỏ các cung con cháu xuất phát từ điểm gốc trong đồ thị TSG.")
    def process_tsg(self):
        AGV = set()
        TASKS = set()
        objective_coeffs = {}
        solver = pywraplp.Solver.CreateSolver('SCIP')
        try:
          with open('TSG.txt', 'r') as file:
              for line in file:
                  parts = line.strip().split()
                  if len(parts) == 3 and parts[0] == 'n':
                      node_id, val = int(parts[1]), int(parts[2])
                      if val == 1:
                          AGV.add(node_id)
                      elif val == -1:
                          TASKS.add(node_id)
                  elif len(parts) == 6 and parts[0] == 'a':
                      i, j, c = int(parts[1]), int(parts[2]), int(parts[5])
                      if (i, j) not in objective_coeffs:
                          objective_coeffs[(i, j)] = c

        except FileNotFoundError:
            print("File TSG.txt không tồn tại.")

        objective = solver.Objective()

        # Thêm các biến quyết định vào mục tiêu
        added_keys = set()  # Sử dụng set để lưu trữ các khóa đã được thêm
        for m in AGV:
            for i, j in objective_coeffs.keys():
                key = f'x_{m}_{i}_{j}'
                if key not in added_keys:  # Chỉ tạo biến nếu chưa được tạo trước đó
                    x = solver.BoolVar(key)
                    objective.SetCoefficient(x, objective_coeffs[(i, j)])  # Đặt hệ số cho mỗi biến
                    added_keys.add(key)  # Thêm khóa vào set đã được thêm

        objective.SetMinimization()
        print(added_keys)
        # Thêm ràng buộc x_m_i_j nhận giá trị 0 hoặc 1
        for m in AGV:
            for i, j in objective_coeffs.keys():
                x = solver.LookupVariable(f'x_{m}_{i}_{j}')
                constraint = solver.Constraint(0, 1)
                constraint.SetCoefficient(x, 1)

        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print('Solution:')
            print('Objective value =', solver.Objective().Value())
            for m in AGV:
                for i, j in objective_coeffs.keys():
                    x = solver.LookupVariable(f'x_{m}_{i}_{j}')
                    if x.solution_value() == 1:
                        print(f'x_{m}_{i}_{j} = 1')
        else:
            print('The problem does not have an optimal solution.')




    def main_menu(self):
        while True:
            print("======================================")
            print("Nhan (a) de chon file dau vao")
            print("Nhan (b) de in ra ma tran HM")
            print("Nhan (c) de in ra ma tran lien ke Adj")
            print("Nhan (d) de tao ra file TSG.txt")
            print("Nhan (e) de nhap vao ID nguon")
            print("Nhan (f) de kiem tra file")
            print("Nhan (g) de cap nhat file TSG.txt")
            print("Nhan (h) de yeu cau nhap ID, earliness, tardiness")
            print("Nhan (i) de loc ra cac cung cho do thi")
            print("Nhan (j) de cap nhat cac rang buoc ve su xuat hien cua xe")
            print("Nhan (k) de cap nhat cac dong dau cua TSG")
            print("Nhan (l) de loai bo cac dong du thua")
            print("Nhan (m) de loai bo cac dong bi trung lap")
            print("Nhan (o) de giai tim loi giai minimum cho completion time")

            print("Nhan cac phim ngoai (a-o) de ket thuc")

            choice = input("Nhap lua chon cua ban: ").strip().lower()

            if choice == 'a':
                filepath = input("Nhap ten file dau vao: ")
                self.process_input_file(filepath)
            elif choice == 'b':
                self.H = int(input("Nhap vao gia tri H: "))
                self.generate_hm_matrix()
            elif choice == 'c':
                self.d = int(input("Nhap vao gia tri d: "))
                self.generate_adj_matrix()
            elif choice == 'd':
                self.create_tsg_file()
            elif choice == 'e':
                self.query_edges_by_source_id()
            elif choice == 'f':
                self.check_file_conditions()
            elif choice == 'g':
                self.update_file()
            elif choice == 'h':
                self.ID = int(input("Nhập ID của điểm trong không gian: "))
                self.earliness = int(input("Nhập giá trị earliness: "))
                self.tardiness = int(input("Nhập giá trị tardiness: "))
                alpha = input("Nhập alpha (nhấn Enter để lấy giá trị mặc định là 1): ")
                beta = input("Nhập beta (nhấn Enter để lấy giá trị mặc định là 1): ")
                self.alpha = int(alpha) if alpha else 1
                self.beta = int(beta) if beta else 1
                self.update_tsg_with_constraints()
            elif choice == 'i':
                self.update_tsg_with_T()
            elif choice == 'j':
                self.add_restrictions()
                self.process_restrictions()
            elif choice == 'k':
                self.add_problem_info()
            elif choice == 'm':
                self.remove_duplicate_lines()
            elif choice == 'l':
                self.remove_redundant_edges()
            elif choice == 'n':
                self.remove_descendant_edges()
            elif choice == 'o':
                self.process_tsg()
            else:
                print("Ket thuc chuong trinh.")
                break

if __name__ == "__main__":
    gp = GraphProcessor()
    gp.main_menu()
