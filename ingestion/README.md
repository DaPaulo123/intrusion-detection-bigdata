# Data ingestion layer

Notes: Will likely to change in the future. Make sure to remove then setup again when happens.

## Data ingestion producer and consumer

Current status: In progress

### Structure

- Java implementation is supported in `kafka_intrusion_java` project
<!-- because Java has better support for this kind of thing -->
- Python implementation is supported in 2 files `kafka_consumer.py` and `kafka_producer.py`
- Shared config files in `settings.toml` file (please open and change in there to appropriate path of your files)

### Issues

- Too barebone, will restructure in the future
- Some escape characters appear when running Python producer to Java consumer.
- Maybe use settings file instead of `.env`

## Insights

- Java has weird ways to do such simple thing (construct new Record from existing Record)
