"""
Bản 2408071018: đã lưu danh sách các đỉnh mốc của khu vực hành lang.
tôi có 1 file txt với nội dung các dòng như sau: a ID1 ID2 L U C ID3. 
Dòng đó mang nghĩa là ID1 và ID2 nối với nhau với trọng số là C. 
Trong đó ID3 có thể không xuất hiện tại một số dòng. Hãy cho tôi mã nguồn Python 
đọc các dòng của file đó, rồi tìm ra 2 đường đi ngắn nhất giữa điểm IDx và IDy 
biết rằng:
(i) IDx và IDy đều có chung giá trị ID3; 
(ii) IDx và IDy đều xuất hiện ở sau chữ a. 
Khi tìm được 2 đường đi giữa 2 đỉnh IDx và IDy thì in các đỉnh trong 
2 đường đi đó ra 1 dòng.
"""
import networkx as nx
import pdb
from enum import Enum

class TYPE_OF_CHECKING(Enum):
    UP = "↑"
    DOWN = "↓"
    LEFT = "<-"
    RIGHT = "->"


def validate_moving_left(move_left_list):
    for tuple in move_left_list:
        most_left = tuple[0]
        most_right = tuple[1]
        #pdb.set_trace()
        num_of_edges = 1 if len(tuple) == 2 else tuple[2]
        for i in range(most_left + 1, most_right + 1):
            paths = find_shortest_paths(G, str(i), str(i-1))
            if(len(paths[0]) != num_of_edges + 1):
                print('\tShortest path 1:', ' -> '.join(paths[0]))
            assert (len(paths) == 1) and len(paths[0]) == (num_of_edges + 1), \
                f'đường đi từ {i} đến {i-1} thì mong đợi {num_of_edges} trong khi thực tế len(paths[0]) = {len(paths[0])}'

def validate_moving_right(move_right_list):
    for tuple in move_right_list:
        most_left = tuple[0]
        most_right = tuple[1]
        #pdb.set_trace()
        num_of_edges = 1 if len(tuple) == 2 else tuple[2]
        for i in range(most_left, most_right):
            paths = find_shortest_paths(G, str(i), str(i+1))
            if(len(paths[0]) != num_of_edges + 1):
                print('\tShortest path 1:', ' -> '.join(paths[0]))
            assert (len(paths) == 1) and len(paths[0]) == (num_of_edges + 1), \
                f'đường đi từ {i} đến {i+1} thì mong đợi {num_of_edges} trong khi thực tế len(paths[0]) = {len(paths[0])}'


def validate_moving_vertically(move_up_or_down_list):
    #pdb.set_trace()
    for tuple in move_up_or_down_list:
        start = tuple[0]
        end = tuple[1]
        #pdb.set_trace()
        steps = (1 if start < end else -1) if len(tuple) == 2 else tuple[2]
        steps = (-1)*abs(steps) if start > end else abs(steps)
        num_of_edges = 1 if len(tuple) <= 3 else tuple[3]
        for i in range(start, end - steps + 1, steps):
            paths = find_shortest_paths(G, str(i), str(i + steps))
            if(len(paths[0]) != num_of_edges + 1):
                print('\tShortest path 1:', ' -> '.join(paths[0]))
            assert (len(paths) == 1) and len(paths[0]) == (num_of_edges + 1), \
                f'đường đi từ {i} đến {i + steps} thì mong đợi {num_of_edges} trong khi thực tế len(paths[0]) = {len(paths[0])}'

def validate_pairs(G, pair_of_moving_vertically):
    next_lines = [item.value for item in pair_of_moving_vertically[1]]
    max_length = max(len(str(item)) for item in pair_of_moving_vertically[0])

    length_of_single_part = 40 #len(next_lines) // 6
    for i in range(0, len(next_lines), length_of_single_part):
    # In ra các phần tử của list1
        for item in pair_of_moving_vertically[0][i : i + length_of_single_part]:
            print(f"{item:<{max_length}}", end=" ")

        print()  # In ra dòng mới


        # In ra các phần tử của list2
        for item in next_lines[i : i + length_of_single_part]:
            print(f"{item:<{max_length}}", end=" ")

        print()

        for item in pair_of_moving_vertically[2][i : i + length_of_single_part]:
            print(f"{item:<{max_length}}", end=" ")
        print()
        print('-------------------------------------------------------------------------', end='')
        print('-------------------------------------------------------------------------')

    for j in range(i, i + length_of_single_part):#len(pair_of_moving_vertically[0])):
        if(j < len(pair_of_moving_vertically[0])):
            validate_pair_nodes([pair_of_moving_vertically[0][j], pair_of_moving_vertically[2][j]],\
            pair_of_moving_vertically[1][j])
        else:
            #print(f'As j = {j} > {len(pair_of_moving_vertically[1])} => out of range exception')
            pass
    
    print()
    print('-------------------------------------------------------------------------')

