package org.example;

import java.io.IOException;
import java.lang.Thread;
import static java.lang.IO.println;

public class Main {
    static void main() throws IOException {
        NetworkTrafficProducer.main();
        NetworkTrafficConsumer.main();
    }
}
