# HFT.PROJECT — Cybersecurity in High-Frequency Finance

**EduQual Level 3 — Topic 32** | **Student:** Anshra Subhaniee
**Diploma in Cloud Cyber Security**

An experimental high-frequency trading project exploring algorithmic trading models, data-driven decision-making, and real-time cybersecurity monitoring. This project demonstrates a secure, compliant HFT architecture using Apache Kafka, the ELK Stack, TLS/mTLS, FPGA gateways, and an automated Kill Switch — fully aligned with Regulation SCI and MiFID II Article 17.

---

## Presentation Overview

| Slide | Topic |
|-------|-------|
| 1 | Title — Cybersecurity in High-Frequency Finance |
| 2 | Presentation Agenda |
| 3 | Basics of HFT & Algorithmic Trading |
| 4 | Cybersecurity Threat Landscape |
| 5 | Technical Monitoring & Anomaly Detection |
| 6 | Secure Communication & Access Control |
| 7 | System & Network Architecture |
| 8 | Implementation & Demonstration |
| 9 | Failure & Recovery Scenarios |
| 10 | Policies, Procedures & Governance |
| 11 | Integrated Security Architecture Diagram |
| 12 | Cloud Architecture — VPC, Security Groups & IAM |
| 13 | Automated Containment & Post-Incident Recovery |
| 14 | Case Study: The 2010 Flash Crash |
| 15 | Technology Justification & Design Decisions |
| 16 | Scalability, Governance & Architecture Depth |
| 17 | Network Architecture — IP Subnets, Firewalls, DMZ & Trust Boundaries |
| 18 | Detailed Security Architecture — Key Storage, Cert Rotation & Audit Logs |
| 19 | Failure & Recovery Deep-Dive + Flash Crash — The Deeper "Why" |
| 20 | Conclusion & Q&A |

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

| File | Purpose | Slide Reference |
|------|---------|-----------------|
| `hft_producer.py` | Simulates HFT trading feed; injects latency anomaly at packet 50 | Slide 8 — Demo |
| `kill_switch.py` | Consumes ticks, detects anomalies, triggers kill switch | Slides 8, 9, 13 — Demo & Recovery |
| `server.properties` | Kafka TLS 1.3 + SASL/SCRAM broker config | Slides 7, 12 — Architecture |
| `setup_kafka_hft.sh` | Creates topic (12 partitions, replication=3), sets ACLs | Slide 8 — Config |
| `hft-pipeline.conf` | Logstash: parses + enriches + flags anomalies + sends to ES | Slides 5, 11 — Data Flow |
| `latency_alert_watcher.json` | Kibana Watcher: auto-triggers kill switch on latency >800µs | Slides 8, 18 — Kibana |
| `index_template.json` | Elasticsearch schema for all HFT market data | Slides 5, 12 — ELK |

---

## HFT & Algorithmic Trading — Key Facts

**HFT Definition:** Trading that uses powerful computers to execute thousands to millions of orders per second at microsecond speeds — faster than a human blink.

**Algorithmic Trading:** Programs that automatically trade based on predefined instructions (price, timing, volume). No human intervention — pure code decisions.

**Why Security Matters:** Any latency injection, data tampering, or unauthorized access can cause cascading failures worth billions in seconds. Security is mission-critical.

| Metric | Value |
|--------|-------|
| Execution speed | ~1 µs |
| Share of US equities volume | 50%+ |
| Uptime requirement | 24/7 |

---

## Cybersecurity Threat Landscape

| Threat | Description |
|--------|-------------|
| **Latency Attacks** | Weaponizing time — injecting microsecond delays to make competitors' data obsolete, gaining unfair market advantage. |
| **Data Tampering** | Poisoning price/volume feeds — unauthorized changes trigger wrong algorithmic decisions, causing flash crashes. |
| **DDoS Attacks** | Flooding trading infrastructure with traffic, causing system downtime and financial losses within seconds. |
| **Man-in-the-Middle** | Intercepting trading communications between exchange and firm — exposing sensitive order data and strategies. |
| **Unauthorized Access** | Compromised credentials allow fraudulent trades or theft of proprietary trading algorithms. |
| **Algorithm Theft** | Exfiltration of trading algorithms — IP theft giving competitors an illegal edge and regulatory exposure. |

