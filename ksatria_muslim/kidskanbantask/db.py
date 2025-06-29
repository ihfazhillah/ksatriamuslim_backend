
# In-memory database for the Kids Kanban Task app.
# This data mirrors the mock data in the mobile application.

# Using a dictionary for tasks to allow for faster lookups by ID.
TASKS = {
    'task1': {'id': 'task1', 'title': 'Merapikan Mainan', 'completed': False, 'childId': 'child1', 'imageUrl': 'https://via.placeholder.com/150/FF0000/FFFFFF?text=Mainan'},
    'task2': {'id': 'task2', 'title': 'Membaca Buku', 'completed': True, 'childId': 'child1', 'imageUrl': 'https://via.placeholder.com/150/00FF00/FFFFFF?text=Buku'},
    'task3': {'id': 'task3', 'title': 'Membantu Ibu', 'completed': False, 'childId': 'child2', 'imageUrl': 'https://via.placeholder.com/150/0000FF/FFFFFF?text=Ibu'},
    'task4': {'id': 'task4', 'title': 'Menyiram Tanaman', 'completed': False, 'childId': 'child2', 'imageUrl': 'https://via.placeholder.com/150/FFFF00/000000?text=Tanaman'},
    'task5': {'id': 'task5', 'title': 'Belajar Mengaji', 'completed': False, 'childId': 'child3', 'imageUrl': 'https://via.placeholder.com/150/FF00FF/FFFFFF?text=Mengaji'},
    'task6': {'id': 'task6', 'title': 'Makan Sayur', 'completed': True, 'childId': 'child3', 'imageUrl': 'https://via.placeholder.com/150/00FFFF/000000?text=Sayur'},
}

CHILDREN = [
    {'id': 'child1', 'name': 'Budi'},
    {'id': 'child2', 'name': 'Siti'},
    {'id': 'child3', 'name': 'Ahmad'},
]

def get_tasks_for_child(child_id):
    """Returns a list of tasks for a given child."""
    return [task for task in TASKS.values() if task['childId'] == child_id]

def get_board_state_data():
    """Constructs the full board state from the in-memory data."""
    board_state = []
    for child in CHILDREN:
        child_data = child.copy()
        child_data['tasks'] = get_tasks_for_child(child['id'])
        board_state.append(child_data)
    return {"children": board_state}

def update_task_status(task_id, completed):
    """Updates the status of a task and returns the updated task."""
    if task_id in TASKS:
        TASKS[task_id]['completed'] = completed
        return TASKS[task_id]
    return None
