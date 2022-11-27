#Read Input & Assign Variables
import time
import csv
import math
with open('speed_to_data_map.csv', newline='') as mapping:
    speed_map = tuple(csv.reader(mapping))
    
    speed_data_map = []
    for i in range (0,len(speed_map)):
        speed_data_map = (*speed_data_map, int(speed_map[i][1]))
    
    
def size_index(data,K):
    index_map = []
    for i in range (0,K):
        max_index = data.index(max(data))+1
        index_map.append(max_index)
        data[max_index-1] = -1
    return index_map


def target_factor(M,init_speed,factor,total_data,index_map,users,flag,avg_speed,instance,data_remaining):
    sent_data = 0
    collocated_factor_list = [0]*M
    for i in range (0,users):
        collocated_factor_list[i] = factor[index_map[i]-1]/100
    
    for i in range (0,users):
        collocated_factor = collocated_factor_list[i] * sum((collocated_factor_list[:i]+collocated_factor_list[i+1:]))
        speed = init_speed[index_map[i]-1] * (1-collocated_factor)
        if collocated_factor > 1:
            speed = 0
        speed_floor = math.floor(speed + 10e-6)
        sent_data = sent_data + speed_data_map[speed_floor]
        if flag == 1:
            data_remaining[index_map[i]-1] = data_remaining[index_map[i]-1] - speed_data_map[speed_floor]
            if (data_remaining[index_map[i]-1] < 0):
                data_remaining[index_map[i]-1] = 0
            avg_speed[index_map[i]-1] = ((avg_speed[index_map[i]-1])*instance[index_map[i]-1] + speed)/(instance[index_map[i]-1]+1)
            instance[index_map[i]-1] = instance[index_map[i]-1] + 1

    target_curr = (sent_data/total_data)*100
    return target_curr

def write(tc,M,N,grid,avg_speed,best_speed,data_loss,total_data,alpha,start_time):
    with open(str(tc)+'.csv', 'w', newline='') as file:
        writer = csv.writer(file)
    
        for i in range (0,M):
            write_data = []
            for j in range (0,N):
                if (grid[j][i] == 0):
                    write_data.append("-")
                else:
                    write_data.append("U"+str(grid[j][i]))
            writer.writerow(write_data)
            
        penalty = sum(list(data_loss))/total_data
        data_loss.append(penalty)
        writer.writerow(data_loss)
        
        obj_func = sum(list(avg_speed))/best_speed
        avg_speed.append(obj_func)
        writer.writerow(avg_speed)
        
        score = []
        score.append(obj_func - (alpha*penalty))
        writer.writerow(score)
        
        execution_time = []
        temp = math.floor((time.time() - start_time)*1000)
        execution_time.append(temp)
        writer.writerow(execution_time)
        

def main():
    for tc in range (1,14):
        start_time = time.time()
        with open('tc'+str(tc)+'.csv', newline='') as input:
        #with open('toy_testcase.csv', newline='') as input:
            data = tuple(csv.reader(input))

        M = int(data[0][0])
        N = int(data[0][1])
        K = int(data[1][0])
        alpha = float(data[2][0])

        init_speed = ()
        data_size = ()
        factor = ()

        for i in range (3,3+K):
            init_speed = (*init_speed, int(data[i][1]))
            data_size = (*data_size, int(data[i][2]))
            factor = (*factor, int(data[i][3]))
        total_data = sum(list(data_size))
        best_speed = sum(list(init_speed))
        data_remaining = list(data_size)

        grid = [[0]*M]*N
        avg_speed = [0]*K
        instance = [0]*K
        data_loss = [0]*K
        
        target_ideal = 100/N
        margin_low = 0.99
        margin_high = 2.15
        for i in range (0,N):       #Columns 
            user_index_map = [0]*M
            index_map_temp = [0]*M
            size_index_map = size_index(data_remaining.copy(),K)         #shows the index of largest and the subsequent largest data_size 
            for j in range (0,M):
                flag = 0
                index_map_temp[j] = size_index_map[j]
                target_factor_temp = target_factor(M,init_speed,factor,total_data,index_map_temp,j+1,flag,avg_speed,instance,data_remaining)
                if (margin_low*target_ideal <= target_factor_temp <= margin_high*target_ideal): #or (((sum(list(data_remaining)))/total_data)*100 <= target_ideal):
                    flag = 1
                    user_index_map = index_map_temp.copy()
                    target_factor(M,init_speed,factor,total_data,user_index_map,j+1,flag,avg_speed,instance,data_remaining)
                    grid[i] = user_index_map.copy()
                    break
        data_loss = data_remaining.copy()
        write(tc,M,N,grid,avg_speed,best_speed,data_loss,total_data,alpha,start_time)
        
main()