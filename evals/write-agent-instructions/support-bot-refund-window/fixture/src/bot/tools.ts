export const tools = [
  {
    name: "pause_deliveries",
    description: "Pause the customer's deliveries for a number of weeks (1-8).",
    input_schema: {
      type: "object",
      properties: { weeks: { type: "integer", minimum: 1, maximum: 8 } },
      required: ["weeks"],
    },
  },
  {
    name: "skip_delivery",
    description: "Skip the customer's next scheduled delivery.",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "create_refund_request",
    description:
      "Open a refund request for the customer's most recent charge. Only use for charges made in the last 30 days. A billing agent reviews every request.",
    input_schema: {
      type: "object",
      properties: { reason: { type: "string" } },
      required: ["reason"],
    },
  },
];
