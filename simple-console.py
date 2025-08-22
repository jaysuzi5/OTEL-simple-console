import logging
import os
import random
import time
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter


# --- Setup Environment Variables: Hard coding for simplicity ---
# These are standard OTEL environment variables
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://otel.home.com"
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"
os.environ["OTEL_SERVICE_NAME"] = "simple-console"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- TRACES ----
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_span_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(otlp_span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)  # type: ignore

# ---- METRICS ----
otlp_metric_exporter = OTLPMetricExporter()
metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Histogram to record sum values
sum_histogram = meter.create_histogram(
    name="sum_values",
    unit="1",
    description="Histogram of sum results",
)

# Counter to count how many times a specific sum value was hit
sum_counter = meter.create_counter(
    name="sum_count",
    unit="1",
    description="Number of times each sum result was observed",
)

def child_method():
    '''
    Simple method just to add a little more interest to the trace
    '''
    with tracer.start_as_current_span("child_method"):
        delay = random.uniform(0, 2)  # random decimal between 0–2
        time.sleep(delay)
        logger.info("Finished child_method (delay=%.2fs)", delay)

def sibling_method():
    '''
    Simple method just to add a little more interest to the trace
    '''
    with tracer.start_as_current_span("sibling_method"):
        delay = random.uniform(0, 2)  # random decimal between 0–2
        time.sleep(delay)
        logger.info("Finished sibling_method (delay=%.2fs)", delay)

def add_numbers(a: int, b: int) -> int:
    '''
    Adds two numbers together
    Has a trace span and two custom metrics
    '''
    with tracer.start_as_current_span("add_numbers"):
        logger.info("Starting add_numbers(%s, %s)", a, b)
        delay = random.uniform(0, 2)  # random decimal between 0–2
        time.sleep(delay)
        result = a + b
        logger.info("Finished add_numbers: result=%s (delay=%.2fs)", result, delay)

        # Record metrics
        sum_histogram.record(result)
        sum_counter.add(1, {"sum_result": str(result)})
        child_method()

        return result

if __name__ == "__main__":
    logger.info("App start")
    with tracer.start_as_current_span("main"):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        total = add_numbers(a, b)
        sibling_method()
        logger.info("App completed, total=%s", total)
