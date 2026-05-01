package org.example;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.KafkaException;
import org.apache.kafka.common.errors.AuthorizationException;
import org.apache.kafka.common.errors.OutOfOrderSequenceException;
import org.apache.kafka.common.errors.ProducerFencedException;
import org.apache.kafka.common.serialization.StringSerializer;
import com.google.gson.Gson;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Comparator;
import java.util.List;
import java.util.Properties;

import static java.lang.IO.println;

final class NetworkTrafficProducer extends Thread {
    static final Settings SETTINGS = Addons.get_config();

    static List<String> simulation() throws IOException {
        final Path csv_feature_file = Path.of(SETTINGS.simulation().csv_header_path());
        final CSVFormat csvFormat = CSVFormat.DEFAULT.builder().setHeader().setSkipHeaderRecord(true).get();
        final CSVParser headers_parser = CSVParser.parse(csv_feature_file, StandardCharsets.UTF_8, csvFormat);
        final String[] headers = headers_parser.stream().map(t -> t.get("Name")).toArray(String[]::new);

        final Path csv_data_file = Path.of(SETTINGS.simulation().csv_sim_path());
        final CSVFormat data_format = CSVFormat.DEFAULT.builder().setHeader(headers).get();
        final CSVParser data_simulation = CSVParser.parse(csv_data_file, StandardCharsets.UTF_8, data_format);

        final Gson create_json = new Gson();
        return data_simulation.stream().sorted(Comparator.comparing(p -> p.get("Stime"))).map(p -> create_json.toJson(p.toMap())).toList();
    }

    public static void test() throws IOException {
        List<String> data = simulation();
        for (String s : data) {
            println(s);
        }

    }

    static void main() {
        final Properties props = new Properties();
        // Hardcode here, may put in config file later
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, SETTINGS.kafka().bootstrap_servers());
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        // Oops, all String
        props.put(ProducerConfig.RETRIES_CONFIG, SETTINGS.kafka().retries());

        final Producer<String, String> producer = new KafkaProducer<>(props);
        try {
            List<String> data = simulation();
            for (String s : data) {
                producer.send(new ProducerRecord<>("network_traffic", s, s));
                Thread.sleep(Duration.ofMillis(10));
            }
        } catch (ProducerFencedException | OutOfOrderSequenceException | AuthorizationException _) {
        } catch (KafkaException err) {
            producer.abortTransaction();
        } catch (IOException | InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            producer.flush();
            producer.close();
        }

    }

}