---

## Technical Monitoring & Anomaly Detection

**Data flow:** Market Exchange → Apache Kafka (TLS 1.3 + SASL) → Logstash (parse, transform, enrich) → Elasticsearch (index & store) → Kibana (dashboards & alerts) → Kill Switch (auto-disconnect)

### Anomaly Detection Logic

| Step | Action | Timing |
|------|--------|--------|
| 1 — Monitor | Kibana watches latency & volume in real-time | Continuous |
| 2 — Detect | Threshold breach? Abnormal pattern? Suspicious access? | <1ms |
| 3 — Alert | Alert fired via Elasticsearch Watcher rules | Within 1 second |
| 4 — Kill Switch | Algorithm instantly disconnected from exchange | <1ms response |
| 5 — Log & Recover | Forensic logs preserved for post-mortem | Restore <3 seconds |

---

## Secure Communication & Access Control

### Secure Communication
- TLS 1.3 encryption protects all data in transit
- Mutual TLS (mTLS) used between Kafka, Elasticsearch & Kibana
- All channels are secured end-to-end
- Zero Trust + network segmentation applied
- Encrypted FIX protocol for order messaging
- Regular certificate rotation & lifecycle management

### Access Control
- Role-Based Access Control (RBAC) by job function
- Least Privilege Principle enforced on all accounts
- Multi-Factor Authentication (MFA) required
- Full Audit Logging of all system actions
- API key management with rate limiting
- Privileged Access Workstations (PAW) for admins

---

## System & Network Architecture

```
EXCHANGE LAYER
  Market Exchange — Real-time data feed (10.0.0.0/24 — DMZ)

EDGE LAYER
  FPGA Gateway — Tick-to-Trade | Smart NIC | Kernel Bypass (10.0.1.0/24)
  Hardware Sanity Checks — Packet filtering & validation

NETWORK CORE
  FPGA-based Trading Engine — Ultra-low latency execution (10.0.2.0/24 — Internal VLAN)
  Arista 7130 / Cisco Nexus — VLAN Micro-segmentation <100ns
  Firewall + IDS/IPS — DDoS mitigation | Intrusion detection

STORAGE LAYER
  NVMe Arrays — High-throughput | Kafka & ES indexing
  AES-256 + mTLS Transport — Replication factor: 3

MGMT LAYER
  OOB Management Network — Jump Host | MFA gated access
  RBAC + Audit Logging — Zero Trust | Least Privilege
```

---

## Implementation & Demonstration (Slide 8)

**Core Technologies:**
- Apache Kafka — Secure high-throughput streaming
- ELK Stack — Logstash + Elasticsearch + Kibana
- Hybrid Architecture: Kafka on-premise + ELK on cloud
- Security: TLS 1.3 + mTLS, SASL/SCRAM, RBAC, Kill Switch

```bash
# 1. Create Secure Kafka Topic
kafka-topics.sh --create --topic market-data \
  --partitions 12 --replication-factor 3 \
  --bootstrap-server 10.0.1.10:9094 --security-protocol SASL_SSL

# 2. Producer — publish live market tick
echo '{"sym":"AAPL","price":182.5,"ts":1717900800}' | \
  kafka-console-producer.sh --topic market-data \
  --bootstrap-server 10.0.1.10:9094 --producer.config ssl.properties

# 3. Consumer — read & verify stream
kafka-console-consumer.sh --topic market-data --from-beginning \
  --bootstrap-server 10.0.1.10:9094 --consumer.config ssl.properties
# Output: {"sym":"AAPL","price":182.5,"ts":1717900800}
```