def validate_pair_nodes(pairs, type = TYPE_OF_CHECKING.UP, num_of_edges = 1):
    paths = []
    if(pairs[0] == 887 or pairs[1] == 887):
        pdb.set_trace()
    source = pairs[0] if (type == TYPE_OF_CHECKING.DOWN or type == TYPE_OF_CHECKING.RIGHT) else pairs[1]
    target = pairs[1] if (type == TYPE_OF_CHECKING.DOWN or type == TYPE_OF_CHECKING.RIGHT) else pairs[0]
    paths = find_shortest_paths(G, str(source), str(target))
    if(len(paths[0]) != num_of_edges + 1):
        print('\tShortest path 1:', ' -> '.join(paths[0]))
    assert (len(paths) == 1) and len(paths[0]) == (num_of_edges + 1), \
        f'đường đi từ {source} đến {target} thì mong đợi {num_of_edges} trong khi thực tế len(paths[0]) = {len(paths[0])}'
"""def validate_moving_right(move_right_list):
    for tuple in move_right_list:
        most_left = tuple[0]
        most_right = tuple[1]
        #pdb.set_trace()
        num_of_edges = 1 if len(tuple) == 2 else tuple[2]
        for i in range(most_left, most_right):
            paths = find_shortest_paths(G, str(i), str(i+1))
            if(len(paths[0]) != num_of_edges + 1):
                print('\tShortest path 1:', ' -> '.join(paths[0]))
            assert (len(paths) == 1) and len(paths[0]) == (num_of_edges + 1), \
                f'đường đi từ {i} đến {i+1} thì mong đợi {num_of_edges} trong khi thực tế len(paths[0]) = {len(paths[0])}'"""
                
def read_graph_from_file(file_name):
    map_id3_id1 = {}
    G = nx.DiGraph()
    count = 0
    checkMissingArcs = bool(input("Bạn có muốn kiểm tra các arc bị thiếu sót không? (True/False. Enter để nhập True)"))
    checkMissingArcs = bool(checkMissingArcs) if checkMissingArcs else True
    enableDebugging = bool(input("Bạn có muốn debug không? (Enter để disable Debugging)"))
    enableDebugging = bool(enableDebugging) if enableDebugging else False
    with open(file_name, 'r') as file:
        for line in file:
            if(enableDebugging):
                pdb.set_trace()
            count = count + 1
            #print(f'Line #{count}')
            parts = line.split()
            if len(parts) >= 7:
                a, ID1, ID2, L, U, C, ID3, _ = parts
                G.add_edge(ID1, ID2, weight=int(C), ID3=ID3)
                if(not checkMissingArcs):
                    G.add_edge(ID2, ID1, weight=int(C), ID3=ID3)#add để thành đồ thị vô hướng
                id1 = parts[1]
                id3 = parts[6]
                if id3 in map_id3_id1:
                    map_id3_id1[id3].append(id1)
                else:
                    map_id3_id1[id3] = [id1]
            else:
                a, ID1, ID2, L, U, C = parts
                G.add_edge(ID1, ID2, weight=int(C))
                if(not checkMissingArcs):
                    G.add_edge(ID2, ID1, weight=int(C))#add để thành đồ thị vô hướng
    return G, map_id3_id1

def find_shortest_paths(G, IDx, IDy):
    paths = []
    try:
        paths = list(nx.all_shortest_paths(G, source=IDx, target=IDy, weight='weight'))
    except nx.NetworkXNoPath:
        print(f"Không thể tìm thấy đường đi từ {IDx} đến {IDy}")
    #paths = list(nx.all_shortest_paths(G, source=IDx, target=IDy, weight='weight'))
    return paths

