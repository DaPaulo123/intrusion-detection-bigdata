import tomllib
from kafka import KafkaConsumer

with open("config.toml", mode="rb") as f:
    config = tomllib.load(f)

consumer = KafkaConsumer(
    bootstrap_servers=config["bootstrap_servers"],
    value_deserializer=lambda x: x.decode("utf-8"),
    # No idea here yet
    # group_id="Idk",
)

consumer.subscribe(["network_traffic"])

try:
    while True:
        items = consumer.poll(timeout_ms=100)
        # TODO: uhh do something?
        print(items)
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