**Live Kibana Dashboard — Real System Output:**
- Latency Spike Detection: median latency spikes to 800µs — Kibana flags anomaly, triggering Kill Switch
- Live Symbol Price Feed: GOOG, AAPL, TSLA, MSFT median prices ~$305–315 — confirms live Kafka stream integrity
- Median Volume: 2,513 — real-time volume tracking; unusual drops trigger anomaly alerts instantly

---

## Failure & Recovery Scenarios

### 4-Stage Protocol

**1 — Detection**
- ELK/Kafka detects strategy drift or network failure
- Network failure: missed heartbeat >500ms timeout triggers alert

**2 — Intervention**
- Hardware Kill-Switch triggered
- Pending orders purged immediately
- Algorithm disconnected from exchange

**3 — Failover**
- Deterministic switch to hot-standby node
- Hot-standby synced via Kafka replication (factor 3) — state lag <1ms
- Secondary data center takes over
- Zero interruption to market position

**4 — Recovery**
- Post-mortem log analysis in Elasticsearch
- Auto-restore: replay Kafka offset from last committed checkpoint
- Phased re-entry after verification

### Kill Switch Protocol
```
ELK detects anomaly → Threshold check → Kafka consumer halted
  → Exchange gateway disconnected → Audit log written
```

---

## Policies, Procedures & Governance

### Security Policies
- All streams use TLS 1.3 + mTLS encryption — TLS 1.3 removes legacy cipher suites; mTLS ensures both sides are authenticated, critical between Kafka brokers
- RBAC + MFA enforced on Kafka, ELK & trading systems
- Anomalies auto-trigger the Kill Switch
- Algorithm changes must be sandbox tested first — untested algo changes caused the 2010 Flash Crash; sandbox prevents live-market feedback loops
- Logs retained minimum 7 years (Reg SCI)

### Incident Response

| Phase | Action | Timeframe | Role |
|-------|--------|-----------|------|
| Detection | ELK/Kibana identifies anomaly | 0–30s | SOC Analyst |
| Containment | Kill Switch activates instantly | <1s | Automated System |
| Investigation | Forensic analysis in Elasticsearch | 0–2h | Security Engineer |
| Eradication | Patch vulnerabilities | 2–8h | Dev + SecOps Team |
| Recovery | Manual verification + phased restart | 8–24h | Head of Trading + CISO |
| Lessons Learned | Update detection rules | Post-incident | All teams |

### Governance & Compliance
- Full adherence to Regulation SCI and MiFID II
- Quarterly security audits & penetration testing
- Annual policy review and team training
- Implements CIA + Accountability principles

---

## Security Architecture Summary

