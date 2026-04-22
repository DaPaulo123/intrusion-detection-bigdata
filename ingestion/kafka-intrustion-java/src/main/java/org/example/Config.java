package org.example;

import java.util.List;

public record Config (
    List<String> bootstrap_servers,
    String csv_sim_path,
    String csv_header_path,
    KafkaConfig kafka_config
) {}

