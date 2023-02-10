from collections import namedtuple
import math
import time
import heapq

h_user = namedtuple("user", ["id", "init_speed", "data_size", "factor", "weight"])


# toycase: "../toy_example/toy_testcase.csv"

def solve(input_file):
    start_time = time.time()

    speed_to_data_map = {}
    cols = {}

    total_data = 0
    res = {}  # total_speed, n_cols, data_loss, user, weighted_speed
    sum_init_speed = 0

    def f(speed):
        return math.floor(speed + 1e-6)

    def comp(user):
        if user.init_speed == 0 or user.factor == 0:
            return 0
        return -user.data_size / (user.init_speed * user.factor)

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
            res[user.id] = [0, 0, user.data_size, user, 0]
            total_data += user.data_size
            users.append(user)
            sum_init_speed += user.init_speed * user.weight
        users.sort(key=lambda u: comp(u))

    # algo

    def filter(us):
        import itertools
        def score(us):
            sum_c = sum([u.factor * 0.01 for u in us])
            data_sent = [speed_to_data_map[
                             f(max(0, u.init_speed * (1 - u.factor * 0.01 * (sum_c - u.factor * 0.01))))] / u.init_speed
                         for u in us]
            return sum(data_sent)

        saved = us
        mx_score = -1
        for i in range(1, len(us) + 1):
            for subset in itertools.combinations(us, i):
                sc = score(list(subset))
                if mx_score < sc:
                    mx_score = sc
                    saved = list(subset)
        return saved

    for i in range(n):
        users.sort(key=lambda u: comp(u))
        m_users = users[:m]
        chosen = filter(m_users)

        # update
        sum_c = sum([u.factor * 0.01 for u in chosen])

        for u in chosen:
            speed = max(0, u.init_speed * (1 - u.factor * 0.01 * (sum_c - u.factor * 0.01)))
            data_transmitted = speed_to_data_map[f(speed)] if speed_to_data_map[
                                                                  f(speed)] < u.data_size else u.data_size
            res[u.id][0] += speed
            res[u.id][2] = max(res[u.id][2] - data_transmitted, 0)
            res[u.id][4] += speed * u.weight
            res[u.id][1] += 1

            new_data_size = max(u.data_size - data_transmitted, 0)
            users.remove(u)
            if new_data_size > 0:
                users.append(h_user(u.id, u.init_speed, new_data_size, u.factor, u.weight))
        cols[i] = sorted([u.id for u in chosen])
    penalty_term = sum([r[2] for r in res.values()]) / sum([r[3].data_size for r in res.values()])
    objective_func = sum([0 if r[1] == 0 else r[4] / r[1] for r in res.values()]) / sum_init_speed

    score = objective_func - alpha * penalty_term

    print(score, "!" if penalty_term == 0 else penalty_term)

    # output
    # total_speed, n_cols, data_loss, user, weighted_speed
    dt = int((time.time() - start_time) * 1000)
    with open('output/%s' % input_file, 'w') as file:
        for i in range(m):
            row = ",".join(["U%i" % cols[j][i] if len(cols[j]) > i else "-" for j in range(n)])
            file.write(row + "\n")
        row = ",".join(str(r[2]) for r in res.values()) + "," + str(penalty_term)
        file.write(row + "\n")
        row = ",".join(str(0 if r[1] == 0 else r[0] / r[1]) for r in res.values()) + "," + str(objective_func)
        file.write(row + "\n")
        file.write(str(score) + "\n")
        # for testing purposes set dt = 0
        dt = 0
        file.write(str(dt) + "\n")


def solve2(input_file):
    start_time = time.time()

    speed_to_data_map = {}
    cols = {}

    total_data = 0
    res = {}  # total_speed, n_cols, data_loss, weighted
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
            res[user.id] = [0, 0, user.data_size, user, 0]
            total_data += user.data_size
            heapq.heappush(users, (-user.data_size, user))
            sum_init_speed += user.init_speed * user.weight

    data_percentage_goal = 1 / n

    for i in range(n):
        curr_data_percentage = 0
        saved_users = []
        max_data_percentage = -1
        while curr_data_percentage < data_percentage_goal and len(users) > 0 and len(saved_users) < m:
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
        factor_sum = sum([u.factor * 0.01 for u in saved_users])
        #     print(saved_users)
        for user in saved_users:
            speed = user.init_speed * (1 - user.factor * 0.01 * (factor_sum - user.factor * 0.01))
            if speed > 0:
                data_transmitted = speed_to_data_map[f(speed)] if speed_to_data_map[
                                                                      f(speed)] < user.data_size else user.data_size
                total_data -= data_transmitted

                res[user.id][0] += speed
                res[user.id][2] = max(res[user.id][2] - data_transmitted, 0)
                res[user.id][4] += speed * user.weight

                new_data_size = max(user.data_size - data_transmitted, 0)
                if new_data_size > 0:
                    heapq.heappush(users,
                                   (-new_data_size,
                                    h_user(user.id, user.init_speed, new_data_size, user.factor, user.weight)))
            res[user.id][1] += 1
        cols[i] = sorted([u.id for u in saved_users])
        data_percentage_goal = 1 if i == (n - 1) else 1 / (n - i - 1)

    penalty_term = sum([r[2] for r in res.values()]) / sum([r[3].data_size for r in res.values()])
    objective_func = sum([0 if r[1] == 0 else r[4] / r[1] for r in res.values()]) / sum_init_speed

    score = objective_func - alpha * penalty_term

    for user, r in res.items():
        tot_speed, n_cols, _, _, _ = r
        # print(user, 1 if n_cols == 0 else tot_speed / n_cols)
    # print(objective_func, penalty_term, alpha, score)
    print(score)

    dt = int((time.time() - start_time) * 1000)
    with open('output/%s' % input_file, 'w') as file:
        for i in range(m):
            row = ",".join(["U%i" % cols[j][i] if len(cols[j]) > i else "-" for j in range(n)])
            file.write(row + "\n")
        row = ",".join(str(r[2]) for r in res.values()) + "," + str(penalty_term)
        file.write(row + "\n")
        row = ",".join(str(0 if r[1] == 0 else r[0] / r[1]) for r in res.values()) + "," + str(objective_func)
        file.write(row + "\n")
        file.write(str(score) + "\n")
        # for testing purposes set dt = 0
        dt = 0
        file.write(str(dt) + "\n")


start_time = time.time()
# solve("toy_example.csv")
stop_time = time.time()
# print(stop_time - start_time)

for i in range(1, 4):
    # print("test case %i" % i)
    start_time = time.time()
    solve("%i.csv" % i)
    stop_time = time.time()
    # print(stop_time - start_time)

for i in range(4, 11):
    # print("test case %i" % i)
    start_time = time.time()
    solve2("%i.csv" % i)
    stop_time = time.time()
    # print(stop_time - start_time)