```
Market Exchange (Untrusted / Zone 1)
      │
      │ TLS 1.3 — FIX/FAST protocol, all traffic validated at FW#1
      ▼
Firewall #1 / DMZ (10.0.0.0/24 — Zone 2)
  Allow: 9094/TLS only | IDS/IPS inline | DDoS mitigation
      │
      │ mTLS
      ▼
ON-PREMISES (10.0.0.0/16 — Zone 3 — Trusted)
  ┌──────────────────────────────────────────────────┐
  │  FPGA Gateway (10.0.1.0/24 — VLAN 10)           │
  │  Tick-to-Trade | Smart NIC | Kernel Bypass        │
  │  Hardware Sanity Checks | Rate-limit at wire speed │
  │                                                    │
  │  Kafka Cluster (10.0.1.10–12:9094 SASL_SSL)      │
  │  SASL/SCRAM-SHA-256, ACLs, Replication=3          │
  │                                                    │
  │  FPGA Trading Engine (10.0.2.0/24 — VLAN 20)     │
  │  Isolated — no internet route                      │
  │                                                    │
  │  NVMe Storage (10.0.3.0/24 — AES-256 at rest)    │
  │  Kafka logs, cert store, audit trail               │
  └──────────────────────────────────────────────────┘
      │
      │ IPsec VPN (AES-256) — Firewall #2 allows VPN only outbound
      ▼
CLOUD VPC — ELK Stack (172.16.0.0/16 — Zone 4)
  ┌──────────────────────────────────────────────────┐
  │  Logstash (172.16.1.10)                           │
  │  Port 5044/TLS | SG: allow from VPN only          │
  │  IAM Role: logstash-ingest-role (write-only to ES)│
  │           │                                        │
  │           ▼                                        │
  │  Elasticsearch (172.16.2.10–12)                   │
  │  Port 9200/TLS | SG: Logstash + Kibana only       │
  │  IAM: es-read-write (Logstash), es-read-only (Kibana)│
  │  AWS KMS cert rotation every 90 days              │
  │  CloudWatch + S3 audit logs — immutable, 7yr      │
  │           │                                        │
  │           ▼                                        │
  │  Kibana Dashboard (172.16.3.10)                   │
  │  Port 5601/HTTPS | MFA | RBAC (kibana-viewer)     │
  │  Watcher alerts — latency >800µs triggers alert   │
  │  Trust boundary: fully isolated from on-prem VLAN │
  └──────────────────────────────────────────────────┘
      │
      │ [Latency > 800µs OR consumer lag > 5,000 msgs?]
      │ YES
      ▼
Kill Switch (Hardware FPGA level — <1ms response)
  │  Algorithm disconnected from exchange instantly
  │  Pending orders purged
  └──► Audit log written (Elasticsearch + WORM S3 — 7-year, Reg SCI)

POST-INCIDENT RECOVERY PIPELINE:
  Analysis (query ES logs) → Eradication (patch stack/network)
    → System Restore (phased re-entry) → Improvement (update detection rules)

Full Flow:
  Exchange → [TLS 1.3] → FW#1/DMZ → [mTLS:9094] → Kafka (VLAN10)
    → [IPsec AES-256 VPN] → Logstash → Elasticsearch → Kibana
```

