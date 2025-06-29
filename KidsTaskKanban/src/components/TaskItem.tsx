import React from 'react';
import { View, Text, Image, StyleSheet, Pressable } from 'react-native';
import { Task } from '../data/mockData';

interface TaskItemProps {
  task: Task;
  onTaskComplete: (taskId: string) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onTaskComplete }) => {
  return (
    <Pressable
      onPress={() => onTaskComplete(task.id)}
      disabled={task.completed}
      style={({ pressed }) => [
        styles.container,
        task.completed && styles.completedContainer,
        pressed && !task.completed && styles.pressedContainer,
      ]}
    >
      <Image source={{ uri: task.imageUrl }} style={styles.image} />
      <Text style={[styles.title, task.completed && styles.completedTitle]}>{task.title}</Text>
      {task.completed && (
        <View style={styles.overlay}>
          <Text style={styles.checkMark}>✓</Text>
        </View>
      )}
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFC0CB', // Light Pink
    padding: 10,
    marginVertical: 5,
    borderRadius: 8,
  },
  completedContainer: {
    backgroundColor: '#ADD8E6', // Light Blue
  },
  pressedContainer: {
    backgroundColor: '#FFB6C1', // Lighter Pink
  },
  image: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333', // Dark Gray
  },
  completedTitle: {
    textDecorationLine: 'line-through',
    color: '#666666', // Medium Gray
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 8,
  },
  checkMark: {
    fontSize: 40,
    color: 'white',
    fontWeight: 'bold',
  },
});

export default TaskItem;
