import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateTask } from '../services/api';
import { Task } from '../data/mockData';

export const useUpdateTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateTask,
    onMutate: async (updatedTask: Partial<Task>) => {
      await queryClient.cancelQueries({ queryKey: ['boardState'] });

      const previousBoardState = queryClient.getQueryData<any>(['boardState']);

      queryClient.setQueryData(['boardState'], (old: any) => {
        if (!old) return old;

        return {
          ...old,
          children: old.children.map((child: any) => ({
            ...child,
            tasks: child.tasks.map((task: Task) =>
              task.id === updatedTask.id ? { ...task, ...updatedTask } : task
            ),
          })),
        };
      });

      return { previousBoardState };
    },
    onError: (err, variables, context) => {
      if (context?.previousBoardState) {
        queryClient.setQueryData(['boardState'], context.previousBoardState);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['boardState'] });
    },
  });
};