**Trust Boundaries:**
- Zone 1 = Untrusted Internet
- Zone 2 = Semi-trusted DMZ (FW#1 separates from Z1)
- Zone 3 = Trusted On-Prem (FW#2 separates from Z2)
- Zone 4 = Cloud VPC (IPsec VPN tunnel AES-256 separates from Z3)

---

## Key Storage, Certificate Rotation & Audit Logs

### Key Storage
- **AWS KMS (cloud)** — all ELK stack TLS/mTLS private keys; access restricted to IAM roles only
- **On-prem NVMe (10.0.3.0/24)** — Kafka broker keystores (JKS format); AES-256 encrypted at rest
- **HashiCorp Vault** — dynamic secret injection for Kafka SASL/SCRAM credentials; no hardcoded passwords anywhere
- **IPsec VPN pre-shared keys** — stored in HSM (Hardware Security Module); tamper-evident, FIPS 140-2 compliant

### Certificate Rotation
- **AWS KMS** auto-rotates ELK TLS certs every 90 days — zero manual intervention; old key versions retained for decrypt only
- **Kafka mTLS certs** — 90-day rotation via cert-manager (K8s operator); rolling restart with zero downtime; brokers negotiate new cert while old remains valid for in-flight connections
- **Kibana HTTPS cert** — Let's Encrypt auto-renewal via ACM (AWS Certificate Manager); alerts 30 days before expiry
- **Expiry monitoring** — Kibana Watcher alert fires 30 days before any cert expiry; SOC ticket auto-created in JIRA

### Audit Log Locations
- **Kafka broker access logs** — NVMe local (10.0.3.0/24) + mirrored to S3 (immutable, 7yr) via Kafka MirrorMaker
- **Elasticsearch security events** — AWS CloudWatch Logs (real-time) + S3 Glacier (long-term archive); Object Lock prevents deletion
- **Kill switch events** — written to Elasticsearch index + simultaneously to WORM S3 bucket; forensic-grade tamper-proof record
- **API access (Kibana/ES)** — AWS CloudTrail; every read/write by IAM role timestamped; meets Reg SCI + MiFID II audit requirements

---

## Failure & Recovery Deep-Dive

### Heartbeat & Timeout Specifics
- **Kafka broker heartbeat** — sent every 100ms; if broker misses 5 consecutive heartbeats (500ms timeout), ZooKeeper marks it dead and triggers leader re-election automatically
- **Network failure detection** — ELK Watcher monitors Kafka consumer lag every 250ms; if lag exceeds 5,000 messages OR latency spikes above 800µs, anomaly alert fires within 1 second
- **FPGA hardware watchdog** — if no valid tick received from exchange within 200ms, hardware kill signal sent; bypass mode activated to prevent stale data trading

### Hot-Standby State Replication & Auto-Restore
- Hot-standby synced via Kafka replication factor 3: all 3 broker replicas receive every write simultaneously — state lag between primary and standby consistently <1ms
- Automated state restoration: on failover, standby node reads last committed Kafka offset from ZooKeeper — replays from that exact point; no manual steps, no data loss; typical restore time <3 seconds
- Secondary data centre: geographically separated; receives Kafka MirrorMaker replication every 500ms; full takeover in under 30 seconds if primary DC loses power

---

## Case Study: 2010 Flash Crash

| Stat | Value |
|------|-------|
| DJIA points dropped | ~1,000 (~9%) |
| Temporary market value lost | $1T+ |
| Algorithmic sell order size | $4.1B |
| Duration | <30 minutes |

**Primary Causes:**
- Execution of a large $4.1B algorithmic sell order (Waddell & Reed)
- Aggressive HFT feedback loops amplified selling
- Rapid liquidity evaporation in milliseconds
- Inadequate real-time monitoring & risk controls

### How Our Architecture Directly Prevents Each Root Cause

| Root Cause | 2010 Failure | Our Fix |
|------------|-------------|---------|
| No real-time visibility | No system monitored the cascade — HFT firms were blind until DJIA had already dropped 600 points; humans couldn't react in milliseconds | Kafka + ELK detects volume and latency anomalies in <1ms; alert fires before the cascade can form — machine speed vs machine speed |
| No automated stop | Algos had no kill mechanism; continued executing the $4.1B sell order even as prices collapsed — feedback loop was self-reinforcing with no circuit breaker at the algo level | Hardware Kill Switch at FPGA level — algo disconnected from exchange in <1ms on anomaly; feedback loop physically impossible once kill switch fires |
| Untested algo deployed live | Waddell & Reed's sell algorithm was not stress-tested for low-liquidity conditions; no sandbox environment validated its behaviour before deployment to live markets | Mandatory sandbox testing with replayed historical Kafka data including the May 6 2010 scenario — algo cannot reach production without CISO sign-off |
| Speed vs security trade-off | Firms chose raw speed; no security layer meant no way to stop runaway execution | Secure low-latency architecture — TLS 1.3 adds <1µs overhead; security and speed are not mutually exclusive |

---

## Technology Justification & Design Decisions

### Why Kafka over RabbitMQ / Pulsar?
- Kafka handles millions of msgs/sec — RabbitMQ tops out ~50k msgs/sec (unsuitable for HFT volumes)
- Kafka log replay (offsets) enables forensic audit — critical for Reg SCI compliance
- Pulsar offers similar throughput but lacks the mature ELK integration ecosystem Kafka provides
- Kafka replication factor 3 ensures zero data loss — no equivalent in RabbitMQ default config

### Why ELK over Splunk / Grafana / Datadog?
- ELK is open-source — no per-GB ingestion cost; Splunk at HFT log volumes = prohibitive licensing
- Native Kafka–Logstash connector: tight pipeline integration without custom middleware
- Grafana is metrics-only; ELK handles full log forensics required for post-incident root-cause analysis
- Datadog requires cloud egress — on-premises ELK keeps sensitive trading data within the security perimeter

### Why Mutual TLS (mTLS)?
- Standard TLS only authenticates the server; in HFT, a rogue client injecting false data is equally dangerous — mTLS forces both sides to present valid certificates
- Prevents MitM attacks between Kafka brokers — a compromised broker cannot impersonate a legitimate node
- AWS KMS auto-rotates certificates every 90 days — eliminates manual cert management risk

### Why TLS 1.3 over TLS 1.2?
- TLS 1.2 supports weak ciphers (RC4, 3DES) — exploitable via POODLE/BEAST attacks
- TLS 1.3 removes all weak cipher suites entirely, mandates forward secrecy (ECDHE), and reduces handshake to 1-RTT — cutting latency while improving security; critical in HFT where every microsecond counts

### Why FPGA + Kernel Bypass?
- FPGA = a reprogrammable chip that executes trade logic in hardware (nanoseconds) rather than software (microseconds); acts as the security gateway, validating every order before it reaches the exchange
- Kernel bypass (DPDK/RDMA): data travels directly from NIC to application, skipping the OS (~10–50µs saved); reduces the software attack surface
- FPGA enforces rate limits and anomaly thresholds at wire speed — no software vulnerability can bypass it, as the logic is burned into silicon

### Why Zero Trust + Network Segmentation?
- In HFT, a single compromised internal node can exfiltrate live order flow
- Zero Trust means every connection is verified regardless of origin — no implicit trust for internal traffic
- VLAN micro-segmentation ensures a breach in the Kafka VLAN cannot reach the FPGA engine VLAN, containing blast radius

### Why Sandbox Testing for Algo Changes?
- The 2010 Flash Crash was triggered by an untested algo deployed directly to live markets — it created a self-reinforcing feedback loop
- Sandbox testing with replayed historical Kafka data catches runaway execution before live deployment
- Mandatory per governance policy; CISO sign-off required before any algo reaches production

### Data Retention & Disposal Procedure
- **Retention:** 7 years per Reg SCI (CloudWatch + S3 immutable storage)
- **Disposal:** After 7-year period, CISO and Compliance Officer issue formal disposal approval; data purged via AWS S3 Object Lock expiry + cryptographic erasure (AES-256 key deletion)
- **Governance chain:** Annual policy review by CISO → Board Audit Committee sign-off required before any disposal

---

## Scalability

| Metric | Value |
|--------|-------|
| Kafka throughput capacity | 1M+ msg/sec per cluster |
| Scaling method | Horizontal — add brokers under load, no downtime; Kafka partitions auto-rebalance across new nodes |
| Traffic spike handling | Consumer group lag monitored; Kibana alerts if queue depth exceeds 10k msgs — triggers auto-scaling |

---

## Governance (RACI)

| Role | R | A | C | I |
|------|---|---|---|---|
| CISO (Policy Owner) | R | A | — | I |
| Head of Trading | — | A | C | I |
| SecOps / Dev Team | R | — | C | — |
| Compliance Officer | — | A | — | I |
| Board Audit Committee | — | A | — | I |

Annual policy review cycle; quarterly penetration testing sign-off required by CISO.

---

## Compliance References

- **Regulation SCI** — 7-year log retention (CloudWatch + S3 immutable), audit trails, incident response
- **MiFID II Article 17** — Kill switch mandatory for algorithmic trading; sandbox testing before deployment
- **CIA Triad** — Confidentiality (TLS 1.3 / AES-256), Integrity (SASL/SCRAM auth), Availability (replication=3)
- **Zero Trust** — Every connection verified regardless of origin; VLAN micro-segmentation limits blast radius

---

## Key Takeaways

- **Speed & Security coexist** — real-time Kafka streaming without sacrificing low-latency
- **Anomaly Detection is feasible** — Kafka + ELK enables real-time monitoring of suspicious patterns
- **Automated Protection works** — Kill Switch disconnects compromised algorithms instantly
- **Architecture:** Exchange → Kafka → Logstash → Elasticsearch → Kibana → Kill Switch
- **Compliance achieved** — fully aligns with Regulation SCI, MiFID II — CIA + Accountability
- **Key lesson from Flash Crash** — automation & monitoring are not optional; they are essential

> *Security is not an option in HFT — it is a prerequisite.*
