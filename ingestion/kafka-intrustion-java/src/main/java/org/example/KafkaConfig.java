package org.example;

public record KafkaConfig (
        int retries,
        int acks
){}
