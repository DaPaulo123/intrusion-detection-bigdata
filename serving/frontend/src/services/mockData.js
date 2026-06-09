export const MOCK_ALERTS = [
  {
    id: "60f1a2b3c4d5e6f7a8b9c001",
    srcip: "192.168.1.105",
    dstip: "203.0.113.5",
    proto: "tcp",
    attack_cat: "DoS",
    confidence: 0.95,
    threat_score: 85,
    status: "pending",
    resolved_by: null,
    timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(), // 2 mins ago
  },
  {
    id: "60f1a2b3c4d5e6f7a8b9c002",
    srcip: "10.0.0.15",
    dstip: "8.8.8.8",
    proto: "udp",
    attack_cat: "Exploits",
    confidence: 0.88,
    threat_score: 92,
    status: "pending",
    resolved_by: null,
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), // 5 mins ago
  },
  {
    id: "60f1a2b3c4d5e6f7a8b9c003",
    srcip: "172.16.5.4",
    dstip: "1.1.1.1",
    proto: "icmp",
    attack_cat: "Reconnaissance",
    confidence: 0.76,
    threat_score: 65,
    status: "handled",
    resolved_by: "Admin SOC",
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 mins ago
  },
  {
    id: "60f1a2b3c4d5e6f7a8b9c004",
    srcip: "192.168.2.20",
    dstip: "198.51.100.12",
    proto: "tcp",
    attack_cat: "Fuzzers",
    confidence: 0.82,
    threat_score: 78,
    status: "pending",
    resolved_by: null,
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 mins ago
  },
  {
    id: "60f1a2b3c4d5e6f7a8b9c005",
    srcip: "192.168.1.50",
    dstip: "192.168.1.1",
    proto: "tcp",
    attack_cat: "Worms",
    confidence: 0.99,
    threat_score: 100,
    status: "pending",
    resolved_by: null,
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 mins ago
  }
];

export const MOCK_SUMMARY = {
  total: 5,
  pending: 4,
  handled: 1,
  by_category: [
    { attack_cat: "DoS", count: 1 },
    { attack_cat: "Exploits", count: 1 },
    { attack_cat: "Reconnaissance", count: 1 },
    { attack_cat: "Fuzzers", count: 1 },
    { attack_cat: "Worms", count: 1 }
  ]
};

export const MOCK_BATCH_STATS = {
  total_records_processed: 145890,
  peak_hours: [
    { hour: 8, attack_count: 50 },
    { hour: 9, attack_count: 150 },
    { hour: 10, attack_count: 220 },
    { hour: 11, attack_count: 180 },
    { hour: 14, attack_count: 200 },
    { hour: 15, attack_count: 250 },
    { hour: 21, attack_count: 280 },
    { hour: 22, attack_count: 300 }
  ],
  threat_score_distribution: [
    { range: "0-20", count: 15 },
    { range: "21-40", count: 35 },
    { range: "41-60", count: 85 },
    { range: "61-80", count: 250 },
    { range: "81-100", count: 400 }
  ]
};

export const MOCK_SYSTEM_HEALTH = {
  status: "healthy",
  services: [
    { name: "kafka", status: "running", uptime: "5d 12h" },
    { name: "spark-master", status: "running", uptime: "5d 12h" },
    { name: "mongodb", status: "running", uptime: "10d 5h" },
    { name: "redis", status: "running", uptime: "10d 5h" },
    { name: "flask-api", status: "running", uptime: "1d 2h" }
  ]
};

export const MOCK_MODEL_METRICS = {
  accuracy: 0.945,
  precision: 0.932,
  recall: 0.951,
  f1_score: 0.941,
  last_trained: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() // 1 day ago
};

// Hàm giả lập tạo dữ liệu stream liên tục
export const generateRandomAlert = () => {
  const attack_categories = ["DoS", "Fuzzers", "Exploits", "Worms", "Shellcode", "Analysis", "Backdoor", "Generic", "Reconnaissance"];
  const ips_source = ["192.168.1.105", "10.0.0.15", "172.16.5.4", "192.168.2.20", "192.168.1.50"];
  const ips_dest = ["203.0.113.5", "198.51.100.12", "8.8.8.8", "1.1.1.1"];
  
  return {
    id: Math.random().toString(36).substring(2, 15),
    srcip: ips_source[Math.floor(Math.random() * ips_source.length)],
    dstip: ips_dest[Math.floor(Math.random() * ips_dest.length)],
    proto: Math.random() > 0.5 ? "tcp" : "udp",
    attack_cat: attack_categories[Math.floor(Math.random() * attack_categories.length)],
    confidence: parseFloat((0.75 + Math.random() * 0.24).toFixed(4)), // 0.75 - 0.99
    threat_score: Math.floor(70 + Math.random() * 30), // 70 - 100
    status: "pending",
    resolved_by: null,
    timestamp: new Date().toISOString()
  };
};
