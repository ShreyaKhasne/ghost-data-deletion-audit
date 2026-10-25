from collections import deque, defaultdict
import sys

def solve():
    try:
        # Read all standard input safely
        input_data = sys.stdin.read().splitlines()
        if not input_data:
            print(-1)
            return

        # Clean and filter out empty lines while preserving line order
        lines = [line.strip() for line in input_data if line.strip() != '']
        if not lines:
            print(-1)
            return

        try:
            n = int(lines[0])
        except (ValueError, IndexError):
            print(-1)
            return

        adj = defaultdict(list)
        nodes = set()
        
        idx = 1
        # Parse tree relationships
        while idx <= n and idx < len(lines):
            line = lines[idx]
            idx += 1
            
            if line.lower() == 'break':
                continue
                
            parts = line.split()
            if len(parts) < 2:
                continue
                
            try:
                parent = int(parts[0])
                nodes.add(parent)
                for c_str in parts[1:]:
                    child = int(c_str)
                    nodes.add(child)
                    # Downward connection (parent -> child): weight 0
                    adj[parent].append((child, 0))
                    # Upward connection (child -> parent / tree switch): weight 1
                    adj[child].append((parent, 1))
            except ValueError:
                continue

        # Parse start and destination nodes
        if idx < len(lines):
            start_dest = lines[idx].split()
            if len(start_dest) >= 2:
                try:
                    start = int(start_dest[0])
                    destination = int(start_dest[1])
                except ValueError:
                    print(-1)
                    return
            else:
                print(-1)
                return
        else:
            print(-1)
            return

        nodes.add(start)
        nodes.add(destination)

        # 0-1 BFS Shortest Path Algorithm
        dist = {node: float('inf') for node in nodes}
        dist[start] = 0
        deque_q = deque([(0, start)]) # (cost, node)

        while deque_q:
            cost, u = deque_q.popleft()

            if u == destination:
                print(cost)
                return

            if cost > dist[u]:
                continue

            for v, weight in adj[u]:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    if weight == 0:
                        deque_q.appendleft((dist[v], v))
                    else:
                        deque_q.append((dist[v], v))

        # Output minimum cost or -1 if unreachable
        result = dist.get(destination, -1)
        if result == float('inf'):
            print(-1)
        else:
            print(result)

    except Exception:
        print(-1)

if __name__ == '__main__':
    solve()
