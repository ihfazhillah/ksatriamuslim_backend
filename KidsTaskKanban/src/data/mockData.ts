export interface Child {
  id: string;
  name: string;
}

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  childId: string;
  imageUrl: string;
}

export const children: Child[] = [
  { id: 'child1', name: 'Budi' },
  { id: 'child2', name: 'Siti' },
  { id: 'child3', name: 'Ahmad' },
];

export const tasks: Task[] = [
  { id: 'task1', title: 'Merapikan Mainan', completed: false, childId: 'child1', imageUrl: 'https://via.placeholder.com/150/FF0000/FFFFFF?text=Mainan' },
  { id: 'task2', title: 'Membaca Buku', completed: true, childId: 'child1', imageUrl: 'https://via.placeholder.com/150/00FF00/FFFFFF?text=Buku' },
  { id: 'task3', title: 'Membantu Ibu', completed: false, childId: 'child2', imageUrl: 'https://via.placeholder.com/150/0000FF/FFFFFF?text=Ibu' },
  { id: 'task4', title: 'Menyiram Tanaman', completed: false, childId: 'child2', imageUrl: 'https://via.placeholder.com/150/FFFF00/000000?text=Tanaman' },
  { id: 'task5', title: 'Belajar Mengaji', completed: false, childId: 'child3', imageUrl: 'https://via.placeholder.com/150/FF00FF/FFFFFF?text=Mengaji' },
  { id: 'task6', title: 'Makan Sayur', completed: true, childId: 'child3', imageUrl: 'https://via.placeholder.com/150/00FFFF/000000?text=Sayur' },
];
