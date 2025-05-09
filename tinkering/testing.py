
import random
import itertools

def g_func_create(n):
    bitstrings = [''.join(bits) for bits in itertools.product('01', repeat=n)]
    result = {b: random.choice('01') for b in bitstrings}
    return result


n = 5
l = 6

secrets = {

}

A_oracle = {

}

g_func = g_func_create(n)

def g_secret_populate(n, l, secrets, g_func, A_oracle, node_id=()):
    level = len(node_id)
    if level == l:
        secret = ''.join(random.choice('01') for _ in range(n))
        secrets[node_id] = secret
        A_oracle[node_id] = g_func[secret]
        return g_func[secret]


    curr_secret = ""
    for i in range(n):
        x = "0" * n
        x = x[:i] + "1" + x[i+1:]
        g_secret = g_secret_populate(n, l, secrets, g_func, A_oracle, node_id + (x,))
        curr_secret += g_secret

    secrets[node_id] = curr_secret

    return g_func[curr_secret]

g_secret_populate(n, l, secrets, g_func, A_oracle)

#print(secrets)


    
call_count = 0

def c_rfs(root_id):

    global call_count
    call_count += 1

    level = len(root_id)

    if level == l:
        return A_oracle[root_id]
    
    secret = ""
    for i in range(n):
        x = "0" * n
        x = x[:i] + "1" + x[i+1:]
        secret += c_rfs(root_id + (x,))

    g_secret = g_func[secret]
    if level == 0:
        print("Root Secret: " + secret)

    return g_secret


start_root_id = ()
root_secret = c_rfs(start_root_id)

print(root_secret)
print(call_count)







import matplotlib.pyplot as plt

ns = [2, 3, 4, 5, 6, 7]
ls = [2, 3, 4, 5, 6, 7]
actual_counts = []
theoretical_counts = []
labels = []

for n in ns:
    for l in ls:
        secrets = {

        }
        A_oracle = {

        }
        g_func = g_func_create(n)
        g_secret_populate(n, l, secrets, g_func, A_oracle)

        call_count = 0
        c_rfs(())
        actual_counts.append(call_count)
        theoretical_counts.append(n ** l)
        labels.append(f"{n}^{l}")



# Step 1: Collect data points into tuples
data = list(zip(actual_counts, theoretical_counts, labels))

# Step 2: Sort by actual count (first item in each tuple)
data.sort(key=lambda tup: tup[0])

# Step 3: Unpack the sorted data back into separate lists
actual_counts_sorted = [d[0] for d in data]
theoretical_counts_sorted = [d[1] for d in data]
labels_sorted = [d[2] for d in data]


# Plotting
plt.plot(actual_counts, label="Real Runtime", marker='o')
plt.plot(theoretical_counts, label="Theoretical Runtime (n^l)", linestyle='--', marker='x')
plt.xticks(ticks=range(len(labels)), labels=labels, rotation=45)
plt.xlabel("Input (n, l)")
plt.ylabel("Runtime")
plt.title("Real vs. Theoretical Runtime")
plt.legend()
# plt.tight_layout()
plt.show()