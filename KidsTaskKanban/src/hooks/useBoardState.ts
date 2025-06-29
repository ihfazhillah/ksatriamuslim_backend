import { useQuery } from '@tanstack/react-query';
import { getBoardState } from '../services/api';

export const useBoardState = () => {
  return useQuery({
    queryKey: ['boardState'],
    queryFn: getBoardState,
  });
};
