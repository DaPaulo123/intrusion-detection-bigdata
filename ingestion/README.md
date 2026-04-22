# Data ingestion layer

## How to setup this part (12 Apr 2026)

Current status: Just created

### Setup

1. Ensure you installed docker-compose or podman-compose
2. TODO: Add configuration in config folder
3. Setup the container

```
podman-compose up -d
```

### Notes

Will likely to change in the future. Make sure to remove then setup again when happens.

## Data ingestion producer

Current status: In progress

### Structure

- Java implementation is supported in `kafka_intrusion_java` project
<!-- because Java has better support for this kind of thing -->
- Python implementation is supported in 2 files `kafka_consumer.py` and `kafka_producer.py`
- Shared config files in `config.toml` file (please open and change in there to appropriate path of your files)

### Issues

- Too barebone, will restructure in the future
- Some escape characters appear when running Python producer to Java consumer.
