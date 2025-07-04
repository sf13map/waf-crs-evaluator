# Purpose
This repository provides a local testbed for evaluating HTTP request compliance against the OWASP Core Rule Set (CRS), running on the ModSecurity WAF engine.

It is designed as a faithful technical mirror of the production environment used in Azure Application Gateway (APG), which leverages the same CRS rule base. This allows for early detection of blocking rules and facilitates debugging before deployment.

This environment enables explicit identification of the rule IDs triggered in case of non-compliance, making diagnostics and upstream adjustments easier.

# Project Structure

```text
WafOwaspCrs/
├── backend/
│   ├── Dockerfile
│   └── app.py
├── waf/
│   └── modsec-exclusions.conf
├── nginx-conf/
│   └── nginx.conf # Include if required, ensuring the volume is mapped in docker-compose.yml
└── docker-compose.yml
```

# How It Works
Send an HTTP GET or POST request (using curl, Postman, etc.) to the URL:
http://localhost:8080/endpoint
	•	The server returns HTTP 200 if the request passes all CRS rules
	•	The server returns HTTP 403 if the request is blocked by a CRS rule


Exemple HTTP 200
```sh
curl -i -X POST "http://localhost:8080/endpoint" \
  -H "Content-Type: application/json" \
  --data '{"username": "admin"}'
```

Exemple HTTP 403 : 
```sh
curl -i -X POST "http://localhost:8080/endpoint" \
  -H "Content-Type: application/json" \
  --data '{"username": "admin\u0000"}'
```

# First Launch
```sh
git clone https://github.com/sf13map/waf-crs-evaluator.git
cd waf-crs-evaluator
docker compose up --build -d
````

# Clean Restart
```sh
docker compose down -v
docker compose build
docker compose up -d
docker compose ps 
```

# Containers
The stack includes:
- A Python Flask backend (handling /endpoint)
- A ModSecurity WAF container with OWASP CRS v4
- Customizable configuration via modsec-exclusions.conf

Logs
```sh
docker compose logs backend
docker compose logs waf
```

Check containers
```sh
docker compose exec backend sh
docker compose exec waf sh
```


# Identifying Blocking Rules
```sh
docker compose logs -f waf | grep --color -E 'id "[0-9]{6}"|ModSecurity'
```
Look for the ruleId field in the JSON log output (from ModSecurity).

Note:
Rule 949110 indicates a threshold breach (anomaly score), not the primary cause.
To determine the actual rule(s) that triggered the block, search for the specific ruleId values prior to 949110.

# Disabling a Rule
To exclude a specific CRS rule, edit the modsec-exclusions.conf file.

Example:
```sh
SecRuleRemoveById 920271
````

# CRS Version
The Docker image owasp/modsecurity-crs:nginx uses a rolling tag, always pointing to the latest major stable release (currently CRS v4.x).

To check the exact version in use:
```sh
docker compose logs waf | grep -m1 -o 'OWASP_CRS/[0-9.]\+'
```

#  Paranoia Level (PL)

The Paranoia Level (PL) determines how strict the WAF behavior is:
- PL1: Baseline (default) – suitable for most production environments
- PL2: Stricter, may require tuning and compatibility testing
- PL3: Very strict, recommended for sensitive APIs
- PL4: Maximum enforcement, usually combined with explicit rule exclusions

Each CRS rule is annotated with its applicable level (e.g., paranoia-level:2).
In this project, the paranoia level is set via the docker-compose.yml file.

#  Resources
-	Azure WAF (APG) — uses OWASP Core Rule Set v3.2 : https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/application-gateway-crs-rulegroups-rules
	
-	Official Docker Image (ModSecurity + Core Rule Set) : https://hub.docker.com/r/owasp/modsecurity-crs/
	
-	OWASP CRS Project Website : https://coreruleset.org
	
-	OWASP Core Rule Set – GitHub Repository : https://github.com/coreruleset/coreruleset.git

- ModSecurity WAF Engine :
    - https://github.com/owasp-modsecurity/ModSecurity/wiki/
    - https://github.com/coreruleset/modsecurity-crs-docker/blob/main/README.md