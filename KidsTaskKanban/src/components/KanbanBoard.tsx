import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Button } from 'react-native';
import ChildColumn from './ChildColumn';
import KeepAwake from 'react-native-keep-awake';
import ConfettiCannon from 'react-native-confetti-cannon';
import { useBoardState } from '../hooks/useBoardState';
import { useUpdateTask } from '../hooks/useUpdateTask';
import { playCringSound } from '../utils/soundEffects'; // Correctly placed import

interface KanbanBoardProps {
  onLogout: () => void;
}

const KanbanBoard: React.FC<KanbanBoardProps> = ({ onLogout }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [showConfetti, setShowConfetti] = useState(false);

  const { data: boardState, isLoading, isError } = useBoardState();
  const updateTaskMutation = useUpdateTask();

  useEffect(() => {
    KeepAwake.activate();
    const interval = setInterval(() => setCurrentDate(new Date()), 60 * 1000);
    return () => {
      KeepAwake.deactivate();
      clearInterval(interval);
    };
  }, []);

  const handleTaskCompletion = (taskId: string) => {
    updateTaskMutation.mutate({ id: taskId, completed: true });
    setShowConfetti(true);
    playCringSound(); // Play the sound effect
    setTimeout(() => setShowConfetti(false), 2000);
  };

  const formattedDate = currentDate.toLocaleDateString('id-ID', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  if (isLoading) {
    return <ActivityIndicator size="large" style={styles.centered} />;
  }

  if (isError) {
    return <Text style={styles.centered}>Error fetching data</Text>;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.dateText}>{formattedDate}</Text>
        <Button title="Logout" onPress={onLogout} />
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.scrollViewContent}>
        {boardState?.children.map(child => (
          <ChildColumn
            key={child.id}
            child={child}
            tasks={child.tasks}
            onTaskComplete={handleTaskCompletion}
          />
        ))}
      </ScrollView>
      {showConfetti && (
        <ConfettiCannon
          count={200}
          origin={{ x: -10, y: 0 }}
          autoStart={true}
          fadeOut={true}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F0F8FF', // Alice Blue
    paddingTop: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  dateText: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#FF69B4', // Hot Pink
  },
  scrollViewContent: {
    paddingHorizontal: 10,
    alignItems: 'flex-start',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default KanbanBoard;
