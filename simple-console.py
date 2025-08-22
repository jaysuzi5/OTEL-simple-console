import logging
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

import os

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://otel.home.com"
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"
os.environ["OTEL_SERVICE_NAME"] = "sum-service"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up OTEL tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter()  # reads OTEL_EXPORTER_OTLP_ENDPOINT env
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)  # type: ignore

def add_numbers(a: int, b: int) -> int:
    with tracer.start_as_current_span("add_numbers"):
        logger.info("Starting add_numbers(%s, %s)", a, b)
        time.sleep(0.5)
        result = a + b
        logger.info("Finished add_numbers: result=%s", result)
        return result

if __name__ == "__main__":
    logger.info("App start")
    with tracer.start_as_current_span("main"):
        total = add_numbers(5, 7)
        logger.info("App completed, total=%s", total)
