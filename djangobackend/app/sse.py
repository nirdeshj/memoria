from queue import Queue

# Keep track of all connected clients per patient
clients = {}

def connect(patient_id):
    print("from connect")
    """Add a new client queue for this patient"""
    q = Queue()
    clients.setdefault(patient_id, []).append(q)
    return q

def disconnect(patient_id, q):
    """Remove client queue when disconnected"""
    clients[patient_id].remove(q)

def push(patient_id, data):
    """Push data to all connected clients of this patient"""
    for q in clients.get(patient_id, []):
        q.put(data)
