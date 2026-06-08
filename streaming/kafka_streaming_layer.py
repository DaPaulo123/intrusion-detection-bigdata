import json
from kafka import KafkaConsumer


def main():
    print(">>> Starting Streaming Layer (Real-time Kafka Consumer)...")
    print(
        ">>> Configuring connection to Kafka (localhost:9092), topic = 'test-topic'..."
    )

    # Init Kafka Consumer
    consumer = KafkaConsumer(
        "network_traffic",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        # How to use this thing
        # group_id="streaming-layer-demo",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=10000,  # Dừng lại nếu 10s không có data
    )

    print(
        "\n---------------------------------------------------------------------------------"
    )
    print(">>> Ready to receive Streaming Layer (Real-time Data) from Kafka:")
    print(
        "---------------------------------------------------------------------------------"
    )
    print(
        f"| {'ID':<5} | {'METRIC EVENT':<25} | {'SEVERITY':<10} | {'SOURCE_IP':<15} | {'TIMESTAMP':<15} |"
    )
    print(
        "---------------------------------------------------------------------------------"
    )

    count = 0
    # Consumer pulls in loop per event
    consumed = sum(consumer.poll(timeout_ms=100, max_records=5).values(), [])
    for message in consumed:
        data = message.value
        # What are these fields
        id_str = str(data.get("id", ""))
        event_str = str(data.get("event", ""))
        sev_str = str(data.get("severity", ""))
        ip_str = str(data.get("source_ip", ""))
        time_str = str(data.get("timestamp", ""))[:10]

        print(
            f"| {id_str:<5} | {event_str:<25} | {sev_str:<10} | {ip_str:<15} | {time_str:<15} |"
        )

        count += 1
        if count >= 5:
            break

    print(
        "---------------------------------------------------------------------------------"
    )
    print(">>> Finished reading Streaming Layer data! Safely disconnected.")


if __name__ == "__main__":
    main()
