import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { Child, Task } from '../data/mockData';
import TaskItem from './TaskItem';
import ProgressCircle from './ProgressCircle';

interface ChildColumnProps {
  child: Child;
  tasks: Task[];
  onTaskComplete: (taskId: string) => void;
}

const ChildColumn: React.FC<ChildColumnProps> = ({ child, tasks, onTaskComplete }) => {
  const completedTasks = tasks.filter(task => task.completed).length;
  const totalTasks = tasks.length;
  const progress = totalTasks > 0 ? completedTasks / totalTasks : 0;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.childName}>{child.name}</Text>
        <ProgressCircle progress={progress} size={50} strokeWidth={5} />
      </View>
      <FlatList
        data={tasks}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <TaskItem task={item} onTaskComplete={onTaskComplete} />}
        contentContainerStyle={styles.taskList}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF', // White
    borderRadius: 10,
    padding: 15,
    marginHorizontal: 10,
    width: 300, // Fixed width for Kanban column
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ADD8E6', // Light Blue
  },
  childName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#00BFFF', // Deep Sky Blue
  },
  taskList: {
    paddingVertical: 5,
  },
});

export default ChildColumn;
