import pino from 'pino';

const options = pino.transport({
    target: 'pino-pretty',
    options: { destination: 1,colorize:true }
})

export default pino(options);
