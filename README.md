# HFT.PROJECT — Cybersecurity in High-Frequency Finance

**EduQual Level 3 — Topic 32** | **Student:** Anshra Subhaniee

An experimental high-frequency trading project exploring algorithmic trading models, data-driven decision-making, and real-time cybersecurity monitoring.

---

## Project Structure

```
hft_demo/
├── scripts/
│   ├── hft_producer.py          ← Kafka market data producer (Python)
│   └── kill_switch.py           ← Anomaly detection engine + kill switch (Python)
├── kafka/
│   ├── server.properties        ← Kafka broker TLS/SASL config
│   └── setup_kafka_hft.sh       ← Topic & ACL setup script
├── logstash/
│   └── hft-pipeline.conf        ← Logstash pipeline (Kafka → Elasticsearch)
├── kibana/
│   ├── latency_alert_watcher.json  ← Kibana Watcher alert rule
│   └── index_template.json         ← Elasticsearch index mapping
└── README.md                    ← This file
```

---

## Quick Demo (No Kafka needed — for presentation)

Run the kill switch simulator directly. It reproduces the exact log output
from the demo screenshots without needing a live Kafka cluster:

```bash
# Install dependency
pip install kafka-python

# Run simulation (press Ctrl+C to stop)
python3 scripts/kill_switch.py
```

You will see the Logstash-style log output, anomaly detection checks,
and the kill switch activation message — matching the screenshots exactly.

---

## Full Stack Setup (Kali Linux / Ubuntu)

### 1. Install Java (Kafka requirement)
```bash
sudo apt update
sudo apt install -y default-jdk
java -version
```

### 2. Install Kafka
```bash
wget https://downloads.apache.org/kafka/3.7.0/kafka_2.13-3.7.0.tgz
tar -xzf kafka_2.13-3.7.0.tgz
sudo mv kafka_2.13-3.7.0 /opt/kafka
```

### 3. Generate TLS Certificates
```bash
# Create CA
keytool -genkeypair -alias ca -keyalg RSA -keysize 4096 \
  -dname "CN=HFT-CA" -keystore /etc/kafka/ssl/ca.jks \
  -storepass ca-pass -validity 365

# Create broker keystore
keytool -genkeypair -alias kafka-broker -keyalg RSA -keysize 2048 \
  -dname "CN=kafka-broker" \
  -keystore /etc/kafka/ssl/kafka.server.keystore.jks \
  -storepass kafka-keystore-pass -validity 365
```

### 4. Start Kafka with Security Config
```bash
# Copy our config
sudo cp kafka/server.properties /opt/kafka/config/

# Start ZooKeeper
/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties &

# Start Kafka broker
/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties &
```

### 5. Create Topics & ACLs
```bash
bash kafka/setup_kafka_hft.sh
```

### 6. Install ELK Stack (Docker — easiest)
```bash
# Pull and start Elasticsearch + Kibana
docker run -d --name elasticsearch \
  -e "discovery.type=single-node" \
  -e "ELASTIC_PASSWORD=elastic-pass" \
  -p 9200:9200 \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0

docker run -d --name kibana \
  -e "ELASTICSEARCH_HOSTS=http://elasticsearch:9200" \
  -p 5601:5601 \
  --link elasticsearch \
  docker.elastic.co/kibana/kibana:8.13.0
```

### 7. Apply Elasticsearch Index Template
```bash
curl -X PUT "localhost:9200/_index_template/hft-template" \
  -H "Content-Type: application/json" \
  -d @kibana/index_template.json \
  -u elastic:elastic-pass
```

### 8. Install Logstash Pipeline
```bash
sudo cp logstash/hft-pipeline.conf /etc/logstash/conf.d/
sudo systemctl restart logstash
```

### 9. Install Kibana Watcher Alert
```bash
curl -X PUT "localhost:5601/api/watcher/watch/hft-latency-alert" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d @kibana/latency_alert_watcher.json \
  -u elastic:elastic-pass
```

### 10. Run the Demo
```bash
# Terminal 1 — Start producer (sends market ticks to Kafka)
python3 scripts/hft_producer.py

# Terminal 2 — Start anomaly engine (watches for attacks, triggers kill switch)
python3 scripts/kill_switch.py
```

---

## What Each File Does

| File | Purpose | Used in slide |
|------|---------|--------------|
| `hft_producer.py` | Simulates HFT trading feed; injects latency anomaly at packet 50 | Slide 8 — Demo |
| `kill_switch.py` | Consumes ticks, detects anomalies, triggers kill switch | Slide 8 — Demo |
| `server.properties` | Kafka TLS 1.3 + SASL/SCRAM broker config | Slide 7 — Architecture |
| `setup_kafka_hft.sh` | Creates topic (12 partitions, replication=3), sets ACLs | Slide 8 — Config |
| `hft-pipeline.conf` | Logstash: parses + enriches + flags anomalies + sends to ES | Slide 5 — Data Flow |
| `latency_alert_watcher.json` | Kibana Watcher: auto-triggers kill switch on latency >50ms | Slide 8 — Kibana |
| `index_template.json` | Elasticsearch schema for all HFT market data | Slide 5 — ELK |

---

## Security Architecture Summary

```
Market Exchange
      │
      │ TLS 1.3
      ▼
Kafka Cluster (SASL/SCRAM-SHA-256, ACLs, Replication=3)
      │
      ├──► Logstash (parses, flags anomalies, enriches)
      │         │
      │         ▼
      │    Elasticsearch (indexed, encrypted at rest, AES-256)
      │         │
      │         ▼
      │      Kibana (real-time dashboard, Watcher alerts)
      │         │
      │    [Latency > 50ms?]
      │         │ YES
      ▼         ▼
Anomaly     Kill Switch ──► Exchange Gateway DISCONNECTED
Detection       │
Engine          └──► Audit log written (7-year retention, Reg SCI)
```

---

## Compliance References

- **Regulation SCI** — 7-year log retention, audit trails, incident response
- **MiFID II Article 17** — Kill switch mandatory for algorithmic trading
- **CIA Triad** — Confidentiality (TLS/AES-256), Integrity (SCRAM auth), Availability (replication=3)
