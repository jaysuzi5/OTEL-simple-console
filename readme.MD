# Create venv
python -m venv .venv
source .venv/bin/activate

# Install minimum OTEL
```bash
pip install opentelemetry-sdk 
pip install opentelemetry-exporter-otlp
```

# Run with OTEL
```bash
python simple-console.py
```

# More for OTEL environment variables:
https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/
https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/

