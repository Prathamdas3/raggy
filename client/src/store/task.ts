import { create } from "zustand";

export const useTasksIdStore = create<{
	taskId: string | undefined;
	setTaskId: (id: string | undefined) => void;
}>((set) => ({
	taskId: undefined,
	setTaskId: (taskId: string | undefined) => set(() => ({ taskId: taskId })),
}));
