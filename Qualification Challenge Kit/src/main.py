from collections import namedtuple
import heapq
import math
import time

h_user = namedtuple("user", ["id", "init_speed", "data_size", "factor"])


# toycase: "../toy_example/toy_testcase.csv"

def solve(input_file):
    start_time = time.time()

    speed_to_data_map = {}
    cols = {}

    total_data = 0
    res = {}  # total_speed, n_cols, data_loss
    sum_init_speed = 0

    def f(speed):
        return math.floor(speed + 1e-6)

    with open("../speed_to_data_map.csv") as file:
        data = file.read().splitlines()
        for row in data:
            speed, data_size = map(int, row.split(","))
            speed_to_data_map[speed] = data_size
    with open("../test_cases/tc%s" % input_file) as file:
        data = file.read().splitlines()
        m, n = map(int, data[0].split(","))
        n_users = int(data[1])
        alpha = float(data[2])

        users = []
        for u in range(3, 3 + n_users):
            user = h_user(*map(int, data[u].split(",")))
            res[user.id] = [0, 0, user.data_size]
            total_data += user.data_size
            heapq.heappush(users, (-user.data_size, user))
            sum_init_speed += user.init_speed

    data_percentage_goal = 1 / n

    for i in range(n):
        curr_data_percentage = 0
        saved_users = []
        while curr_data_percentage < data_percentage_goal and len(users) > 0:
            curr_data_transmitted = 0
            _, user = heapq.heappop(users)
            factor_sum = sum([u.factor * 0.01 for u in saved_users])
            speed = user.init_speed * (1 - user.factor * 0.01 * (factor_sum - user.factor * 0.01))
            if speed > 0:
                saved_users.append(user)
                factor_sum += user.factor * 0.01
                for user in saved_users:
                    speed = user.init_speed * (1 - user.factor * 0.01 * (factor_sum - user.factor * 0.01))
                    if speed > 0:
                        data_transmitted = speed_to_data_map[f(speed)] if speed_to_data_map[
                                                                              f(speed)] < user.data_size else user.data_size

                        curr_data_transmitted += data_transmitted
            curr_data_percentage = curr_data_transmitted / total_data
        # update
        # factor_sum = sum([u.factor * 0.01 for u in saved_users])
        print(saved_users)
        for user in saved_users:
            speed = user.init_speed * (1 - user.factor * 0.01 * (factor_sum - user.factor * 0.01))
            if speed > 0:
                data_transmitted = speed_to_data_map[f(speed)] if speed_to_data_map[
                                                                      f(speed)] < user.data_size else user.data_size
                total_data -= data_transmitted

                res[user.id][0] += speed
                res[user.id][1] += 1
                res[user.id][2] = max(res[user.id][2] - data_transmitted, 0)

                new_data_size = max(user.data_size - data_transmitted, 0)
                if new_data_size > 0:
                    heapq.heappush(users,
                                   (-new_data_size, h_user(user.id, user.init_speed, new_data_size, user.factor)))
            print(speed)
        cols[i] = sorted([u.id for u in saved_users])
        data_percentage_goal = 1 if i == (n - 1) else 1 / (n - i - 1)

    penalty_term = sum([r[2] for r in res.values()])
    objective_func = sum([0 if r[1] == 0 else r[0] / r[1] for r in res.values()]) / sum_init_speed

    score = objective_func - alpha * penalty_term

    for user, r in res.items():
        tot_speed, n_cols, _ = r
        print(user, 1 if n_cols == 0 else tot_speed / n_cols)
    print(objective_func, penalty_term, alpha, score)
    print(cols)

    dt = int((time.time() - start_time) * 1000)
    print(res)
    with open('output/%s' % input_file, 'w') as file:
        for i in range(m):
            row = ",".join(["U%i" % cols[j][i] if len(cols[j]) > i else "-" for j in range(n)])
            file.write(row + "\n")
        row = ",".join(str(r[2]) for r in res.values()) + "," + str(penalty_term)
        file.write(row + "\n")
        row = ",".join(str(0 if r[1] == 0 else r[0] / r[1]) for r in res.values()) + "," + str(objective_func)
        file.write(row + "\n")
        file.write(str(score) + "\n")
        file.write(str(dt) + "\n")


start_time = time.time()
#solve("toy_testcase.csv")
stop_time = time.time()
print(stop_time - start_time)

for i in range(1, 14):
    print("test case %i" % i)
    start_time = time.time()
    solve("%i.csv" % i)
    stop_time = time.time()
    print(stop_time - start_time)