G, lobbies = read_graph_from_file('3x3Wards.txt')

for key, value in lobbies.items():
    #print(key, value)
    # Replace 'IDx' and 'IDy' with the actual values
    IDx = value[0]
    IDy = value[1]
    paths = find_shortest_paths(G, IDx, IDy)
    # Print the two shortest paths
    print(f'Vùng {key}: ')
    print('\tShortest path 1:', ' -> '.join(paths[0]))
    paths = find_shortest_paths(G, IDy, IDx)
    print('\tShortest path 2:', ' -> '.join(paths[0]))
    print("=============================================")
    
move_left_list = [[1, 38, 1], #most left, most right, num of edges
                  [306, 317, 1], [318, 329], [330, 341],
                  [610, 621], [622, 633], [634, 645],
                  [914, 925], [926, 937], [938, 949]]

validate_moving_left(move_left_list)

move_right_list = [ [39, 76], #most left, most right, num of edges
                  [344, 355, 1], [356, 367, 1], [368, 379],
                  [648, 659], [660, 671], [672, 683],
                  [951, 988]]

validate_moving_right(move_right_list)

move_up_and_down_list = [[914, 648, 38], [610, 344, 38], [306, 40, 38],
                         [926, 660, 38], [622, 356, 38], [318, 52, 38], 
                         [938, 672, 38], [634, 368, 38], [330, 64, 38], 
                         [988, 38, 38],
                         [51, 317, 38], [355, 621, 38], [659, 925, 38],
                         [63, 339, 38], [367, 633, 38], [671, 937, 38],
                         [75, 351, 38], [379, 645, 38], [683, 949, 38],
                         [1, 951, 38] ]
validate_moving_vertically(move_up_and_down_list)

pair_of_moving_vertically = [[ ],
                     [ ],
                     [ ]]
for i in range(2, 38):
    pair_of_moving_vertically[0].append(i)
for i in range(306, 342):
    pair_of_moving_vertically[0].append(i)
for i in range(610, 646):
    pair_of_moving_vertically[0].append(i)
for i in range(914, 950):
    pair_of_moving_vertically[0].append(i)
up_and_down_checking = len(pair_of_moving_vertically[0])
for i in range(77, 951, 38):
    pair_of_moving_vertically[0].append(i)
for i in range(89, 963, 38):
    pair_of_moving_vertically[0].append(i)    
for i in range(101, 975, 38):
    pair_of_moving_vertically[0].append(i)
for i in range(113, 987, 38):
    pair_of_moving_vertically[0].append(i)

left_and_right_checking = len(pair_of_moving_vertically[0])
        
for i in range(0, up_and_down_checking):
    pair_of_moving_vertically[1].append(TYPE_OF_CHECKING.UP if i % 2 == 1 else TYPE_OF_CHECKING.DOWN)

delta = left_and_right_checking - up_and_down_checking
for j in range(0, 2):
    for i in range(up_and_down_checking + j*delta, up_and_down_checking + (j+1)*delta + 1):
        pair_of_moving_vertically[1].append(TYPE_OF_CHECKING.LEFT if (i - up_and_down_checking - j*delta) \
            % 2 == 1 else TYPE_OF_CHECKING.RIGHT)
    
for i in range(40, 76):
    pair_of_moving_vertically[2].append(i)
for i in range(344, 380):
    pair_of_moving_vertically[2].append(i)
for i in range(648, 684):
    pair_of_moving_vertically[2].append(i)    
for i in range(952, 988):
    pair_of_moving_vertically[2].append(i)    
#print(pair_of_moving_vertically[0])
for i in range(78, 952, 38):
    pair_of_moving_vertically[2].append(i)
for i in range(90, 964, 38):
    pair_of_moving_vertically[2].append(i)
for i in range(102, 976, 38):
    pair_of_moving_vertically[2].append(i)
for i in range(114, 988, 38):
    pair_of_moving_vertically[2].append(i)
validate_pairs(G, pair_of_moving_vertically)






















print("\n==========================END==========================")
