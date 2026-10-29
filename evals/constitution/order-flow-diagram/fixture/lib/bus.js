// Publish and subscribe to events; RabbitMQ topic exchange "shop" in production.
import amqp from "amqplib";

let channel;
async function open() {
  if (!channel) {
    const conn = await amqp.connect(process.env.AMQP_URL);
    channel = await conn.createChannel();
    await channel.assertExchange("shop", "topic", { durable: true });
  }
  return channel;
}

export async function publish(event, payload) {
  (await open()).publish("shop", event, Buffer.from(JSON.stringify(payload)), { persistent: true });
}

export async function subscribe(event, queue, handler) {
  const ch = await open();
  await ch.assertQueue(queue, { durable: true });
  await ch.bindQueue(queue, "shop", event);
  ch.consume(queue, async (msg) => {
    await handler(JSON.parse(msg.content.toString()));
    ch.ack(msg);
  });
}
