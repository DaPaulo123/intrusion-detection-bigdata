package org.example;

import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.time.Duration;
import java.util.List;
import java.util.Properties;

import static java.lang.IO.println;

final class NetworkTrafficConsumer {
    final static Settings SETTINGS = Addons.get_config();

    static void main() {
        final Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, SETTINGS.kafka().bootstrap_servers());
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "Idk");

        try (final Consumer<String, String> consumer = new KafkaConsumer<>(props)) {
            consumer.subscribe(List.of("network_traffic"));
            // Gson json_parser = new Gson();
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
                for (ConsumerRecord<String, String> s: records) {
                    // key = json_parser.fromJson(s);
                    println(s.value());
                }
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
