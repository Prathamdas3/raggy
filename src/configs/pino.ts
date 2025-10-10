import pino from "pino";

// Optional custom levels
const customLevels = {
	logs: 35,
};

// Base logger configuration
const baseLoggerConfig = {
	customLevels,
	transport: {
		target: "pino-pretty",
		options: {
			colorize: true,
		},
	},
	timestamp: pino.stdTimeFunctions.isoTime,
	enabled: true,
	formatters: {
		bindings: (bindings: any) => ({
			pid: bindings.pid,
			host: bindings.hostname,
		}),
		level: (label: string) => ({ level: label.toUpperCase() }),
	},
};

// Factory function to create logger with context
export function createLogger(
	context: {
		ip?: string;
		requestId?: string;
		userId?: string | null;
		workerId?: string;
		queueName?: string;
		jobId?: string;
	} = {},
) {
	return pino({
		...baseLoggerConfig,
		base: {
			...context,
		},
	});
}
